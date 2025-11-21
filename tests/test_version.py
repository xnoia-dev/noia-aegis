"""
Tests for Version Management

Tests centralized version system and metadata.
"""

import pytest
from noia_aegis import __version__, __version_info__, __author__, __title__
from noia_aegis.__version__ import (
    __version__ as direct_version,
    __description__,
    __license__,
    __url__,
    __release__,
    __release_date__,
)


class TestVersionManagement:
    """Test version management and metadata"""

    def test_version_string(self):
        """Should have valid version string"""
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        # Should follow semantic versioning (major.minor.patch)
        parts = __version__.split('.')
        assert len(parts) >= 2  # At least major.minor

    def test_version_info_tuple(self):
        """Should have version info tuple"""
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) >= 2
        # All parts should be integers
        for part in __version_info__:
            assert isinstance(part, int)

    def test_version_consistency(self):
        """Version string and tuple should be consistent"""
        version_from_string = tuple(map(int, __version__.split('.')))
        assert version_from_string == __version_info__

    def test_metadata_fields(self):
        """Should have all metadata fields"""
        assert isinstance(__title__, str)
        assert isinstance(__description__, str)
        assert isinstance(__author__, str)
        assert isinstance(__license__, str)
        assert isinstance(__url__, str)

    def test_title(self):
        """Should have correct title"""
        assert 'Noia' in __title__ or 'Aegis' in __title__

    def test_description(self):
        """Should have meaningful description"""
        assert len(__description__) > 10
        assert 'APK' in __description__ or 'Android' in __description__

    def test_author(self):
        """Should have author name"""
        assert len(__author__) > 0

    def test_license(self):
        """Should specify license"""
        assert len(__license__) > 0

    def test_url(self):
        """Should have project URL"""
        assert __url__.startswith('http')
        assert 'github.com' in __url__ or 'gitlab.com' in __url__

    def test_release_info(self):
        """Should have release information"""
        assert isinstance(__release__, str)
        assert isinstance(__release_date__, str)
        assert len(__release__) > 0

    def test_import_from_package(self):
        """Should be importable from main package"""
        from noia_aegis import __version__ as pkg_version
        assert pkg_version == direct_version

    def test_version_in_cli(self):
        """CLI should use same version"""
        from noia_aegis.cli import __version__ as cli_version
        assert cli_version == __version__

    def test_current_version(self):
        """Should be at least version 1.4.0"""
        major, minor, patch = __version_info__[:3] if len(__version_info__) >= 3 else __version_info__ + (0,)
        assert major >= 1
        if major == 1:
            assert minor >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])