import os
from typing import Optional

from dev.helpers import run_command


class HomebrewHelper:

    @staticmethod
    def prefix() -> Optional[str]:
        return run_command('brew --prefix', output=True, silent=True)

    @classmethod
    def already_installed(cls, formula: str) -> bool:
        if '/' in formula:
            # Remove tapped repository from formula name
            formula = formula.split('/')[-1]
        path = f'{cls.prefix()}/opt/{formula}'
        return os.path.isdir(path)

    @classmethod
    def cask_already_installed(cls, cask: str) -> bool:
        path = f'{cls.prefix()}/Caskroom/{cask}'
        return os.path.isdir(path)

    @classmethod
    def install_formula(cls, formula: str) -> bool:
        if cls.already_installed(formula):
            return False
        run_command(f'brew install {formula}')
        return True

    @classmethod
    def install_cask(cls, cask: str) -> None:
        if cls.cask_already_installed(cask):
            return
        run_command(f'brew install --cask {cask}')
