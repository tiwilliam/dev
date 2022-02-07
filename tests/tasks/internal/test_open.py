from unittest.mock import call, patch

import docopt
import pytest

from dev.tasks.internal.open import Open


@patch('dev.tasks.internal.open.run_command')
def test_up_without_argument(run_command_mock):
    with pytest.raises(docopt.DocoptExit):
        Open([], extra_args=[])
    run_command_mock.assert_not_called()


@patch('dev.tasks.internal.open.run_command')
def test_up_with_missing_target(run_command_mock):
    with pytest.raises(SystemExit):
        Open(['missing'])
    run_command_mock.assert_not_called()


@patch('dev.tasks.internal.open.GitHelper')
@patch('dev.tasks.internal.open.run_command')
def test_up_pr(run_command_mock, git_helper_mock):
    git_helper_mock.current_branch.return_value = 'feature'
    git_helper_mock.get_remote_origin.return_value = ('github.com', 'MasonData', 'repo')

    Open(['pr'])

    run_command_mock.assert_has_calls([
        call('open https://github.com/MasonData/repo/pull/feature'),
    ])


@patch('dev.tasks.internal.open.GitHelper')
@patch('dev.tasks.internal.open.error_console.print')
@patch('dev.tasks.internal.open.run_command')
def test_up_pr_on_gitlab(run_command_mock, error_console_mock, git_helper_mock):
    git_helper_mock.get_remote_origin.return_value = ('gitlab.com', 'MasonData', 'repo')

    with pytest.raises(SystemExit):
        Open(['pr'])

    run_command_mock.assert_not_called()
    error_console_mock.assert_called_once_with('Feature only supported on Github remotes.', style='red')


@patch('dev.tasks.internal.open.GitHelper')
@patch('dev.tasks.internal.open.error_console.print')
@patch('dev.tasks.internal.open.run_command')
def test_up_pr_on_main_branch(run_command_mock, error_console_mock, git_helper_mock):
    git_helper_mock.current_branch.return_value = 'main'
    git_helper_mock.get_remote_origin.return_value = ('github.com', 'MasonData', 'repo')

    with pytest.raises(SystemExit):
        Open(['pr'])

    run_command_mock.assert_not_called()
    error_console_mock.assert_called_once_with('Cannot open PR for default branch')


@patch('dev.tasks.internal.open.GitHelper')
@patch('dev.tasks.internal.open.run_command')
def test_up_gh(run_command_mock, git_helper_mock):
    git_helper_mock.current_branch.return_value = 'main'
    git_helper_mock.get_remote_origin.return_value = ('github.com', 'MasonData', 'repo')

    Open(['gh'])

    run_command_mock.assert_has_calls([
        call('open https://github.com/MasonData/repo'),
    ])


@patch('dev.tasks.internal.open.GitHelper')
@patch('dev.tasks.internal.open.error_console.print')
@patch('dev.tasks.internal.open.run_command')
def test_up_gh_on_gitlab(run_command_mock, error_console_mock, git_helper_mock):
    git_helper_mock.get_remote_origin.return_value = ('gitlab.com', 'MasonData', 'repo')

    with pytest.raises(SystemExit):
        Open(['gh'])

    run_command_mock.assert_not_called()
    error_console_mock.assert_called_once_with('Feature only supported on Github remotes.', style='red')


@patch('dev.tasks.internal.open.run_command')
@patch('dev.tasks.internal.open.config.devfile')
def test_up_custom_target(devfile_mock, run_command_mock):
    devfile_mock.get.return_value = {
        'alpha': 'https://example.com/alpha',
        'sierra': 'https://example.com/sierra',
        'tango': 'https://example.com/tango',
    }

    Open(['sierra'])

    run_command_mock.assert_has_calls([
        call('open https://example.com/sierra'),
    ])
