import os
from typing import Any, Optional

from schema import Schema

from dev.exceptions import TaskError
from dev.helpers import run_command
from dev.task import Task


class Pypi(Task):
    __schema__ = Schema(str)
    __description__ = 'Manage packages on PyPi'

    def up(self, command: Optional[Any], extra_args: Optional[Any]) -> None:
        if not os.environ.get('TWINE_USERNAME'):
            raise TaskError('You need to set TWINE_USERNAME')

        if not os.environ.get('TWINE_PASSWORD'):
            raise TaskError('You need to set TWINE_PASSWORD')

        if command == 'upload':
            self.build()
            self.upload()
        else:
            raise TaskError(f'Unknown argument [b]{command}[/]')

    def build(self) -> None:
        run_command('rm -rf dist')
        run_command('pip install --upgrade twine build')
        run_command('python -m build')

    def upload(self) -> None:
        run_command('python -m twine check dist/*')
        run_command('python -m twine upload dist/*')
