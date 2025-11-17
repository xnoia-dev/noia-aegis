import subprocess
import shutil
import sys
import os
from pathlib import Path
from noia_aegis.core.env_config import EnvConfig
from noia_aegis.core.tool_manager import ToolManager

class APKProcessor:
    def __init__(self, apk_path, verbose=False, env_config=None):
        self.apk_path = Path(apk_path)
        self.app_name = self.apk_path.stem
        self.verbose = verbose
        
        # Load environment config
        self.env_config = env_config or EnvConfig()
        
        # Initialize tool manager
        self.tool_manager = ToolManager(verbose=verbose)
        
        # Ensure tools are available (auto-download if needed)
        self.tool_paths = self.tool_manager.ensure_tools()
        
        # Set directories
        output_base = self.env_config.get_output_dir('output')
        self.work_dir = output_base / f"{self.app_name}_work"
        
        # Tools directory from tool manager
        self.tools_dir = self.tool_manager.tools_dir
        
        if not self.apk_path.exists():
            raise FileNotFoundError(f"APK not found: {apk_path}")
        
        if self.verbose:
            print(f"Using tools from: {self.tools_dir}")
    
    def decompile(self):
        """Decompile APK using apktool"""
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)
        
        # Get apktool path from tool manager
        apktool_path = self.tool_paths['apktool']
        
        cmd = [
            "java", "-jar",
            str(apktool_path),
            "d", str(self.apk_path),
            "-o", str(self.work_dir),
            "-f"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Decompile failed: {result.stderr}")
        
        return self.work_dir
    
    def recompile(self, output_name=None):
        """Recompile APK"""
        if output_name is None:
            output_name = f"{self.app_name}_protected.apk"
        
        output_path = Path("output/apks") / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get apktool path from tool manager
        apktool_path = self.tool_paths['apktool']
        
        cmd = [
            "java", "-jar",
            str(apktool_path),
            "b", str(self.work_dir),
            "-o", str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Recompile failed: {result.stderr}")
        
        return output_path
    
    def sign(self, unsigned_apk, keystore_path=None, keystore_pass=None, 
             key_alias=None, key_pass=None):
        """Sign APK with custom or debug keystore"""
        
        if keystore_path and keystore_pass and key_alias and key_pass:
            # Use custom keystore (PRODUCTION)
            return self._sign_with_keystore(
                unsigned_apk, keystore_path, keystore_pass, 
                key_alias, key_pass
            )
        else:
            # Use uber-apk-signer (DEBUG)
            return self._sign_with_uber(unsigned_apk)
    
    def _sign_with_uber(self, unsigned_apk):
        """Sign APK using uber-apk-signer (debug keystore)"""
        # Get uber-apk-signer path from tool manager
        uber_signer_path = self.tool_paths['uber-apk-signer']
        
        cmd = [
            "java", "-jar",
            str(uber_signer_path),
            "--apks", str(unsigned_apk),
            "--allowResign"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Signing failed: {result.stderr}")
        
        signed_apk = unsigned_apk.parent / f"{unsigned_apk.stem}-aligned-debugSigned.apk"
        return signed_apk
    
    def _sign_with_keystore(self, unsigned_apk, keystore_path, 
                            keystore_pass, key_alias, key_pass):
        """Sign with production keystore using apksigner (v2 signature)"""
        
        keystore_file = Path(keystore_path)
        if not keystore_file.exists():
            raise FileNotFoundError(f"Keystore not found: {keystore_path}")
        
        if self.verbose:
            print(f"  Signing with keystore: {keystore_file.name}")
            print(f"  Alias: {key_alias}")
        
        # Output filename
        signed_apk = unsigned_apk.parent / f"{unsigned_apk.stem}-aligned-signed.apk"
        
        # Try to find apksigner
        apksigner_path = self._find_apksigner()
        
        if apksigner_path:
            # Use apksigner (recommended - supports v2/v3)
            if self.verbose:
                print(f"  Using apksigner for v2 signature")
            
            cmd = [
                apksigner_path,
                "sign",
                "--ks", str(keystore_file),
                "--ks-key-alias", key_alias,
                "--ks-pass", f"pass:{keystore_pass}",
                "--key-pass", f"pass:{key_pass}",
                "--out", str(signed_apk),
                str(unsigned_apk)
            ]
            
            if self.verbose:
                cmd.insert(2, "--verbose")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Signing failed: {result.stderr}")
            
            if self.verbose:
                print(f"  Signed with v1 and v2 schemes")
            
            # Remove unsigned APK
            if unsigned_apk.exists():
                unsigned_apk.unlink()
            
            return signed_apk
        
        else:
            # Fallback to jarsigner + manual v2 signing
            if self.verbose:
                print(f"  Warning: apksigner not found, using jarsigner (v1 only)")
                print(f"  This may cause issues with modern Android versions!")
            
            # Use jarsigner for v1
            cmd_sign = [
                "jarsigner",
                "-sigalg", "SHA256withRSA",
                "-digestalg", "SHA-256",
                "-keystore", str(keystore_file),
                "-storepass", keystore_pass,
                "-keypass", key_pass,
                str(unsigned_apk),
                key_alias
            ]
            
            if self.verbose:
                cmd_sign.insert(1, "-verbose")
            
            result = subprocess.run(cmd_sign, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Signing failed: {result.stderr}")
            
            # Zipalign
            zipalign_cmd = self._find_zipalign()
            if zipalign_cmd:
                cmd_align = [
                    zipalign_cmd,
                    "-f", "4",
                    str(unsigned_apk),
                    str(signed_apk)
                ]
                
                if self.verbose:
                    cmd_align.insert(1, "-v")
                
                result = subprocess.run(cmd_align, capture_output=True, text=True)
                
                if result.returncode == 0:
                    unsigned_apk.unlink()
                else:
                    unsigned_apk.rename(signed_apk)
            else:
                unsigned_apk.rename(signed_apk)
            
            return signed_apk

    def _find_apksigner(self):
        """Find apksigner executable - uses config or auto-detect"""
        import shutil as sh
        import re
        
        # 1. Check if explicitly configured
        apksigner_path = self.env_config.get_tool_path('apksigner')
        if apksigner_path and apksigner_path.exists():
            if self.verbose:
                print(f"  Using configured apksigner: {apksigner_path}")
            return str(apksigner_path)
        
        # 2. Try to find in PATH
        apksigner = sh.which('apksigner')
        if apksigner:
            if self.verbose:
                print(f"  Found apksigner in PATH: {apksigner}")
            return apksigner
        
        # 3. Auto-detect from Android SDK
        sdk_root = self.env_config.get_android_sdk_root()
        if not sdk_root or not sdk_root.exists():
            if self.verbose:
                print(f"  Android SDK not found")
            return None
        
        build_tools_dir = sdk_root / 'build-tools'
        if not build_tools_dir.exists():
            if self.verbose:
                print(f"  build-tools directory not found in SDK")
            return None
        
        if self.verbose:
            print(f"  Searching in: {build_tools_dir}")
        
        # Get preferred version
        preferred_version = self.env_config.get_build_tools_version()
        
        # Get all version directories
        versions = [d for d in build_tools_dir.iterdir() if d.is_dir()]
        
        # Sort by version number
        def version_key(path):
            numbers = re.findall(r'\d+', path.name)
            return tuple(int(n) for n in numbers) if numbers else (0,)
        
        versions.sort(key=version_key, reverse=True)
        
        if self.verbose and versions:
            print(f"  Available versions: {[v.name for v in versions[:5]]}")
        
        # If specific version requested, try it first
        if preferred_version != 'latest':
            for version_dir in versions:
                if version_dir.name == preferred_version:
                    apksigner_path = version_dir / 'apksigner'
                    if sys.platform == 'win32':
                        apksigner_path = version_dir / 'apksigner.bat'
                    
                    if apksigner_path.exists():
                        if self.verbose:
                            print(f"  Using requested version: {version_dir.name}")
                        return str(apksigner_path)
        
        # Try each version (latest first)
        for version_dir in versions:
            apksigner_path = version_dir / 'apksigner'
            if sys.platform == 'win32':
                apksigner_path = version_dir / 'apksigner.bat'
            
            if apksigner_path.exists():
                if self.verbose:
                    print(f"  Using apksigner from: {version_dir.name}")
                return str(apksigner_path)
        
        if self.verbose:
            print(f"  apksigner not found")
        
        return None
    

    def _find_zipalign(self):
        """Find zipalign executable"""
        import shutil as sh
        
        # Try to find in PATH
        zipalign = sh.which('zipalign')
        if zipalign:
            return zipalign
        
        # Try common Android SDK locations
        possible_paths = []
        
        # Windows
        if sys.platform == 'win32':
            possible_paths.extend([
                Path.home() / 'AppData/Local/Android/Sdk/build-tools',
                Path('C:/Android/Sdk/build-tools'),
                Path('C:/Users') / os.getenv('USERNAME', '') / 'AppData/Local/Android/Sdk/build-tools',
            ])
        # Mac
        elif sys.platform == 'darwin':
            possible_paths.extend([
                Path.home() / 'Library/Android/sdk/build-tools',
                Path('/Users') / os.getenv('USER', '') / 'Library/Android/sdk/build-tools',
            ])
        # Linux
        else:
            possible_paths.extend([
                Path.home() / 'Android/Sdk/build-tools',
                Path('/opt/android-sdk/build-tools'),
            ])
        
        # Search in build-tools directories
        for base_path in possible_paths:
            if base_path.exists():
                # Find latest version
                versions = sorted([d for d in base_path.iterdir() if d.is_dir()], reverse=True)
                for version_dir in versions:
                    zipalign_path = version_dir / 'zipalign'
                    if sys.platform == 'win32':
                        zipalign_path = version_dir / 'zipalign.exe'
                    
                    if zipalign_path.exists():
                        return str(zipalign_path)
        
        return None
    
    def verify_signature(self, apk_path):
        """Verify APK signature"""
        try:
            result = subprocess.run(
                ["keytool", "-printcert", "-jarfile", str(apk_path)],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
        except Exception as e:
            return None
    
    def cleanup(self):
        """Remove temporary files"""
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)