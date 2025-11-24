"""
Tests for APKProcessor

Comprehensive tests for APK processing including decompile, recompile,
signing, and tool management.
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from noia_aegis.core.processor import APKProcessor


class TestProcessorInitialization:
    """Test APKProcessor initialization"""

    def test_init_with_valid_apk(self, tmp_path):
        """Should initialize with valid APK path"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')  # ZIP header (APK is ZIP)

        with patch('noia_aegis.core.processor.ToolManager'):
            processor = APKProcessor(str(apk_file))

            assert processor.apk_path == apk_file
            assert processor.app_name == 'test'
            assert processor.verbose is False

    def test_init_with_missing_apk(self, tmp_path):
        """Should raise FileNotFoundError for missing APK"""
        apk_file = tmp_path / "missing.apk"

        with patch('noia_aegis.core.processor.ToolManager'):
            with pytest.raises(FileNotFoundError):
                APKProcessor(str(apk_file))

    def test_init_with_verbose(self, tmp_path):
        """Should initialize with verbose mode"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager'):
            processor = APKProcessor(str(apk_file), verbose=True)

            assert processor.verbose is True

    def test_init_creates_work_directory_path(self, tmp_path):
        """Should create work directory path"""
        apk_file = tmp_path / "myapp.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager'):
            processor = APKProcessor(str(apk_file))

            assert 'myapp_work' in str(processor.work_dir)


class TestProcessorDecompile:
    """Test APK decompilation"""

    def test_decompile_success(self, tmp_path):
        """Should decompile APK successfully"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            # Mock tool manager
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            # Mock subprocess
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')

                result = processor.decompile()

                assert result == processor.work_dir
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert 'java' in args
                assert '-jar' in args
                assert 'd' in args

    def test_decompile_failure(self, tmp_path):
        """Should raise exception on decompile failure"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr='Decompile error')

                with pytest.raises(Exception, match="Decompile failed"):
                    processor.decompile()

    def test_decompile_removes_existing_work_dir(self, tmp_path):
        """Should remove existing work directory"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            # Create existing work dir
            processor.work_dir.mkdir(parents=True, exist_ok=True)
            (processor.work_dir / "old_file.txt").write_text("old")

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')

                processor.decompile()

                # Old file should be gone
                assert not (processor.work_dir / "old_file.txt").exists()


