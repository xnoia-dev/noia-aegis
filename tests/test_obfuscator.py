"""
Unit tests for String Obfuscator
Tests all edge cases including UTF-8, emojis, special chars, performance
"""
import pytest
import time
from noia_aegis.core.obfuscator import (
    StringObfuscator,
    ObfuscatedString,
    SmaliStringReplacer,
    create_obfuscator
)


class TestKeyGeneration:
    """Test key generation functionality"""
    
    def test_default_key_length(self):
        """Test default key length is 16 bytes"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        assert len(key) == 16
    
    def test_custom_key_length(self):
        """Test custom key lengths"""
        obfuscator = StringObfuscator(default_key_length=32)
        key = obfuscator.generate_key()
        assert len(key) == 32
        
        # Test with parameter
        key8 = obfuscator.generate_key(8)
        assert len(key8) == 8
        
        key64 = obfuscator.generate_key(64)
        assert len(key64) == 64
    
    def test_key_randomness(self):
        """Test that generated keys are random"""
        obfuscator = StringObfuscator()
        key1 = obfuscator.generate_key()
        key2 = obfuscator.generate_key()
        key3 = obfuscator.generate_key()
        
        # Keys should be different
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3
    
    def test_invalid_key_length(self):
        """Test invalid key lengths raise ValueError"""
        with pytest.raises(ValueError, match="Key length must be between"):
            StringObfuscator(default_key_length=7)
        
        with pytest.raises(ValueError, match="Key length must be between"):
            StringObfuscator(default_key_length=257)
        
        obfuscator = StringObfuscator()
        with pytest.raises(ValueError):
            obfuscator.generate_key(5)
        
        with pytest.raises(ValueError):
            obfuscator.generate_key(300)


class TestXOREncoding:
    """Test XOR encoding/decoding functionality"""
    
    def test_basic_encoding(self):
        """Test basic ASCII string encoding"""
        obfuscator = StringObfuscator()
        key = b'\x01\x02\x03\x04'
        
        text = "Hello"
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
        assert encoded != text.encode('utf-8')  # Should be different
    
    def test_empty_string(self):
        """Test empty string encoding"""
        obfuscator = StringObfuscator()
        key = b'\x01\x02\x03\x04'
        
        encoded = obfuscator.xor_encode("", key)
        assert encoded == b''
        
        decoded = obfuscator.xor_decode(b'', key)
        assert decoded == ""
    
    def test_utf8_multibyte_chinese(self):
        """Test Chinese characters (3-byte UTF-8)"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        text = "你好世界"  # Hello World in Chinese
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
    
    def test_utf8_multibyte_arabic(self):
        """Test Arabic characters (2-byte UTF-8)"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        text = "مرحبا بك"  # Welcome in Arabic
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
    
    def test_emojis_4byte(self):
        """Test emojis (4-byte UTF-8)"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        text = "Hello 😀🔥💖🚀"
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
    
    def test_mixed_unicode(self):
        """Test mix of ASCII, multibyte, and emojis"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        text = "API: 12345 中文 العربية 😀"
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
    
    def test_special_characters(self):
        """Test special characters like newline, tab"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        text = "Line1\nLine2\tTabbed\rReturn"
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
    
    def test_null_bytes(self):
        """Test strings containing null bytes"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        # Note: Python strings can contain null chars
        text = "Before\x00After"
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
    
    def test_long_string(self):
        """Test very long strings (1000+ chars)"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        text = "A" * 1000 + "B" * 500 + "中文" * 250
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
    
    def test_string_too_long(self):
        """Test max string length enforcement"""
        obfuscator = StringObfuscator()
        key = obfuscator.generate_key()
        
        text = "A" * (obfuscator.MAX_STRING_LENGTH + 1)
        
        with pytest.raises(ValueError, match="String too long"):
            obfuscator.xor_encode(text, key)
    
    def test_empty_key(self):
        """Test that empty key raises error"""
        obfuscator = StringObfuscator()
        
        with pytest.raises(ValueError, match="Key cannot be empty"):
            obfuscator.xor_encode("test", b'')
        
        with pytest.raises(ValueError, match="Key cannot be empty"):
            obfuscator.xor_decode(b'test', b'')
    
    def test_key_repetition(self):
        """Test that short key is repeated for long strings"""
        obfuscator = StringObfuscator()
        key = b'\x01\x02'  # 2-byte key
        
        text = "Hello World!"  # 12 chars = more than key length
        encoded = obfuscator.xor_encode(text, key)
        decoded = obfuscator.xor_decode(encoded, key)
        
        assert decoded == text
        
        # Verify key repetition pattern
        text_bytes = text.encode('utf-8')
        assert encoded[0] == text_bytes[0] ^ key[0]
        assert encoded[1] == text_bytes[1] ^ key[1]
        assert encoded[2] == text_bytes[2] ^ key[0]  # Key repeats
        assert encoded[3] == text_bytes[3] ^ key[1]


