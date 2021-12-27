import sys
from typing import Any, Optional

from docopt import DocoptExit
from schema import Schema

from dev.console import error_console
from dev.helpers import root_path
from dev.task import InternalTask


class Init(InternalTask):
    __schema__ = Schema([str])
    __description__ = 'Initialize shell environment'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args or len(args) != 1:
            raise DocoptExit

        shell = args[0]
        supported_shells = ['bash', 'zsh']

        if shell not in supported_shells:
            supported = ', '.join(supported_shells)
            error_console.print(f'Could not init shell [b]{shell}[/]. Supported shells: {supported}', style='red')
            sys.exit(1)

        with open(f'{root_path}/data/dev-init-{shell}.sh', 'r') as fp:
            data = fp.read().replace('{dev-bare}', sys.argv[0])
            print(data)
