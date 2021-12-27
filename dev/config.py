import sys
from typing import Dict, Generator, List, Optional, Tuple, Union

import yaml
from schema import Optional as SchemaOptional
from schema import Or, Schema, SchemaError

from dev import environment
from dev.console import error_console
from dev.exceptions import CommandNotFoundError
from dev.task import InternalTask

# Accepted argument types to tasks, can be nested in list and dict
arg_definition = Or(str, int, bool, float, list, dict)

tasks_definition = Or(
    # command: date
    str,
    [
        Or(
            # command:
            #     - pip
            str,
            {
                str: Or(
                    # command:
                    #     - pip: requirements.txt
                    arg_definition,
                    # command:
                    #     - pip:
                    #         - requirements/base.txt
                    #         - requirements/dev.txt
                    [arg_definition],
                    # command:
                    #     - env:
                    #         DEVELOPMENT: "1"
                    {str: arg_definition},
                )
            },
        )
    ],
)


class ConfigTask:
    def __init__(self, name: str, args: Optional[str]):
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return f'<{self.name}: {self.args}>'


class ConfigParser:
    __schema__ = Schema(
        Or(
            None,
            {
                'name': str,
                SchemaOptional('up'): tasks_definition,
                SchemaOptional('down'): tasks_definition,
                SchemaOptional('open'): {str: str},
                SchemaOptional('commands'): {
                    str: Or(
                        tasks_definition,
                        {
                            'tasks': tasks_definition,
                            SchemaOptional('description'): str,
                        },
                    )
                },
            },
        )
    )

    reserved_commands = ['up', 'down']

    def __init__(self, filename: str) -> None:
        try:
            self.devfile = self.load_devfile(filename)
            self.tasks = self.load_tasks()
            environment.set_name(self.devfile.get('name', 'unknown'))
        except yaml.scanner.ScannerError as e:
            error_console.print(f'Failed to load {filename}: {e}', style='red')
            sys.exit(1)
        except SchemaError as e:
            fancy_error = ' '.join(e.code.split('\n')[-2:])
            error_console.print(f'Failed to validate {filename}: {fancy_error}', style='red')
            sys.exit(1)

    def load_devfile(self, filename: str) -> dict:
        try:
            with open(filename) as file:
                devfile = yaml.load(file, Loader=yaml.FullLoader)

            if not devfile:
                raise FileNotFoundError

            self.__schema__.validate(devfile)
            return devfile
        except yaml.parser.ParserError as e:
            error_console.print(f'Failed to parse {filename}: {e}', style='red')
            sys.exit(1)
        except FileNotFoundError:
            return {}

    @property
    def custom_command_config(self) -> dict:
        return self.devfile.get('commands', {})

    @property
    def custom_commands(self) -> Generator[Tuple[str, Optional[str]], None, None]:
        # We support three styles of custom command definitions:
        #
        # commands:
        #     lint: flake8
        #     test:
        #         - run: py.test
        #     logs:
        #         description: Tail development logs
        #         tasks:
        #             - run: docker-compose logs -f
        for command, data in self.custom_command_config.items():
            if not isinstance(data, dict):
                yield command, None
            else:
                yield command, data.get('description')

    def resolve_tasks(self, command: str, extra_args: str) -> Dict[str, List[ConfigTask]]:
        if command in InternalTask.tasks():
            # Treat internal tasks as commands: dev update -> dev.tasks.internal.update.
            return {'up': [ConfigTask(command, extra_args)]}

        if command not in list(self.custom_command_config) + self.reserved_commands:
            raise CommandNotFoundError(command)

        tasks_to_run = {
            'up': self.tasks[command],
        }

        if command == 'down':
            tasks_to_run['down'] = self.tasks['up']

        return tasks_to_run

    def load_tasks(self) -> Dict[str, List[ConfigTask]]:
        tasks = {}

        for command in self.custom_command_config:
            tasks[command] = self.parse_commands(self.custom_command_config[command])

        for command in self.reserved_commands:
            tasks[command] = self.parse_commands(self.devfile.get(command, []))

        return tasks

    def parse_commands(self, definition: Union[str, dict, list]) -> List[ConfigTask]:
        output = []
        if isinstance(definition, str):
            output.append(ConfigTask('run', definition))
        if isinstance(definition, dict):
            for d in definition.get('tasks', []):
                output += self.parse_task_definition(d)
        if isinstance(definition, list):
            for d in definition:
                output += self.parse_task_definition(d)
        return output

    def parse_task_definition(self, definition: Union[str, dict]) -> List[ConfigTask]:
        output = []
        if isinstance(definition, str):
            output.append(ConfigTask(definition, None))
        if isinstance(definition, dict):
            for task, args in definition.items():
                output.append(ConfigTask(task, args))
        return output


config = ConfigParser('Devfile')
