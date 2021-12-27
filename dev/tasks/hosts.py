from typing import Any, Optional

from schema import Schema

from dev.console import console
from dev.exceptions import NonZeroReturnCodeError
from dev.helpers import run_command
from dev.task import Task


class Hosts(Task):
    __schema__ = Schema({str: str})
    __description__ = 'Configure hosts file'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        hosts_to_write = []

        for host, address in args.items():
            data = f'{address:<20} {host}'
            try:
                run_command(f'grep -q "{data}" /etc/hosts', silent=True)
            except NonZeroReturnCodeError as e:
                if e.code != 1:
                    raise
                hosts_to_write.append(data)

        if not hosts_to_write:
            return

        data = '\n'.join(hosts_to_write)
        console.print(f'=> Writing hosts to /etc/hosts:\n{data}', style='blue')
        run_command(f'echo "{data}" >> /etc/hosts', sudo=True, silent=True)
