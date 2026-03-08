from dataclasses import dataclass, field

@dataclass
class CommandResult:
    success: bool
    message: str
    category: str
    metadata: dict = field(default_factory=dict)

    @staticmethod
    def failure(message: str, category: str, metadata: dict = None):
        return CommandResult(success=False, message=message, category=category, metadata=metadata or {})

def _success(message: str, category: str, metadata: dict = None):
    return CommandResult(success=True, message=message, category=category, metadata=metadata or {})

CommandResult.success = staticmethod(_success)
