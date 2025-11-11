# Changelog

All notable changes to Noia Aegis will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-01-12

### 🎉 Initial Release

First stable release of Noia Aegis - APK Security Injection Tool.

### ✨ Added

#### Core Features
- **CLI Interface** - Complete command-line interface with 4 main commands
  - `aegis shield` - Protect APK with security shields
  - `aegis scan` - Analyze APK structure
  - `aegis init-config` - Generate configuration file
  - `aegis about` - Display tool information

#### Security Shields
- **Root Detection** - Detects rooted Android devices
  - Checks for su binary in multiple locations
  - Detects Magisk and SuperSU
  - Verifies build tags
- **Emulator Detection** - Prevents running on Android emulators
  - Checks Build.FINGERPRINT, MODEL, BRAND, HARDWARE
  - Detects Genymotion and generic emulators
- **Debug Detection** - Blocks debugging attempts
  - Detects connected debuggers
  - Checks ApplicationInfo debuggable flag
  - Monitors debug waiting state
- **Developer Options Detection** - Detects developer mode
  - Checks ADB enabled status
  - Detects development settings enabled
  - Monitors stay awake settings

#### Configuration System
- **YAML Configuration** - Flexible configuration via `.aegis.yml`
  - Enable/disable individual shields
  - Customize behavior (toast messages, exit on threat)
  - Custom threat messages
  - Development mode options
- **Multiple Config Locations** - Auto-loads from:
  - `.aegis.yml`
  - `.aegis.yaml`
  - `aegis.yml`
  - `aegis.yaml`
- **Custom Config Support** - Use custom config via `-c` option

#### React Native Support
- **Auto-Detection** - Automatically detects React Native apps
- **Smart Injection** - Adapts injection strategy for RN apps
- **Application Class Handling** - Works with ReactApplication
- **MainActivity Support** - Creates onCreate if not present

#### APK Processing
- **Decompilation** - Uses apktool for APK decompilation
- **Smali Injection** - Injects security checks via Smali bytecode
- **Recompilation** - Rebuilds modified APK
- **Auto-Signing** - Signs APK with debug certificate
- **Cleanup** - Automatic cleanup of temporary files

#### CLI Features
- **Colored Output** - Beautiful colored terminal output
- **ASCII Logo** - Stylish Noia Aegis branding
- **Verbose Mode** - Detailed output with `-v` flag
- **Progress Indicators** - Clear step-by-step progress
- **Error Handling** - Comprehensive error messages
- **Keep Temp Option** - `--keep-temp` for debugging

#### Analysis Features
- **APK Scanning** - Analyze APK structure without injection
- **Type Detection** - Identifies Native Android vs React Native
- **Activity Discovery** - Lists all activities in APK
- **Package Information** - Extracts package name and metadata
- **Injection Point Detection** - Identifies optimal injection locations

### 🏗️ Architecture

#### Package Structure
```
noia_aegis/
├── cli.py              - CLI interface
├── core/
│   ├── processor.py    - APK processing (decompile/recompile/sign)
│   ├── injector.py     - Shield injection logic
│   ├── analyzer.py     - APK analysis
│   ├── verifier.py     - Protection verification
│   └── config.py       - Configuration management
└── templates/smali/    - Security shield implementations
    ├── AegisCore.smali
    ├── RootShield.smali
    ├── EmulatorShield.smali
    ├── DebugShield.smali
    └── DeveloperShield.smali
```

#### Dependencies
- **click** >= 8.1.0 - CLI framework
- **colorama** >= 0.4.6 - Terminal colors
- **PyYAML** >= 6.0 - YAML parsing

#### External Tools (Required)
- **apktool.jar** - APK decompilation
- **uber-apk-signer.jar** - APK signing
- **Java 8+** - Required for tools

### 📝 Technical Details

#### Injection Strategy
1. Decompile APK to Smali bytecode
2. Analyze app structure and detect type
3. Copy shield classes to `com/noiaegis/` package
4. Generate dynamic `AegisCore.smali` based on config
5. Inject `AegisCore.protect()` to Application/Activity onCreate
6. Recompile and sign modified APK

#### Shield Implementation
- **Smali Bytecode** - Native Android bytecode level
- **Zero Dependencies** - No runtime dependencies in target app
- **Minimal Overhead** - Checks run only at app startup
- **Configurable** - Each shield can be enabled/disabled independently

#### Supported Android Versions
- **Minimum SDK:** 21 (Android 5.0)
- **Target SDK:** 34 (Android 14)
- **Tested on:** Android 5.0 - 14

### 🔧 Configuration Options

#### Shield Configuration
```yaml
shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true
  integrity_check: false  # Coming in v2.0
```

#### Behavior Configuration
```yaml
behavior:
  show_toast: true        # Show warning toast
  exit_on_threat: true    # Exit app on threat
  log_threats: false      # Log to logcat
```

#### Message Customization
```yaml
messages:
  root_detected: "🔓 Root detected!"
  emulator_detected: "🖥️ Emulator detected!"
  debug_detected: "🐛 Debug mode detected!"
  developer_detected: "⚙️ Developer options enabled!"
```

### 📚 Documentation
- **README.md** - Complete usage guide
- **CHANGELOG.md** - Version history
- **LICENSE** - MIT License
- **examples/config.yml** - Configuration examples

### 🧪 Testing
- Tested on React Native apps
- Tested on Native Android apps
- Verified on rooted devices
- Verified on emulators
- Verified with debuggers attached

### 🎯 Known Limitations
- Requires Java 8+ installed
- Debug signature only (not production-ready signing)
- Some heavily obfuscated APKs may fail to decompile
- Cannot modify APKs with custom protection (e.g., DexGuard)

### 🔜 Future Plans (v2.0)
- String Encryption
- SSL Pinning Injection
- Code Obfuscation
- Integrity Verification
- Anti-Tampering
- Screen Protection

---

## [Unreleased]

### Planned for v1.1.0
- [ ] Auto-download tools script
- [ ] Progress bars (tqdm)
- [ ] Protection report (JSON output)
- [ ] Backup original APK option
- [ ] Better error messages
- [ ] Web dashboard (optional)

### Planned for v2.0.0
- [ ] String Encryption shield
- [ ] SSL Pinning injection
- [ ] Basic code obfuscation
- [ ] APK integrity verification
- [ ] Anti-tampering detection
- [ ] Screenshot prevention

### Planned for v3.0.0
- [ ] Native library protection
- [ ] Advanced obfuscation
- [ ] RASP (Runtime Application Self-Protection)
- [ ] Memory protection
- [ ] Anti-hooking (Frida/Xposed)
- [ ] Batch processing
- [ ] GUI interface

---

## Version History

### [1.0.0] - 2025-01-12
- Initial stable release
- Core security shields implemented
- Configuration system
- React Native support
- CLI interface

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

**⚔️ Protected by the Aegis of Noia 💖**