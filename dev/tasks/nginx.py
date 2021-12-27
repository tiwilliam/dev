import os
from typing import Any, Dict, Optional

import jinja2
from schema import Schema

from dev.helpers import run_command
from dev.helpers.homebrew import HomebrewHelper
from dev.task import Task


class Nginx(Task):
    __schema__ = Schema({
        'sites': [str],
    })
    __description__ = 'Configure and control nginx'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        HomebrewHelper.install_formula('nginx')
        homebrew_prefix = run_command('brew --prefix', silent=True, output=True)

        template_loader = jinja2.FileSystemLoader(searchpath=".")
        template_env = jinja2.Environment(loader=template_loader)

        for site in args['sites']:
            template = template_env.get_template(site)
            output = template.render(**self.get_variables(site))

            filename = os.path.basename(site)
            with open(f'{homebrew_prefix}/etc/nginx/servers/{filename}', 'w+') as fp:
                fp.write(output)

        self.install_sudoers(homebrew_prefix)

        # Stop nginx if it is running as the user, we need root to bind 80 and 443
        run_command('brew services stop nginx', silent=True, ok_exit_codes=[0, 1])
        run_command('brew services stop nginx', sudo=True, wrap_sudo_in_shell=False)
        run_command('brew services start nginx', sudo=True, wrap_sudo_in_shell=False)

    def install_sudoers(self, homebrew_prefix) -> None:
        sudoers_target = '/private/etc/sudoers.d/brew_services_nginx'
        if os.path.exists(sudoers_target):
            return

        with open('/tmp/brew_services_nginx', 'w+') as fp:
            fp.write(f'%staff ALL=(root) NOPASSWD: {homebrew_prefix}/bin/brew services stop nginx\n')
            fp.write(f'%staff ALL=(root) NOPASSWD: {homebrew_prefix}/bin/brew services start nginx\n')

        run_command('chown root /tmp/brew_services_nginx', sudo=True)
        run_command(f'mv /tmp/brew_services_nginx {sudoers_target}', sudo=True)

    def get_variables(self, site: str) -> Dict[str, Any]:
        return {
            'repo_base_path': os.path.abspath(os.path.dirname(site) + '/..'),
        }
