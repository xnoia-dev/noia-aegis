# 🛡️ Noia Aegis

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/arr-code/noia-aegis)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)# 🛡️ Noia Aegis

[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](https://github.com/arr-code/noia-aegis)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

**Noia Aegis** - APK security injection tool that adds runtime protection while maintaining your original production signature.

Named after Noia, protected with love 💖

---

## ✨ Features

- 🔐 **Root Detection** - Block rooted devices
- 🖥️ **Emulator Detection** - Prevent running on emulators
- 🐛 **Debug Detection** - Block debuggers
- ⚙️ **Developer Options Detection** - Detect USB debugging
- 🔒 **String Obfuscation** - 🆕 Protect API keys, tokens, URLs (v1.3.0)
- 🔑 **Production Signing** - Keep your original APK signature
- ⚛️ **React Native Support** - Works seamlessly with RN apps
- 🛠️ **Auto-Download Tools** - No manual setup needed

---

## 🆕 What's New in v1.3.0

### String Obfuscation
Protect hardcoded secrets with XOR-based obfuscation:

```yaml
obfuscation:
  enabled: true
```

**Results:**
- ✅ API keys, tokens, URLs obfuscated
- ✅ Unique encryption keys per APK
- ✅ Protects against static analysis

---

## 📦 Installation

```bash
git clone https://github.com/arr-code/noia-aegis.git
cd noia-aegis
pip install -r requirements.txt
pip install -e .
```

---

## 🚀 Quick Start

### 1. Generate Config
```bash
aegis init-signing production-config.yml --production
```

### 2. Edit Config
```yaml
apk:
  input: "android/app/build/outputs/apk/release/app-release.apk"
  output: "app-protected.apk"

signing:
  use_custom: true
  keystore: "android/release.keystore"
  keystore_password: "your_password"
  key_alias: "your_alias"
  key_password: "your_password"

shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true

obfuscation:
  enabled: true  # 🆕 v1.3.0
```

### 3. Protect
```bash
aegis protect production-config.yml
```

### 4. Done
```bash
adb install output/apks/app-protected-aligned-signed.apk
```

---

## 📖 Usage

```bash
# Protect APK
aegis protect production-config.yml

# Scan APK
aegis scan app.apk

# Tool management
aegis tools list
aegis tools update

# Generate config
aegis init-config
aegis init-signing config.yml --production
```

---

## 🔧 Configuration

### Shields
```yaml
shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true
```

### Obfuscation (v1.3.0)
```yaml
obfuscation:
  enabled: true  # XOR-based string encoding
```

### Behavior
```yaml
behavior:
  show_toast: true
  exit_on_threat: true
  log_threats: false
```

---

## 🔍 Signature Verification

```bash
# Original APK
apksigner verify --print-certs app-release.apk

# Protected APK
apksigner verify --print-certs app-protected.apk

# SHA-256 should be IDENTICAL ✅
```

---

## 🛡️ How It Works

```
Original APK → Decompile → Inject Shields → Obfuscate Strings → 
Recompile → Sign → Protected APK (Same Signature!)
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/arr-code/noia-aegis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/arr-code/noia-aegis/discussions)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**⚔️ Protected by the Aegis of Noia 💖**

Made with ❤️ by Rizaldy
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

**Noia Aegis** is an APK security injection tool that adds runtime protection to your Android apps while maintaining your original production signature.

Named after Noia, protected with love 💖

---

## ✨ Features

- 🔐 **Root Detection** - Block rooted devices
- 🖥️ **Emulator Detection** - Prevent running on emulators
- 🐛 **Debug Detection** - Block debuggers
- ⚙️ **Developer Options** Detection - Detect USB debugging
- 🔒 **String Obfuscation** - 🆕 Protect API keys, tokens, URLs (v1.3.0)
- 🔑 **Production Signing** - Keep your original APK signature
- ⚛️ **React Native Support** - Works seamlessly with RN apps
- 📝 **Easy Configuration** - Simple YAML config files
- 🛠️ **Auto-Download Tools** - No manual setup needed (v1.2.0)


---

## 📦 Installation

### Requirements
- Python 3.7+
- Java 8+
- Android SDK (for apksigner/zipalign)

### Install
```bash
git clone https://github.com/arr-code/noia-aegis.git
cd noia-aegis
pip install -e .
```

### Tools Auto-Download
Noia Aegis automatically downloads required tools on first use! No manual setup needed.

```bash
# Optional: Download tools manually
aegis tools download
```

---

## 🚀 Quick Start

### Step 1: Generate Config
```bash
aegis init-signing production-config.yml --production
```

### Step 2: Edit Config

Edit `production-config.yml`:
```yaml
apk:
  input: "./apks/app-release.apk"
  output: "app-protected.apk"

signing:
  use_custom: true
  keystore: "./apks/test-release.keystore"
  keystore_password: "your_password"
  key_alias: "your_alias"
  key_password: "your_password"

shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true
```

### Step 3: Protect
```bash
aegis protect production-config.yml
```

### Step 4: Install & Test
```bash
adb install output/apks/app-protected-aligned-signed.apk
```

**Done!** ✅

---

## 📖 Usage

### Config File Mode (Recommended)
```bash
# Production build
aegis protect production-config.yml

# Debug build
aegis protect debug-config.yml
```

### Command Line Mode
```bash
aegis shield app.apk \
  --keystore release.keystore \
  --ks-pass "password" \
  --ks-alias "release" \
  --key-pass "password" \
  -o protected.apk
```

### Other Commands
```bash
# Generate configs
aegis init-signing production-config.yml --production
aegis init-config  # Generate .aegis.yml

# Scan APK
aegis scan app.apk

# Show info
aegis about
aegis --help
```

---

## 🔧 Configuration

### Shield Configuration
```yaml
shields:
  root_detection: true       # Detect rooted devices
  emulator_detection: true   # Detect emulators
  debug_detection: true      # Detect debuggers
  developer_options: true    # Detect developer mode
```

### Behavior
```yaml
behavior:
  show_toast: true          # Show warning message
  exit_on_threat: true      # Exit app on threat
  log_threats: false        # Log to logcat
```

### Custom Messages
```yaml
messages:
  root_detected: "🔓 Device tidak aman!"
  emulator_detected: "🖥️ Tidak dapat berjalan di emulator!"
  debug_detected: "🐛 Debug mode terdeteksi!"
  developer_detected: "⚙️ Developer options harus dimatikan!"
```

---

## 🔍 Signature Verification

Verify your protected APK has the same signature as original:
```bash
# Original APK
apksigner verify --print-certs app-release.apk

# Protected APK
apksigner verify --print-certs app-protected.apk

# SHA-256 should be IDENTICAL ✅
```

---

## 🎯 Use Cases

### Production Release
- ✅ Keep original signature
- ✅ Can update existing apps
- ✅ Ready for Play Store
- ✅ API keys work (Firebase, Google Maps, etc.)

### Development/Testing
- ✅ Test shields on emulator
- ✅ Debug mode allowed
- ✅ Quick iteration

---

## 🛡️ How It Works
```
Original APK
    ↓
Decompile (apktool)
    ↓
Inject Security Shields (Smali)
    ↓
Recompile (apktool)
    ↓
Sign with Your Keystore (apksigner)
    ↓
Protected APK (Same Signature!)
```

---

## 📋 Configuration Templates

### Production Config
```yaml
# production-config.yml
apk:
  input: "android/app/build/outputs/apk/release/app-release.apk"
  output: "app-protected.apk"

signing:
  use_custom: true
  keystore: "release.keystore"
  keystore_password: "env:KEYSTORE_PASSWORD"  # From environment
  key_alias: "release"
  key_password: "env:KEY_PASSWORD"

shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true

options:
  verbose: false
```

### Debug Config
```yaml
# debug-config.yml
apk:
  input: "android/app/build/outputs/apk/debug/app-debug.apk"
  output: "app-debug-protected.apk"

signing:
  use_custom: false  # Use debug keystore

shields:
  root_detection: false      # Allow everything for testing
  emulator_detection: false
  debug_detection: false
  developer_options: false

options:
  verbose: true
  keep_temp: true
```

---

## 🐛 Troubleshooting

### APK Not Signed

**Problem:** `keytool -printcert` says "Not a signed jar file"

**Solution:** Make sure keystore path is correct in config
```yaml
signing:
  keystore: "./apks/release.keystore"  # ← Check this path
```

### Signature Mismatch

**Problem:** Different SHA-256 after protection

**Solution:** Make sure you're using the **same keystore** that signed the original APK

### Build Tools Not Found

**Problem:** `apksigner not found`

**Solution:** Set `ANDROID_HOME` environment variable:
```bash
export ANDROID_HOME=/path/to/Android/Sdk  # Linux/Mac
set ANDROID_HOME=C:\Android\Sdk           # Windows
```

---

## 🔜 Roadmap

### v1.4 (Planned)
- Custom obfuscation patterns
- Obfuscation reporting
- Selective string obfuscation

### v2.0 (Future)
- Native Library Obfuscation (.so)
- SSL Pinning
- Integrity Verification
- Screen Protection
- Anti-Hooking (Frida/Xposed)

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Apktool** - APK decompilation
- **Uber APK Signer** - APK signing
- **Android Build Tools** - apksigner, zipalign
- **Community** - Testing and feedback

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/arr-code/noia-aegis/issues)
- **Discussions:** [GitHub Discussions](https://github.com/arr-code/noia-aegis/discussions)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## ⚠️ Disclaimer

This tool is for educational and security research purposes. Always ensure you have permission to modify and distribute any APK files.

---

<div align="center">

**⚔️ Protected by the Aegis of Noia 💖**

Made with ❤️ by Rizaldy

[GitHub](https://github.com/arr-code/noia-aegis) • 
[Issues](https://github.com/arr-code/noia-aegis/issues) • 
[Changelog](CHANGELOG.md)

</div>