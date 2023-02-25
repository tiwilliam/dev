import os
from unittest import TestCase
from unittest.mock import call, patch

import pytest

from dev.helpers import root_path
from dev.tasks.internal.cd import Cd, SearchEntry


class TestCd(TestCase):
    def setUp(self):
        Cd.base_path = '/dummy'  # type: ignore

    @patch('dev.tasks.internal.cd.IntPrompt')
    @patch('dev.tasks.internal.cd.ParentShellHelper')
    @patch('dev.tasks.internal.cd.Cd.list_entries')
    def test_up_without_arg(self, list_entries_mock, parent_shell_mock, int_prompt_mock):
        int_prompt_mock.ask.return_value = 1
        list_entries_mock.return_value = [
            SearchEntry(host='github.com', organization='acme', repository='b')
        ]

        Cd([], extra_args=[])

        int_prompt_mock.ask.assert_called_once()
        parent_shell_mock.run.assert_called_once_with('cd /dummy/github.com/acme/b')

    @patch('dev.tasks.internal.cd.IntPrompt')
    @patch('dev.tasks.internal.cd.ParentShellHelper')
    @patch('dev.tasks.internal.cd.Cd.list_entries')
    @patch('dev.tasks.internal.cd.Table.add_row')
    def test_up_fuzzy_search(
        self, add_row_mock, list_entries_mock, parent_shell_mock, int_prompt_mock
    ):
        list_entries_mock.return_value = [
            SearchEntry(repository='abc', host='github.com', organization='acme'),
            SearchEntry(repository='bcd', host='github.com', organization='acme'),
            SearchEntry(repository='cde', host='github.com', organization='acme'),
        ]

        Cd(['a'], extra_args=[])

        add_row_mock.assert_not_called()
        int_prompt_mock.ask.assert_not_called()
        parent_shell_mock.run.assert_called_once_with('cd /dummy/github.com/acme/abc')

        int_prompt_mock.ask.reset_mock()
        add_row_mock.reset_mock()
        parent_shell_mock.run.reset_mock()

        int_prompt_mock.ask.return_value = 2
        Cd(['b'], extra_args=[])

        int_prompt_mock.ask.assert_called_once()
        add_row_mock.assert_has_calls(
            [
                call('1', 'abc', 'acme', 'github.com', '/dummy/github.com/acme/abc'),
                call('2', 'bcd', 'acme', 'github.com', '/dummy/github.com/acme/bcd'),
            ]
        )
        parent_shell_mock.run.assert_has_calls([call('cd /dummy/github.com/acme/bcd')])

        int_prompt_mock.ask.reset_mock()
        add_row_mock.reset_mock()
        parent_shell_mock.run.reset_mock()

        int_prompt_mock.ask.return_value = 3
        Cd(['c'], extra_args=[])

        int_prompt_mock.ask.assert_called_once()
        add_row_mock.assert_has_calls(
            [
                call('1', 'abc', 'acme', 'github.com', '/dummy/github.com/acme/abc'),
                call('2', 'bcd', 'acme', 'github.com', '/dummy/github.com/acme/bcd'),
                call('3', 'cde', 'acme', 'github.com', '/dummy/github.com/acme/cde'),
            ]
        )
        parent_shell_mock.run.assert_has_calls([call('cd /dummy/github.com/acme/cde')])

    @patch('dev.tasks.internal.cd.Cd.list_entries')
    @patch('dev.tasks.internal.cd.error_console.print')
    def test_up_fuzzy_search_without_hits(self, console_print_mock, list_entries_mock):
        list_entries_mock.return_value = [
            SearchEntry(host='github.com', organization='acme', repository='abc'),
        ]

        with pytest.raises(SystemExit):
            Cd(['d'], extra_args=[])

        console_print_mock.assert_called_once_with(
            'Could not find any repositories matching [b]d[/]', style='red'
        )

    @patch('dev.tasks.internal.cd.IntPrompt')
    @patch('dev.tasks.internal.cd.Cd.list_entries')
    @patch('dev.tasks.internal.cd.error_console.print')
    def test_up_select_out_of_range(self, console_print_mock, list_entries_mock, int_prompt_mock):
        list_entries_mock.return_value = [
            SearchEntry(host='github.com', organization='acme', repository='abc'),
            SearchEntry(host='github.com', organization='acme', repository='bcd'),
        ]

        int_prompt_mock.ask.return_value = 3

        with pytest.raises(SystemExit):
            Cd(['b'], extra_args=[])

        console_print_mock.assert_called_once_with('Answer must be in interval 1 to 2', style='red')

    @patch('dev.tasks.internal.cd.IntPrompt')
    @patch('dev.tasks.internal.cd.Table.add_row')
    @patch('dev.tasks.internal.cd.SearchEntry.path')
    def test_up_list_entries(self, path_mock, add_row_mock, int_prompt_mock):
        Cd.git_identifier = ".fakegit"
        Cd.base_path = os.path.abspath(f'{root_path}/../tests/data/src')  # type: ignore

        int_prompt_mock.ask.return_value = 1

        Cd(['a'], extra_args=[])

        add_row_mock.assert_has_calls(
            [
                call('1', 'abc_one', 'MasonData', 'github.com', path_mock),
                call('2', 'abc_onprem', None, 'example.com', path_mock),
                call('3', 'abc_root', None, None, path_mock),
                call('4', 'abc_two', 'MasonData', 'github.com', path_mock),
            ]
        )
