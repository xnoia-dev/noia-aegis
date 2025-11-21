"""
Tests for Flutter Support and Encoding Fallback

Tests the new Flutter framework detection, multi-encoding file reading,
and binary file detection features added in v1.3.1.
"""

import pytest
import tempfile
from pathlib import Path
from noia_aegis.core.injector import AegisInjector


class TestFlutterDetection:
    """Test Flutter framework detection"""

    def test_detect_flutter_activity(self, tmp_path):
        """Should detect Flutter app via FlutterActivity"""
        injector = self._create_injector(tmp_path)

        # Create Flutter smali structure
        flutter_dir = tmp_path / "smali" / "io" / "flutter" / "embedding" / "android"
        flutter_dir.mkdir(parents=True)
        (flutter_dir / "FlutterActivity.smali").write_text(".class public Lio/flutter/embedding/android/FlutterActivity;")

        assert injector._is_flutter() is True

    def test_detect_flutter_libflutter_so(self, tmp_path):
        """Should detect Flutter app via libflutter.so"""
        injector = self._create_injector(tmp_path)

        # Create libflutter.so
        lib_dir = tmp_path / "lib" / "arm64-v8a"
        lib_dir.mkdir(parents=True)
        (lib_dir / "libflutter.so").write_bytes(b"FLUTTER_BINARY")

        assert injector._is_flutter() is True

    def test_detect_flutter_assets(self, tmp_path):
        """Should detect Flutter app via flutter_assets"""
        injector = self._create_injector(tmp_path)

        # Create flutter_assets
        assets_dir = tmp_path / "assets" / "flutter_assets"
        assets_dir.mkdir(parents=True)
        (assets_dir / "kernel_blob.bin").write_bytes(b"FLUTTER")

        assert injector._is_flutter() is True

    def test_not_flutter_app(self, tmp_path):
        """Should return False for non-Flutter apps"""
        injector = self._create_injector(tmp_path)

        # Create non-Flutter structure
        smali_dir = tmp_path / "smali" / "com" / "example"
        smali_dir.mkdir(parents=True)
        (smali_dir / "MainActivity.smali").write_text(".class public Lcom/example/MainActivity;")

        assert injector._is_flutter() is False

    def _create_injector(self, work_dir):
        """Helper to create injector instance"""
        return AegisInjector(str(work_dir), verbose=False)


