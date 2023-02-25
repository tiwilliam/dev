import re
from typing import Optional, Tuple

from dev.helpers import run_command

git_url_pattern = re.compile(r'git@(?P<host>.+):(?P<organization>.+)\/(?P<repository>.+)\.git')
http_url_pattern = re.compile(
    r'http(s)?\:\/\/(?P<host>.+)\/(?P<organization>.+)\/(?P<repository>.+)\.git'
)


class GitHelper:
    @staticmethod
    def setup_config() -> str:
        output = run_command(
            'git config --global url."git@github.com:".insteadOf "https://github.com/"',
            output=True,
            silent=True,
        )
        assert output is not None
        return output

    @staticmethod
    def current_branch() -> str:
        output = run_command('git branch --show-current', output=True, silent=True)
        assert output is not None
        return output

    @staticmethod
    def remote_origin_url() -> str:
        output = run_command(
            'git config --get remote.origin.url', output=True, silent=True, ok_exit_codes=[0, 1]
        )
        assert output is not None
        return output

    @staticmethod
    def get_remote_origin() -> Optional[Tuple[str, str, str]]:
        remote_url = GitHelper.remote_origin_url()
        return GitHelper.parse_url(remote_url)

    @staticmethod
    def parse_url(remote_url: str) -> Optional[Tuple[str, str, str]]:
        git_url_match = git_url_pattern.match(remote_url)
        if git_url_match:
            return (
                git_url_match.group('host'),
                git_url_match.group('organization'),
                git_url_match.group('repository'),
            )

        http_url_match = http_url_pattern.match(remote_url)
        if http_url_match:
            return (
                http_url_match.group('host'),
                http_url_match.group('organization'),
                http_url_match.group('repository'),
            )

        return None
