from pathlib import Path
from typing import Any, Optional

from schema import Schema

from dev import environment
from dev.helpers import run_command
from dev.helpers.homebrew import HomebrewHelper
from dev.helpers.shadowenv import (
    ShadowenvHelper,
)
from dev.task import Task


class Rust(Task):
    __schema__ = Schema(str)
    __description__ = 'Install a specific Rust version'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        HomebrewHelper.install_formula('rustup-init')

        self.install_rust(version)
        self.rust_path = self.get_rust_path(version)
        environment.prepend_path(f'{self.rust_path}/bin')

        ShadowenvHelper.configure_provider('rust', version, self.rust_path)

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        ...

    def install_rust(self, version: str) -> None:
        run_command(f'rustup default {version}')

    def get_rust_path(self, version: str) -> Path:
        prefix = run_command('rustc --print sysroot', output=True, silent=True)
        return Path(f'{prefix}/bin')
