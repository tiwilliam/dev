from typing import Any, Optional

from schema import Optional as SchemaOptional
from schema import Or, Schema

from dev.exceptions import NonZeroReturnCodeError
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
                SchemaOptional('if'): str,
            },
        )
    )
    __description__ = 'Run shell args'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        if not args:
            return

        if isinstance(args, dict):
            env = args.get('env')
            if_command = args.get('if')
            commands_from_args = args['command']
        else:
            env = None
            if_command = None
            commands_from_args = args

        if isinstance(commands_from_args, str):
            commands = [commands_from_args]
        else:
            commands = commands_from_args

        if if_command:
            try:
                run_command(if_command, silent=True)
            except NonZeroReturnCodeError:
                ...  # If test failed - run command
            else:
                return  # If test succeeded - do not run command

        for command in commands:
            full_command: str = command
            if extra_args:
                full_command += " " + " ".join(extra_args)
            run_command(full_command, env=env)
