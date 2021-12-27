from typing import Any, Optional

from rich.table import Table
from schema import Or, Schema

from dev.console import console
from dev.task import InternalTask, Task


class HelpTask(InternalTask):
    __schema__ = Schema(Or(None, str))

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if args:
            console.print(f'Could not find task [b]{args}[/]', style='red')

        table = Table(title='Tasks', show_header=True, header_style='bold')
        table.add_column('Task')
        table.add_column('Description')

        for name, description in Task.subclasses():
            if name in InternalTask.tasks():
                continue
            table.add_row(name, description)

        console.print(table)
