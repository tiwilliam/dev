from unittest import TestCase
from unittest.mock import patch

import pytest
import docopt

from dev.tasks.internal.clone import Clone


class TestClone(TestCase):
    def setUp(self):
        Clone.base_path = '/dummy'

    def test_up_without_arg(self):
        with pytest.raises(docopt.DocoptExit):
            Clone([], extra_args=[])

    @patch('dev.tasks.internal.clone.ParentShellHelper')
    @patch('dev.tasks.internal.clone.GitHelper')
    @patch('dev.tasks.internal.clone.run_command')
    def test_up(self, run_command_mock, git_helper_mock, parent_shell_mock):
        git_helper_mock.get_remote_origin.return_value = ('github.com', 'a', 'b')

        Clone(['c'], extra_args=[])

        git_helper_mock.setup_config.assert_called_once_with()
        git_helper_mock.get_remote_origin.assert_called_once_with()
        run_command_mock.assert_called_once_with('git clone https://github.com/a/c.git /dummy/github.com/a/c')
        parent_shell_mock.run.assert_called_once_with('cd /dummy/github.com/a/c')

        git_helper_mock.parse_url.assert_not_called()

    @patch('dev.tasks.internal.clone.os.path.isdir')
    @patch('dev.tasks.internal.clone.ParentShellHelper')
    @patch('dev.tasks.internal.clone.GitHelper')
    @patch('dev.tasks.internal.clone.run_command')
    def test_up_already_cloned(self, run_command_mock, git_helper_mock, parent_shell_mock, isdir_mock):
        isdir_mock.return_value = True
        git_helper_mock.get_remote_origin.return_value = ('github.com', 'a', 'b')

        Clone(['c'], extra_args=[])

        git_helper_mock.get_remote_origin.assert_called_once_with()
        parent_shell_mock.run.assert_called_once_with('cd /dummy/github.com/a/c')

        git_helper_mock.setup_config.assert_not_called()
        git_helper_mock.parse_url.assert_not_called()
        run_command_mock.assert_not_called()

    @patch('dev.task.error_console.print')
    @patch('dev.tasks.internal.clone.ParentShellHelper')
    @patch('dev.tasks.internal.clone.GitHelper')
    @patch('dev.tasks.internal.clone.run_command')
    def test_up_by_name_when_not_in_git_repo(
        self, run_command_mock, git_helper_mock, parent_shell_mock, console_print_mock
    ):
        git_helper_mock.get_remote_origin.return_value = None

        with pytest.raises(SystemExit):
            Clone(['c'], extra_args=[])

        git_helper_mock.get_remote_origin.assert_called_once_with()
        console_print_mock.assert_called_once_with(
            'Failed to run [b]Clone[/] task: Can not clone using only repository name when not in a repository',
            style='red'
        )

        git_helper_mock.setup_config.assert_not_called()
        git_helper_mock.parse_url.assert_not_called()
        run_command_mock.assert_not_called()
        parent_shell_mock.run.assert_not_called()

    @patch('dev.task.error_console.print')
    @patch('dev.tasks.internal.clone.ParentShellHelper')
    @patch('dev.tasks.internal.clone.GitHelper')
    @patch('dev.tasks.internal.clone.run_command')
    def test_up_by_name_when_not_github(self, run_command_mock, git_helper_mock, parent_shell_mock, console_print_mock):
        git_helper_mock.get_remote_origin.return_value = ('gitlab.com', 'a', 'b')

        with pytest.raises(SystemExit):
            Clone(['c'], extra_args=[])

        git_helper_mock.get_remote_origin.assert_called_once_with()
        console_print_mock.assert_called_once_with(
            'Failed to run [b]Clone[/] task: Can only clone Github repositories by name', style='red'
        )

        git_helper_mock.setup_config.assert_not_called()
        git_helper_mock.parse_url.assert_not_called()
        run_command_mock.assert_not_called()
        parent_shell_mock.run.assert_not_called()

    @patch('dev.tasks.internal.clone.ParentShellHelper')
    @patch('dev.tasks.internal.clone.GitHelper')
    @patch('dev.tasks.internal.clone.run_command')
    def test_up_by_org_and_name(self, run_command_mock, git_helper_mock, parent_shell_mock):
        Clone(['c/d'], extra_args=[])

        git_helper_mock.setup_config.assert_called_once_with()
        run_command_mock.assert_called_once_with('git clone https://github.com/c/d.git /dummy/github.com/c/d')
        parent_shell_mock.run.assert_called_once_with('cd /dummy/github.com/c/d')

        git_helper_mock.get_remote_origin.assert_not_called()
        git_helper_mock.parse_url.assert_not_called()

    @patch('dev.tasks.internal.clone.ParentShellHelper')
    @patch('dev.tasks.internal.clone.GitHelper.setup_config')
    @patch('dev.tasks.internal.clone.GitHelper.get_remote_origin')
    @patch('dev.tasks.internal.clone.run_command')
    def test_up_by_url(self, run_command_mock, get_remote_origin_mock, setup_config_mock, parent_shell_mock):
        Clone(['https://github.com/c/d.git'], extra_args=[])

        setup_config_mock.assert_called_once_with()
        run_command_mock.assert_called_once_with('git clone https://github.com/c/d.git /dummy/github.com/c/d')
        parent_shell_mock.run.assert_called_once_with('cd /dummy/github.com/c/d')

        get_remote_origin_mock.assert_not_called()

    @patch('dev.task.error_console.print')
    @patch('dev.tasks.internal.clone.ParentShellHelper')
    @patch('dev.tasks.internal.clone.GitHelper.setup_config')
    @patch('dev.tasks.internal.clone.GitHelper.get_remote_origin')
    @patch('dev.tasks.internal.clone.run_command')
    def test_up_with_invalid_url(
        self, run_command_mock, get_remote_origin_mock, setup_config_mock, parent_shell_mock, console_print_mock
    ):
        with pytest.raises(SystemExit):
            Clone(['ftp://pass/invalid/url'], extra_args=[])

        console_print_mock.assert_called_once_with(
            'Failed to run [b]Clone[/] task: Could not parse [b]ftp://pass/invalid/url[/] for clone', style='red'
        )

        setup_config_mock.assert_not_called()
        run_command_mock.assert_not_called()
        parent_shell_mock.run.assert_not_called()
        get_remote_origin_mock.assert_not_called()