class TestEncodingFallback:
    """Test multi-encoding file reading"""

    def test_read_utf8_file(self, tmp_path):
        """Should read UTF-8 encoded file"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "test.smali"
        test_file.write_text("Hello UTF-8 世界", encoding='utf-8')

        content, encoding = injector._read_smali_file_safe(test_file)

        assert content is not None
        assert encoding == 'utf-8'
        assert "世界" in content

    def test_read_latin1_file(self, tmp_path):
        """Should fallback to Latin-1 for non-UTF-8 files"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "test.smali"
        # Write Latin-1 encoded content (byte 0x97 = em-dash in Windows-1252)
        test_file.write_bytes(b"Hello \x97 World")

        content, encoding = injector._read_smali_file_safe(test_file)

        assert content is not None
        assert encoding in ['latin-1', 'iso-8859-1', 'cp1252']
        assert len(content) > 0

    def test_read_cp1252_file(self, tmp_path):
        """Should handle Windows-1252 encoding"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "test.smali"
        # Windows-1252 specific characters
        test_file.write_bytes(b"Quote: \x93Hello\x94")  # Smart quotes

        content, encoding = injector._read_smali_file_safe(test_file)

        assert content is not None
        assert encoding in ['latin-1', 'iso-8859-1', 'cp1252']

    def test_read_corrupted_file_with_ignore(self, tmp_path):
        """Should use error ignore mode for badly corrupted files"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "test.smali"
        # Mix of valid and invalid bytes
        test_file.write_bytes(b"Valid\xFFInvalid\xFEBytes")

        content, encoding = injector._read_smali_file_safe(test_file)

        assert content is not None
        # Should fall back to utf-8-ignore
        assert "Valid" in content

    def test_read_nonexistent_file(self, tmp_path):
        """Should return None for nonexistent file"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "nonexistent.smali"

        content, encoding = injector._read_smali_file_safe(test_file)

        assert content is None
        assert encoding is None

    def _create_injector(self, work_dir):
        """Helper to create injector instance"""
        smali_dir = work_dir / "smali"
        smali_dir.mkdir(exist_ok=True)
        return AegisInjector(str(work_dir), verbose=False)


class TestBinaryDetection:
    """Test binary file detection"""

    def test_detect_binary_with_null_bytes(self, tmp_path):
        """Should detect binary files with null bytes"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "binary.smali"
        test_file.write_bytes(b"Some text\x00with null bytes")

        assert injector._is_likely_binary(test_file) is True

    def test_detect_text_file(self, tmp_path):
        """Should not detect text files as binary"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "text.smali"
        test_file.write_text(".class public Lcom/example/Test;\n.super Ljava/lang/Object;")

        assert injector._is_likely_binary(test_file) is False

    def test_detect_mostly_binary(self, tmp_path):
        """Should detect files with low printable ratio as binary"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "mostly_binary.smali"
        # Less than 70% printable characters
        binary_data = bytes(range(256)) * 10
        test_file.write_bytes(binary_data)

        assert injector._is_likely_binary(test_file) is True

    def test_text_with_some_special_chars(self, tmp_path):
        """Should allow text files with some special characters"""
        injector = self._create_injector(tmp_path)

        test_file = tmp_path / "text_special.smali"
        # Mostly printable with tabs and newlines
        content = ".class public Test\n\tconst-string v0, \"Hello\"\n\treturn-void"
        test_file.write_text(content)

        assert injector._is_likely_binary(test_file) is False

    def _create_injector(self, work_dir):
        """Helper to create injector instance"""
        smali_dir = work_dir / "smali"
        smali_dir.mkdir(exist_ok=True)
        return AegisInjector(str(work_dir), verbose=False)


class TestSkipObfuscation:
    """Test file skipping during obfuscation"""

    def test_skip_flutter_framework_files(self, tmp_path):
        """Should skip Flutter framework files"""
        injector = self._create_injector(tmp_path)

        flutter_files = [
            "smali/io/flutter/embedding/FlutterEngine.smali",
            "smali/io/flutter/app/FlutterApplication.smali",
            "smali/io/flutter/plugin/common/MethodChannel.smali",
            "smali/io/flutter/view/FlutterView.smali",
        ]

        for file_path in flutter_files:
            test_file = tmp_path / file_path
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(".class public Test;")

            assert injector._should_skip_obfuscation(test_file) is True

    def test_skip_react_native_files(self, tmp_path):
        """Should skip React Native framework files"""
        injector = self._create_injector(tmp_path)

        rn_files = [
            "smali/com/facebook/react/ReactActivity.smali",
            "smali/com/facebook/hermes/HermesExecutor.smali",
            "smali/com/facebook/jni/HybridData.smali",
        ]

        for file_path in rn_files:
            test_file = tmp_path / file_path
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(".class public Test;")

            assert injector._should_skip_obfuscation(test_file) is True

    def test_skip_android_framework(self, tmp_path):
        """Should skip Android framework files"""
        injector = self._create_injector(tmp_path)

        android_files = [
            "smali/android/app/Activity.smali",
            "smali/androidx/appcompat/app/AppCompatActivity.smali",
            "smali/com/google/android/material/button/MaterialButton.smali",
        ]

        for file_path in android_files:
            test_file = tmp_path / file_path
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(".class public Test;")

            assert injector._should_skip_obfuscation(test_file) is True

    def test_skip_aegis_own_classes(self, tmp_path):
        """Should skip Noia Aegis own classes"""
        injector = self._create_injector(tmp_path)

        aegis_file = tmp_path / "smali/com/noiaegis/AegisCore.smali"
        aegis_file.parent.mkdir(parents=True, exist_ok=True)
        aegis_file.write_text(".class public Lcom/noiaegis/AegisCore;")

        assert injector._should_skip_obfuscation(aegis_file) is True

    def test_skip_binary_files(self, tmp_path):
        """Should skip binary files"""
        injector = self._create_injector(tmp_path)

        binary_file = tmp_path / "smali/com/example/Binary.smali"
        binary_file.parent.mkdir(parents=True, exist_ok=True)
        binary_file.write_bytes(b"Binary\x00Content\x00Here")

        assert injector._should_skip_obfuscation(binary_file) is True

    def test_do_not_skip_app_files(self, tmp_path):
        """Should NOT skip application files"""
        injector = self._create_injector(tmp_path)

        app_files = [
            "smali/com/example/myapp/MainActivity.smali",
            "smali/com/mycompany/models/User.smali",
            "smali/id/myapp/utils/ApiClient.smali",
        ]

        for file_path in app_files:
            test_file = tmp_path / file_path
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(".class public Lcom/example/Test;")

            assert injector._should_skip_obfuscation(test_file) is False

    def _create_injector(self, work_dir):
        """Helper to create injector instance"""
        smali_dir = work_dir / "smali"
        smali_dir.mkdir(exist_ok=True)
        return AegisInjector(str(work_dir), verbose=False)


