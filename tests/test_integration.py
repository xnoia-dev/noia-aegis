"""
Integration Tests for Noia Aegis

End-to-end tests for the full APK protection workflow including
decompile, inject, recompile, and signing.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from noia_aegis.core.processor import APKProcessor
from noia_aegis.core.injector import AegisInjector
from noia_aegis.core.config import AegisConfig


class TestFullProtectionWorkflow:
    """Test complete APK protection workflow"""

    def test_full_workflow_native_app(self, tmp_path):
        """Should protect Native Android app end-to-end"""
        # Setup
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            # Create processor
            processor = APKProcessor(str(apk_file))

            # Step 1: Decompile
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            # Setup APK structure
            setup_native_apk_structure(work_dir)
            setup_shield_templates(work_dir)

            # Step 2: Inject shields
            injector = AegisInjector(str(work_dir))
            result = injector.forge_aegis()

            assert result['injection_count'] > 0
            assert result['success_rate'] == 100

            # Step 3: Recompile
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                recompiled_apk = processor.recompile()

            assert recompiled_apk.name.endswith('.apk')

            # Step 4: Sign
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                signed_apk = processor.sign(recompiled_apk)

            assert signed_apk.name.endswith('.apk')

    def test_full_workflow_flutter_app(self, tmp_path):
        """Should protect Flutter app end-to-end"""
        apk_file = tmp_path / "flutter.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            # Decompile
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            # Setup Flutter structure
            setup_flutter_apk_structure(work_dir)
            setup_shield_templates(work_dir)

            # Analyze and inject
            injector = AegisInjector(str(work_dir))
            analysis = injector.analyze()

            assert analysis['app_type'] == 'Flutter'

            result = injector.forge_aegis()
            assert result['injection_count'] > 0

    def test_full_workflow_react_native_app(self, tmp_path):
        """Should protect React Native app end-to-end"""
        apk_file = tmp_path / "rn.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            # Decompile
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            # Setup React Native structure
            setup_react_native_apk_structure(work_dir)
            setup_shield_templates(work_dir)

            # Analyze and inject
            injector = AegisInjector(str(work_dir))
            analysis = injector.analyze()

            assert analysis['app_type'] == 'React Native'

            result = injector.forge_aegis()
            assert result['injection_count'] > 0


class TestWorkflowWithCustomConfiguration:
    """Test workflow with custom configurations"""

    def test_workflow_with_selective_shields(self, tmp_path):
        """Should apply only selected shields"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            setup_native_apk_structure(work_dir)
            setup_shield_templates(work_dir)

            # Custom config: only root detection
            config = AegisConfig()
            config.config['shields']['root_detection'] = True
            config.config['shields']['emulator_detection'] = False
            config.config['shields']['debug_detection'] = False
            config.config['shields']['developer_options'] = False

            injector = AegisInjector(str(work_dir), config=config)
            result = injector.forge_aegis()

            enabled = result['enabled_shields']
            assert 'Root Detection' in enabled
            assert len(enabled) == 1

    def test_workflow_with_obfuscation(self, tmp_path):
        """Should obfuscate strings during workflow"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            setup_native_apk_structure(work_dir)
            setup_shield_templates(work_dir)
            create_smali_with_sensitive_strings(work_dir)

            # Enable obfuscation
            injector = AegisInjector(str(work_dir), obfuscate_strings=True)
            result = injector.forge_aegis()

            # Should have obfuscated strings
            assert 'obfuscated_strings' in result
            assert 'obfuscated_files' in result

    def test_workflow_with_custom_messages(self, tmp_path):
        """Should use custom threat messages"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            setup_native_apk_structure(work_dir)
            setup_shield_templates(work_dir)

            # Custom messages
            config = AegisConfig()
            config.config['messages']['root_detected'] = "Custom Root Message"

            injector = AegisInjector(str(work_dir), config=config)
            injector.forge_aegis()

            # Check AegisCore contains custom message
            aegis_core = work_dir / "smali" / "com" / "noiaegis" / "AegisCore.smali"
            if aegis_core.exists():
                content = aegis_core.read_text()
                assert "Custom Root Message" in content


class TestWorkflowSigningModes:
    """Test different signing modes"""

    def test_workflow_with_production_keystore(self, tmp_path):
        """Should sign with production keystore"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        keystore = tmp_path / "release.keystore"
        keystore.write_bytes(b'keystore_data')

        unsigned_apk = tmp_path / "unsigned.apk"
        unsigned_apk.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch.object(processor, '_sign_with_keystore') as mock_sign:
                mock_sign.return_value = tmp_path / "signed.apk"

                signed_apk = processor.sign(
                    unsigned_apk,
                    keystore_path=str(keystore),
                    keystore_pass="pass123",
                    key_alias="release",
                    key_pass="keypass"
                )

                mock_sign.assert_called_once()
                assert signed_apk.name == "signed.apk"

    def test_workflow_with_debug_signing(self, tmp_path):
        """Should sign with debug keystore"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        unsigned_apk = tmp_path / "unsigned.apk"
        unsigned_apk.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')

                signed_apk = processor.sign(unsigned_apk)

                assert 'debugSigned' in signed_apk.name


