import os
from typing import Callable, Dict, Optional

from dev.console import console
from dev.helpers import current_shell, run_command
from dev.helpers.homebrew import HomebrewHelper
from dev.helpers.parent_shell import ParentShellHelper

SHADOWENV_CONFIG_DIRECTORY = '.shadowenv.d'


def ensure_shadowenv_installed(func: Callable) -> Callable:
    def inner(*args: str, **kwargs: str) -> None:
        if HomebrewHelper.install_formula('shadowenv'):
            ShadowenvHelper.install_init_script()
        if not os.path.isdir(SHADOWENV_CONFIG_DIRECTORY):
            os.mkdir(SHADOWENV_CONFIG_DIRECTORY)
        func(*args, **kwargs)
        run_command('shadowenv trust', silent=True)

    return inner


def append_to_file(filename: str, data: str) -> None:
    with open(filename, 'a+') as fp:
        fp.seek(0)
        if data in fp.read():
            return
        fp.write(f'{data}\n')


class ShadowenvHelper:
    @classmethod
    def install_init_script(cls) -> None:
        home_path = os.environ.get('HOME')
        if not home_path:
            console.print(
                'Could not find HOME environment variable:',
                'Failed to install shadowenv, set it up manually:',
                'https://shopify.github.io/shadowenv/getting-started/#add-to-your-shell-profile',
                style='red'
            )
            return
        shell = current_shell()
        if shell == 'zsh':
            append_to_file(f'{home_path}/.zshrc', 'eval "$(shadowenv init zsh)"')
            ParentShellHelper.run(f'source {home_path}/.zshrc')
        else:
            append_to_file(f'{home_path}/.profile', 'eval "$(shadowenv init bash)"')
            ParentShellHelper.run(f'source {home_path}/.profile')

    @classmethod
    @ensure_shadowenv_installed
    def configure_provider(
        cls,
        provider: str,
        provider_version: str,
        provider_path: Optional[str] = None,
        env_name: str = 'PROVIDER_PATH'
    ) -> None:
        with open(f'{SHADOWENV_CONFIG_DIRECTORY}/500_{provider}.lisp', 'w+') as fp:
            fp.write(f'(provide "{provider}" "{provider_version}")\n')
            if provider_path:
                fp.write(f'(env/set "{env_name}" "{provider_path}")\n')
                fp.write(f'(env/prepend-to-pathlist "PATH" (path-concat (env/get "{env_name}") "bin"))\n')

    @classmethod
    @ensure_shadowenv_installed
    def set_environments(cls, environments: Dict[str, str]) -> None:
        with open(f'{SHADOWENV_CONFIG_DIRECTORY}/400_environment.lisp', 'w+') as fp:
            for k, v in environments.items():
                console.print(f'=> Setting environment variable {k} to {v}', style='blue')
                fp.write(f'(env/set "{k}" "{v}")\n')

    @classmethod
    def unset_environments(cls) -> None:
        path = f'{SHADOWENV_CONFIG_DIRECTORY}/400_environment.lisp'
        if os.path.exists(path):
            os.unlink(path)

    @classmethod
    def unconfigure_provider(cls, provider: str) -> None:
        path = f'{SHADOWENV_CONFIG_DIRECTORY}/500_{provider}.lisp'
        if os.path.exists(path):
            os.unlink(path)
