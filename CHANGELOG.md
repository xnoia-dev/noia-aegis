# Changelog

All notable changes to Noia Aegis will be documented in this file.

---

## [1.2.0] - 2025-01-17

### 🎉 Auto-Download Tools

No more manual setup! Tools download automatically on first use.

### ✨ Added

**Auto-Download System**
- Auto-download apktool and uber-apk-signer on first use
- Progress bars with tqdm
- SHA-256 checksum verification
- Tools cached in `~/.noia-aegis/tools/`

**New Commands**
- `aegis tools list` - List installed tools
- `aegis tools download` - Download all tools
- `aegis tools update` - Update to latest versions
- `aegis tools clean` - Remove all tools
- `aegis tools path` - Show tools directory

**New Dependencies**
- requests>=2.31.0
- tqdm>=4.66.0

### 🔧 Changed

**Files Modified**
- `noia_aegis/core/processor.py` - Uses ToolManager for auto-download
- `noia_aegis/cli.py` - Added tool management commands
- `requirements.txt` - Added requests and tqdm

**Files Added**
- `noia_aegis/core/tool_manager.py` - Auto-download implementation

### 🎯 Upgrade

```bash
pip install -r requirements.txt
aegis tools download 
```

### ⚠️ Breaking Changes

None - fully backward compatible with v1.1.0

---

**⚔️ Protected by the Aegis of Noia 💖**