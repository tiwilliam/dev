from unittest.mock import call, patch, Mock

from dev.tasks.docker_compose import DockerCompose


@patch('dev.tasks.docker_compose.ShadowenvHelper.configure_provider')
class TestDockerCompose:
    @patch('dev.tasks.docker_compose.run_command')
    def test_up(self, run_command_mock: Mock, config_provider_mock: Mock):
        DockerCompose()
        config_provider_mock.assert_called_once_with('docker-compose', run_command_mock())
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f docker-compose.yaml up -d', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_up_custom_config(self, run_command_mock: Mock, config_provider_mock: Mock):
        DockerCompose(dict(config='custom.yaml'))
        config_provider_mock.assert_called_once_with('docker-compose', run_command_mock())
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f custom.yaml up -d', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_up_custom_service(self, run_command_mock: Mock, config_provider_mock: Mock):
        DockerCompose(dict(service='web'))
        config_provider_mock.assert_called_once_with('docker-compose', run_command_mock())
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f docker-compose.yaml up -d web', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_down_custom_service(self, run_command_mock: Mock, config_provider_mock: Mock):
        DockerCompose(dict(service='web'), direction='down')
        config_provider_mock.assert_not_called()
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f docker-compose.yaml down web', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_up_custom_config_list(self, run_command_mock: Mock, config_provider_mock: Mock):
        DockerCompose(dict(config=['a.yaml', 'b.yaml']))
        config_provider_mock.assert_called_once_with('docker-compose', run_command_mock())
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f a.yaml -f b.yaml up -d', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_up_remove_orphans_with_config(
        self, run_command_mock: Mock, config_provider_mock: Mock
    ):
        DockerCompose(dict(config='custom.yaml', remove_orphans=True))
        config_provider_mock.assert_called_once_with('docker-compose', run_command_mock())
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f custom.yaml up -d', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_down(self, run_command_mock: Mock, config_provider_mock: Mock):
        DockerCompose(direction='down')
        config_provider_mock.assert_not_called()
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f docker-compose.yaml down', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_down_remove_orphans_true_with_config(
        self, run_command_mock: Mock, config_provider_mock: Mock
    ):
        DockerCompose(args=dict(config='custom.yaml', remove_orphans=True), direction='down')
        config_provider_mock.assert_not_called()
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f custom.yaml down --remove-orphans', env={}),
            ]
        )

    @patch('dev.tasks.docker_compose.run_command')
    def test_down_remove_orphans_false_with_config(
        self, run_command_mock: Mock, config_provider_mock: Mock
    ):
        DockerCompose(args=dict(config='custom.yaml', remove_orphans=False), direction='down')
        config_provider_mock.assert_not_called()
        run_command_mock.assert_has_calls(
            [
                call('docker-compose -f custom.yaml down', env={}),
            ]
        )
