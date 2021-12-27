from typing import Any, Optional

from schema import Or, Schema

from dev.console import console
from dev.exceptions import NonZeroReturnCodeError
from dev.helpers import run_command
from dev.task import Task


class Npm(Task):
    __schema__ = Schema(Or(str, [str]))
    __description__ = 'Run npm install -g'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        if isinstance(args, str):
            to_install = [args]
        else:
            to_install = args

        for pkg in to_install:
            if self.already_installed(pkg):
                continue
            self.install_package(pkg)

    def already_installed(self, package: str) -> bool:
        try:
            run_command(f'npm list -g {package}', silent=True)
        except NonZeroReturnCodeError as e:
            if e.code == 1:
                return False
            raise
        return True

    def install_package(self, package: str) -> None:
        run_command(f'npm install -g {package}')
        console.print(f'npm package [b]{package}[/] installed successfully', style='green')