class TestAnalyzeAppType:
    """Test app type detection in analyze()"""

    def test_analyze_flutter_app(self, tmp_path):
        """Should detect Flutter app type"""
        injector = self._create_injector(tmp_path)

        # Create Flutter structure
        flutter_dir = tmp_path / "smali" / "io" / "flutter" / "embedding" / "android"
        flutter_dir.mkdir(parents=True)
        (flutter_dir / "FlutterActivity.smali").write_text(".class public Lio/flutter/embedding/android/FlutterActivity;")

        result = injector.analyze()

        assert result['app_type'] == 'Flutter'

    def test_analyze_react_native_app(self, tmp_path):
        """Should detect React Native app type"""
        injector = self._create_injector(tmp_path)

        # Create React Native structure
        rn_dir = tmp_path / "smali" / "com" / "facebook" / "react"
        rn_dir.mkdir(parents=True)
        (rn_dir / "ReactActivity.smali").write_text(".class public Lcom/facebook/react/ReactActivity;")

        result = injector.analyze()

        assert result['app_type'] == 'React Native'

    def test_analyze_native_app(self, tmp_path):
        """Should detect Native Android app type"""
        injector = self._create_injector(tmp_path)

        # Create native Android structure
        native_dir = tmp_path / "smali" / "com" / "example" / "app"
        native_dir.mkdir(parents=True)
        (native_dir / "MainActivity.smali").write_text(".class public Lcom/example/app/MainActivity;")

        result = injector.analyze()

        assert result['app_type'] == 'Native Android'

    def test_flutter_takes_precedence(self, tmp_path):
        """Flutter detection should take precedence over React Native"""
        injector = self._create_injector(tmp_path)

        # Create both Flutter and React Native structures
        flutter_dir = tmp_path / "smali" / "io" / "flutter" / "embedding" / "android"
        flutter_dir.mkdir(parents=True)
        (flutter_dir / "FlutterActivity.smali").write_text(".class public Test;")

        rn_dir = tmp_path / "smali" / "com" / "facebook" / "react"
        rn_dir.mkdir(parents=True)
        (rn_dir / "ReactActivity.smali").write_text(".class public Test;")

        result = injector.analyze()

        # Flutter should be detected first
        assert result['app_type'] == 'Flutter'

    def _create_injector(self, work_dir):
        """Helper to create injector instance"""
        smali_dir = work_dir / "smali"
        smali_dir.mkdir(exist_ok=True)

        # Create AndroidManifest for package name
        manifest = work_dir / "AndroidManifest.xml"
        manifest.write_text('<?xml version="1.0" encoding="utf-8"?><manifest package="com.test.app"></manifest>')

        return AegisInjector(str(work_dir), verbose=False)


@pytest.fixture
def tmp_path():
    """Provide temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])