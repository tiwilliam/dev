import io
import os
import subprocess
import sys
from importlib import import_module
from pkgutil import iter_modules
from typing import Callable, List, Optional, Tuple

from dev import environment, pty
from dev.console import console
from dev.exceptions import NonZeroReturnCodeError, TaskNotFoundError

root_path = os.path.dirname(os.path.abspath(__file__ + '/..'))


def snake_to_camel(word: str) -> str:
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def camel_to_snake(word: str) -> str:
    return ''.join(['_' + c.lower() if c.isupper() else c for c in word]).lstrip('_')


def task_to_class(task_name: str) -> Callable:
    try:
        if f'dev.tasks.internal.{task_name}' in sys.modules:
            return getattr(sys.modules[f'dev.tasks.internal.{task_name}'], snake_to_camel(task_name))
        return getattr(sys.modules[f'dev.tasks.{task_name}'], snake_to_camel(task_name))
    except KeyError:
        raise TaskNotFoundError(task_name)


def load_local_taks(directory: str = 'devs') -> None:
    for _, module_name, _ in iter_modules([directory]):
        sys.path.append(directory)
        sys.modules.setdefault(f'dev.tasks.{module_name}', import_module(module_name))


def run_command(
    command: str,
    output: bool = False,
    silent: bool = False,
    sudo: bool = False,
    wrap_sudo_in_shell: bool = True,
    ok_exit_codes: List[int] = [0],
    env: Optional[dict] = None
) -> Optional[str]:
    all_env = environment.env

    if env:
        all_env.update(env)

    if not silent:
        console.print(f'=> Running command: {command}', style='blue')

    if sudo or silent:
        return subprocess_run(
            command,
            output=output,
            sudo=sudo,
            wrap_sudo_in_shell=wrap_sudo_in_shell,
            ok_exit_codes=ok_exit_codes,
            env=all_env
        )

    return pty_spawn(command, output=output, ok_exit_codes=ok_exit_codes, env=all_env)


def subprocess_run(
    command: str,
    output: bool = False,
    sudo: bool = False,
    wrap_sudo_in_shell: bool = True,
    ok_exit_codes: List[int] = [0],
    env: Optional[dict] = None,
) -> Optional[str]:
    if sudo:
        command = command.replace('"', '\\"')
        if wrap_sudo_in_shell:
            command = f'sudo bash -c "{command}"'
        else:
            command = f'sudo {command}'
    completed_process = subprocess.run(command, capture_output=True, shell=True, env=env)
    exit_code = completed_process.returncode
    if exit_code not in ok_exit_codes:
        raise NonZeroReturnCodeError(exit_code, command)
    if output:
        return completed_process.stdout.decode().strip()
    return None


def pty_spawn(
    command: str,
    output: bool = False,
    ok_exit_codes: List[int] = [0],
    env: Optional[dict] = None,
) -> Optional[str]:
    pty_output = io.StringIO()
    argv: Tuple[str, ...] = ('bash', '-c', command)

    def read_pty(fd: int) -> bytes:
        data = os.read(fd, 1024)
        if output is True:
            pty_output.write(data.decode())
        return data

    status = pty.spawn(argv, master_read=read_pty, env=env)
    exit_code = pty.waitstatus_to_exitcode(status)

    if exit_code not in ok_exit_codes:
        raise NonZeroReturnCodeError(exit_code, command)

    if output:
        pty_output.seek(0)
        return pty_output.read().strip()

    return None


def current_shell() -> Optional[str]:
    return run_command("ps | cut -d '-' -f 2 | head -2 | tail -1", output=True)