class TestSmaliFormatting:
    """Test smali code generation"""
    
    def test_bytes_to_smali_array_empty(self):
        """Test empty byte array"""
        obfuscator = StringObfuscator()
        smali = obfuscator.bytes_to_smali_array(b'')
        
        assert "const/4 v0, 0x0" in smali
        assert "new-array v0, v0, [B" in smali
    
    def test_bytes_to_smali_array_simple(self):
        """Test simple byte array"""
        obfuscator = StringObfuscator()
        smali = obfuscator.bytes_to_smali_array(b'\x01\x02\x03')
        
        assert "const/4 v0, 0x3" in smali
        assert "new-array v0, v0, [B" in smali
        assert "aput-byte v1, v0, v2" in smali
    
    def test_bytes_to_smali_array_large_values(self):
        """Test byte array with values > 127"""
        obfuscator = StringObfuscator()
        smali = obfuscator.bytes_to_smali_array(b'\xff\x80\x7f')
        
        assert "const/16 v1, -1" in smali  # 0xff as signed
        assert "const/16 v1, -128" in smali  # 0x80 as signed
        assert "const/4 v1, 0x7f" in smali  # 0x7f fits in const/4
    
    def test_prepare_smali_format_empty(self):
        """Test smali format for empty string"""
        obfuscator = StringObfuscator()
        smali = obfuscator.prepare_smali_format(b'', b'\x01\x02')
        
        assert 'const-string v0, ""' in smali
    
    def test_prepare_smali_format_complete(self):
        """Test complete smali code generation"""
        obfuscator = StringObfuscator()
        encoded = b'\x01\x02\x03'
        key = b'\x0a\x0b'
        
        smali = obfuscator.prepare_smali_format(encoded, key)
        
        # Check all required elements
        assert "# Obfuscated string" in smali
        assert ".locals 5" in smali
        assert "# Encoded data" in smali
        assert "# Key" in smali
        assert ":decode_loop" in smali
        assert "xor-int/2addr v2, v5" in smali
        assert "Ljava/lang/String;" in smali
        assert "UTF-8" in smali


