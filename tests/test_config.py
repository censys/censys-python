import unittest
from configparser import ConfigParser
from unittest.mock import patch, mock_open, Mock, MagicMock

from censys.config import (
    get_config,
    censys_path,
    config_path,
    default_config,
    DEFAULT,
)

os = MagicMock()
os.path = MagicMock()
os.path.isdir = Mock(return_value=False)
os.path.exists = Mock(return_value=False)
mkdir = Mock()


def update_status(*args):
    mkdir(args[0])
    os.path.isdir.return_value = True


os.mkdir = Mock(side_effect=update_status)

test_config = ConfigParser()
test_config[DEFAULT] = default_config

censys = MagicMock()
censys.config = MagicMock()
censys.config.get_config = Mock(return_value=test_config)

test_config_path = config_path + ".test"


@patch("censys.config.config_path", test_config_path)
class CensysConfigTest(unittest.TestCase):
    @patch("censys.config.os.path", os.path)
    @patch("censys.config.os.mkdir", os.mkdir)
    @patch("builtins.open", new_callable=mock_open)
    def test_write_default(self, mock_file):
        get_config()
        os.path.isdir.assert_called_with(censys_path)
        os.mkdir.assert_called_with(censys_path)
        os.path.exists.assert_called_with(test_config_path)
        mock_file.assert_called_with(test_config_path, "w")

    @patch("builtins.open", new_callable=mock_open)
    def test_write_version(self, mock_file):
        config = get_config()
        pre_version = config.get(DEFAULT, "version")

        new_version = "test" + pre_version
        with patch("censys.config.__version__", new_version):
            config = get_config()
            self.assertEqual(config.get(DEFAULT, "version"), new_version)

        mock_file.assert_called_with(test_config_path, "w")
