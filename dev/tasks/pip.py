import os
from typing import Any, Optional

from schema import Or, Schema

from dev.console import console
from dev.exceptions import TaskError
from dev.helpers import run_command
from dev.task import Task


class Pip(Task):
    __schema__ = Schema(Or(None, str, [str]))
    __description__ = 'Run pip install'

    pip_flags = '--disable-pip-version-check -q'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if args is None:
            to_install = ['requirements.txt']
        elif isinstance(args, str):
            to_install = [args]
        else:
            to_install = args

        for pkg_or_filename in to_install:
            if pkg_or_filename.endswith('.txt'):
                self.install_requirements(pkg_or_filename)
                continue
            self.install_package(pkg_or_filename)

    def install_requirements(self, filename: str) -> None:
        if not os.path.exists(filename):
            raise TaskError(f'{filename} does not exist')
        run_command(f'pip {self.pip_flags} install -r {filename}')
        console.print(f'Python dependencies from [b]{filename}[/] installed successfully', style='green')

    def install_package(self, package: str) -> None:
        run_command(f'pip {self.pip_flags} install {package}')
        console.print(f'Python package [b]{package}[/] installed successfully', style='green')
