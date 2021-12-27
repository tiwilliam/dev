import os
import re
from pathlib import Path
from typing import Any, Optional, Tuple

from docopt import DocoptExit
from schema import Schema

from dev.console import console
from dev.exceptions import TaskError
from dev.helpers import run_command
from dev.helpers.git import GitHelper
from dev.helpers.parent_shell import ParentShellHelper
from dev.task import InternalTask

repo_pattern = re.compile(r'^[a-zA-Z0-9\-\_\.]+$')
org_and_repo_pattern = re.compile(r'^([a-zA-Z0-9\-\_\.]+)/([a-zA-Z0-9\-\_\.]+)$')


class Clone(InternalTask):
    __schema__ = Schema([str])
    __description__ = 'Clone remote repository'

    base_path: Path = Path(f"{os.environ['HOME']}/src")

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args or len(args) < 1 or len(args) > 1:
            raise DocoptExit

        clone_url, clone_dir = self.parse_arg(args[0])

        if os.path.isdir(clone_dir):
            console.print(f'Already cloned in {clone_dir}')
        else:
            GitHelper.setup_config()
            run_command(f'git clone {clone_url} {clone_dir}')

        ParentShellHelper.run(f'cd {clone_dir}')

    def parse_arg(self, arg: str) -> Tuple[str, str]:
        repo_match = repo_pattern.match(arg)
        if repo_match:
            # dev clone dev
            remote_components = GitHelper.get_remote_origin()
            if not remote_components:
                raise TaskError('Can not clone using only repository name when not in a repository')

            host, organization, _ = remote_components
            if host != 'github.com':
                raise TaskError('Can only clone Github repositories by name')

            clone_url = f'https://github.com/{organization}/{arg}.git'
            clone_dir = f'{self.base_path}/github.com/{organization}/{arg}'
            return clone_url, clone_dir

        org_and_repo_match = org_and_repo_pattern.match(arg)
        if org_and_repo_match:
            # dev clone MasonData/dev
            organization, repository = org_and_repo_match.groups()
            clone_url = f'https://github.com/{organization}/{repository}.git'
            clone_dir = f'{self.base_path}/github.com/{organization}/{repository}'
            return clone_url, clone_dir

        url_components = GitHelper.parse_url(arg)
        if url_components:
            # dev clone https://github.com/MasonData/dev.git
            # dev clone git@github.com:MasonData/dev.git
            host, organization, repository = url_components
            clone_url = arg
            clone_dir = f'{self.base_path}/{host}/{organization}/{repository}'
            return clone_url, clone_dir

        raise TaskError(f'Could not parse [b]{arg}[/] for clone')