class TestObfuscation:
    """Test complete obfuscation workflow"""
    
    def test_obfuscate_basic(self):
        """Test basic string obfuscation"""
        obfuscator = StringObfuscator()
        result = obfuscator.obfuscate("Hello World")
        
        assert isinstance(result, ObfuscatedString)
        assert result.original == "Hello World"
        assert len(result.key) == 16
        assert len(result.encoded_bytes) > 0
        assert len(result.smali_code) > 0
        
        # Verify decoding works
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        assert decoded == "Hello World"
    
    def test_obfuscate_with_custom_key(self):
        """Test obfuscation with custom key"""
        obfuscator = StringObfuscator()
        custom_key = b'\x01\x02\x03\x04\x05\x06\x07\x08'
        
        result = obfuscator.obfuscate("Test", key=custom_key)
        
        assert result.key == custom_key
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        assert decoded == "Test"
    
    def test_obfuscate_unicode(self):
        """Test obfuscation with unicode strings"""
        obfuscator = StringObfuscator()
        
        test_cases = [
            "Hello 世界",
            "مرحبا",
            "Привет",
            "こんにちは",
            "😀🔥💖",
        ]
        
        for text in test_cases:
            result = obfuscator.obfuscate(text)
            decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
            assert decoded == text
    
    def test_obfuscate_special_chars(self):
        """Test obfuscation with special characters"""
        obfuscator = StringObfuscator()
        
        text = "Line1\nLine2\tTab\rReturn"
        result = obfuscator.obfuscate(text)
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        
        assert decoded == text
    
    def test_obfuscate_api_key(self):
        """Test obfuscating realistic API key"""
        obfuscator = StringObfuscator()
        
        api_key = "sk-1234567890abcdef1234567890abcdef"
        result = obfuscator.obfuscate(api_key)
        
        # Verify encoding is different from original
        assert result.encoded_bytes != api_key.encode('utf-8')
        
        # Verify decoding works
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        assert decoded == api_key
    
    def test_obfuscate_url(self):
        """Test obfuscating URL"""
        obfuscator = StringObfuscator()
        
        url = "https://api.example.com/v1/users?key=secret123"
        result = obfuscator.obfuscate(url)
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        
        assert decoded == url
    
    def test_obfuscate_invalid_type(self):
        """Test that non-string input raises error"""
        obfuscator = StringObfuscator()
        
        with pytest.raises(ValueError, match="Text must be string"):
            obfuscator.obfuscate(123)
        
        with pytest.raises(ValueError, match="Text must be string"):
            obfuscator.obfuscate(None)
    
    def test_obfuscate_batch(self):
        """Test batch obfuscation"""
        obfuscator = StringObfuscator()
        
        strings = ["API_KEY_1", "API_KEY_2", "SECRET_TOKEN"]
        results = obfuscator.obfuscate_batch(strings)
        
        assert len(results) == 3
        
        # Verify each string
        for i, result in enumerate(results):
            decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
            assert decoded == strings[i]
    
    def test_obfuscate_batch_same_key(self):
        """Test batch obfuscation with same key"""
        obfuscator = StringObfuscator()
        
        strings = ["String1", "String2", "String3"]
        results = obfuscator.obfuscate_batch(strings, use_same_key=True)
        
        # All should use same key
        first_key = results[0].key
        for result in results[1:]:
            assert result.key == first_key
    
    def test_obfuscate_batch_empty(self):
        """Test batch obfuscation with empty list"""
        obfuscator = StringObfuscator()
        results = obfuscator.obfuscate_batch([])
        
        assert results == []
    
    def test_obfuscate_batch_skips_empty_strings(self):
        """Test batch obfuscation skips empty strings"""
        obfuscator = StringObfuscator()
        
        strings = ["Valid", "", "AlsoValid", ""]
        results = obfuscator.obfuscate_batch(strings)
        
        assert len(results) == 2
        assert results[0].original == "Valid"
        assert results[1].original == "AlsoValid"


