# 🛡️ Shield Architecture - Technical Documentation

## Overview

Noia Aegis implements runtime security protection through **Smali bytecode injection**. This document provides detailed technical information about the shield architecture, implementation, and how to extend it.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Directory Structure](#directory-structure)
- [Shield Components](#shield-components)
- [How Shields Work](#how-shields-work)
- [Detection Techniques](#detection-techniques)
- [Adding Custom Shields](#adding-custom-shields)
- [Technical Details](#technical-details)

---

## Architecture Overview

### Why Smali Bytecode?

Noia Aegis uses **Smali bytecode** (Android's intermediate representation) instead of Java/Kotlin for shield implementation. This design choice offers several advantages:

| Aspect | Smali Approach | Source Code Approach |
|--------|---------------|---------------------|
| **Integration** | Direct bytecode injection | Requires source code modification |
| **Compatibility** | Works with any APK | Needs source access |
| **Runtime** | Native Android execution | Native Android execution |
| **Signature** | Preserves original signature | Changes signature |
| **Framework Support** | Flutter, React Native, Native | Limited to source-available apps |

### Architecture Layers

```
┌─────────────────────────────────────────┐
│         APK (Decompiled)                │
│  ┌───────────────────────────────────┐  │
│  │   Application/MainActivity        │  │
│  │   onCreate() {                    │  │
│  │     AegisCore.protect(this) ←───┐ │  │  ← Injection Point
│  │   }                             │ │  │
│  └─────────────────────────────────┘ │  │
│                                      │ │  │
│  ┌───────────────────────────────────┼─┐│
│  │ com/noiaegis/                    │ ││
│  │  ├── AegisCore.smali ←───────────┘ ││  ← Orchestrator
│  │  ├── RootShield.smali              ││  ← Individual Shields
│  │  ├── EmulatorShield.smali          ││
│  │  ├── DebugShield.smali             ││
│  │  └── DeveloperShield.smali         ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

---

## Directory Structure

### Project Structure

```
noia-aegis/
├── noia_aegis/
│   ├── shields/                    # Python package (PLACEHOLDERS)
│   │   ├── __init__.py
│   │   ├── base_shield.py         # 0 bytes - not used
│   │   ├── root_shield.py         # 0 bytes - not used
│   │   ├── emulator_shield.py     # 0 bytes - not used
│   │   └── debug_shield.py        # 0 bytes - not used
│   │
│   └── templates/smali/           # Actual shield implementations
│       ├── AegisCore.smali        # Main orchestrator (generated)
│       ├── RootShield.smali       # Root detection
│       ├── EmulatorShield.smali   # Emulator detection
│       ├── DebugShield.smali      # Debug detection
│       └── DeveloperShield.smali  # Developer mode detection
```

### Important Notes

⚠️ **The `shields/` Python directory contains EMPTY placeholder files.**

The actual shield logic is implemented in **Smali bytecode** files located in `templates/smali/`. This is intentional because:

1. **Shields run on Android devices** - They need to be Smali bytecode, not Python
2. **Runtime execution** - Shields execute when the APK runs, not during build
3. **Direct API access** - Smali can directly call Android APIs (File, Build, Debug, Settings)

---

## Shield Components

### 1. Individual Shield Files

Each shield is a self-contained Smali class with static detection methods.

#### RootShield.smali (1,567 bytes)

**Purpose:** Detect rooted Android devices

**Detection Methods:**
- Check for `su` binary in common locations:
  - `/system/bin/su`
  - `/system/xbin/su`
  - `/sbin/su`
  - `/system/app/Superuser.apk`
- Check for Magisk installation
- Uses `File.exists()` API

**Smali Structure:**
```smali
.class public Lcom/noiaegis/RootShield;
.super Ljava/lang/Object;

.method public static isRooted()Z
    # Returns true if device is rooted
    # Implementation uses file existence checks
.end method

.method private static fileExists(Ljava/lang/String;)Z
    # Helper method with try-catch for safety
.end method
```

#### EmulatorShield.smali (1,392 bytes)

**Purpose:** Detect Android emulators

**Detection Methods:**
- Check `Build.FINGERPRINT` for "generic"
- Check `Build.MODEL` for "sdk"
- Check `Build.BRAND` for "generic"
- Check `Build.HARDWARE` for "goldfish" or "ranchu"

**Smali Structure:**
```smali
.class public Lcom/noiaegis/EmulatorShield;
.super Ljava/lang/Object;

.method public static isEmulator()Z
    # Returns true if running on emulator
    # Checks Build.* properties
.end method
```

#### DebugShield.smali (2,598 bytes)

**Purpose:** Detect debuggers and debuggable apps

**Detection Methods:**
- `Debug.isDebuggerConnected()`
- `Debug.waitingForDebugger()`
- `ApplicationInfo.flags & FLAG_DEBUGGABLE`

**Smali Structure:**
```smali
.class public Lcom/noiaegis/DebugShield;
.super Ljava/lang/Object;

.method public static isDebuggable(Landroid/content/Context;)Z
    # Returns true if app is debuggable or debugger attached
.end method
```

#### DeveloperShield.smali (1,577 bytes)

**Purpose:** Detect developer options enabled

**Detection Methods:**
- Check `Settings.Global.ADB_ENABLED`
- Check `Settings.Global.DEVELOPMENT_SETTINGS_ENABLED`

**Smali Structure:**
```smali
.class public Lcom/noiaegis/DeveloperShield;
.super Ljava/lang/Object;

.method public static isDeveloperMode(Landroid/content/Context;)Z
    # Returns true if developer options enabled
.end method
```

### 2. AegisCore.smali (Orchestrator)

**Purpose:** Coordinate all shields and implement threat response

**Features:**
- **Dynamic generation** - Built at runtime based on configuration
- **Singleton pattern** - Uses `hasRun` flag to prevent duplicate execution
- **Configurable behavior** - Toast messages, app exit, logging
- **Conditional execution** - Only calls enabled shields

**Generation Process:**

`AegisCore.smali` is **NOT** a static file. It's generated dynamically by:

```python
# noia_aegis/core/injector.py, line 267
def _build_aegis_core_smali(self):
    """Build AegisCore.smali dynamically based on config"""
```

**Generated Code Structure:**

```smali
.class public Lcom/noiaegis/AegisCore;
.super Ljava/lang/Object;

# Static flag - ensures single execution per app session
.field private static hasRun:Z

.method public static protect(Landroid/content/Context;)V
    .locals 5

    # Check if already executed
    sget-boolean v0, Lcom/noiaegis/AegisCore;->hasRun:Z
    if-eqz v0, :not_executed_yet
    return-void
    :not_executed_yet

    # Mark as executed
    const/4 v0, 0x1
    sput-boolean v0, Lcom/noiaegis/AegisCore;->hasRun:Z

    # Root Detection (if enabled)
    invoke-static {}, Lcom/noiaegis/RootShield;->isRooted()Z
    move-result v0
    if-eqz v0, :check_1
        # Show toast: "🔓 Device is rooted"
        # Throw RuntimeException (app exits)
    :check_1

    # Emulator Detection (if enabled)
    invoke-static {}, Lcom/noiaegis/EmulatorShield;->isEmulator()Z
    move-result v0
    if-eqz v0, :check_2
        # Show toast: "🖥️ Running on emulator"
        # Throw RuntimeException
    :check_2

    # ... (other shields)

    return-void
.end method
```

---

## How Shields Work

### Execution Flow

```
1. APK Launches
   ↓
2. Application.onCreate() OR MainActivity.onCreate()
   ↓
3. AegisCore.protect(Context) called
   ↓
4. Check hasRun flag
   ├─ true  → Skip (already executed)
   └─ false → Continue
       ↓
5. Set hasRun = true
   ↓
6. Call enabled shields sequentially
   ├─ RootShield.isRooted()
   ├─ EmulatorShield.isEmulator()
   ├─ DebugShield.isDebuggable()
   └─ DeveloperShield.isDeveloperMode()
       ↓
7. If threat detected:
   ├─ Show Toast message (if configured)
   ├─ Log to logcat (if configured)
   └─ Throw RuntimeException (app crashes/exits)
```

### Injection Points

Noia Aegis injects the protection call at the earliest possible point:

**Priority 1: Application.onCreate()**
```smali
.method public onCreate()V
    .locals 0

    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    # AEGIS INJECTED - Runs before any Activity
    invoke-static {p0}, Lcom/noiaegis/AegisCore;->protect(Landroid/content/Context;)V

    return-void
.end method
```

**Priority 2: MainActivity.onCreate()** (fallback if no Application class)
```smali
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 0

    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    # AEGIS INJECTED
    invoke-static {p0}, Lcom/noiaegis/AegisCore;->protect(Landroid/content/Context;)V

    return-void
.end method
```

### Injection Process

```python
# Simplified injection logic
def forge_aegis(self):
    # 1. Copy enabled shields to com/noiaegis/
    self._copy_shields()

    # 2. Generate AegisCore.smali based on config
    self._generate_aegis_core()

    # 3. Find injection points
    app_class = self._find_application_class()
    main_activity = self._find_main_activity()

    # 4. Inject protection call
    if app_class:
        self._inject_to_application(app_class)
    if main_activity:
        self._inject_or_create_oncreate(main_activity)
```

---

## Detection Techniques

### Root Detection (RootShield)

**Binary Locations Checked:**
```
/system/bin/su
/system/xbin/su
/sbin/su
/system/app/Superuser.apk
/system/app/Magisk
```

**Implementation:**
```smali
.method private static fileExists(Ljava/lang/String;)Z
    .locals 3

    :try_start
        new-instance v0, Ljava/io/File;
        invoke-direct {v0, p0}, Ljava/io/File;-><init>(Ljava/lang/String;)V
        invoke-virtual {v0}, Ljava/io/File;->exists()Z
        move-result v1
        return v1
    :try_end

    :catch_all
        const/4 v1, 0x0
        return v1
.end method
```

### Emulator Detection (EmulatorShield)

**Build Properties Checked:**
```java
Build.FINGERPRINT.contains("generic")
Build.MODEL.contains("sdk")
Build.BRAND.contains("generic")
Build.HARDWARE.contains("goldfish")
Build.HARDWARE.contains("ranchu")
```

**Why This Works:**
- Most emulators use generic Android builds
- Hardware name "goldfish" is the Android emulator's internal name
- "ranchu" is the newer emulator backend

### Debug Detection (DebugShield)

**Three-Layer Detection:**

1. **Debugger Connection:**
   ```smali
   invoke-static {}, Landroid/os/Debug;->isDebuggerConnected()Z
   ```

2. **Waiting for Debugger:**
   ```smali
   invoke-static {}, Landroid/os/Debug;->waitingForDebugger()Z
   ```

3. **Debuggable Flag:**
   ```smali
   invoke-virtual {p0}, Landroid/content/Context;->getApplicationInfo()Landroid/content/pm/ApplicationInfo;
   move-result-object v0
   iget v1, v0, Landroid/content/pm/ApplicationInfo;->flags:I
   and-int/lit8 v1, v1, 0x2  # FLAG_DEBUGGABLE
   ```

### Developer Options Detection (DeveloperShield)

**Settings Checked:**
```java
Settings.Global.getInt(resolver, Settings.Global.ADB_ENABLED, 0)
Settings.Global.getInt(resolver, Settings.Global.DEVELOPMENT_SETTINGS_ENABLED, 0)
```

---

## Adding Custom Shields

### Step 1: Create Smali Shield File

Create `templates/smali/CustomShield.smali`:

```smali
.class public Lcom/noiaegis/CustomShield;
.super Ljava/lang/Object;

.method public static isCustomThreat()Z
    .locals 2

    # Your detection logic here
    # Return true if threat detected

    const/4 v0, 0x0  # Return false (no threat)
    return v0
.end method
```

### Step 2: Update Configuration

Add to `noia_aegis/core/config.py`:

```python
DEFAULT_CONFIG = {
    'shields': {
        'custom_shield': True,  # Add your shield
    }
}
```

### Step 3: Update Injector

Add to `noia_aegis/core/injector.py`:

```python
def _copy_shields(self):
    shields_map = {
        'custom_shield': 'CustomShield.smali',  # Add mapping
    }
```

```python
def _build_aegis_core_smali(self):
    # Add check generation
    if self.config.is_shield_enabled('custom_shield'):
        message = self.config.get_message('custom_detected')
        checks.append(self._generate_check_code(
            'CustomShield', 'isCustomThreat', message, next_label
        ))
```

### Step 4: Add Message

Add to default config:

```python
'messages': {
    'custom_detected': '⚠️ Custom threat detected!'
}
```

---

## Technical Details

### Smali Language Primer

**Basic Syntax:**
```smali
.class public Lcom/example/MyClass;  # Class declaration
.super Ljava/lang/Object;            # Inheritance

.field private static myField:I      # Static field (int)

.method public myMethod()V           # Public void method
    .locals 2                        # Local variables count

    const/4 v0, 0x0                  # v0 = 0
    const/4 v1, 0x1                  # v1 = 1

    if-eqz v0, :label               # if (v0 == 0) goto label
        return-void
    :label

    return-void
.end method
```

**Common Instructions:**
- `invoke-static` - Call static method
- `invoke-virtual` - Call instance method
- `move-result` - Get method return value
- `const/4` - Load small constant
- `const-string` - Load string constant
- `if-eqz` - Branch if equal to zero
- `return-void` - Return from void method

### Performance Considerations

**Shield Overhead:**
- **Execution time:** ~5-15ms on modern devices
- **APK size increase:** ~8KB for all shields
- **Memory impact:** Minimal (~4KB static allocation)

**Optimization:**
- Single execution per app session (`hasRun` flag)
- No runtime obfuscation overhead
- Static method calls (no object instantiation)
- Early returns on first threat detected

### Security Considerations

**Limitations:**
1. **Not foolproof** - Advanced attackers can bypass
2. **Static detection** - Checks are predictable
3. **Smali is readable** - Can be reverse-engineered
4. **No code obfuscation** - Shield logic is visible

**Best Practices:**
1. Use shields as **part** of security strategy, not sole defense
2. Combine with server-side validation
3. Implement certificate pinning for network security
4. Use ProGuard/R8 for code obfuscation
5. Regular updates to detection techniques

---

## FAQ

**Q: Why are Python shield files empty?**
A: Shields run on Android devices at runtime, so they must be Smali bytecode. The Python files are placeholders for potential future use.

**Q: Can I write shields in Java/Kotlin?**
A: Yes! Write in Java/Kotlin, compile to APK, decompile with apktool, extract the Smali, and use it as a template.

**Q: Do shields work with obfuscated APKs?**
A: Yes, but injection becomes harder. AegisCore and shields are NOT obfuscated to ensure reliability.

**Q: Can shields be removed by attackers?**
A: Yes, if they decompile, find the injection point, and remove it. Consider this a deterrent, not absolute protection.

**Q: How to test shields?**
A: Test on rooted devices, emulators, debug builds, and with developer options enabled to verify detection.

---

## Resources

- [Smali Language Guide](https://github.com/JesusFreke/smali/wiki)
- [Android API Reference](https://developer.android.com/reference)
- [Apktool Documentation](https://ibotpeaches.github.io/Apktool/)
- [Android Security Best Practices](https://developer.android.com/training/articles/security-tips)

---

## License

This documentation is part of Noia Aegis and is licensed under the MIT License.

---

**Made with ❤️ by Rizaldy**

For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md)
