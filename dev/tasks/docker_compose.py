from typing import Any, Dict, List, Optional, Tuple

from schema import Optional as SchemaOptional
from schema import Or, Schema

from dev.helpers import run_command
from dev.helpers.shadowenv import ShadowenvHelper
from dev.task import Task


class DockerCompose(Task):
    __schema__ = Schema(
        Or(
            # - docker_compose
            None,
            {
                SchemaOptional('service'): Or(str, list),
                SchemaOptional('env'): {str: str},
                'config': Or(
                    # - docker_compose:
                    #     config: docker-compose.yml
                    str,
                    # - docker_compose:
                    #     config:
                    #       - docker-compose.traefik.yml
                    #       - docker-compose.state.yml
                    #       - docker-compose.yml
                    [str],
                )
            },
        )
    )
    __description__ = 'Manage docker-compose'

    def up(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        config, service, env = self.parse_args(args)
        joined_services = ' '.join(service)
        flags = self.flags_from_config(config)

        run_command(f'docker-compose {flags} up -d {joined_services}', env=env)
        version = run_command("docker-compose -v | cut -d ' ' -f 3 | cut -d ',' -f 1", output=True, silent=True)
        ShadowenvHelper.configure_provider("docker-compose", version)

    def down(self, args: Optional[Any], extra_args: Optional[Any]) -> None:
        config, service, env = self.parse_args(args)
        joined_services = ' '.join(service)
        flags = self.flags_from_config(config)

        run_command(f'docker-compose {flags} down {joined_services}', env=env)
        ShadowenvHelper.unconfigure_provider("docker-compose")

    def parse_args(self, args: Optional[dict]) -> Tuple[List[str], List[str], Dict[str, str]]:
        if args is None:
            args = {}

        config = args.get('config', ['docker-compose.yml'])
        service = args.get('service', '')
        env = args.get('env', {})

        if isinstance(config, str):
            config = [config]

        if isinstance(service, str):
            service = [service]

        return config, service, env

    def flags_from_env(self, env: dict) -> str:
        out = ''
        for k, v in env.items():
            out += f'{k}="{v}" '
        return out.strip()

    def flags_from_config(self, config: List[str]) -> str:
        flags = ''
        for c in config:
            flags += f' -f {c}'
        return flags.strip()
