from __future__ import annotations

import numpy as np
from PySide6.QtGui import QMatrix4x4, QOpenGLContext
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)

GL_BLEND = 0x0BE2
GL_PROGRAM_POINT_SIZE = 0x8642
GL_DEPTH_TEST = 0x0B71
GL_LEQUAL = 0x0203
GL_COLOR_BUFFER_BIT = 0x00004000
GL_DEPTH_BUFFER_BIT = 0x00000100
GL_SRC_ALPHA = 0x0302
GL_ONE = 1
GL_ONE_MINUS_SRC_ALPHA = 0x0303
GL_POINTS = 0x0000
GL_LINES = 0x0001
GL_FLOAT = 0x1406


_POINT_VERT = """
#version 330 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec4 a_color;
layout(location = 2) in float a_size;

uniform mat4 u_mvp;
out vec4 v_color;

void main() {
    gl_Position = u_mvp * vec4(a_position, 1.0);
    gl_PointSize = max(1.0, a_size);
    v_color = a_color;
}
"""


_POINT_FRAG = """
#version 330 core
in vec4 v_color;
out vec4 fragColor;

void main() {
    vec2 c = gl_PointCoord * 2.0 - vec2(1.0);
    float r2 = dot(c, c);
    if (r2 > 1.0) {
        discard;
    }
    float falloff = exp(-r2 * 2.6);
    fragColor = vec4(v_color.rgb, v_color.a * falloff);
}
"""


_LINE_VERT = """
#version 330 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec4 a_color;
uniform mat4 u_mvp;
out vec4 v_color;

void main() {
    gl_Position = u_mvp * vec4(a_position, 1.0);
    v_color = a_color;
}
"""


_LINE_FRAG = """
#version 330 core
in vec4 v_color;
out vec4 fragColor;

void main() {
    fragColor = v_color;
}
"""


class GPUParticleRenderer:
    def __init__(self) -> None:
        self._ctx = None
        self._f = None

        self._point_program: QOpenGLShaderProgram | None = None
        self._line_program: QOpenGLShaderProgram | None = None

        self._point_vbo: QOpenGLBuffer | None = None
        self._line_vbo: QOpenGLBuffer | None = None

        self._point_vao: QOpenGLVertexArrayObject | None = None
        self._line_vao: QOpenGLVertexArrayObject | None = None

    def initialize(self) -> None:
        self._ctx = QOpenGLContext.currentContext()
        if self._ctx is None:
            raise RuntimeError("OpenGL context is unavailable")
        self._f = self._ctx.functions()

        self._f.glEnable(GL_BLEND)
        self._f.glEnable(GL_PROGRAM_POINT_SIZE)
        self._f.glEnable(GL_DEPTH_TEST)
        self._f.glDepthFunc(GL_LEQUAL)

        self._point_program = self._build_program(_POINT_VERT, _POINT_FRAG)
        self._line_program = self._build_program(_LINE_VERT, _LINE_FRAG)

        self._point_vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self._point_vbo.create()
        self._point_vbo.bind()
        self._point_vbo.setUsagePattern(QOpenGLBuffer.DynamicDraw)
        self._point_vbo.allocate(1)
        self._point_vbo.release()

        self._line_vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self._line_vbo.create()
        self._line_vbo.bind()
        self._line_vbo.setUsagePattern(QOpenGLBuffer.DynamicDraw)
        self._line_vbo.allocate(1)
        self._line_vbo.release()

        self._point_vao = QOpenGLVertexArrayObject()
        self._point_vao.create()
        self._line_vao = QOpenGLVertexArrayObject()
        self._line_vao.create()

    def clear(self, width: int, height: int) -> None:
        if self._f is None:
            return
        self._f.glViewport(0, 0, width, height)
        self._f.glClearColor(0.02, 0.03, 0.09, 1.0)
        self._f.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def render_points(self, points: np.ndarray, mvp: QMatrix4x4, additive: bool = False) -> None:
        if self._f is None or self._point_program is None or self._point_vbo is None:
            return
        if points.size == 0:
            return

        data = np.ascontiguousarray(points.astype(np.float32))
        stride = 8 * 4

        self._point_program.bind()
        self._point_program.setUniformValue("u_mvp", mvp)

        self._point_vbo.bind()
        self._point_vbo.allocate(data.tobytes(), data.nbytes)

        self._point_program.enableAttributeArray(0)
        self._point_program.enableAttributeArray(1)
        self._point_program.enableAttributeArray(2)

        self._point_program.setAttributeBuffer(0, GL_FLOAT, 0, 3, stride)
        self._point_program.setAttributeBuffer(1, GL_FLOAT, 3 * 4, 4, stride)
        self._point_program.setAttributeBuffer(2, GL_FLOAT, 7 * 4, 1, stride)

        if additive:
            self._f.glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        else:
            self._f.glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._f.glDrawArrays(GL_POINTS, 0, int(data.shape[0]))

        self._point_program.disableAttributeArray(0)
        self._point_program.disableAttributeArray(1)
        self._point_program.disableAttributeArray(2)
        self._point_vbo.release()
        self._point_program.release()

    def render_lines(self, lines: np.ndarray, mvp: QMatrix4x4, additive: bool = False, width: float = 1.0) -> None:
        if self._f is None or self._line_program is None or self._line_vbo is None:
            return
        if lines.size == 0:
            return

        data = np.ascontiguousarray(lines.astype(np.float32))
        stride = 7 * 4

        self._line_program.bind()
        self._line_program.setUniformValue("u_mvp", mvp)

        self._line_vbo.bind()
        self._line_vbo.allocate(data.tobytes(), data.nbytes)

        self._line_program.enableAttributeArray(0)
        self._line_program.enableAttributeArray(1)

        self._line_program.setAttributeBuffer(0, GL_FLOAT, 0, 3, stride)
        self._line_program.setAttributeBuffer(1, GL_FLOAT, 3 * 4, 4, stride)

        self._f.glLineWidth(max(width, 1.0))
        if additive:
            self._f.glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        else:
            self._f.glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._f.glDrawArrays(GL_LINES, 0, int(data.shape[0]))

        self._line_program.disableAttributeArray(0)
        self._line_program.disableAttributeArray(1)
        self._line_vbo.release()
        self._line_program.release()

    def _build_program(self, vert_src: str, frag_src: str) -> QOpenGLShaderProgram:
        program = QOpenGLShaderProgram()
        if not program.addShaderFromSourceCode(QOpenGLShader.Vertex, vert_src):
            raise RuntimeError(f"Vertex shader compile failed: {program.log()}")
        if not program.addShaderFromSourceCode(QOpenGLShader.Fragment, frag_src):
            raise RuntimeError(f"Fragment shader compile failed: {program.log()}")
        if not program.link():
            raise RuntimeError(f"Shader link failed: {program.log()}")
        return program