class TestProcessorRecompile:
    """Test APK recompilation"""

    def test_recompile_success(self, tmp_path):
        """Should recompile APK successfully"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))
            processor.work_dir.mkdir(parents=True, exist_ok=True)

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')

                result = processor.recompile()

                assert 'test_protected.apk' in str(result)
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert 'java' in args
                assert 'b' in args

    def test_recompile_with_custom_output(self, tmp_path):
        """Should recompile with custom output name"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))
            processor.work_dir.mkdir(parents=True, exist_ok=True)

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')

                result = processor.recompile("custom_output.apk")

                assert 'custom_output.apk' in str(result)

    def test_recompile_failure(self, tmp_path):
        """Should raise exception on recompile failure"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr='Recompile error')

                with pytest.raises(Exception, match="Recompile failed"):
                    processor.recompile()


class TestProcessorSigning:
    """Test APK signing"""

    def test_sign_with_custom_keystore(self, tmp_path):
        """Should sign with custom keystore"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        unsigned_apk = tmp_path / "unsigned.apk"
        unsigned_apk.write_bytes(b'PK\x03\x04')

        keystore = tmp_path / "release.keystore"
        keystore.write_bytes(b'keystore')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch.object(processor, '_sign_with_keystore') as mock_sign:
                mock_sign.return_value = tmp_path / "signed.apk"

                result = processor.sign(
                    unsigned_apk,
                    keystore_path=str(keystore),
                    keystore_pass="pass123",
                    key_alias="myalias",
                    key_pass="keypass"
                )

                mock_sign.assert_called_once()
                assert result == tmp_path / "signed.apk"

    def test_sign_with_uber_signer(self, tmp_path):
        """Should sign with uber-apk-signer for debug"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        unsigned_apk = tmp_path / "unsigned.apk"
        unsigned_apk.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'apktool': tmp_path / 'apktool.jar',
                'uber-apk-signer': tmp_path / 'uber.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch.object(processor, '_sign_with_uber') as mock_uber:
                mock_uber.return_value = tmp_path / "signed-debug.apk"

                result = processor.sign(unsigned_apk)

                mock_uber.assert_called_once()
                assert result == tmp_path / "signed-debug.apk"

    def test_sign_with_uber_success(self, tmp_path):
        """Should sign with uber-apk-signer successfully"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        unsigned_apk = tmp_path / "unsigned.apk"
        unsigned_apk.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {
                'uber-apk-signer': tmp_path / 'uber.jar'
            }
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr='')

                result = processor._sign_with_uber(unsigned_apk)

                assert 'aligned-debugSigned.apk' in str(result)
                mock_run.assert_called_once()

    def test_sign_with_keystore_missing_file(self, tmp_path):
        """Should raise error for missing keystore"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        unsigned_apk = tmp_path / "unsigned.apk"
        unsigned_apk.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {}
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with pytest.raises(FileNotFoundError, match="Keystore not found"):
                processor._sign_with_keystore(
                    unsigned_apk,
                    "missing.keystore",
                    "pass",
                    "alias",
                    "keypass"
                )


class TestProcessorToolDetection:
    """Test tool detection (apksigner, zipalign)"""

    def test_find_apksigner_from_android_home(self, tmp_path):
        """Should find apksigner from ANDROID_HOME"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        # Create fake Android SDK structure
        android_home = tmp_path / "android_sdk"
        build_tools = android_home / "build-tools" / "33.0.0"
        build_tools.mkdir(parents=True, exist_ok=True)
        apksigner = build_tools / "apksigner"
        apksigner.write_text("#!/bin/bash")

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {}
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch.dict('os.environ', {'ANDROID_HOME': str(android_home)}):
                result = processor._find_apksigner()

                assert result is not None
                assert 'apksigner' in str(result)

    def test_find_apksigner_not_found(self, tmp_path):
        """Should return None if apksigner not found"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {}
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch.dict('os.environ', {}, clear=True):
                result = processor._find_apksigner()

                assert result is None

    def test_find_zipalign(self, tmp_path):
        """Should find zipalign from ANDROID_HOME"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        # Create fake Android SDK structure
        android_home = tmp_path / "android_sdk"
        build_tools = android_home / "build-tools" / "33.0.0"
        build_tools.mkdir(parents=True, exist_ok=True)
        zipalign = build_tools / "zipalign"
        zipalign.write_text("#!/bin/bash")

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {}
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch.dict('os.environ', {'ANDROID_HOME': str(android_home)}):
                result = processor._find_zipalign()

                assert result is not None
                assert 'zipalign' in str(result)


class TestProcessorVerification:
    """Test APK signature verification"""

    def test_verify_signature_success(self, tmp_path):
        """Should verify APK signature successfully"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        signed_apk = tmp_path / "signed.apk"
        signed_apk.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {}
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            with patch.object(processor, '_find_apksigner') as mock_find:
                mock_find.return_value = "/usr/bin/apksigner"

                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = Mock(
                        returncode=0,
                        stdout="Verified successfully",
                        stderr=""
                    )

                    result = processor.verify_signature(signed_apk)

                    assert result is True


class TestProcessorCleanup:
    """Test cleanup functionality"""

    def test_cleanup_removes_work_dir(self, tmp_path):
        """Should remove work directory on cleanup"""
        apk_file = tmp_path / "test.apk"
        apk_file.write_bytes(b'PK\x03\x04')

        with patch('noia_aegis.core.processor.ToolManager') as mock_tool_manager:
            mock_instance = Mock()
            mock_instance.ensure_tools.return_value = {}
            mock_instance.tools_dir = tmp_path / 'tools'
            mock_tool_manager.return_value = mock_instance

            processor = APKProcessor(str(apk_file))

            # Create work directory
            processor.work_dir.mkdir(parents=True, exist_ok=True)
            (processor.work_dir / "test.txt").write_text("test")

            assert processor.work_dir.exists()

            processor.cleanup()

            assert not processor.work_dir.exists()


@pytest.fixture
def tmp_path():
    """Provide temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
