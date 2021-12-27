import sys
from typing import Any, List, Optional

from docopt import DocoptExit
from schema import Schema

from dev.config import config
from dev.console import error_console
from dev.helpers import run_command
from dev.helpers.git import GitHelper
from dev.task import InternalTask


class Open(InternalTask):
    __schema__ = Schema([str])
    __description__ = 'Open links in your browser'

    builtin_targets: List[str] = ['pr', 'issue']

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args or len(args) < 1 or len(args) > 1:
            raise DocoptExit

        target = args[0]
        if target in self.builtin_targets:
            self.handle_builtin(target)
            return

        open_config = config.devfile.get('open', {})
        url = open_config.get(target)
        if not url:
            valid_values = list(open_config.keys()) + self.builtin_targets
            joined_valid_values = '[/], [b]'.join(valid_values)
            error_console.print(
                f'No URL configured for [b]{target}[/].',
                f'Valid targets are [b]{joined_valid_values}[/].',
                style='red'
            )
            sys.exit(1)

        self.open(url)

    def open(self, url: str) -> None:
        run_command(f'open {url}')

    def handle_builtin(self, target: str) -> None:
        if target == 'pr':
            self.handle_pr()
        elif target == 'issue':
            self.handle_issue()

    def ensure_github_remote(self) -> None:
        remote = GitHelper.get_remote_origin()
        if remote and remote[0] == 'github.com':
            return
        error_console.print('Feature only supported on Github remotes.', style='red')
        sys.exit(1)

    def handle_pr(self) -> None:
        self.ensure_github_remote()

        branch = GitHelper.current_branch()
        if branch in ['main', 'master']:
            error_console.print('Cannot open PR for default branch')
            sys.exit(1)

        components = GitHelper.get_remote_origin()
        if not components:
            return

        _, organization, repository = components
        self.open(f'https://github.com/{organization}/{repository}/pull/{branch}')

    def handle_issue(self) -> None:
        self.ensure_github_remote()

        components = GitHelper.get_remote_origin()
        if not components:
            return

        _, organization, repository = components
        self.open(f'https://github.com/{organization}/{repository}/issues/new')
