import unittest
from configparser import ConfigParser
from unittest.mock import patch, mock_open, Mock, MagicMock

from censys.common.config import (
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
os.mkdir = Mock()

test_config = ConfigParser()
test_config[DEFAULT] = default_config

test_config_path = config_path + ".test"


@patch("censys.common.config.config_path", test_config_path)
class CensysConfigTest(unittest.TestCase):
    @patch("censys.common.config.os.path", os.path)
    @patch("censys.common.config.os.mkdir", os.mkdir)
    @patch("builtins.open", new_callable=mock_open)
    def test_write_default(self, mock_file):
        get_config()
        os.path.isdir.assert_called_with(censys_path)
        os.mkdir.assert_called_with(censys_path)
        os.path.exists.assert_called_with(test_config_path)
        mock_file.assert_called_with(test_config_path, "w")
