import os
import re
import sys
from pathlib import Path
from typing import Generator, List, Optional

from rich.prompt import IntPrompt
from rich.table import Table
from schema import Schema

from dev.console import console, error_console
from dev.helpers.parent_shell import ParentShellHelper
from dev.task import InternalTask

repo_pattern = re.compile(r'[a-zA-Z0-9\-\_\.]+')
org_and_repo_pattern = re.compile(r'[a-zA-Z0-9\-\_\.]+/[a-zA-Z0-9\-\_\.]+')


class SearchEntry:

    def __init__(self, repository: str, host: Optional[str] = None, organization: Optional[str] = None) -> None:
        self.repository: str = repository
        self.host: Optional[str] = host
        self.organization: Optional[str] = organization

    @property
    def path(self) -> str:
        return os.path.abspath(
            f'{Cd.base_path}/{self.host or str()}/{self.organization or str()}/{self.repository or str()}'
        )


class Cd(InternalTask):
    __schema__ = Schema([str])
    __description__ = 'Change directory'

    base_path: Path = Path(f'{os.environ["HOME"]}/src/')
    git_identifier: str = ".git"

    def up(self, args: Optional[str], extra_args: Optional[str]) -> None:
        selected_index: int
        selectable_entries: List[SearchEntry]
        search_entries: List[SearchEntry]

        search_entries = sorted(self.list_entries(self.base_path), key=lambda e: e.repository.lower())

        if not args or len(args) < 1:
            selectable_entries = search_entries
            selected_index = self.render_table(search_entries)
        else:
            arg = args[0]
            selected_index = 1
            search_pattern = re.compile(f'.*{re.escape(arg)}.*')

            selectable_entries = [entry for entry in search_entries if self.match_search_term(entry, search_pattern)]
            if len(selectable_entries) == 0:
                error_console.print(f'Could not find any repositories matching [b]{arg}[/]', style='red')
                sys.exit(1)

            if len(selectable_entries) > 1:
                selected_index = self.render_table(selectable_entries)

        ParentShellHelper.run(f'cd {selectable_entries[selected_index - 1].path}')

    def render_table(self, entries: List[SearchEntry], default_selection: int = 1) -> int:
        console.print('Found multiple matches, select which one you meant:', style='blue')

        table = Table(show_header=True, header_style="bold")
        table.add_column("Index", justify='center')
        table.add_column("Repository")
        table.add_column("Organization")
        table.add_column("Host")
        table.add_column("Path")

        for index, hit in enumerate(entries):
            table.add_row(str(index + 1), hit.repository, hit.organization, hit.host, hit.path)

        console.print(table)

        selected_index: int = IntPrompt.ask('Which one?', default=default_selection)
        if selected_index > len(entries) or selected_index <= 0:
            error_console.print(f'Answer must be in interval {1} to {len(entries)}', style='red')
            sys.exit(1)

        return selected_index

    def match_search_term(self, entry: SearchEntry, search_pattern: re.Pattern) -> Optional[re.Match]:
        return search_pattern.match(entry.repository)

    def is_git_repo(self, path: Path) -> bool:
        return (path / self.git_identifier).is_dir()

    def list_entries(self,
                     parent: Path,
                     grand_parent: Optional[Path] = None,
                     level: int = 0) -> Generator[SearchEntry, None, None]:
        level += 1
        for child in Path(parent).iterdir():
            if not child.is_dir():
                continue

            if not self.is_git_repo(child):
                yield from self.list_entries(parent=child, grand_parent=parent, level=level)
                continue

            parent_dir = os.path.basename(parent)
            child_dir = os.path.basename(child)

            if level == 1:
                # Repository without host and organization (src/repository-name)
                # grand_parent_dir = None
                #       parent_dir = src
                #        child_dir = repository-name
                yield SearchEntry(repository=child_dir)
            elif level == 2:
                # Repository without organization (src/example.com/repository-name)
                # grand_parent_dir = src
                #       parent_dir = example.com
                #        child_dir = repository-name
                yield SearchEntry(repository=child_dir, host=parent_dir)
            elif level == 3:
                # Repository with organization (src/example.com/company/repository-name)
                # grand_parent_dir = example.com
                #       parent_dir = company
                #        child_dir = repository-name
                grand_parent_dir = os.path.basename(str(grand_parent))
                yield SearchEntry(repository=child_dir, host=grand_parent_dir, organization=parent_dir)
