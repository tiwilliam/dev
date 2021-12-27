from typing import Any, Optional

from schema import Optional as SchemaOptional
from schema import Or, Schema

from dev.helpers import run_command
from dev.task import Task


class Run(Task):
    __schema__ = Schema(
        Or(
            # - run: date
            str,
            # - run:
            #     - date
            #     - date
            [str],
            # - run:
            #     command: echo $SCOPE
            #     env:
            #       SCOPE: something
            {
                'command': Or(str, [str]),
                SchemaOptional('env'): {str: str},
            },
        )
    )
    __description__ = 'Run shell args'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        if isinstance(args, dict):
            env = args.get('env')
            commands_from_args = args['command']
        else:
            env = None
            commands_from_args = args

        if isinstance(commands_from_args, str):
            commands = [commands_from_args]
        else:
            commands = commands_from_args

        for command in commands:
            full_command: str = command
            if extra_args:
                full_command += " " + " ".join(extra_args)
            run_command(full_command, env=env)