class TestWorkflowErrorHandling:
    """Test error handling in workflow"""

    def test_workflow_handles_decompile_error(self, tmp_path):
        """Should handle decompile errors gracefully"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr='Decompile error')

                with pytest.raises(Exception, match="Decompile failed"):
                    processor.decompile()

    def test_workflow_handles_recompile_error(self, tmp_path):
        """Should handle recompile errors gracefully"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))
            processor.work_dir.mkdir(parents=True, exist_ok=True)

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr='Recompile error')

                with pytest.raises(Exception, match="Recompile failed"):
                    processor.recompile()

    def test_workflow_handles_missing_keystore(self, tmp_path):
        """Should handle missing keystore error"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        unsigned_apk = tmp_path / "unsigned.apk"
        unsigned_apk.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with pytest.raises(FileNotFoundError):
                processor._sign_with_keystore(
                    unsigned_apk,
                    "missing.keystore",
                    "pass",
                    "alias",
                    "keypass"
                )

    def test_workflow_handles_invalid_apk(self, tmp_path):
        """Should handle invalid APK file"""
        apk_file = tmp_path / "invalid.apk"
        # Don't create the file

        with patch('noia_aegis.core.processor.ToolManager'):
            with pytest.raises(FileNotFoundError):
                APKProcessor(str(apk_file))


class TestWorkflowAnalysis:
    """Test analysis during workflow"""

    def test_workflow_detects_application_class(self, tmp_path):
        """Should detect Application class during analysis"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            setup_native_apk_structure(work_dir)
            create_application_class(work_dir)

            injector = AegisInjector(str(work_dir))
            analysis = injector.analyze()

            assert analysis['has_application'] is True
            assert analysis['package'] == 'com.example.app'

    def test_workflow_counts_activities(self, tmp_path):
        """Should count activities during analysis"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = setup_mock_tool_manager(tmp_path)
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')
                work_dir = processor.decompile()

            setup_native_apk_structure(work_dir)
            create_main_activity(work_dir)
            create_secondary_activity(work_dir)

            injector = AegisInjector(str(work_dir))
            analysis = injector.analyze()

            assert analysis['activity_count'] >= 2


# Helper Functions

def setup_mock_tool_manager(tmp_path):
    """Setup mock tool manager"""
    mock_instance = Mock()
    mock_instance.ensure_tools.return_value = {
        'apktool': tmp_path / 'apktool.jar',
        'uber-apk-signer': tmp_path / 'uber.jar'
    }
    mock_instance.tools_dir = tmp_path / 'tools'
    return mock_instance


def setup_native_apk_structure(work_dir: Path):
    """Setup native Android APK structure"""
    smali_dir = work_dir / "smali"
    smali_dir.mkdir(parents=True, exist_ok=True)

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

    create_main_activity(work_dir)


def setup_flutter_apk_structure(work_dir: Path):
    """Setup Flutter APK structure"""
    setup_native_apk_structure(work_dir)

    # Add Flutter activity
    flutter_dir = work_dir / "smali" / "io" / "flutter" / "embedding" / "android"
    flutter_dir.mkdir(parents=True, exist_ok=True)

    flutter_file = flutter_dir / "FlutterActivity.smali"
    flutter_file.write_text("""
.class public Lio/flutter/embedding/android/FlutterActivity;
.super Landroid/app/Activity;
""")


def setup_react_native_apk_structure(work_dir: Path):
    """Setup React Native APK structure"""
    setup_native_apk_structure(work_dir)

    # Add React Native activity
    rn_dir = work_dir / "smali" / "com" / "facebook" / "react"
    rn_dir.mkdir(parents=True, exist_ok=True)

    rn_file = rn_dir / "ReactActivity.smali"
    rn_file.write_text("""
.class public Lcom/facebook/react/ReactActivity;
.super Landroid/app/Activity;
""")


def setup_shield_templates(work_dir: Path):
    """Setup shield template files"""
    templates_dir = work_dir.parent / "templates" / "smali"
    templates_dir.mkdir(parents=True, exist_ok=True)

    shields = ['RootShield.smali', 'EmulatorShield.smali',
               'DebugShield.smali', 'DeveloperShield.smali']

    for shield in shields:
        (templates_dir / shield).write_text(
            f'.class public Lcom/noiaegis/{shield.replace(".smali", "")};'
        )


def create_application_class(work_dir: Path):
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


def create_main_activity(work_dir: Path):
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


def create_secondary_activity(work_dir: Path):
    """Create secondary activity"""
    activity_dir = work_dir / "smali" / "com" / "example" / "app"
    activity_dir.mkdir(parents=True, exist_ok=True)

    activity_file = activity_dir / "SecondActivity.smali"
    activity_file.write_text("""
.class public Lcom/example/app/SecondActivity;
.super Landroid/app/Activity;
""")


def create_smali_with_sensitive_strings(work_dir: Path):
    """Create smali file with sensitive strings for obfuscation"""
    app_dir = work_dir / "smali" / "com" / "example" / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    config_file = app_dir / "Config.smali"
    config_file.write_text("""
.class public Lcom/example/app/Config;
.super Ljava/lang/Object;

.method public static getApiKey()Ljava/lang/String;
    .locals 1
    const-string v0, "sk_live_1234567890abcdef"
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
