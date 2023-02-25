from unittest.mock import patch

import docopt
import pytest

from dev.tasks.internal.init import Init


def test_up_without_arg():
    with pytest.raises(docopt.DocoptExit):
        Init([], extra_args=[])


@patch('dev.tasks.internal.init.print')
def test_up_bash(print_mock):
    Init(['bash'], extra_args=[])

    script_output = print_mock.call_args_list[0][0][0]

    assert 'exec 100>& -' in script_output
    assert 'exec 101>& -' in script_output


@patch('dev.tasks.internal.init.print')
def test_up_zsh(print_mock):
    Init(['zsh'], extra_args=[])

    script_output = print_mock.call_args_list[0][0][0]

    assert 'exec {DEV_SHELL_RFD}>& -' in script_output
    assert 'exec {DEV_SHELL_WFD}>& -' in script_output


def test_up_fish():
    with pytest.raises(SystemExit):
        Init(['fish'], extra_args=[])
