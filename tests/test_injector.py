"""
Tests for AegisInjector

Comprehensive tests for injector functionality including obfuscation,
encoding handling, framework detection, and edge cases.
"""

import pytest
import tempfile
from pathlib import Path
from noia_aegis.core.injector import AegisInjector
from noia_aegis.core.config import AegisConfig


class TestInjectorFrameworkDetection:
    """Test framework detection capabilities"""

    def test_detect_react_native(self, tmp_path):
        """Should detect React Native apps"""
        setup_basic_apk(tmp_path)
        setup_react_native_structure(tmp_path)

        injector = AegisInjector(str(tmp_path))
        analysis = injector.analyze()

        assert analysis['app_type'] == 'React Native'

    def test_detect_flutter(self, tmp_path):
        """Should detect Flutter apps"""
        setup_basic_apk(tmp_path)
        setup_flutter_structure(tmp_path)

        injector = AegisInjector(str(tmp_path))
        analysis = injector.analyze()

        assert analysis['app_type'] == 'Flutter'

    def test_detect_native_android(self, tmp_path):
        """Should detect Native Android apps"""
        setup_basic_apk(tmp_path)

        injector = AegisInjector(str(tmp_path))
        analysis = injector.analyze()

        assert analysis['app_type'] == 'Native Android'

    def test_is_react_native_by_activity(self, tmp_path):
        """Should detect React Native by ReactActivity"""
        setup_basic_apk(tmp_path)
        create_react_activity(tmp_path)

        injector = AegisInjector(str(tmp_path))

        assert injector._is_react_native() is True

    def test_is_flutter_by_activity(self, tmp_path):
        """Should detect Flutter by FlutterActivity"""
        setup_basic_apk(tmp_path)
        create_flutter_activity(tmp_path)

        injector = AegisInjector(str(tmp_path))

        assert injector._is_flutter() is True

    def test_is_flutter_by_lib(self, tmp_path):
        """Should detect Flutter by libflutter.so"""
        setup_basic_apk(tmp_path)
        lib_dir = tmp_path / "lib" / "arm64-v8a"
        lib_dir.mkdir(parents=True, exist_ok=True)
        (lib_dir / "libflutter.so").write_bytes(b'\x7fELF')  # ELF header

        injector = AegisInjector(str(tmp_path))

        assert injector._is_flutter() is True


class TestInjectorObfuscation:
    """Test string obfuscation functionality"""

    def test_obfuscate_all_strings(self, tmp_path):
        """Should obfuscate strings in smali files"""
        setup_basic_apk(tmp_path)
        create_smali_with_strings(tmp_path)

        injector = AegisInjector(str(tmp_path), obfuscate_strings=True)
        count, files = injector._obfuscate_all_strings()

        assert count > 0
        assert files > 0

    def test_should_skip_aegis_classes(self, tmp_path):
        """Should skip Noia Aegis own classes"""
        setup_basic_apk(tmp_path)
        aegis_file = tmp_path / "smali" / "com" / "noiaegis" / "AegisCore.smali"
        aegis_file.parent.mkdir(parents=True, exist_ok=True)
        aegis_file.write_text('.class public Lcom/noiaegis/AegisCore;')

        injector = AegisInjector(str(tmp_path))

        assert injector._should_skip_obfuscation(aegis_file) is True

    def test_should_skip_android_framework(self, tmp_path):
        """Should skip Android framework classes"""
        setup_basic_apk(tmp_path)
        android_file = tmp_path / "smali" / "android" / "app" / "Activity.smali"
        android_file.parent.mkdir(parents=True, exist_ok=True)
        android_file.write_text('.class public Landroid/app/Activity;')

        injector = AegisInjector(str(tmp_path))

        assert injector._should_skip_obfuscation(android_file) is True

    def test_should_skip_flutter_framework(self, tmp_path):
        """Should skip Flutter framework classes"""
        setup_basic_apk(tmp_path)
        flutter_file = tmp_path / "smali" / "io" / "flutter" / "embedding" / "Test.smali"
        flutter_file.parent.mkdir(parents=True, exist_ok=True)
        flutter_file.write_text('.class public Lio/flutter/embedding/Test;')

        injector = AegisInjector(str(tmp_path))

        assert injector._should_skip_obfuscation(flutter_file) is True

    def test_should_skip_react_native_framework(self, tmp_path):
        """Should skip React Native framework classes"""
        setup_basic_apk(tmp_path)
        rn_file = tmp_path / "smali" / "com" / "facebook" / "react" / "Test.smali"
        rn_file.parent.mkdir(parents=True, exist_ok=True)
        rn_file.write_text('.class public Lcom/facebook/react/Test;')

        injector = AegisInjector(str(tmp_path))

        assert injector._should_skip_obfuscation(rn_file) is True

    def test_should_skip_binary_files(self, tmp_path):
        """Should skip binary files"""
        setup_basic_apk(tmp_path)
        binary_file = tmp_path / "smali" / "Binary.smali"
        # Create file with null bytes (binary indicator)
        binary_file.write_bytes(b'\x00\x00\x00\x00' + b'some text')

        injector = AegisInjector(str(tmp_path))

        assert injector._should_skip_obfuscation(binary_file) is True


