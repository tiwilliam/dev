import os
from pathlib import Path
from typing import Any, Optional

from schema import Schema

from dev import environment
from dev.helpers import run_command
from dev.helpers.homebrew import HomebrewHelper
from dev.helpers.shadowenv import ShadowenvHelper
from dev.task import Task


class Python(Task):
    __schema__ = Schema(str)
    __description__ = 'Install a specific Python version'

    def init(self, version: str) -> None:
        self.python_path = self.get_python_path(version)
        self.virtualenv_path = self.get_virtualenv_path(version)

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        HomebrewHelper.install_formula('pyenv')

        self.init(version)
        self.install_python(version)
        self.create_virtualenv(version)

        ShadowenvHelper.configure_provider("python", version, self.virtualenv_path, env_name='WORKON_HOME')

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        self.init(version)
        if self.virtualenv_already_created:
            run_command(f'rm -rf {self.virtualenv_path}')

    def install_python(self, version: str) -> None:
        if self.python_already_installed:
            return

        run_command(f'pyenv install --skip-existing {version}')

    def create_virtualenv(self, version: str) -> None:
        if not self.virtualenv_already_created:
            run_command(f'pyenv local {version}')
            run_command(f'pyenv exec python -m venv {self.virtualenv_path}')
        environment.prepend_path(f'{self.virtualenv_path}/bin')

    @property
    def python_already_installed(self) -> bool:
        return os.path.isdir(self.python_path)

    @property
    def virtualenv_already_created(self) -> bool:
        return os.path.isdir(self.virtualenv_path)

    def get_python_path(self, version: str) -> Path:
        prefix = run_command('pyenv root', output=True, silent=True)
        return Path(f'{prefix}/versions/{version}')

    def get_virtualenv_path(self, version: str) -> Path:
        return Path(f'{self.python_path}/virtualenvs/{environment.name}')
