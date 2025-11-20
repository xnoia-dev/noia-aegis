"""
String Obfuscator - XOR-based string obfuscation for APK protection
Noia Aegis v1.3.0
"""
import os
import secrets
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ObfuscatedString:
    """Container for obfuscated string data"""
    original: str
    encoded_bytes: bytes
    key: bytes
    smali_code: str
    
    def __repr__(self) -> str:
        return f"ObfuscatedString(original_length={len(self.original)}, key_length={len(self.key)})"


class StringObfuscator:
    """
    XOR-based string obfuscator for smali code injection.
    
    Features:
    - Cryptographically secure random key generation
    - XOR encoding with proper UTF-8 handling
    - Support for multi-byte characters (Chinese, Arabic, emojis)
    - Special character handling (\n, \t, \r)
    - Optimized smali code generation
    
    Example:
        >>> obfuscator = StringObfuscator()
        >>> result = obfuscator.obfuscate("Hello 世界! 😀")
        >>> print(result.smali_code)
    """
    
    DEFAULT_KEY_LENGTH = 16
    MAX_STRING_LENGTH = 10000  # Safety limit
    
    def __init__(self, default_key_length: int = DEFAULT_KEY_LENGTH):
        """
        Initialize StringObfuscator.
        
        Args:
            default_key_length: Default length for generated keys (bytes)
        
        Raises:
            ValueError: If key length is invalid
        """
        if default_key_length < 8 or default_key_length > 256:
            raise ValueError("Key length must be between 8 and 256 bytes")
        
        self.default_key_length = default_key_length
        self._stats = {
            'total_obfuscated': 0,
            'total_bytes_processed': 0
        }
    
    def generate_key(self, length: Optional[int] = None) -> bytes:
        """
        Generate cryptographically secure random key.
        
        Args:
            length: Key length in bytes (uses default if None)
        
        Returns:
            Random bytes suitable for XOR encryption
        
        Raises:
            ValueError: If length is invalid
        
        Example:
            >>> key = obfuscator.generate_key(16)
            >>> len(key)
            16
        """
        key_len = length if length is not None else self.default_key_length
        
        if key_len < 8 or key_len > 256:
            raise ValueError("Key length must be between 8 and 256 bytes")
        
        # Use secrets module for cryptographically secure random bytes
        return secrets.token_bytes(key_len)
    
    def xor_encode(self, text: str, key: bytes) -> bytes:
        """
        XOR encode text with key (repeating key if necessary).
        
        Args:
            text: String to encode (any UTF-8 text)
            key: Key bytes for XOR operation
        
        Returns:
            Encoded bytes
        
        Raises:
            ValueError: If text is too long or key is empty
            UnicodeEncodeError: If text cannot be encoded as UTF-8
        
        Example:
            >>> key = b'\\x01\\x02\\x03\\x04'
            >>> encoded = obfuscator.xor_encode("Hello", key)
            >>> decoded = obfuscator.xor_decode(encoded, key)
            >>> decoded == "Hello"
            True
        """
        if not text:
            return b''
        
        if not key:
            raise ValueError("Key cannot be empty")
        
        if len(text) > self.MAX_STRING_LENGTH:
            raise ValueError(f"String too long (max {self.MAX_STRING_LENGTH} chars)")
        
        # Convert text to UTF-8 bytes
        try:
            text_bytes = text.encode('utf-8')
        except UnicodeEncodeError as e:
            raise UnicodeEncodeError(
                e.encoding, e.object, e.start, e.end,
                f"Cannot encode text as UTF-8: {e.reason}"
            )
        
        # XOR each byte with repeating key
        key_len = len(key)
        encoded = bytes(
            text_bytes[i] ^ key[i % key_len]
            for i in range(len(text_bytes))
        )
        
        # Update stats
        self._stats['total_bytes_processed'] += len(text_bytes)
        
        return encoded
    
    def xor_decode(self, encoded: bytes, key: bytes) -> str:
        """
        XOR decode bytes with key (for verification).
        
        Args:
            encoded: Encoded bytes
            key: Key bytes used for encoding
        
        Returns:
            Decoded string
        
        Raises:
            ValueError: If key is empty
            UnicodeDecodeError: If decoded bytes are not valid UTF-8
        """
        if not encoded:
            return ''
        
        if not key:
            raise ValueError("Key cannot be empty")
        
        # XOR each byte with repeating key
        key_len = len(key)
        decoded_bytes = bytes(
            encoded[i] ^ key[i % key_len]
            for i in range(len(encoded))
        )
        
        # Convert back to string
        try:
            return decoded_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end,
                f"Cannot decode as UTF-8: {e.reason}"
            )
    
    def bytes_to_smali_array(self, data: bytes) -> str:
        """
        Convert bytes to smali byte array initialization code.
        
        Args:
            data: Bytes to convert
        
        Returns:
            Smali array initialization code
        
        Example:
            >>> obfuscator.bytes_to_smali_array(b'\\x01\\x02\\x03')
            'const/4 v0, 0x3\\n    new-array v0, v0, [B\\n    const/4 v1, 0x1\\n    ...'
        """
        if not data:
            return "const/4 v0, 0x0\n    new-array v0, v0, [B"
        
        lines = []
        
        # Create array
        lines.append(f"const/4 v0, 0x{len(data):x}")
        lines.append("new-array v0, v0, [B")
        
        # Fill array with bytes
        for i, byte in enumerate(data):
            # Use optimal const instruction based on value
            if byte == 0:
                const_instr = "const/4 v1, 0x0"
            elif byte <= 127:
                const_instr = f"const/4 v1, 0x{byte:x}"
            else:
                # For bytes > 127, use signed representation
                signed_value = byte if byte < 128 else byte - 256
                const_instr = f"const/16 v1, {signed_value}"
            
            lines.append(f"{const_instr}")
            lines.append(f"const/4 v2, 0x{i:x}")
            lines.append("aput-byte v1, v0, v2")
        
        return "\n    ".join(lines)
    
    def prepare_smali_format(self, encoded: bytes, key: bytes) -> str:
        """
        Generate complete smali code for decoding obfuscated string.
        
        Creates a smali method that:
        1. Initializes encoded byte array
        2. Initializes key byte array
        3. XOR decodes the data
        4. Returns decoded string
        
        Args:
            encoded: Encoded string bytes
            key: Key bytes
        
        Returns:
            Complete smali method code
        """
        if not encoded:
            # Return empty string constant
            return 'const-string v0, ""'
        
        # Generate smali code
        smali_code = f"""# Obfuscated string (XOR encoded)
    .locals 5
    
    # Encoded data
    {self.bytes_to_smali_array(encoded)}
    move-result-object v3
    
    # Key
    {self.bytes_to_smali_array(key)}
    move-result-object v4
    
    # XOR decode
    array-length v0, v3
    const/4 v1, 0x0
    
    :decode_loop
    if-ge v1, v0, :decode_end
    
    aget-byte v2, v3, v1
    array-length v5, v4
    rem-int v5, v1, v5
    aget-byte v5, v4, v5
    xor-int/2addr v2, v5
    int-to-byte v2, v2
    aput-byte v2, v3, v1
    
    add-int/lit8 v1, v1, 0x1
    goto :decode_loop
    
    :decode_end
    # Convert to string
    new-instance v0, Ljava/lang/String;
    const-string v1, "UTF-8"
    invoke-direct {{v0, v3, v1}}, Ljava/lang/String;-><init>([BLjava/lang/String;)V"""
        
        return smali_code
    
    def obfuscate(
        self,
        text: str,
        key: Optional[bytes] = None
    ) -> ObfuscatedString:
        """
        Obfuscate a string with XOR encoding.
        
        Args:
            text: String to obfuscate
            key: Optional custom key (generates new one if None)
        
        Returns:
            ObfuscatedString with all necessary data
        
        Raises:
            ValueError: If text is invalid
        
        Example:
            >>> result = obfuscator.obfuscate("My API Key: 12345")
            >>> print(result.smali_code)
            >>> # Verify decoding works
            >>> decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
            >>> decoded == "My API Key: 12345"
            True
        """
        if not isinstance(text, str):
            raise ValueError(f"Text must be string, got {type(text)}")
        
        # Generate key if not provided
        if key is None:
            key = self.generate_key()
        
        # Encode
        encoded = self.xor_encode(text, key)
        
        # Generate smali code
        smali_code = self.prepare_smali_format(encoded, key)
        
        # Update stats
        self._stats['total_obfuscated'] += 1
        
        return ObfuscatedString(
            original=text,
            encoded_bytes=encoded,
            key=key,
            smali_code=smali_code
        )
    
    def obfuscate_batch(
        self,
        strings: List[str],
        use_same_key: bool = False
    ) -> List[ObfuscatedString]:
        """
        Obfuscate multiple strings efficiently.
        
        Args:
            strings: List of strings to obfuscate
            use_same_key: If True, use same key for all strings (less secure)
        
        Returns:
            List of ObfuscatedString objects
        
        Example:
            >>> strings = ["API_KEY", "SECRET_TOKEN", "PASSWORD"]
            >>> results = obfuscator.obfuscate_batch(strings)
            >>> len(results)
            3
        """
        if not strings:
            return []
        
        results = []
        shared_key = self.generate_key() if use_same_key else None
        
        for text in strings:
            if not text:  # Skip empty strings
                continue
            
            result = self.obfuscate(text, key=shared_key)
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get obfuscation statistics.
        
        Returns:
            Dictionary with stats
        """
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self._stats = {
            'total_obfuscated': 0,
            'total_bytes_processed': 0
        }


class SmaliStringReplacer:
    """
    Helper class to replace string constants in smali files with obfuscated versions.
    """
    
    def __init__(self, obfuscator: Optional[StringObfuscator] = None):
        """
        Initialize SmaliStringReplacer.
        
        Args:
            obfuscator: StringObfuscator instance (creates new one if None)
        """
        self.obfuscator = obfuscator or StringObfuscator()
    
    def find_string_constants(self, smali_content: str) -> List[Tuple[str, str]]:
        """
        Find all const-string declarations in smali code.
        
        Args:
            smali_content: Smali file content
        
        Returns:
            List of (line, string_value) tuples
        
        Example:
            >>> replacer = SmaliStringReplacer()
            >>> smali = 'const-string v0, "Hello"\\nconst-string v1, "World"'
            >>> results = replacer.find_string_constants(smali)
            >>> len(results)
            2
        """
        import re
        
        # Pattern: const-string vX, "string value"
        pattern = r'const-string\s+v\d+,\s+"([^"]*)"'
        
        matches = []
        for match in re.finditer(pattern, smali_content):
            full_line = match.group(0)
            string_value = match.group(1)
            matches.append((full_line, string_value))
        
        return matches
    
    def should_obfuscate(self, string_value: str) -> bool:
        """
        Determine if a string should be obfuscated.
        
        Args:
            string_value: String to check
        
        Returns:
            True if string should be obfuscated
        
        Heuristics:
        - Skip very short strings (< 3 chars)
        - Skip common framework strings
        - Obfuscate URLs, API keys, tokens, etc.
        """
        if len(string_value) < 3:
            return False
        
        # Skip common framework strings
        framework_patterns = [
            'android.', 'androidx.', 'com.google.',
            'UTF-8', 'ISO-8859-1',
        ]
        
        if any(string_value.startswith(p) for p in framework_patterns):
            return False
        
        # Obfuscate patterns that look like sensitive data
        sensitive_patterns = [
            'http://', 'https://',
            'api', 'key', 'token', 'secret', 'password',
            '://', 'Bearer ', 'Authorization',
        ]
        
        lower_value = string_value.lower()
        if any(p in lower_value for p in sensitive_patterns):
            return True
        
        # Obfuscate if contains mix of alphanumeric (likely API key/token)
        if any(c.isdigit() for c in string_value) and any(c.isalpha() for c in string_value):
            if len(string_value) > 10:
                return True
        
        return False
    
    def replace_in_smali(
        self,
        smali_content: str,
        strings_to_obfuscate: Optional[List[str]] = None
    ) -> Tuple[str, int]:
        """
        Replace string constants in smali code with obfuscated versions.
        
        Args:
            smali_content: Original smali content
            strings_to_obfuscate: Specific strings to obfuscate (None = auto-detect)
        
        Returns:
            Tuple of (modified_content, replacement_count)
        """
        matches = self.find_string_constants(smali_content)
        
        if not matches:
            return smali_content, 0
        
        modified_content = smali_content
        replacement_count = 0
        
        for original_line, string_value in matches:
            # Check if should obfuscate
            if strings_to_obfuscate is not None:
                should_replace = string_value in strings_to_obfuscate
            else:
                should_replace = self.should_obfuscate(string_value)
            
            if not should_replace:
                continue
            
            # Obfuscate
            result = self.obfuscator.obfuscate(string_value)
            
            # Replace in content
            modified_content = modified_content.replace(
                original_line,
                result.smali_code,
                1  # Replace only first occurrence
            )
            replacement_count += 1
        
        return modified_content, replacement_count


def create_obfuscator(key_length: int = 16) -> StringObfuscator:
    """
    Factory function to create StringObfuscator instance.
    
    Args:
        key_length: Key length in bytes
    
    Returns:
        Configured StringObfuscator
    """
    return StringObfuscator(default_key_length=key_length)