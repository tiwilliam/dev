"""Pseudo terminal utilities."""

# Bugs: No signal handling.  Doesn't set slave termios and window size.
#       Only tested on Linux.
# See:  W. Richard Stevens. 1992.  Advanced Programming in the
#       UNIX Environment.  Chapter 19.
# Author: Steen Lumholt -- with additions by Guido.

import os
import termios
from os import close, waitpid
from select import select
from termios import tcgetattr, tcsetattr
from tty import setraw
from typing import Callable, Tuple

__all__ = ["fork", "spawn", "waitstatus_to_exitcode"]

STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2

CHILD = 0


def fork() -> Tuple[int, int]:
    """fork() -> (pid, master_fd)
    Fork and make the child a session leader with a controlling terminal."""

    try:
        pid, fd = os.forkpty()
    except (AttributeError, OSError):
        ...
    else:
        if pid == CHILD:
            try:
                os.setsid()
            except OSError:
                ...
        return pid, fd

    master_fd, slave_fd = os.openpty()
    pid = os.fork()
    if pid == CHILD:
        # Establish a new session.
        os.setsid()
        os.close(master_fd)

        # Slave becomes stdin/stdout/stderr of child.
        os.dup2(slave_fd, STDIN_FILENO)
        os.dup2(slave_fd, STDOUT_FILENO)
        os.dup2(slave_fd, STDERR_FILENO)
        if slave_fd > STDERR_FILENO:
            os.close(slave_fd)

        # Explicitly open the tty to make it become a controlling tty.
        tmp_fd = os.open(os.ttyname(STDOUT_FILENO), os.O_RDWR)
        os.close(tmp_fd)
    else:
        os.close(slave_fd)

    # Parent and child process.
    return pid, master_fd


def _writen(fd: int, data: bytes) -> None:
    """Write all the data to a descriptor."""
    while data:
        n = os.write(fd, data)
        data = data[n:]


def _read(fd: int) -> bytes:
    """Default read function."""
    return os.read(fd, 1024)


def _copy(
    master_fd: int, master_read: Callable[[int], bytes] = _read, stdin_read: Callable[[int], bytes] = _read
) -> None:
    """Parent copy loop.
    Copies
            pty master -> standard output   (master_read)
            standard input -> pty master    (stdin_read)"""
    fds = [master_fd, STDIN_FILENO]
    while fds:
        rfds, _wfds, _xfds = select(fds, [], [])

        if master_fd in rfds:
            # Some OSes signal EOF by returning an empty byte string,
            # some throw OSErrors.
            try:
                data = master_read(master_fd)
            except OSError:
                data = b""
            if not data:  # Reached EOF.
                return  # Assume the child process has exited and is
                # unreachable, so we clean up.
            else:
                os.write(STDOUT_FILENO, data)

        if STDIN_FILENO in rfds:
            data = stdin_read(STDIN_FILENO)
            if not data:
                fds.remove(STDIN_FILENO)
            else:
                _writen(master_fd, data)


def spawn(
    argv: Tuple[str, ...],
    master_read: Callable[[int], bytes] = _read,
    stdin_read: Callable[[int], bytes] = _read,
    env: dict = None
) -> int:
    """Create a spawned process."""
    pid, master_fd = fork()
    if pid == CHILD:
        os.execlpe(argv[0], *argv, env)

    try:
        mode = tcgetattr(STDIN_FILENO)
        setraw(STDIN_FILENO)
        restore = True
    except termios.error:  # This is the same as termios.error
        restore = False

    try:
        _copy(master_fd, master_read, stdin_read)
    finally:
        if restore:
            tcsetattr(STDIN_FILENO, termios.TCSAFLUSH, mode)

    close(master_fd)
    return waitpid(pid, 0)[1]


def waitstatus_to_exitcode(status: int) -> int:
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    elif os.WIFSIGNALED(status):
        return -os.WTERMSIG(status)
    else:
        raise ValueError(f"invalid wait status: {status!r}")
