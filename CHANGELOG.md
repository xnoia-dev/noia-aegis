# Changelog

All notable changes to Noia Aegis will be documented in this file.

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