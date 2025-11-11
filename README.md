# 🛡️ Noia Aegis

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/noia-aegis)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

**Noia Aegis** is an APK security injection tool that protects Android applications from common security threats including root detection, emulator detection, debugging attempts, and developer options.

Named after Noia, protected with love 💖

---

## ✨ Features

- 🔐 **Root Detection** - Blocks rooted devices
- 🖥️ **Emulator Detection** - Prevents running on emulators
- 🐛 **Debug Detection** - Blocks debugging attempts
- ⚙️ **Developer Options Detection** - Detects USB debugging
- ⚛️ **React Native Support** - Works seamlessly with React Native apps
- 🎛️ **Configurable Shields** - Enable/disable specific protections
- 🚀 **Easy to Use** - Simple CLI interface
- 📝 **YAML Configuration** - Flexible configuration system

---

## 📋 Requirements

- **Python 3.7+**
- **Java 8+** (for apktool and signing)
- **Tools** (included in `tools/` directory):
  - apktool.jar
  - uber-apk-signer.jar

---

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/arr-code/noia-aegis.git
cd noia-aegis
```

### 2. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install package
pip install -e .
```

### 3. Download Tools

Download and place in `tools/` directory:
- [apktool.jar](https://github.com/iBotPeaches/Apktool/releases)
- [uber-apk-signer.jar](https://github.com/patrickfav/uber-apk-signer/releases)

Or use the provided script:
```bash
# Coming soon: auto-download script
```

---

## 📖 Quick Start

### Generate Default Configuration
```bash
aegis init-config
```

This creates `.aegis.yml` in your current directory.

### Protect Your APK
```bash
aegis shield app.apk -o protected.apk
```

### Install Protected APK
```bash
adb install protected.apk
```

---

## 🎛️ Configuration

Edit `.aegis.yml` to customize protection:
```yaml
# Shield Configuration
shields:
  root_detection: true        # Detect rooted devices
  emulator_detection: true    # Detect emulators
  debug_detection: true       # Detect debuggers
  developer_options: true     # Detect developer mode

# Behavior
behavior:
  show_toast: true           # Show warning message
  exit_on_threat: true       # Exit app when threat detected
  log_threats: false         # Log to logcat

# Custom Messages
messages:
  root_detected: "🔓 Root detected!"
  emulator_detected: "🖥️ Emulator detected!"
  debug_detected: "🐛 Debug mode detected!"
  developer_detected: "⚙️ Developer options enabled!"
```

### Configuration Examples

**Example 1: Only Root Detection**
```yaml
shields:
  root_detection: true
  emulator_detection: false
  debug_detection: false
  developer_options: false
```

**Example 2: All Except Emulator (for testing)**
```yaml
shields:
  root_detection: true
  emulator_detection: false   # Disabled for emulator testing
  debug_detection: true
  developer_options: true
```

**Example 3: Custom Messages (Indonesian)**
```yaml
shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true

messages:
  root_detected: "⚠️ Perangkat tidak aman! Aplikasi akan ditutup."
  emulator_detected: "⚠️ Aplikasi tidak dapat berjalan di emulator."
  debug_detected: "⚠️ Mode debug terdeteksi."
  developer_detected: "⚠️ Developer options terdeteksi."
```

---

## 💻 CLI Commands

### `aegis shield`

Protect APK with Aegis shields.
```bash
aegis shield <apk_path> [OPTIONS]

Options:
  -o, --output PATH      Output APK filename
  -c, --config PATH      Custom config file path
  -v, --verbose          Verbose output
  --keep-temp            Keep temporary files
  --no-logo              Hide logo
```

**Examples:**
```bash
# Basic usage
aegis shield app.apk

# Custom output name
aegis shield app.apk -o protected-app.apk

# Use custom config
aegis shield app.apk -c custom-config.yml

# Verbose mode
aegis shield app.apk -v

# Keep temporary files for debugging
aegis shield app.apk --keep-temp
```

### `aegis scan`

Analyze APK structure without injection.
```bash
aegis scan <apk_path>
```

**Example:**
```bash
aegis scan app.apk
```

Output:
```
🔍 Scanning: app.apk

Results:
  • Type: React Native
  • Package: com.example.app
  • Activities: 3
  • Application Class: Yes

Activities:
  • smali/com/example/MainActivity.smali
  • smali/com/example/SettingsActivity.smali
  • ...
```

### `aegis init-config`

Generate default configuration file.
```bash
aegis init-config [output_path]
```

**Examples:**
```bash
# Generate .aegis.yml in current directory
aegis init-config

# Generate with custom name
aegis init-config my-config.yml
```

### `aegis about`

Display information about Noia Aegis.
```bash
aegis about
```

---

## 🔒 How It Works

### 1. Decompilation
APK is decompiled to Smali bytecode using apktool.

### 2. Analysis
Analyzes app structure:
- Detects app type (Native Android / React Native)
- Finds Application class
- Locates MainActivity
- Identifies injection points

### 3. Shield Injection
Injects security checks based on configuration:
- Copies shield classes to `com/noiaegis/` package
- Generates dynamic `AegisCore.smali` based on enabled shields
- Injects `AegisCore.protect()` call to Application/Activity onCreate

### 4. Recompilation & Signing
- Recompiles modified Smali to APK
- Signs APK with debug key
- Output: `protected-apk-aligned-debugSigned.apk`

---

## 🛡️ Security Shields

### Root Detection

Detects rooted Android devices by checking:
- `/system/bin/su`
- `/system/xbin/su`
- `/sbin/su`
- Magisk/SuperSU presence
- Build tags (test-keys)

**File:** `RootShield.smali`

### Emulator Detection

Detects Android emulators by checking:
- Build.FINGERPRINT (contains "generic")
- Build.MODEL (contains "sdk", "Emulator")
- Build.BRAND (contains "generic")
- Build.HARDWARE (contains "goldfish", "ranchu")

**File:** `EmulatorShield.smali`

### Debug Detection

Detects debugging attempts by checking:
- `Debug.isDebuggerConnected()`
- `Debug.waitingForDebugger()`
- ApplicationInfo debuggable flag

**File:** `DebugShield.smali`

### Developer Options Detection

Detects developer mode by checking:
- ADB enabled (`adb_enabled`)
- Development settings enabled
- Stay awake while charging

**File:** `DeveloperShield.smali`

---

## 📊 Project Structure
```
noia-aegis/
├── noia_aegis/
│   ├── __init__.py
│   ├── cli.py                    # CLI interface
│   ├── core/
│   │   ├── __init__.py
│   │   ├── processor.py          # APK decompile/recompile/sign
│   │   ├── injector.py           # Shield injection logic
│   │   ├── analyzer.py           # APK analysis
│   │   ├── verifier.py           # Protection verification
│   │   └── config.py             # Configuration management
│   ├── shields/
│   │   └── (future: Python shield implementations)
│   ├── templates/
│   │   └── smali/
│   │       ├── AegisCore.smali
│   │       ├── RootShield.smali
│   │       ├── EmulatorShield.smali
│   │       ├── DebugShield.smali
│   │       └── DeveloperShield.smali
│   └── utils/
│       ├── logger.py
│       └── helpers.py
├── tools/
│   ├── apktool.jar               # APK decompiler
│   └── uber-apk-signer.jar       # APK signer
├── tests/
│   ├── test_processor.py
│   └── test_injector.py
├── examples/
│   └── config.yml                # Example configuration
├── output/                       # Build outputs
├── .aegis.yml                    # Default config
├── .gitignore
├── setup.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## 🧪 Testing

### Test on Real Device
```bash
# Protect APK
aegis shield app.apk -o protected.apk

# Install on device
adb install protected.apk

# Test scenarios:
# 1. Normal device → App should work
# 2. Rooted device → App should show toast and exit
# 3. With debugger attached → App should block
# 4. Developer options enabled → App should block
```

### Test on Emulator
```bash
# Disable emulator detection for testing
# Edit .aegis.yml:
shields:
  emulator_detection: false

# Protect and install
aegis shield app.apk -o protected.apk
adb install protected.apk
```

---

## 🐛 Troubleshooting

### "APK not found" Error

Make sure the APK path is correct:
```bash
aegis shield /path/to/your/app.apk
```

### "Java not found" Error

Install Java 8 or higher:
```bash
# Check Java version
java -version

# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# macOS
brew install openjdk@11

# Windows
# Download from: https://www.oracle.com/java/technologies/downloads/
```

### "Decompile failed" Error

The APK might be obfuscated or use custom protection. Try:
```bash
aegis shield app.apk -v
```

Check verbose output for details.

### Shields Not Working

1. **Check config:**
```bash
   aegis shield app.apk -v
```
   
2. **Verify injection:**
```bash
   aegis scan protected.apk
```

3. **Check logcat:**
```bash
   adb logcat | grep -i aegis
```

---

## 🗺️ Roadmap

### Version 1.x (Current)
- ✅ Root Detection
- ✅ Emulator Detection
- ✅ Debug Detection
- ✅ Developer Options Detection
- ✅ Configurable shields
- ✅ React Native support

### Version 2.0 (Planned)
- 🔄 String Encryption
- 🔄 SSL Pinning Injection
- 🔄 Code Obfuscation
- 🔄 Integrity Verification
- 🔄 Anti-Tampering
- 🔄 Screen Protection (prevent screenshots)

### Version 3.0 (Future)
- 🔄 Native Library Protection
- 🔄 Advanced Obfuscation
- 🔄 RASP (Runtime Application Self-Protection)
- 🔄 Memory Protection
- 🔄 Anti-Hooking (Frida/Xposed detection)
- 🔄 Batch Processing

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/arr-code/noia-aegis.git
cd noia-aegis

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Apktool** - APK decompilation tool
- **Uber APK Signer** - APK signing tool
- **Click** - Python CLI framework
- **Colorama** - Terminal colors
- **PyYAML** - YAML parser

Special thanks to the Android reverse engineering community.

---

## 👨‍💻 Author

**Rizaldy Setiawan Hasanuddin**

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/noia-aegis/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/noia-aegis/discussions)
- **Email:** your.email@example.com

---

## ⚠️ Disclaimer

This tool is for educational and security research purposes. Always ensure you have permission to modify and distribute any APK files. The authors are not responsible for any misuse of this tool.

---

## 📸 Screenshots

### CLI Interface
```
    _   __      _           ___                _    
   / | / /___  (_)___ _    /   | ___  ____ _  (_)____
  /  |/ / __ \/ / __ `/   / /| |/ _ \/ __ `/ / / ___/
 / /|  / /_/ / / /_/ /   / ___ /  __/ /_/ / / (__  ) 
/_/ |_/\____/_/\__,_/   /_/  |_\___/\__, / /_/____/  
                                   /____/             

        ⚔️  Divine Shield of Protection ⚔️
      APK Security Injection Tool v1.0.0
```

### Protection Process
```
======================================================================
⚔️  AEGIS PROTECTION
======================================================================

📱 Input: app.apk

[1/5] 🔍 Decompiling APK...
✓ Decompiled

[2/5] 📊 Analyzing...
  • Type: React Native
  • Activities: 3
  • Application: Yes
✓ Analysis complete

[3/5] 🛡️  Injecting shields...
  • Classes added: 5
  • Injection points: 2
✓ Shields activated

[4/5] 🔨 Recompiling...
✓ Recompiled

[5/5] ✍️  Signing...
✓ Signed

======================================================================
✅ SUCCESS
======================================================================

📦 Protected APK: output/apks/app-protected-aligned-debugSigned.apk
⏱️  Time: 45.32s
📊 Size: 25.4 MB → 25.6 MB

Active Shields:
  ✓ Root Detection
  ✓ Emulator Detection
  ✓ Debug Detection
  ✓ Developer Options Detection

Install: adb install output/apks/app-protected-aligned-debugSigned.apk
```

---

<div align="center">

**⚔️ Protected by the Aegis of Noia 💖**

Made with ❤️ by Rigels Dev

</div>