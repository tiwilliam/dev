from typing import Any, Optional

from schema import Optional as SchemaOptional
from schema import Or, Schema

from dev.helpers import run_command
from dev.task import Task


class DockerComposeExec(Task):
    __schema__ = Schema({
        'container': str,
        'run': Or(str, [str]),
        SchemaOptional('env'): {str: str},
    })
    __description__ = 'Run shell commands in docker-compose'

    def up(self, args: Any, extra_args: Optional[Any]) -> None:
        env = args.get('env', {})
        container = args['container']

        commands = args['run']
        if isinstance(commands, str):
            commands = [commands]

        env_flags = ''
        for k, v in env.items():
            env_flags += f' -e {k}={v}'

        for command in commands:
            run_command(f'docker-compose exec{env_flags} {container} {command}')