class TestStatistics:
    """Test statistics tracking"""
    
    def test_stats_initial(self):
        """Test initial stats are zero"""
        obfuscator = StringObfuscator()
        stats = obfuscator.get_stats()
        
        assert stats['total_obfuscated'] == 0
        assert stats['total_bytes_processed'] == 0
    
    def test_stats_single_obfuscation(self):
        """Test stats after single obfuscation"""
        obfuscator = StringObfuscator()
        obfuscator.obfuscate("Hello")
        
        stats = obfuscator.get_stats()
        assert stats['total_obfuscated'] == 1
        assert stats['total_bytes_processed'] == 5  # "Hello" = 5 bytes
    
    def test_stats_multiple_obfuscations(self):
        """Test stats after multiple obfuscations"""
        obfuscator = StringObfuscator()
        obfuscator.obfuscate("Hello")  # 5 bytes
        obfuscator.obfuscate("World")  # 5 bytes
        obfuscator.obfuscate("测试")    # 6 bytes (3 chars * 2 bytes each in UTF-8)
        
        stats = obfuscator.get_stats()
        assert stats['total_obfuscated'] == 3
        assert stats['total_bytes_processed'] >= 16  # At least 16 bytes
    
    def test_stats_reset(self):
        """Test stats reset"""
        obfuscator = StringObfuscator()
        obfuscator.obfuscate("Hello")
        obfuscator.obfuscate("World")
        
        obfuscator.reset_stats()
        stats = obfuscator.get_stats()
        
        assert stats['total_obfuscated'] == 0
        assert stats['total_bytes_processed'] == 0
    
    def test_stats_batch(self):
        """Test stats with batch obfuscation"""
        obfuscator = StringObfuscator()
        strings = ["A", "B", "C", "D", "E"]
        obfuscator.obfuscate_batch(strings)
        
        stats = obfuscator.get_stats()
        assert stats['total_obfuscated'] == 5
        assert stats['total_bytes_processed'] == 5


class TestPerformance:
    """Test performance requirements"""
    
    def test_performance_100_strings(self):
        """Test encoding 100 strings in < 1 second"""
        obfuscator = StringObfuscator()
        
        # Generate test strings
        strings = [f"API_KEY_{i:04d}_SECRET_TOKEN" for i in range(100)]
        
        start_time = time.time()
        results = obfuscator.obfuscate_batch(strings)
        elapsed = time.time() - start_time
        
        assert len(results) == 100
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s for 100 strings"
    
    def test_performance_large_string(self):
        """Test encoding large string is reasonably fast"""
        obfuscator = StringObfuscator()
        
        # 5000 char string
        large_string = "A" * 5000
        
        start_time = time.time()
        result = obfuscator.obfuscate(large_string)
        elapsed = time.time() - start_time
        
        assert elapsed < 0.1, f"Too slow: {elapsed:.3f}s for 5000 chars"
        
        # Verify correctness
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        assert decoded == large_string


class TestSmaliStringReplacer:
    """Test SmaliStringReplacer functionality"""
    
    def test_find_string_constants(self):
        """Test finding string constants in smali code"""
        replacer = SmaliStringReplacer()
        
        smali = '''
        .method public test()V
            const-string v0, "Hello"
            const-string v1, "World"
            const-string v2, "API_KEY_12345"
        .end method
        '''
        
        results = replacer.find_string_constants(smali)
        
        assert len(results) == 3
        assert results[0][1] == "Hello"
        assert results[1][1] == "World"
        assert results[2][1] == "API_KEY_12345"
    
    def test_should_obfuscate_heuristics(self):
        """Test should_obfuscate heuristics"""
        replacer = SmaliStringReplacer()
        
        # Should obfuscate
        assert replacer.should_obfuscate("https://api.example.com")
        assert replacer.should_obfuscate("API_KEY_12345")
        assert replacer.should_obfuscate("secret_token_abc123")
        assert replacer.should_obfuscate("Bearer xyz123abc")
        
        # Should NOT obfuscate
        assert not replacer.should_obfuscate("Hi")  # Too short
        assert not replacer.should_obfuscate("android.app.Activity")
        assert not replacer.should_obfuscate("UTF-8")
        assert not replacer.should_obfuscate("com.google.firebase")
    
    def test_replace_in_smali_auto_detect(self):
        """Test automatic detection and replacement"""
        replacer = SmaliStringReplacer()
        
        smali = '''
        .method public test()V
            const-string v0, "Hello"
            const-string v1, "https://api.example.com/secret"
            const-string v2, "android.app.Activity"
        .end method
        '''
        
        modified, count = replacer.replace_in_smali(smali)
        
        # Should replace URL but not others
        assert count == 1
        assert "Hello" in modified  # Short string kept
        assert "android.app.Activity" in modified  # Framework string kept
        assert "https://api.example.com/secret" not in modified  # URL replaced
        assert "# Obfuscated string" in modified
    
    def test_replace_in_smali_explicit_list(self):
        """Test replacement with explicit string list"""
        replacer = SmaliStringReplacer()
        
        smali = '''
        .method public test()V
            const-string v0, "Hello"
            const-string v1, "World"
            const-string v2, "SECRET"
        .end method
        '''
        
        modified, count = replacer.replace_in_smali(
            smali,
            strings_to_obfuscate=["Hello", "SECRET"]
        )
        
        assert count == 2
        assert "Hello" not in modified
        assert "World" in modified  # Not in list, kept
        assert "SECRET" not in modified
        assert modified.count("# Obfuscated string") == 2
    
    def test_replace_in_smali_no_matches(self):
        """Test replacement with no matching strings"""
        replacer = SmaliStringReplacer()
        
        smali = '''
        .method public test()V
            const/4 v0, 0x1
            return-void
        .end method
        '''
        
        modified, count = replacer.replace_in_smali(smali)
        
        assert count == 0
        assert modified == smali


