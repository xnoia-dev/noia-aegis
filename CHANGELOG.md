# Changelog

All notable changes to Noia Aegis will be documented in this file.

---

## [1.4.0] - 2025-01-21

### 🦋 Flutter Support, Encoding Fixes & Centralized Version Management

Full Flutter framework compatibility with robust encoding fallback!

### Added

- **Flutter Framework Detection**
  - Auto-detect Flutter apps via `FlutterActivity`, `libflutter.so`, `flutter_assets`
  - New method: `_is_flutter()` in `injector.py`
  - APK analysis now shows "Flutter" app type

- **Multi-Encoding File Reading**
  - New helper: `_read_smali_file_safe()` with encoding fallback
  - Tries: UTF-8 → Latin-1 → ISO-8859-1 → CP1252 → UTF-8 (ignore errors)
  - Solves: `'utf-8' codec can't decode byte 0x97` error

- **Binary File Detection**
  - New method: `_is_likely_binary()` detects binary files
  - Automatically skips binary files during obfuscation
  - Prevents processing corrupted/non-text smali files

- **Flutter Framework Skipping**
  - Extended `_should_skip_obfuscation()` with Flutter patterns:
    - `io/flutter/embedding/`
    - `io/flutter/app/`
    - `io/flutter/plugin/`
    - `io/flutter/view/`
    - `com/facebook/hermes/` (React Native)
    - `kotlinx/` (Kotlin libraries)

- **Comprehensive Unit Tests** ⭐ NEW
  - `tests/test_flutter_support.py` - 24 tests for Flutter support
  - `tests/test_config.py` - 16 tests for configuration management
  - `tests/test_injector_core.py` - 10 tests for core injection
  - `tests/test_version.py` - 13 tests for version management
  - **Total: 63 comprehensive tests**

### Changed

- **Centralized Version Management** ⭐ NEW
  - Created `noia_aegis/__version__.py` as single source of truth
  - Updated `setup.py`, `cli.py`, `__init__.py` to import from `__version__.py`
  - Version now only needs to be changed in ONE file

- `noia_aegis/core/injector.py`:
  - All file read operations now use safe encoding fallback
  - Updated: `_obfuscate_all_strings()`, `_inject_to_application()`,
    `_inject_or_create_oncreate()`, `_find_application_class()`, `_find_activities()`
  - Added verbose logging for non-UTF-8 encodings
  - Flutter detection integrated into `analyze()` method

- `noia_aegis/core/config.py`:
  - Added `compatibility` section to DEFAULT_CONFIG

- `noia_aegis/cli.py`:
  - All init templates now include `compatibility` section
  - Updated production, debug, and default templates

- `.aegis.yml`:
  - Added `compatibility` section with `react_native`, `flutter`, `native_android` flags

- `.gitignore`:
  - Improved to keep `.aegis.yml` template while ignoring user configs
  - Removed `signing-config.yml`, `aegis.toml`, `.env` from tracking

- `README.md`:
  - Added "Flutter Support" section with usage examples
  - Added troubleshooting for UTF-8 encoding errors
  - Updated features list to include Flutter and Native Android

### Fixed

- **Critical:** UTF-8 decoding errors when processing Flutter APKs
- File reading failures with non-UTF-8 encoded smali files
- Binary file processing that caused crashes
- Missing framework detection for Flutter apps

### Technical Details

- **Supported Encodings**: UTF-8, Latin-1, ISO-8859-1, Windows-1252
- **Fallback Strategy**: Graceful degradation with error ignore mode
- **Binary Detection**: Null byte check + printable character ratio (< 70%)
- **Framework Compatibility**: React Native, Flutter, Native Android

### Migration

No breaking changes! Update to v1.4.0 and Flutter APKs will work automatically:

```bash
git pull
pip install -e .
aegis protect flutter-app.yml  # Just works! ✅

# Version now centralized - update only __version__.py!
```

### Known Limitations

- Flutter engine (C++ code) is not obfuscated
- Platform channels are preserved for functionality
- Native plugins (.so files) are not modified

---

## [1.3.0] - 2025-01-XX

### 🔐 String Obfuscation

Protect hardcoded secrets with XOR-based string obfuscation.

### Added

- **String Obfuscation Module**
  - XOR-based encoding with random keys
  - Auto-detection of sensitive strings (API keys, tokens, URLs)
  - UTF-8 support (Chinese, Arabic, emojis)
  - Configurable via YAML (`obfuscation.enabled: true`)
  - Unique keys per APK

- **New Files**
  - `noia_aegis/core/obfuscator.py` - Obfuscation engine
  - `tests/test_obfuscator.py` - 38 comprehensive tests

### Changed

- `noia_aegis/core/injector.py` - Add string obfuscation support
- `noia_aegis/core/config.py` - Add obfuscation config option
- `noia_aegis/cli.py` - Show obfuscation stats in output

### Usage

```yaml
obfuscation:
  enabled: true  # Enable string obfuscation
```

```bash
aegis protect signing-config.yml
# Output: ✓ 47 strings obfuscated in 12 files
```

### Technical Details

- **Algorithm**: XOR encoding
- **Key Length**: 16 bytes (cryptographically secure)
- **Encoding**: UTF-8 safe
- **Runtime Overhead**: Minimal (decode once)
- **APK Size**: +5-10 KB

### Breaking Changes

None - fully backward compatible with v1.2.0

---

## [1.2.0] - 2025-01-17

### 🎉 Auto-Download Tools

### Added

- Auto-download apktool and uber-apk-signer on first use
- Progress bars with SHA-256 verification
- Tools cached in `~/.noia-aegis/tools/`
- New commands: `aegis tools list|download|update|clean|path`

### Changed

- `noia_aegis/core/processor.py` - Use ToolManager
- `noia_aegis/cli.py` - Add tool commands
- Add dependencies: requests, tqdm

### Upgrade

```bash
pip install -r requirements.txt
aegis tools download
```

---

## [1.1.0] - 2025-01-10

### Initial Release

- Root Detection
- Emulator Detection
- Debug Detection
- Developer Options Detection
- Production Signing (maintains original signature)
- React Native Support
- YAML Configuration
- Custom Messages

---

**⚔️ Protected by the Aegis of Noia 💖**