class TestInjectorEncodingHandling:
    """Test multi-encoding file reading"""

    def test_read_smali_utf8(self, tmp_path):
        """Should read UTF-8 encoded files"""
        setup_basic_apk(tmp_path)
        smali_file = tmp_path / "test.smali"
        content = ".class public Lcom/test/Test;\n# UTF-8: `}L"
        smali_file.write_text(content, encoding='utf-8')

        injector = AegisInjector(str(tmp_path))
        read_content, encoding = injector._read_smali_file_safe(smali_file)

        assert read_content is not None
        assert encoding == 'utf-8'
        assert '`}L' in read_content

    def test_read_smali_latin1_fallback(self, tmp_path):
        """Should fallback to latin-1 encoding"""
        setup_basic_apk(tmp_path)
        smali_file = tmp_path / "test.smali"
        content = ".class public Lcom/test/Test;\n# Latin-1"
        smali_file.write_bytes(content.encode('latin-1'))

        injector = AegisInjector(str(tmp_path))
        read_content, encoding = injector._read_smali_file_safe(smali_file)

        assert read_content is not None
        assert encoding in ['utf-8', 'latin-1']  # Might succeed with utf-8 too

    def test_read_smali_binary_file(self, tmp_path):
        """Should return None for binary files"""
        setup_basic_apk(tmp_path)
        smali_file = tmp_path / "binary.smali"
        smali_file.write_bytes(b'\x00\x00\x00\x00\xFF\xFF')

        injector = AegisInjector(str(tmp_path))
        read_content, encoding = injector._read_smali_file_safe(smali_file)

        assert read_content is None

    def test_is_likely_binary_with_null_bytes(self, tmp_path):
        """Should detect binary files with null bytes"""
        setup_basic_apk(tmp_path)
        smali_file = tmp_path / "binary.smali"
        smali_file.write_bytes(b'\x00\x00\x00some text')

        injector = AegisInjector(str(tmp_path))

        assert injector._is_likely_binary(smali_file) is True

    def test_is_likely_binary_low_printable_ratio(self, tmp_path):
        """Should detect binary files with low printable ratio"""
        setup_basic_apk(tmp_path)
        smali_file = tmp_path / "binary.smali"
        # Create mostly non-printable content
        binary_content = bytes([i % 256 for i in range(256)])
        smali_file.write_bytes(binary_content)

        injector = AegisInjector(str(tmp_path))

        assert injector._is_likely_binary(smali_file) is True

    def test_is_not_binary_normal_smali(self, tmp_path):
        """Should not flag normal smali files as binary"""
        setup_basic_apk(tmp_path)
        smali_file = tmp_path / "normal.smali"
        smali_file.write_text('.class public Lcom/test/Test;\n.super Ljava/lang/Object;')

        injector = AegisInjector(str(tmp_path))

        assert injector._is_likely_binary(smali_file) is False