class TestFactoryFunction:
    """Test factory function"""
    
    def test_create_obfuscator_default(self):
        """Test factory with default parameters"""
        obfuscator = create_obfuscator()
        
        assert isinstance(obfuscator, StringObfuscator)
        assert obfuscator.default_key_length == 16
    
    def test_create_obfuscator_custom(self):
        """Test factory with custom parameters"""
        obfuscator = create_obfuscator(key_length=32)
        
        assert isinstance(obfuscator, StringObfuscator)
        assert obfuscator.default_key_length == 32


class TestRealWorldScenarios:
    """Test with real-world strings from APKs"""
    
    def test_firebase_api_key(self):
        """Test Firebase API key format"""
        obfuscator = StringObfuscator()
        
        api_key = "AIzaSyDhbXdWrBT0X9EKH4qxYZ1234567890abc"
        result = obfuscator.obfuscate(api_key)
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        
        assert decoded == api_key
    
    def test_google_maps_key(self):
        """Test Google Maps API key format"""
        obfuscator = StringObfuscator()
        
        maps_key = "AIzaSyC1234567890abcdefghijklmnopqrstuv"
        result = obfuscator.obfuscate(maps_key)
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        
        assert decoded == maps_key
    
    def test_rest_api_endpoint(self):
        """Test REST API endpoint"""
        obfuscator = StringObfuscator()
        
        endpoint = "https://api.myapp.com/v2/users/profile?auth=xyz123"
        result = obfuscator.obfuscate(endpoint)
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        
        assert decoded == endpoint
    
    def test_jwt_token(self):
        """Test JWT token format"""
        obfuscator = StringObfuscator()
        
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = obfuscator.obfuscate(jwt)
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        
        assert decoded == jwt
    
    def test_database_connection_string(self):
        """Test database connection string"""
        obfuscator = StringObfuscator()
        
        conn_str = "mongodb://user:pass123@cluster0.mongodb.net/mydb?retryWrites=true"
        result = obfuscator.obfuscate(conn_str)
        decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
        
        assert decoded == conn_str
    
    def test_mixed_language_app_strings(self):
        """Test multilingual app strings"""
        obfuscator = StringObfuscator()
        
        strings = [
            "Welcome to the app!",
            "欢迎使用本应用！",
            "مرحبا بك في التطبيق!",
            "Добро пожаловать в приложение!",
            "アプリへようこそ！",
        ]
        
        results = obfuscator.obfuscate_batch(strings)
        
        for i, result in enumerate(results):
            decoded = obfuscator.xor_decode(result.encoded_bytes, result.key)
            assert decoded == strings[i]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])