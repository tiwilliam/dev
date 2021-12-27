class TaskError(Exception):
    ...


class CommandNotFoundError(Exception):
    ...


class TaskNotFoundError(Exception):

    def __init__(self, task: str) -> None:
        self.task = task


class NonZeroReturnCodeError(Exception):

    def __init__(self, code: int, command: str) -> None:
        self.code = code
        self.command = command
