import os
from pathlib import Path
from typing import Any, Optional

from schema import Schema

from dev import environment
from dev.helpers import run_command
from dev.helpers.homebrew import HomebrewHelper
from dev.helpers.shadowenv import ShadowenvHelper
from dev.task import Task


class Node(Task):
    __schema__ = Schema(str)
    __description__ = 'Install a specific Node version'

    def init(self, version: str) -> None:
        self.node_path = self.get_node_path(version)

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        HomebrewHelper.install_formula('nodenv')

        self.init(version)
        self.install_node(version)
        self.create_local_env(version)

        ShadowenvHelper.configure_provider("node", version, self.node_path)

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        self.init(version)

    def install_node(self, version: str) -> None:
        if self.node_already_installed:
            return

        run_command(f'nodenv install --skip-existing {version}')

    def create_local_env(self, version: str) -> None:
        run_command(f'nodenv local {version}')
        environment.prepend_path(f'{self.node_path}/bin')

    @property
    def node_already_installed(self) -> bool:
        return os.path.isdir(self.node_path)

    def get_node_path(self, version: str) -> Path:
        prefix = run_command('nodenv root', output=True, silent=True)
        return Path(f'{prefix}/versions/{version}')
