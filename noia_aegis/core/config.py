import yaml
from pathlib import Path
from typing import Dict, Any


class AegisConfig:
    """Aegis configuration manager"""
    
    DEFAULT_CONFIG = {
        'shields': {
            'root_detection': True,
            'emulator_detection': True,
            'debug_detection': True,
            'developer_options': True,
            'integrity_check': False,
        },
        'obfuscation': {
            'enable': True
        },
        'behavior': {
            'show_toast': True,
            'exit_on_threat': True,
            'log_threats': False,
        },
        'messages': {
            'root_detected': '🔓 Root detected!',
            'emulator_detected': '🖥️ Emulator detected!',
            'debug_detected': '🐛 Debug mode detected!',
            'developer_detected': '⚙️ Developer options enabled!',
            'integrity_failed': '⚠️ App integrity check failed!',
        },
        'development': {
            'skip_in_dev': False,
            'verbose': False,
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load_from_file(config_path)
        else:
            # Try to load from default locations
            self._load_default_config()
    
    def load_from_file(self, config_path: str):
        """Load config from YAML file"""
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f)
        
        # Merge with default config
        self._merge_config(user_config)
    
    def _load_default_config(self):
        """Load from default locations"""
        default_paths = [
            Path('.aegis.yml'),
            Path('.aegis.yaml'),
            Path('aegis.yml'),
            Path('aegis.yaml'),
        ]
        
        for path in default_paths:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                self._merge_config(user_config)
                break
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Merge user config with default config"""
        if not user_config:
            return
        
        for section, values in user_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
    
    def is_shield_enabled(self, shield_name: str) -> bool:
        """Check if a shield is enabled"""
        return self.config['shields'].get(shield_name, False)
    
    def get_message(self, message_key: str) -> str:
        """Get custom message"""
        return self.config['messages'].get(message_key, '')
    
    def should_show_toast(self) -> bool:
        """Check if toast should be shown"""
        return self.config['behavior'].get('show_toast', True)
    
    def should_exit_on_threat(self) -> bool:
        """Check if app should exit on threat"""
        return self.config['behavior'].get('exit_on_threat', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return self.config.copy()
    
    def save_to_file(self, output_path: str):
        """Save config to YAML file"""
        path = Path(output_path)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)