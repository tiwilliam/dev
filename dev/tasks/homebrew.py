from typing import Any, Optional

from schema import Or, Schema

from dev.helpers.homebrew import HomebrewHelper
from dev.task import Task


class Homebrew(Task):
    __schema__ = Schema(Or(str, [str]))
    __description__ = 'Install formulas on macOS'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        if isinstance(args, str):
            args = [args]

        for formula in args:
            HomebrewHelper.install_formula(formula)
