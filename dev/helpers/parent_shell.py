import os
from typing import List

queue: List[str] = []


class ParentShellHelper:

    @staticmethod
    def run(command: str) -> None:
        queue.append(command)

    @staticmethod
    def send_queued_commands() -> None:
        try:
            fd = int(os.environ.get('SHELL_FD', 101))
            with os.fdopen(fd, 'w') as pipe:
                for command in queue:
                    pipe.write(f'{command}\n')
                pipe.write('\0')
        except OSError:
            ...
