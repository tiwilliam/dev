import sys
from typing import Any, List, Optional, Tuple

from schema import Schema, SchemaError

from dev.console import error_console
from dev.exceptions import TaskError
from dev.helpers import camel_to_snake


class BaseTask:
    __schema__: Optional[Schema] = None
    __description__: Optional[str] = None

    def __init__(
        self, args: Optional[Any] = None, extra_args: Optional[Any] = None, direction: str = 'up'
    ) -> None:
        self.task_name = self.__class__.__name__
        self.validate(args)
        self.run_and_catch(args, extra_args, direction)

    def validate(self, args: Optional[Any]) -> None:
        if not self.__schema__:
            return
        try:
            self.__schema__.validate(args)
        except SchemaError as e:
            error_console.print(f'Failed to validate input to {self.task_name}: {e}', style='red')
            sys.exit(1)

    def run_and_catch(self, args: Optional[Any], extra_args: Optional[Any], direction: str) -> None:
        try:
            if direction == 'down':
                self.down(args, extra_args)
            else:
                self.up(args, extra_args)
        except TaskError as e:
            error_console.print(
                f'Failed to run [b]{self.task_name}[/] task: {e}',
                style='red',
            )
            sys.exit(1)

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        ...

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        ...

    @classmethod
    def subclasses(cls) -> List[Tuple[str, Optional[str]]]:
        return [(camel_to_snake(c.__name__), c.__description__) for c in cls.__subclasses__()]

    @classmethod
    def tasks(cls) -> List[str]:
        return [name for name, _ in cls.subclasses()]


class Task(BaseTask):
    ...


class InternalTask(BaseTask):
    ...
