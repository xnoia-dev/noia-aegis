"""
Tool Manager - Auto-download and manage external tools
"""
import os
import hashlib
import requests
from pathlib import Path
from tqdm import tqdm
import json
from datetime import datetime


class ToolManager:
    """Manage external tools (apktool, uber-apk-signer)"""
    
    # Tool definitions
    TOOLS = {
        'apktool': {
            'version': '2.9.3',
            'url': 'https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar',
            'filename': 'apktool.jar',
            'size': 10_500_000,  # ~10 MB
            'sha256': None,  # Will add after first download
        },
        'uber-apk-signer': {
            'version': '1.3.0',
            'url': 'https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar',
            'filename': 'uber-apk-signer.jar',
            'size': 5_200_000,  # ~5 MB
            'sha256': None,
        }
    }
    
    def __init__(self, tools_dir=None, verbose=False):
        """
        Initialize ToolManager
        
        Args:
            tools_dir: Custom tools directory (default: ~/.noia-aegis/tools or ./tools)
            verbose: Show detailed output
        """
        self.verbose = verbose
        
        # Determine tools directory
        if tools_dir:
            self.tools_dir = Path(tools_dir)
        else:
            # Try user home directory first
            home_tools = Path.home() / '.noia-aegis' / 'tools'
            local_tools = Path('tools')
            
            # Use home directory if writable, otherwise local
            try:
                home_tools.mkdir(parents=True, exist_ok=True)
                # Test write permission
                test_file = home_tools / '.test'
                test_file.touch()
                test_file.unlink()
                self.tools_dir = home_tools
            except (PermissionError, OSError):
                self.tools_dir = local_tools
        
        # Create directory
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
        # Versions file
        self.versions_file = self.tools_dir / '.versions.json'
        
        if self.verbose:
            print(f"Tools directory: {self.tools_dir}")
    
    def ensure_tools(self):
        """
        Ensure all required tools are available
        Downloads missing tools automatically
        
        Returns:
            dict: Paths to all tools
        """
        tool_paths = {}
        
        for tool_name, tool_info in self.TOOLS.items():
            tool_path = self.tools_dir / tool_info['filename']
            
            if tool_path.exists():
                if self.verbose:
                    print(f"✓ {tool_name} found: {tool_path}")
                tool_paths[tool_name] = tool_path
            else:
                print(f"📥 Downloading {tool_name} v{tool_info['version']}...")
                self._download_tool(tool_name, tool_info, tool_path)
                tool_paths[tool_name] = tool_path
        
        return tool_paths
    
    def _download_tool(self, tool_name, tool_info, output_path):
        """
        Download a tool with progress bar
        
        Args:
            tool_name: Name of the tool
            tool_info: Tool metadata
            output_path: Where to save the file
        """
        url = tool_info['url']
        
        try:
            # Start download
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            with open(output_path, 'wb') as f:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=tool_info['filename'],
                    ncols=80
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            # Verify file size
            actual_size = output_path.stat().st_size
            if actual_size == 0:
                output_path.unlink()
                raise Exception("Downloaded file is empty!")
            
            # Verify checksum if available
            if tool_info.get('sha256'):
                if not self._verify_checksum(output_path, tool_info['sha256']):
                    output_path.unlink()
                    raise Exception("Checksum verification failed!")
            
            # Save version info
            self._save_version_info(tool_name, tool_info['version'])
            
            print(f"✓ {tool_name} downloaded successfully")
            
        except requests.RequestException as e:
            if output_path.exists():
                output_path.unlink()
            raise Exception(f"Download failed: {str(e)}")
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise Exception(f"Error downloading {tool_name}: {str(e)}")
    
    def _verify_checksum(self, file_path, expected_sha256):
        """
        Verify file SHA-256 checksum
        
        Args:
            file_path: Path to file
            expected_sha256: Expected SHA-256 hash
            
        Returns:
            bool: True if checksum matches
        """
        if self.verbose:
            print(f"  Verifying checksum...")
        
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        actual = sha256.hexdigest()
        matches = actual == expected_sha256
        
        if self.verbose:
            print(f"  Expected: {expected_sha256}")
            print(f"  Actual:   {actual}")
            print(f"  Match: {matches}")
        
        return matches
    
    def _save_version_info(self, tool_name, version):
        """Save tool version information"""
        versions = {}
        
        if self.versions_file.exists():
            with open(self.versions_file, 'r') as f:
                versions = json.load(f)
        
        versions[tool_name] = {
            'version': version,
            'downloaded_at': datetime.now().isoformat()
        }
        
        with open(self.versions_file, 'w') as f:
            json.dump(versions, f, indent=2)
    
    def get_tool_path(self, tool_name):
        """
        Get path to a specific tool
        
        Args:
            tool_name: Name of the tool ('apktool' or 'uber-apk-signer')
            
        Returns:
            Path: Path to the tool
        """
        if tool_name not in self.TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return self.tools_dir / self.TOOLS[tool_name]['filename']
    
    def list_tools(self):
        """List all installed tools"""
        versions = {}
        if self.versions_file.exists():
            with open(self.versions_file, 'r') as f:
                versions = json.load(f)
        
        print(f"\n📦 Installed Tools (in {self.tools_dir}):\n")
        
        for tool_name, tool_info in self.TOOLS.items():
            tool_path = self.tools_dir / tool_info['filename']
            installed = tool_path.exists()
            
            status = "✓ Installed" if installed else "✗ Missing"
            version = versions.get(tool_name, {}).get('version', 'Unknown')
            
            print(f"  {tool_name}:")
            print(f"    Status: {status}")
            if installed:
                print(f"    Version: {version}")
                size_mb = tool_path.stat().st_size / 1024 / 1024
                print(f"    Size: {size_mb:.1f} MB")
                print(f"    Path: {tool_path}")
            print()
    
    def clean_tools(self):
        """Remove all downloaded tools"""
        removed = 0
        
        for tool_name, tool_info in self.TOOLS.items():
            tool_path = self.tools_dir / tool_info['filename']
            
            if tool_path.exists():
                tool_path.unlink()
                print(f"✓ Removed {tool_name}")
                removed += 1
        
        if self.versions_file.exists():
            self.versions_file.unlink()
        
        print(f"\n✓ Cleaned {removed} tool(s)")
    
    def update_tools(self):
        """Re-download all tools to get latest versions"""
        print("🔄 Updating tools...\n")
        
        # Remove existing tools
        for tool_name, tool_info in self.TOOLS.items():
            tool_path = self.tools_dir / tool_info['filename']
            if tool_path.exists():
                tool_path.unlink()
                print(f"  Removed old {tool_name}")
        
        print()
        
        # Re-download
        self.ensure_tools()
        
        print("\n✓ All tools updated")


def get_tool_manager(verbose=False):
    """
    Get or create ToolManager instance
    
    Args:
        verbose: Show detailed output
        
    Returns:
        ToolManager: Tool manager instance
    """
    return ToolManager(verbose=verbose)