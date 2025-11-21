"""
Tests for Core Injector Functionality

Tests injection, shield management, and code generation.
"""

import pytest
import tempfile
from pathlib import Path
from noia_aegis.core.injector import AegisInjector
from noia_aegis.core.config import AegisConfig


class TestAegisInjectorCore:
    """Test core AegisInjector functionality"""

    def test_injector_initialization(self, tmp_path):
        """Should initialize injector"""
        setup_basic_apk_structure(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=False)

        assert injector.work_dir == tmp_path
        assert injector.smali_dir == tmp_path / "smali"
        assert injector.verbose is False

    def test_analyze_native_app(self, tmp_path):
        """Should analyze native Android app"""
        setup_basic_apk_structure(tmp_path)
        setup_native_app(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=False)
        analysis = injector.analyze()

        assert analysis['app_type'] == 'Native Android'
        assert analysis['package'] == 'com.example.app'

    def test_get_enabled_shields(self, tmp_path):
        """Should return list of enabled shields"""
        setup_basic_apk_structure(tmp_path)

        config = AegisConfig()
        injector = AegisInjector(str(tmp_path), config=config)

        shields = injector._get_enabled_shields()

        assert 'Root Detection' in shields
        assert 'Emulator Detection' in shields
        assert 'Debug Detection' in shields
        assert 'Developer Options Detection' in shields

    def test_copy_shields(self, tmp_path):
        """Should copy enabled shield files"""
        setup_basic_apk_structure(tmp_path)

        # Create template files
        templates_dir = tmp_path.parent / "templates" / "smali"
        templates_dir.mkdir(parents=True, exist_ok=True)

        shield_files = ['RootShield.smali', 'EmulatorShield.smali',
                        'DebugShield.smali', 'DeveloperShield.smali']
        for shield in shield_files:
            (templates_dir / shield).write_text(f".class public L{shield};")

        # Monkey patch templates_dir
        injector = AegisInjector(str(tmp_path), verbose=False)
        injector.templates_dir = templates_dir

        copied = injector._copy_shields()

        # Should copy all enabled shields + AegisCore
        assert copied == 5  # 4 shields + 1 core

        # Verify files were copied
        aegis_dir = tmp_path / "smali" / "com" / "noiaegis"
        assert aegis_dir.exists()

    def test_generate_aegis_core(self, tmp_path):
        """Should generate AegisCore.smali with enabled shields"""
        setup_basic_apk_structure(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=False)
        injector._generate_aegis_core()

        aegis_core = tmp_path / "smali" / "com" / "noiaegis" / "AegisCore.smali"
        assert aegis_core.exists()

        content = aegis_core.read_text()
        assert '.class public Lcom/noiaegis/AegisCore;' in content
        assert '.method public static protect(Landroid/content/Context;)V' in content
        assert 'RootShield' in content
        assert 'EmulatorShield' in content

    def test_inject_to_application(self, tmp_path):
        """Should inject to Application.onCreate()"""
        setup_basic_apk_structure(tmp_path)

        app_file = create_application_class(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=False)
        result = injector._inject_to_application(app_file)

        assert result is True

        content = app_file.read_text()
        assert '# AEGIS INJECTED' in content
        assert 'invoke-static {p0}, Lcom/noiaegis/AegisCore;->protect' in content

    def test_inject_twice_should_skip(self, tmp_path):
        """Should not inject twice"""
        setup_basic_apk_structure(tmp_path)

        app_file = create_application_class(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=False)

        # First injection
        result1 = injector._inject_to_application(app_file)
        assert result1 is True

        # Second injection should be skipped
        result2 = injector._inject_to_application(app_file)
        assert result2 is False

    def test_inject_or_create_oncreate(self, tmp_path):
        """Should inject to existing onCreate"""
        setup_basic_apk_structure(tmp_path)

        activity_file = create_activity_class(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=False)
        result = injector._inject_or_create_oncreate(activity_file)

        assert result is True

        content = activity_file.read_text()
        assert '# AEGIS INJECTED' in content
        assert 'invoke-static {p0}, Lcom/noiaegis/AegisCore;->protect' in content

    def test_create_oncreate_if_not_exists(self, tmp_path):
        """Should create onCreate if it doesn't exist"""
        setup_basic_apk_structure(tmp_path)

        activity_file = create_activity_without_oncreate(tmp_path)

        injector = AegisInjector(str(tmp_path), verbose=False)
        result = injector._inject_or_create_oncreate(activity_file)

        assert result is True

        content = activity_file.read_text()
        assert '# AEGIS INJECTED' in content
        assert '.method protected onCreate(Landroid/os/Bundle;)V' in content


# Helper functions

def setup_basic_apk_structure(work_dir: Path):
    """Create basic APK structure"""
    smali_dir = work_dir / "smali"
    smali_dir.mkdir(parents=True, exist_ok=True)

    # Create AndroidManifest.xml
    manifest = work_dir / "AndroidManifest.xml"
    manifest.write_text('<?xml version="1.0" encoding="utf-8"?>'
                        '<manifest package="com.example.app"></manifest>')


def setup_native_app(work_dir: Path):
    """Setup native Android app structure"""
    # This is already created by setup_basic_apk_structure
    pass


def create_application_class(work_dir: Path) -> Path:
    """Create Application class with onCreate"""
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


def create_activity_class(work_dir: Path) -> Path:
    """Create Activity class with onCreate"""
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


def create_activity_without_oncreate(work_dir: Path) -> Path:
    """Create Activity class without onCreate"""
    activity_dir = work_dir / "smali" / "com" / "example" / "app"
    activity_dir.mkdir(parents=True, exist_ok=True)

    activity_file = activity_dir / "SimpleActivity.smali"
    activity_file.write_text("""
.class public Lcom/example/app/SimpleActivity;
.super Landroidx/appcompat/app/AppCompatActivity;
""")
    return activity_file


@pytest.fixture
def tmp_path():
    """Provide temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])