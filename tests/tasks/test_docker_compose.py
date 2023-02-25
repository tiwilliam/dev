from unittest.mock import call, patch

from dev.tasks.docker_compose import DockerCompose


@patch('dev.tasks.docker_compose.run_command')
def test_up(run_command_mock):
    DockerCompose()
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f docker-compose.yml up -d', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_up_custom_config(run_command_mock):
    DockerCompose(dict(config='custom.yml'))
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f custom.yml up -d', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_up_custom_service(run_command_mock):
    DockerCompose(dict(service='web'))
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f docker-compose.yml up -d web', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_down_custom_service(run_command_mock):
    DockerCompose(dict(service='web'), direction='down')
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f docker-compose.yml down web', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_up_custom_config_list(run_command_mock):
    DockerCompose(dict(config=['a.yml', 'b.yml']))
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f a.yml -f b.yml up -d', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_up_remove_orphans_with_config(run_command_mock):
    DockerCompose(dict(config='custom.yml', remove_orphans=True))
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f custom.yml up -d', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_down(run_command_mock):
    DockerCompose(direction='down')
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f docker-compose.yml down', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_down_remove_orphans_true_with_config(run_command_mock):
    DockerCompose(args=dict(config='custom.yml', remove_orphans=True), direction='down')
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f custom.yml down --remove-orphans', env={}),
        ]
    )


@patch('dev.tasks.docker_compose.run_command')
def test_down_remove_orphans_false_with_config(run_command_mock):
    DockerCompose(args=dict(config='custom.yml', remove_orphans=False), direction='down')
    run_command_mock.assert_has_calls(
        [
            call('docker-compose -f custom.yml down', env={}),
        ]
    )