class TestInjectorAnalysis:
    """Test APK analysis functionality"""

    def test_analyze_returns_complete_info(self, tmp_path):
        """Should return complete analysis info"""
        setup_basic_apk(tmp_path)
        create_application_class(tmp_path)
        create_main_activity(tmp_path)

        injector = AegisInjector(str(tmp_path))
        analysis = injector.analyze()

        assert 'app_type' in analysis
        assert 'has_application' in analysis
        assert 'activity_count' in analysis
        assert 'activities' in analysis
        assert 'has_main_activity' in analysis
        assert 'package' in analysis

    def test_analyze_detects_application_class(self, tmp_path):
        """Should detect Application class"""
        setup_basic_apk(tmp_path)
        create_application_class(tmp_path)

        injector = AegisInjector(str(tmp_path))
        analysis = injector.analyze()

        assert analysis['has_application'] is True

    def test_analyze_counts_activities(self, tmp_path):
        """Should count activities correctly"""
        setup_basic_apk(tmp_path)
        create_main_activity(tmp_path)
        create_secondary_activity(tmp_path)

        injector = AegisInjector(str(tmp_path))
        analysis = injector.analyze()

        assert analysis['activity_count'] >= 2

    def test_get_package_name(self, tmp_path):
        """Should extract package name from manifest"""
        setup_basic_apk(tmp_path)

        injector = AegisInjector(str(tmp_path))
        package = injector._get_package_name()

        assert package == 'com.example.app'


class TestInjectorForgeAegis:
    """Test main injection workflow"""

    def test_forge_aegis_returns_stats(self, tmp_path):
        """Should return forge statistics"""
        setup_basic_apk(tmp_path)
        create_main_activity(tmp_path)
        setup_shield_templates(tmp_path)

        injector = AegisInjector(str(tmp_path))
        result = injector.forge_aegis()

        assert 'classes_added' in result
        assert 'injection_count' in result
        assert 'success_rate' in result
        assert 'enabled_shields' in result

    def test_forge_aegis_with_custom_config(self, tmp_path):
        """Should respect custom configuration"""
        setup_basic_apk(tmp_path)
        create_main_activity(tmp_path)
        setup_shield_templates(tmp_path)

        # Custom config with only root detection
        config = AegisConfig()
        config.config['shields']['emulator_detection'] = False
        config.config['shields']['debug_detection'] = False
        config.config['shields']['developer_options'] = False

        injector = AegisInjector(str(tmp_path), config=config)
        result = injector.forge_aegis()

        enabled = result['enabled_shields']
        assert 'Root Detection' in enabled
        assert 'Emulator Detection' not in enabled

    def test_forge_aegis_injection_success(self, tmp_path):
        """Should inject successfully"""
        setup_basic_apk(tmp_path)
        create_main_activity(tmp_path)
        setup_shield_templates(tmp_path)

        injector = AegisInjector(str(tmp_path))
        result = injector.forge_aegis()

        assert result['injection_count'] > 0
        assert result['success_rate'] == 100

    def test_get_enabled_shields_all(self, tmp_path):
        """Should return all enabled shields"""
        setup_basic_apk(tmp_path)

        config = AegisConfig()
        injector = AegisInjector(str(tmp_path), config=config)

        shields = injector._get_enabled_shields()

        assert 'Root Detection' in shields
        assert 'Emulator Detection' in shields
        assert 'Debug Detection' in shields
        assert 'Developer Options Detection' in shields

    def test_get_enabled_shields_partial(self, tmp_path):
        """Should return only enabled shields"""
        setup_basic_apk(tmp_path)

        config = AegisConfig()
        config.config['shields']['root_detection'] = True
        config.config['shields']['emulator_detection'] = False
        config.config['shields']['debug_detection'] = False
        config.config['shields']['developer_options'] = False

        injector = AegisInjector(str(tmp_path), config=config)
        shields = injector._get_enabled_shields()

        assert 'Root Detection' in shields
        assert len(shields) == 1


class TestInjectorVerboseMode:
    """Test verbose logging"""

    def test_verbose_initialization(self, tmp_path):
        """Should initialize with verbose mode"""
        setup_basic_apk(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=True)

        assert injector.verbose is True

    def test_verbose_with_obfuscation(self, tmp_path):
        """Should enable obfuscation with verbose logging"""
        setup_basic_apk(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=True, obfuscate_strings=True)

        assert injector.verbose is True
        assert injector.obfuscate_strings is True


# Helper Functions

