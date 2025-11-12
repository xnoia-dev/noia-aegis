# Changelog

All notable changes to Noia Aegis will be documented in this file.

---

## [1.1.0] - 2025-01-12

### 🎉 Major Release - Custom Keystore Support

This release adds **production keystore signing**, ensuring protected APKs maintain the same signature as the original APK.

### ✨ Added

#### Custom Keystore Signing
- **Production keystore support** - Sign with your own keystore instead of debug keystore
- **apksigner integration** - Uses modern apksigner for v2/v3 signature schemes
- **Auto-detection** - Automatically finds apksigner and zipalign from Android SDK
- **Multiple build-tools versions** - Smart version detection (supports 34.0.0, 35.0.0, 36.0.0, 36.1.0-rc1)
- **Semantic versioning** - Properly sorts and selects latest build-tools version

#### Config File Mode
- **YAML configuration** - Use `signing-config.yml` for complete protection workflow
- **Environment variables** - Support for `env:VARIABLE_NAME` in config files
- **Multiple config templates**:
  - `production-config.yml` - For production builds
  - `debug-config.yml` - For development/testing
  - `signing-config.yml` - Default configuration
- **Config generation** - New command: `aegis init-signing`

#### New CLI Commands
- **`aegis protect`** - Protect APK using configuration file (recommended)
- **`aegis init-signing`** - Generate signing configuration templates
  - `--production` flag for production config
  - `--debug` flag for debug config
- **Signature verification** - Automatic signature comparison

#### Enhanced CLI Features
- **Improved output** - Better formatted messages and progress indicators
- **Detailed statistics** - Shows APK size increase, processing time, active shields
- **Signature comparison** - Automatically verifies signature matches original
- **Production warnings** - Clear warnings when using debug keystore

### 🔧 Improved

#### Signing Process
- **v1 + v2 + v3 schemes** - Modern APK signature support
- **Keystore validation** - Validates keystore exists before signing
- **Better error messages** - Clear error messages for signing failures
- **Gradle compatibility** - Works with gradle.properties signing configs

#### Tool Detection
- **Smart path finding** - Searches multiple SDK locations:
  - `ANDROID_HOME` / `ANDROID_SDK_ROOT` environment variables
  - `%LOCALAPPDATA%\Android\Sdk` (Windows)
  - `~/Library/Android/sdk` (macOS)
  - `~/Android/Sdk` (Linux)
  - Custom paths: `C:/Env/Android/Sdk`
- **Build-tools auto-detection** - Finds latest version automatically
- **Verbose mode** - Shows tool paths and versions when using `-v` flag

#### APK Processing
- **Better temp file handling** - More reliable cleanup
- **Output directory structure** - Organized output in `output/apks/`
- **File naming** - Clear protected APK naming

### 🐛 Fixed

- **jarsigner compatibility** - Removed unsupported `-quiet` flag for older Java versions
- **Zipalign detection** - Better path detection across platforms
- **CMake build errors** - Improved handling of React Native build cache issues
- **Windows path handling** - Better support for Windows-style paths
- **Signature scheme compatibility** - Fixed "Target SDK requires v2 scheme" errors

### 📚 Documentation

- **Complete README.md** - Comprehensive usage guide with examples
- **Config file examples** - Multiple configuration templates
- **Troubleshooting guide** - Common issues and solutions
- **Signature verification guide** - How to verify APK signatures

### 🔐 Security

- **Production-ready signing** - Same signature as original APK
- **Play Store compatible** - Can update existing apps
- **API keys preserved** - Firebase, Google Maps, etc. continue working
- **Certificate matching** - SHA-256 digest verification

### ⚠️ Breaking Changes

None - backward compatible with v1.0.0

### 📦 Dependencies

No new dependencies required for core functionality

### 🎯 Upgrade Notes

**From v1.0.0 to v1.1.0:**

1. Update installation:
```bash
   pip install -e . --upgrade
```

2. Generate new config file (recommended):
```bash
   aegis init-signing production-config.yml --production
```

3. Use new `protect` command:
```bash
   aegis protect production-config.yml
```

**Old command still works:**
```bash
aegis shield app.apk --keystore key.jks --ks-pass xxx --ks-alias xxx --key-pass xxx
```

### 🙏 Acknowledgments

- **Android Build Tools** - apksigner, zipalign
- **Community feedback** - Testing and bug reports
- **Tested with** - React Native 0.75+, Android SDK 24-36

---

## [1.0.0] - 2025-01-12

### 🎉 Initial Release

First stable release of Noia Aegis - APK Security Injection Tool.

### ✨ Features

- Root Detection
- Emulator Detection
- Debug Detection
- Developer Options Detection
- React Native Support
- Configurable shields via `.aegis.yml`
- Debug keystore signing (uber-apk-signer)

---

**⚔️ Protected by the Aegis of Noia 💖**