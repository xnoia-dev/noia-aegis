from setuptools import setup, find_packages

setup(
    name='noia-aegis',
    version='1.3.0',
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
    author='Rigels Dev',
    description='APK Security Injection Tool',
    python_requires='>=3.7',
)