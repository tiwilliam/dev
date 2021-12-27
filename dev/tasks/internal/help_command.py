from typing import Any, Optional

from rich.table import Table
from schema import Or, Schema

from dev.config import config
from dev.console import console
from dev.task import InternalTask


class HelpCommand(InternalTask):
    __schema__ = Schema(Or(None, str))

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if args:
            console.print(f'Could not find command [b]{args}', style='red')

        table = Table(title='Builtin commands', show_header=True, header_style="bold")
        table.add_column("Command", min_width=10)
        table.add_column("Description", min_width=50)

        table.add_row('up', 'Setup your local environment')
        table.add_row('down', 'Shutdown your local environment')

        for command, desc in InternalTask.subclasses():
            if command.startswith('help_'):
                continue
            table.add_row(command, desc)

        console.print(table)

        table = Table(title='Custom commands', show_header=True, header_style="bold")
        table.add_column("Command", min_width=10)
        table.add_column("Description", min_width=50)

        for command, desc in config.custom_commands:
            table.add_row(command, desc)

        if table.row_count:
            console.print(table)
