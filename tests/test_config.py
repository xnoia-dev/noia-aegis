"""
Tests for AegisConfig

Tests configuration loading, merging, and shield management.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from noia_aegis.core.config import AegisConfig


class TestAegisConfig:
    """Test AegisConfig class"""

    def test_default_config(self):
        """Should load default configuration"""
        config = AegisConfig()

        assert config.is_shield_enabled('root_detection') is True
        assert config.is_shield_enabled('emulator_detection') is True
        assert config.is_shield_enabled('debug_detection') is True
        assert config.is_shield_enabled('developer_options') is True
        assert config.is_shield_enabled('integrity_check') is False

    def test_custom_config_file(self, tmp_path):
        """Should load custom configuration from file"""
        config_file = tmp_path / "custom.yml"
        config_data = {
            'shields': {
                'root_detection': False,
                'emulator_detection': False,
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = AegisConfig(str(config_file))

        assert config.is_shield_enabled('root_detection') is False
        assert config.is_shield_enabled('emulator_detection') is False
        # Should keep defaults for unspecified shields
        assert config.is_shield_enabled('debug_detection') is True

    def test_config_file_not_found(self):
        """Should raise FileNotFoundError for missing config"""
        with pytest.raises(FileNotFoundError):
            AegisConfig('nonexistent.yml')

    def test_get_message(self):
        """Should return custom messages"""
        config = AegisConfig()

        assert '🔓' in config.get_message('root_detected')
        assert '🖥️' in config.get_message('emulator_detected')
        assert '🐛' in config.get_message('debug_detected')
        assert '⚙️' in config.get_message('developer_detected')

    def test_custom_message(self, tmp_path):
        """Should load custom messages"""
        config_file = tmp_path / "custom.yml"
        config_data = {
            'messages': {
                'root_detected': 'Custom root message',
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = AegisConfig(str(config_file))

        assert config.get_message('root_detected') == 'Custom root message'
        # Should keep default for unspecified messages
        assert '🖥️' in config.get_message('emulator_detected')

    def test_should_show_toast(self):
        """Should return toast setting"""
        config = AegisConfig()
        assert config.should_show_toast() is True

    def test_should_exit_on_threat(self):
        """Should return exit behavior setting"""
        config = AegisConfig()
        assert config.should_exit_on_threat() is True

    def test_custom_behavior(self, tmp_path):
        """Should load custom behavior settings"""
        config_file = tmp_path / "custom.yml"
        config_data = {
            'behavior': {
                'show_toast': False,
                'exit_on_threat': False,
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = AegisConfig(str(config_file))

        assert config.should_show_toast() is False
        assert config.should_exit_on_threat() is False

    def test_to_dict(self):
        """Should convert config to dictionary"""
        config = AegisConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert 'shields' in config_dict
        assert 'behavior' in config_dict
        assert 'messages' in config_dict

    def test_save_to_file(self, tmp_path):
        """Should save config to file"""
        output_file = tmp_path / "output.yml"
        config = AegisConfig()

        config.save_to_file(str(output_file))

        assert output_file.exists()

        # Verify saved config can be loaded
        loaded_config = AegisConfig(str(output_file))
        assert loaded_config.is_shield_enabled('root_detection') is True

    def test_load_default_aegis_yml(self, tmp_path, monkeypatch):
        """Should load from .aegis.yml if present"""
        # Change working directory to tmp_path
        monkeypatch.chdir(tmp_path)

        config_file = tmp_path / ".aegis.yml"
        config_data = {
            'shields': {
                'root_detection': False,
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = AegisConfig()  # No path specified

        assert config.is_shield_enabled('root_detection') is False

    def test_compatibility_section(self):
        """Should have compatibility section in default config"""
        config = AegisConfig()
        config_dict = config.to_dict()

        assert 'compatibility' in config_dict
        assert config_dict['compatibility']['react_native'] is True
        assert config_dict['compatibility']['flutter'] is True
        assert config_dict['compatibility']['native_android'] is True

    def test_obfuscation_section(self):
        """Should have obfuscation section in default config"""
        config = AegisConfig()
        config_dict = config.to_dict()

        assert 'obfuscation' in config_dict
        assert config_dict['obfuscation']['enable'] is True

    def test_merge_partial_config(self, tmp_path):
        """Should merge partial config with defaults"""
        config_file = tmp_path / "partial.yml"
        config_data = {
            'shields': {
                'root_detection': False,
                # Other shields not specified - should use defaults
            },
            'messages': {
                'root_detected': 'Custom message',
                # Other messages not specified - should use defaults
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        config = AegisConfig(str(config_file))

        # Custom values
        assert config.is_shield_enabled('root_detection') is False
        assert config.get_message('root_detected') == 'Custom message'

        # Default values
        assert config.is_shield_enabled('emulator_detection') is True
        assert '🖥️' in config.get_message('emulator_detected')


@pytest.fixture
def tmp_path():
    """Provide temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])