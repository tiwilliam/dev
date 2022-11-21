import os
from typing import Any, Optional

from schema import Schema

from dev import environment
from dev.console import console
from dev.helpers import run_command
from dev.helpers.hash_cache import HashCacheHelper
from dev.helpers.homebrew import HomebrewHelper
from dev.task import Task


class Mkcert(Task):
    __schema__ = Schema({
        'key': str,
        'crt': str,
        'names': [str],
    })
    __description__ = 'Generate self-signed certificates'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        HomebrewHelper.install_formula('nss')
        HomebrewHelper.install_formula('mkcert')
        run_command('mkcert -install', silent=True)

        if not args['names']:
            console.print('No certificate names to generate', style='yellow')
            return

        key = args['key']
        crt = args['crt']
        joined_names = ' '.join(args['names'])

        if (os.path.exists(key) and os.path.exists(crt)
                and not HashCacheHelper.changed(environment.name + key + crt, joined_names)):
            return

        try:
            os.mkdir(os.path.dirname(key))
            os.mkdir(os.path.dirname(crt))
        except FileExistsError:
            ...

        run_command(f'mkcert -cert-file {crt} -key-file {key} {joined_names}')
