import os
from pathlib import Path
from typing import Any, Optional

from schema import Or, Schema

from dev import environment
from dev.helpers import run_command
from dev.helpers.homebrew import HomebrewHelper
from dev.helpers.shadowenv import ShadowenvHelper
from dev.task import Task


class Ruby(Task):
    __schema__ = Schema(Or(str, int, float))
    __description__ = 'Install a specific Ruby version'

    def init(self, version: str) -> None:
        self.ruby_path = self.get_ruby_path(version)

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        HomebrewHelper.install_formula('rbenv')

        self.init(version)
        self.install_ruby(version)
        self.create_local_env(version)

        ShadowenvHelper.configure_provider("ruby", version, self.ruby_path)

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        self.init(version)

    def install_ruby(self, version: str) -> None:
        if self.ruby_already_installed:
            return

        run_command(f'rbenv install --skip-existing {version}')

    def create_local_env(self, version: str) -> None:
        run_command(f'rbenv local {version}')
        environment.prepend_path(f'{self.ruby_path}/bin')

    @property
    def ruby_already_installed(self) -> bool:
        return os.path.isdir(self.ruby_path)

    def get_ruby_path(self, version: str) -> Path:
        prefix = run_command('rbenv root', output=True, silent=True)
        return Path(f'{prefix}/versions/{version}')
