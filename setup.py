from setuptools import setup, find_packages
from pathlib import Path

# Read version from __version__.py
version_file = Path(__file__).parent / 'noia_aegis' / '__version__.py'
version_dict = {}
with open(version_file, 'r', encoding='utf-8') as f:
    exec(f.read(), version_dict)

setup(
    name='noia-aegis',
    version=version_dict['__version__'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.1.0',
        'colorama>=0.4.6',
        'PyYAML>=6.0',
        'python-dotenv>=1.0.0',
        'toml>=0.10.2',
    ],
    entry_points={
        'console_scripts': [
            'aegis=noia_aegis.cli:cli',
        ],
    },
    author=version_dict['__author__'],
    author_email=version_dict['__author_email__'],
    description=version_dict['__description__'],
    url=version_dict['__url__'],
    license=version_dict['__license__'],
    python_requires='>=3.7',
)