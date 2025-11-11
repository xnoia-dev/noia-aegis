import subprocess
import shutil
from pathlib import Path


class APKProcessor:
    def __init__(self, apk_path, verbose=False):
        self.apk_path = Path(apk_path)
        self.app_name = self.apk_path.stem
        self.work_dir = Path(f"output/{self.app_name}_work")
        self.tools_dir = Path(__file__).parent.parent.parent / "tools"
        self.verbose = verbose
        
        if not self.apk_path.exists():
            raise FileNotFoundError(f"APK not found: {apk_path}")
    
    def decompile(self):
        """Decompile APK using apktool"""
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)
        
        cmd = [
            "java", "-jar",
            str(self.tools_dir / "apktool.jar"),
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
        
        cmd = [
            "java", "-jar",
            str(self.tools_dir / "apktool.jar"),
            "b", str(self.work_dir),
            "-o", str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Recompile failed: {result.stderr}")
        
        return output_path
    
    def sign(self, unsigned_apk):
        """Sign APK using uber-apk-signer"""
        cmd = [
            "java", "-jar",
            str(self.tools_dir / "uber-apk-signer.jar"),
            "--apks", str(unsigned_apk),
            "--allowResign"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Signing failed: {result.stderr}")
        
        signed_apk = unsigned_apk.parent / f"{unsigned_apk.stem}-aligned-debugSigned.apk"
        return signed_apk
    
    def cleanup(self):
        """Remove temporary files"""
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)