def setup_basic_apk(work_dir: Path):
    """Create basic APK structure"""
    smali_dir = work_dir / "smali"
    smali_dir.mkdir(parents=True, exist_ok=True)

    # Create AndroidManifest.xml
    manifest = work_dir / "AndroidManifest.xml"
    manifest.write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<manifest package="com.example.app">'
        '<application android:name=".MyApplication">'
        '<activity android:name=".MainActivity">'
        '<intent-filter><action android:name="android.intent.action.MAIN"/></intent-filter>'
        '</activity>'
        '</application>'
        '</manifest>'
    )


def setup_shield_templates(work_dir: Path):
    """Setup shield template files"""
    templates_dir = work_dir.parent / "templates" / "smali"
    templates_dir.mkdir(parents=True, exist_ok=True)

    shields = ['RootShield.smali', 'EmulatorShield.smali',
               'DebugShield.smali', 'DeveloperShield.smali']

    for shield in shields:
        (templates_dir / shield).write_text(f'.class public Lcom/noiaegis/{shield.replace(".smali", "")};')


def create_application_class(work_dir: Path) -> Path:
    """Create Application class"""
    app_dir = work_dir / "smali" / "com" / "example" / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    app_file = app_dir / "MyApplication.smali"
    app_file.write_text("""
.class public Lcom/example/app/MyApplication;
.super Landroid/app/Application;

.method public onCreate()V
    .locals 0
    invoke-super {p0}, Landroid/app/Application;->onCreate()V
    return-void
.end method
""")
    return app_file


def create_main_activity(work_dir: Path) -> Path:
    """Create MainActivity"""
    activity_dir = work_dir / "smali" / "com" / "example" / "app"
    activity_dir.mkdir(parents=True, exist_ok=True)

    activity_file = activity_dir / "MainActivity.smali"
    activity_file.write_text("""
.class public Lcom/example/app/MainActivity;
.super Landroidx/appcompat/app/AppCompatActivity;

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 0
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V
    return-void
.end method
""")
    return activity_file


def create_secondary_activity(work_dir: Path) -> Path:
    """Create secondary activity"""
    activity_dir = work_dir / "smali" / "com" / "example" / "app"
    activity_dir.mkdir(parents=True, exist_ok=True)

    activity_file = activity_dir / "SecondActivity.smali"
    activity_file.write_text("""
.class public Lcom/example/app/SecondActivity;
.super Landroid/app/Activity;
""")
    return activity_file


def setup_react_native_structure(work_dir: Path):
    """Setup React Native app structure"""
    create_react_activity(work_dir)


def create_react_activity(work_dir: Path) -> Path:
    """Create React Native activity"""
    rn_dir = work_dir / "smali" / "com" / "facebook" / "react"
    rn_dir.mkdir(parents=True, exist_ok=True)

    rn_file = rn_dir / "ReactActivity.smali"
    rn_file.write_text("""
.class public Lcom/facebook/react/ReactActivity;
.super Landroid/app/Activity;
""")
    return rn_file


def setup_flutter_structure(work_dir: Path):
    """Setup Flutter app structure"""
    create_flutter_activity(work_dir)


def create_flutter_activity(work_dir: Path) -> Path:
    """Create Flutter activity"""
    flutter_dir = work_dir / "smali" / "io" / "flutter" / "embedding" / "android"
    flutter_dir.mkdir(parents=True, exist_ok=True)

    flutter_file = flutter_dir / "FlutterActivity.smali"
    flutter_file.write_text("""
.class public Lio/flutter/embedding/android/FlutterActivity;
.super Landroid/app/Activity;
""")
    return flutter_file


def create_smali_with_strings(work_dir: Path):
    """Create smali file with sensitive strings"""
    app_dir = work_dir / "smali" / "com" / "example" / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    smali_file = app_dir / "Config.smali"
    smali_file.write_text("""
.class public Lcom/example/app/Config;
.super Ljava/lang/Object;

.method public static getApiKey()Ljava/lang/String;
    .locals 1
    const-string v0, "sk_live_1234567890abcdef"
    return-object v0
.end method

.method public static getApiUrl()Ljava/lang/String;
    .locals 1
    const-string v0, "https://api.example.com/v1"
    return-object v0
.end method
""")


@pytest.fixture
def tmp_path():
    """Provide temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
