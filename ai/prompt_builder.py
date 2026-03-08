class PromptBuilder:
    def build(self, task_type: str, topic: str, personal_memory: list = None,
              detail_level: str = "short") -> str:
        role = (
            "You are Jarvis, a highly capable personal assistant. "
            "You provide clear, structured, and concise responses."
        )

        memory_context = ""
        if personal_memory:
            snippets = []
            for m in personal_memory:
                snippets.append("- " + m["content"])
            if snippets:
                memory_context = (
                    "\n\nRelevant personal context:\n"
                    + "\n".join(snippets[:10])
                )

        instructions = {
            "draft": (
                "Create a well-structured document on the following topic. "
                "Include an introduction, main sections with clear headings, detailed content "
                "in each section, and a conclusion. Be thorough and professional."
            ),
            "research": (
                "Create a comprehensive, detailed research report on the following topic. "
                "Structure it as a proper academic-style report with: "
                "1. Executive Summary, 2. Introduction, 3. Background/Literature Review, "
                "4. Detailed Analysis with subsections, 5. Key Findings, "
                "6. Conclusions, 7. References (cite real sources where possible). "
                "Make it multi-page quality with deep detail. Use proper headings and bullet points."
            ),
            "explain": self._explain_instruction(detail_level),
            "plan": (
                "Create a detailed, structured action plan for the following. "
                "Include: 1. Overview/Goal, 2. Prerequisites, "
                "3. Phase-by-phase breakdown with specific tasks and timelines, "
                "4. Key milestones, 5. Resources needed, "
                "6. Potential challenges and mitigation strategies, "
                "7. Success metrics. Make it actionable and professional. "
                "CRITICAL: If the plan spans multiple days or weeks (e.g., a 30-day plan), "
                "you MUST generate and detail EVERY SINGLE DAY or phase. "
                "DO NOT cluster days together (e.g., 'Days 5-10'). "
                "DO NOT summarize or stop early. Provide the full complete timeline."
            ),
            "notes": (
                "Create concise, well-organized study notes on the following topic. "
                "Use short bullet points, key definitions, and important takeaways. "
                "Keep it scannable and easy to review. No lengthy paragraphs."
            ),
            "code": (
                "Write clean, working code for the following request. "
                "Output ONLY the code with helpful comments. "
                "Do NOT wrap the code in markdown code blocks (no ``` markers). "
                "Do NOT include any explanations before or after the code. "
                "Just the raw code that can be saved directly as a file."
            ),
            "analyze": (
                "Perform a detailed analysis/comparison on the following topic. "
                "Structure your response as data-friendly content:\n"
                "- Use markdown tables for all comparisons\n"
                "- Include numerical ratings or scores where applicable (1-10 scale)\n"
                "- Create clear categories for comparison\n"
                "- Include a summary section with key takeaways\n"
                "- Format data so it can be easily converted to spreadsheet form"
            )
        }

        instruction = instructions.get(task_type, instructions["explain"])
        prompt = role + "\n\n" + instruction + memory_context + "\n\nTopic: " + topic
        return prompt

    def _explain_instruction(self, detail_level: str) -> str:
        if detail_level == "short":
            return (
                "Answer in exactly 2-3 sentences. Be precise and direct. "
                "Give only the core answer, no examples or elaboration."
            )
        elif detail_level == "medium":
            return (
                "Explain in one concise paragraph (4-6 sentences). "
                "Include one brief example if helpful. Stay focused."
            )
        else:
            return (
                "Explain the topic clearly but concisely. "
                "STRICT LIMIT: Your entire response must be at most 4 sentences long. "
                "Do not use markdown formatting. "
                "At the very end of your explanation, always add the exact phase: "
                "'Would you like me to create a full document on this?'"
            )
