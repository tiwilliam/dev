from pathlib import Path
from typing import Any, Optional

from schema import Schema

from dev import environment
from dev.helpers import run_command
from dev.helpers.homebrew import HomebrewHelper
from dev.helpers.shadowenv import ShadowenvHelper
from dev.task import Task


class Rust(Task):
    __schema__ = Schema(str)
    __description__ = 'Install a specific Rust version'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        version = args

        if HomebrewHelper.install_formula('rustup-init'):
            run_command('rustup-init -y')

        run_command(f'rustup default {version}')
        environment.prepend_path(f'{self.rust_path}/bin')

        ShadowenvHelper.configure_provider('rust', version, self.rust_path)

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        ...

    @property
    def rust_path(self) -> Path:
        prefix = run_command('rustc --print sysroot', output=True, silent=True)
        return Path(f'{prefix}/bin')
