"""
Environment and TOML configuration loader
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import toml


class EnvConfig:
    """Load configuration from .env and aegis.toml"""
    
    def __init__(self, project_root=None):
        self.project_root = project_root or Path.cwd()
        
        # Load .env file
        env_file = self.project_root / '.env'
        if env_file.exists():
            load_dotenv(env_file)
        
        # Load aegis.toml
        self.toml_config = {}
        toml_file = self.project_root / 'aegis.toml'
        if toml_file.exists():
            with open(toml_file, 'r') as f:
                self.toml_config = toml.load(f)
    
    def get_tool_path(self, tool_name):
        """Get tool path from config or environment"""
        # Priority: Environment > TOML > Default
        
        # 1. Check environment variable
        env_var = f"{tool_name.upper()}_PATH"
        env_path = os.getenv(env_var)
        if env_path:
            return Path(env_path)
        
        # 2. Check TOML config
        if 'tools' in self.toml_config:
            toml_path = self.toml_config['tools'].get(tool_name)
            if toml_path:
                return Path(toml_path)
        
        # 3. Return None (use auto-detection)
        return None
    
    def get_android_sdk_root(self):
        """Get Android SDK root path"""
        # Priority: TOML > Environment > Default
        
        # 1. Check TOML
        if 'android_sdk' in self.toml_config:
            toml_root = self.toml_config['android_sdk'].get('root')
            if toml_root:
                return Path(toml_root)
        
        # 2. Check environment
        sdk_root = os.getenv('ANDROID_SDK_ROOT') or os.getenv('ANDROID_HOME')
        if sdk_root:
            return Path(sdk_root)
        
        # 3. Check common locations
        if os.name == 'nt':  # Windows
            return Path.home() / 'AppData/Local/Android/Sdk'
        elif os.name == 'posix':
            if 'darwin' in os.sys.platform:  # macOS
                return Path.home() / 'Library/Android/sdk'
            else:  # Linux
                return Path.home() / 'Android/Sdk'
        
        return None
    
    def get_build_tools_version(self):
        """Get preferred build-tools version"""
        # Priority: TOML > Environment > "latest"
        
        # 1. Check TOML
        if 'android_sdk' in self.toml_config:
            version = self.toml_config['android_sdk'].get('build_tools_version')
            if version:
                return version
        
        # 2. Check environment
        version = os.getenv('ANDROID_BUILD_TOOLS_VERSION')
        if version:
            return version
        
        # 3. Use latest
        return 'latest'
    
    def get_output_dir(self, dir_type='output'):
        """Get output directory path"""
        if 'paths' in self.toml_config:
            path = self.toml_config['paths'].get(f"{dir_type}_dir")
            if path:
                return Path(path)
        
        return Path('output')
    
    def get_verbose(self):
        """Get default verbose setting"""
        if 'logging' in self.toml_config:
            return self.toml_config['logging'].get('verbose', False)
        return False
    
    def get_keep_temp(self):
        """Get default keep_temp setting"""
        if 'logging' in self.toml_config:
            return self.toml_config['logging'].get('keep_temp', False)
        return False