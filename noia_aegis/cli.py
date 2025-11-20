"""
Noia Aegis - CLI Interface
APK Security Injection Tool
"""
import click
from colorama import init, Fore, Style
from pathlib import Path
import sys
from datetime import datetime
import os
import getpass
from noia_aegis.core.env_config import EnvConfig

init(autoreset=True)

__version__ = '1.3.0'

LOGO = f"""{Fore.CYAN}
    _   __      _           ___                _    
   / | / /___  (_)___ _    /   | ___  ____ _  (_)____
  /  |/ / __ \/ / __ `/   / /| |/ _ \/ __ `/ / / ___/
 / /|  / /_/ / / /_/ /   / ___ /  __/ /_/ / / (__  ) 
/_/ |_/\____/_/\__,_/   /_/  |_\___/\__, / /_/____/  
                                   /____/             
{Style.RESET_ALL}
{Fore.YELLOW}        ⚔️  Divine Shield of Protection ⚔️{Style.RESET_ALL}
{Fore.CYAN}      APK Security Injection Tool v{__version__}{Style.RESET_ALL}
"""


@click.group()
@click.version_option(version=__version__, prog_name='Noia Aegis')
def cli():
    """
    🛡️  Noia Aegis - APK Security Injection Tool
    
    Protect your Android apps with divine shields.
    """
    pass


@cli.command()
@click.argument('apk_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output APK filename')
@click.option('--config', '-c', type=click.Path(), help='Config file path (.aegis.yml)')
@click.option('--keystore', type=click.Path(exists=True), help='Production keystore (.jks/.keystore)')
@click.option('--ks-pass', help='Keystore password')
@click.option('--ks-alias', help='Key alias')
@click.option('--key-pass', help='Key password')
@click.option('--keep-temp', is_flag=True, help='Keep temporary files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--no-logo', is_flag=True, help='Hide logo')
def shield(apk_path, output, config, keystore, ks_pass, ks_alias, 
           key_pass, keep_temp, verbose, no_logo):
    """
    Protect APK with Aegis shield
    
    Examples:
        aegis shield app.apk
        aegis shield app.apk -o protected.apk
        aegis shield app.apk --keystore release.keystore --ks-pass xxx --ks-alias release --key-pass xxx
    """
    if not no_logo:
        click.echo(LOGO)
    
    try:
        start_time = datetime.now()
        
        click.echo(f"\n{Fore.CYAN}{'='*70}")
        click.echo(f"{Fore.CYAN}⚔️  AEGIS PROTECTION")
        click.echo(f"{Fore.CYAN}{'='*70}\n")
        
        from noia_aegis.core.processor import APKProcessor
        from noia_aegis.core.injector import AegisInjector
        from noia_aegis.core.config import AegisConfig
        
        # Check for keystore from environment variables
        if not keystore and os.getenv('AEGIS_KEYSTORE'):
            keystore = os.getenv('AEGIS_KEYSTORE')
            ks_pass = os.getenv('AEGIS_KS_PASS')
            ks_alias = os.getenv('AEGIS_KS_ALIAS')
            key_pass = os.getenv('AEGIS_KEY_PASS')
            if verbose:
                click.echo(f"{Fore.YELLOW}Using keystore from environment variables{Style.RESET_ALL}\n")
        
        # Validate keystore params
        if keystore:
            if not (ks_pass and ks_alias and key_pass):
                click.echo(f"{Fore.RED}Error: When using custom keystore, all parameters required:{Style.RESET_ALL}")
                click.echo(f"  --keystore, --ks-pass, --ks-alias, --key-pass")
                click.echo(f"\nOr set environment variables:")
                click.echo(f"  AEGIS_KEYSTORE, AEGIS_KS_PASS, AEGIS_KS_ALIAS, AEGIS_KEY_PASS")
                sys.exit(1)
            
            click.echo(f"{Fore.YELLOW}🔑 Custom Keystore Mode{Style.RESET_ALL}")
            click.echo(f"  Keystore: {Path(keystore).name}")
            click.echo(f"  Alias: {ks_alias}\n")
        else:
            click.echo(f"{Fore.YELLOW}🔓 Debug Keystore Mode{Style.RESET_ALL}")
            click.echo(f"  Note: Signature will be different from original\n")
        
        # Load config
        aegis_config = AegisConfig(config)
        
        if verbose:
            click.echo(f"{Fore.YELLOW}Config:{Style.RESET_ALL}")
            click.echo(f"  • Root Detection: {aegis_config.is_shield_enabled('root_detection')}")
            click.echo(f"  • Emulator Detection: {aegis_config.is_shield_enabled('emulator_detection')}")
            click.echo(f"  • Debug Detection: {aegis_config.is_shield_enabled('debug_detection')}")
            click.echo(f"  • Developer Options: {aegis_config.is_shield_enabled('developer_options')}")
            click.echo()
        
        click.echo(f"{Fore.YELLOW}📱 Input:{Style.RESET_ALL} {apk_path}")
        if output:
            click.echo(f"{Fore.YELLOW}📦 Output:{Style.RESET_ALL} {output}\n")
        
        # Get original signature
        processor = APKProcessor(apk_path, verbose=verbose)
        
        if keystore and verbose:
            click.echo(f"{Fore.CYAN}Original APK Signature:{Style.RESET_ALL}")
            original_sig = processor.verify_signature(apk_path)
            if original_sig:
                for line in original_sig.split('\n')[:5]:  # Show first 5 lines
                    click.echo(f"  {line}")
            click.echo()
        
        # Step 1: Decompile
        click.echo(f"{Fore.CYAN}[1/5] 🔍 Decompiling APK...{Style.RESET_ALL}")
        work_dir = processor.decompile()
        click.echo(f"{Fore.GREEN}✓ Decompiled{Style.RESET_ALL}\n")
        
        # Step 2: Analyze
        click.echo(f"{Fore.CYAN}[2/5] 📊 Analyzing...{Style.RESET_ALL}")
        injector = AegisInjector(work_dir, verbose=verbose, config=aegis_config)
        analysis = injector.analyze()
        
        click.echo(f"  • Type: {analysis['app_type']}")
        click.echo(f"  • Activities: {analysis['activity_count']}")
        click.echo(f"  • Application: {'Yes' if analysis['has_application'] else 'No'}")
        click.echo(f"{Fore.GREEN}✓ Analysis complete{Style.RESET_ALL}\n")
        
        # Step 3: Inject
        click.echo(f"{Fore.CYAN}[3/5] 🛡️  Injecting shields...{Style.RESET_ALL}")
        result = injector.forge_aegis()
        
        click.echo(f"  • Classes added: {result['classes_added']}")
        click.echo(f"  • Injection points: {result['injection_count']}")
        click.echo(f"{Fore.GREEN}✓ Shields activated{Style.RESET_ALL}\n")
        
        # Step 4: Recompile
        click.echo(f"{Fore.CYAN}[4/5] 🔨 Recompiling...{Style.RESET_ALL}")
        unsigned_apk = processor.recompile(output)
        click.echo(f"{Fore.GREEN}✓ Recompiled{Style.RESET_ALL}\n")
        
        # Step 5: Sign
        click.echo(f"{Fore.CYAN}[5/5] ✍️  Signing...{Style.RESET_ALL}")
        
        if keystore:
            signed_apk = processor.sign(
                unsigned_apk,
                keystore_path=keystore,
                keystore_pass=ks_pass,
                key_alias=ks_alias,
                key_pass=key_pass
            )
            click.echo(f"{Fore.GREEN}✓ Signed with custom keystore{Style.RESET_ALL}\n")
        else:
            signed_apk = processor.sign(unsigned_apk)
            click.echo(f"{Fore.GREEN}✓ Signed with debug keystore{Style.RESET_ALL}\n")
        
        # Verify signature
        if keystore and verbose:
            click.echo(f"{Fore.CYAN}Protected APK Signature:{Style.RESET_ALL}")
            protected_sig = processor.verify_signature(signed_apk)
            if protected_sig:
                for line in protected_sig.split('\n')[:5]:
                    click.echo(f"  {line}")
            click.echo()
        
        # Cleanup
        if not keep_temp:
            processor.cleanup()
        
        # Stats
        duration = (datetime.now() - start_time).total_seconds()
        original_size = Path(apk_path).stat().st_size / 1024 / 1024
        protected_size = signed_apk.stat().st_size / 1024 / 1024
        
        # Success
        click.echo(f"{Fore.GREEN}{'='*70}")
        click.echo(f"{Fore.GREEN}✅ SUCCESS")
        click.echo(f"{Fore.GREEN}{'='*70}\n")
        
        click.echo(f"{Fore.YELLOW}📦 Protected APK:{Style.RESET_ALL} {signed_apk}")
        click.echo(f"{Fore.YELLOW}⏱️  Time:{Style.RESET_ALL} {duration:.2f}s")
        click.echo(f"{Fore.YELLOW}📊 Size:{Style.RESET_ALL} {original_size:.2f} MB → {protected_size:.2f} MB")
        
        click.echo(f"\n{Fore.CYAN}Active Shields:{Style.RESET_ALL}")
        for shield in result['enabled_shields']:
            click.echo(f"{Fore.GREEN}  ✓ {shield}{Style.RESET_ALL}")
        
        if keystore:
            click.echo(f"\n{Fore.GREEN}✓ Signed with your production keystore{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}✓ Signature matches original APK{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}✓ Can update existing app on device{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}✓ Can upload to Play Store{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.YELLOW}⚠️  Signed with debug keystore{Style.RESET_ALL}")
            click.echo(f"{Fore.YELLOW}⚠️  Cannot update existing app{Style.RESET_ALL}")
            click.echo(f"{Fore.YELLOW}⚠️  Cannot upload to Play Store{Style.RESET_ALL}")
            click.echo(f"\n{Fore.CYAN}Tip: Use --keystore for production builds{Style.RESET_ALL}")
        
        click.echo(f"\n{Fore.CYAN}Install: {Fore.YELLOW}adb install {signed_apk}{Style.RESET_ALL}\n")
        
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}⚠️  Cancelled{Style.RESET_ALL}\n")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--no-logo', is_flag=True, help='Hide logo')
def protect(config_file, no_logo):
    """
    Protect APK using configuration file
    
    Examples:
        aegis protect signing-config.yml
        aegis protect production-config.yml
    """
    if not no_logo:
        click.echo(LOGO)

    # Load environment config
    env_config = EnvConfig()
    
    try:
        import yaml
        
        click.echo(f"\n{Fore.CYAN}{'='*70}")
        click.echo(f"{Fore.CYAN}⚔️  AEGIS PROTECTION (Config File Mode)")
        click.echo(f"{Fore.CYAN}{'='*70}\n")
        
        # Load config file
        click.echo(f"{Fore.YELLOW}📄 Loading config: {config_file}{Style.RESET_ALL}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        if 'apk' not in config or 'input' not in config['apk']:
            click.echo(f"{Fore.RED}❌ Error: 'apk.input' is required in config file{Style.RESET_ALL}\n")
            sys.exit(1)
        
        # Extract APK config
        apk_input = config['apk']['input']
        apk_output = config['apk'].get('output', f"{Path(apk_input).stem}-protected.apk")
        
        # Validate APK exists
        if not Path(apk_input).exists():
            click.echo(f"{Fore.RED}❌ Error: APK not found: {apk_input}{Style.RESET_ALL}\n")
            sys.exit(1)
        
        # Extract signing config
        signing_config = config.get('signing', {})
        use_custom = signing_config.get('use_custom', False)
        
        keystore_path = None
        ks_pass = None
        ks_alias = None
        key_pass = None
        
        if use_custom:
            keystore_path = signing_config.get('keystore')
            ks_pass = signing_config.get('keystore_password')
            ks_alias = signing_config.get('key_alias')
            key_pass = signing_config.get('key_password')
            
            # Validate keystore config
            if not all([keystore_path, ks_pass, ks_alias, key_pass]):
                click.echo(f"{Fore.RED}❌ Error: Incomplete keystore configuration{Style.RESET_ALL}")
                click.echo(f"Required fields: keystore, keystore_password, key_alias, key_password\n")
                sys.exit(1)
            
            # Handle env variables
            if isinstance(ks_pass, str) and ks_pass.startswith('env:'):
                env_var = ks_pass.replace('env:', '')
                ks_pass = os.getenv(env_var)
                if not ks_pass:
                    click.echo(f"{Fore.RED}❌ Error: Environment variable not set: {env_var}{Style.RESET_ALL}\n")
                    sys.exit(1)
            
            if isinstance(key_pass, str) and key_pass.startswith('env:'):
                env_var = key_pass.replace('env:', '')
                key_pass = os.getenv(env_var)
                if not key_pass:
                    click.echo(f"{Fore.RED}❌ Error: Environment variable not set: {env_var}{Style.RESET_ALL}\n")
                    sys.exit(1)
            
            # Validate keystore exists
            if not Path(keystore_path).exists():
                click.echo(f"{Fore.RED}❌ Error: Keystore not found: {keystore_path}{Style.RESET_ALL}\n")
                sys.exit(1)
        
        # Extract options
        options = config.get('options', {})
        verbose = options.get('verbose', False)
        keep_temp = options.get('keep_temp', False)
        
        # Display configuration summary
        click.echo(f"\n{Fore.CYAN}Configuration Summary:{Style.RESET_ALL}")
        click.echo(f"  📱 Input APK: {apk_input}")
        click.echo(f"  📦 Output APK: {apk_output}")
        click.echo(f"  🔑 Signing: {Fore.GREEN if use_custom else Fore.YELLOW}{'Custom keystore' if use_custom else 'Debug keystore'}{Style.RESET_ALL}")
        
        if use_custom:
            click.echo(f"      Keystore: {Path(keystore_path).name}")
            click.echo(f"      Alias: {ks_alias}")
        
        # Show enabled shields
        shields_config = config.get('shields', {})
        enabled_shields = [name.replace('_', ' ').title() for name, enabled in shields_config.items() if enabled]
        
        if enabled_shields:
            click.echo(f"  🛡️  Shields: {', '.join(enabled_shields)}")
        
        click.echo()
        
        # Import modules
        from noia_aegis.core.processor import APKProcessor
        from noia_aegis.core.injector import AegisInjector
        from noia_aegis.core.config import AegisConfig
        
        start_time = datetime.now()
        
        # Create Aegis config from file
        aegis_config = AegisConfig()
        obfuscate_strings = config.get('obfuscation', {}).get('enabled', False)
        
        # Update shields from config file
        if 'shields' in config:
            for shield_name, enabled in config['shields'].items():
                if shield_name in aegis_config.config['shields']:
                    aegis_config.config['shields'][shield_name] = enabled
        
        # Update behavior from config file
        if 'behavior' in config:
            for behavior_name, value in config['behavior'].items():
                if behavior_name in aegis_config.config['behavior']:
                    aegis_config.config['behavior'][behavior_name] = value
        
        # Update messages from config file
        if 'messages' in config:
            for message_name, value in config['messages'].items():
                if message_name in aegis_config.config['messages']:
                    aegis_config.config['messages'][message_name] = value
        
        # Initialize processor
        processor = APKProcessor(apk_input, verbose=verbose, env_config=env_config)
        
        # Step 1: Decompile
        click.echo(f"{Fore.CYAN}[1/5] 🔍 Decompiling APK...{Style.RESET_ALL}")
        work_dir = processor.decompile()
        click.echo(f"{Fore.GREEN}✓ Decompiled{Style.RESET_ALL}\n")
        
        # Extract obfuscation config (v1.3.0)
        obfuscate_strings = config.get('obfuscation', {}).get('enabled', False)

        # Step 2: Analyze
        click.echo(f"{Fore.CYAN}[2/5] 📊 Analyzing structure...{Style.RESET_ALL}")
        injector = AegisInjector(work_dir, verbose=verbose, config=aegis_config, obfuscate_strings=obfuscate_strings)
        analysis = injector.analyze()
        
        click.echo(f"  • Type: {analysis['app_type']}")
        click.echo(f"  • Activities: {analysis['activity_count']}")
        click.echo(f"  • Application Class: {'Yes' if analysis['has_application'] else 'No'}")
        click.echo(f"{Fore.GREEN}✓ Analysis complete{Style.RESET_ALL}\n")
        
        # Step 3: Inject
        click.echo(f"{Fore.CYAN}[3/5] 🛡️  Forging Aegis shields...{Style.RESET_ALL}")
        result = injector.forge_aegis()

        click.echo(f"  • Shield classes: {result['classes_added']}")
        click.echo(f"  • Injection points: {result['injection_count']}")

        # Show obfuscation results if enabled
        if result.get('obfuscated_strings', 0) > 0:
            click.echo(f"  • Obfuscated strings: {result['obfuscated_strings']} in {result['obfuscated_files']} files")

        click.echo(f"{Fore.GREEN}✓ Shields activated{Style.RESET_ALL}\n")
        
        # Step 4: Recompile
        click.echo(f"{Fore.CYAN}[4/5] 🔨 Recompiling APK...{Style.RESET_ALL}")
        unsigned_apk = processor.recompile(apk_output)
        click.echo(f"{Fore.GREEN}✓ Recompiled{Style.RESET_ALL}\n")
        
        # Step 5: Sign
        click.echo(f"{Fore.CYAN}[5/5] ✍️  Signing APK...{Style.RESET_ALL}")
        
        if use_custom and keystore_path:
            signed_apk = processor.sign(
                unsigned_apk,
                keystore_path=keystore_path,
                keystore_pass=ks_pass,
                key_alias=ks_alias,
                key_pass=key_pass
            )
            click.echo(f"{Fore.GREEN}✓ Signed with custom keystore{Style.RESET_ALL}\n")
        else:
            signed_apk = processor.sign(unsigned_apk)
            click.echo(f"{Fore.GREEN}✓ Signed with debug keystore{Style.RESET_ALL}\n")
        
        # Cleanup
        if not keep_temp:
            processor.cleanup()
        
        # Calculate stats
        duration = (datetime.now() - start_time).total_seconds()
        original_size = Path(apk_input).stat().st_size / 1024 / 1024
        protected_size = signed_apk.stat().st_size / 1024 / 1024
        size_increase = ((protected_size - original_size) / original_size) * 100
        
        # Success summary
        click.echo(f"{Fore.GREEN}{'='*70}")
        click.echo(f"{Fore.GREEN}✅ PROTECTION COMPLETE")
        click.echo(f"{Fore.GREEN}{'='*70}\n")
        
        click.echo(f"{Fore.YELLOW}📦 Protected APK:{Style.RESET_ALL} {signed_apk}")
        click.echo(f"{Fore.YELLOW}⏱️  Processing time:{Style.RESET_ALL} {duration:.2f}s")
        click.echo(f"{Fore.YELLOW}📊 Size:{Style.RESET_ALL} {original_size:.2f} MB → {protected_size:.2f} MB (+{size_increase:.1f}%)")
        
        click.echo(f"\n{Fore.CYAN}🛡️  Active Shields:{Style.RESET_ALL}")
        for shield in result['enabled_shields']:
            click.echo(f"{Fore.GREEN}  ✓ {shield}{Style.RESET_ALL}")
        
        # Show obfuscation summary
        if result.get('obfuscated_strings', 0) > 0:
            click.echo(f"\n{Fore.CYAN}🔐 String Obfuscation:{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}  ✓ {result['obfuscated_strings']} strings obfuscated{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}  ✓ {result['obfuscated_files']} files modified{Style.RESET_ALL}")
            click.echo(f"{Fore.CYAN}  Protection against static analysis ✓{Style.RESET_ALL}")
        
        if use_custom and keystore_path:
            click.echo(f"\n{Fore.GREEN}✓ Signed with production keystore{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}✓ Signature matches original APK{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}✓ Ready for Play Store upload{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.YELLOW}⚠️  Debug signature - not for production{Style.RESET_ALL}")
        
        click.echo(f"\n{Fore.CYAN}📲 Next steps:{Style.RESET_ALL}")
        click.echo(f"  1. Install: {Fore.YELLOW}adb install {signed_apk}{Style.RESET_ALL}")
        click.echo(f"  2. Test on real device")
        click.echo(f"  3. Verify shields are working\n")
        
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}⚠️  Cancelled{Style.RESET_ALL}\n")
        sys.exit(130)
    except yaml.YAMLError as e:
        click.echo(f"\n{Fore.RED}❌ Invalid YAML syntax in config file:{Style.RESET_ALL}")
        click.echo(f"{str(e)}\n")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


@cli.command()
@click.argument('apk_path', type=click.Path(exists=True))
def scan(apk_path):
    """
    Scan APK structure without injection
    
    Example:
        aegis scan app.apk
    """
    try:
        click.echo(f"\n{Fore.CYAN}🔍 Scanning: {apk_path}{Style.RESET_ALL}\n")
        
        from noia_aegis.core.processor import APKProcessor
        from noia_aegis.core.injector import AegisInjector
        
        processor = APKProcessor(apk_path)
        work_dir = processor.decompile()
        
        injector = AegisInjector(work_dir)
        analysis = injector.analyze()
        
        click.echo(f"{Fore.CYAN}Results:{Style.RESET_ALL}")
        click.echo(f"  • Type: {analysis['app_type']}")
        click.echo(f"  • Package: {analysis.get('package', 'Unknown')}")
        click.echo(f"  • Activities: {analysis['activity_count']}")
        click.echo(f"  • Application Class: {'Yes' if analysis['has_application'] else 'No'}")
        
        if analysis['activities']:
            click.echo(f"\n{Fore.CYAN}Activities:{Style.RESET_ALL}")
            for act in analysis['activities'][:5]:
                click.echo(f"  • {act}")
            if len(analysis['activities']) > 5:
                click.echo(f"  ... and {len(analysis['activities']) - 5} more")
        
        processor.cleanup()
        click.echo(f"\n{Fore.GREEN}✓ Scan complete{Style.RESET_ALL}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


@cli.command()
@click.argument('output_path', type=click.Path(), default='.aegis.yml')
def init_config(output_path):
    """
    Generate default .aegis.yml configuration file
    
    Example:
        aegis init-config
        aegis init-config custom-config.yml
    """
    try:
        from noia_aegis.core.config import AegisConfig
        
        output_file = Path(output_path)
        
        if output_file.exists():
            if not click.confirm(f"\n{Fore.YELLOW}File exists. Overwrite?{Style.RESET_ALL}", default=False):
                click.echo(f"\n{Fore.YELLOW}⚠️  Cancelled{Style.RESET_ALL}\n")
                return
        
        config = AegisConfig()
        config.save_to_file(output_path)
        
        click.echo(f"\n{Fore.GREEN}✓ Config file created: {output_path}{Style.RESET_ALL}")
        click.echo(f"\n{Fore.CYAN}Edit the file to customize shields:{Style.RESET_ALL}")
        click.echo(f"  {Fore.YELLOW}{output_path}{Style.RESET_ALL}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)

@cli.command()
@click.option('--env', is_flag=True, help='Generate .env file')
@click.option('--toml', is_flag=True, help='Generate aegis.toml file')
def init_env(env, toml):
    """
    Generate environment configuration files
    
    Examples:
        aegis init-env --env         # Generate .env
        aegis init-env --toml        # Generate aegis.toml
        aegis init-env --env --toml  # Generate both
    """
    if not env and not toml:
        # Generate both by default
        env = toml = True
    
    try:
        if env:
            env_file = Path('.env')
            if env_file.exists():
                if not click.confirm(f"\n{Fore.YELLOW}.env exists. Overwrite?{Style.RESET_ALL}", default=False):
                    click.echo(f"{Fore.YELLOW}Skipped .env{Style.RESET_ALL}")
                else:
                    _create_env_file(env_file)
            else:
                _create_env_file(env_file)
        
        if toml:
            toml_file = Path('aegis.toml')
            if toml_file.exists():
                if not click.confirm(f"\n{Fore.YELLOW}aegis.toml exists. Overwrite?{Style.RESET_ALL}", default=False):
                    click.echo(f"{Fore.YELLOW}Skipped aegis.toml{Style.RESET_ALL}")
                else:
                    _create_toml_file(toml_file)
            else:
                _create_toml_file(toml_file)
        
        click.echo(f"\n{Fore.GREEN}✓ Configuration files created{Style.RESET_ALL}")
        click.echo(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
        click.echo(f"  1. Edit configuration files")
        click.echo(f"  2. Run: {Fore.CYAN}aegis protect signing-config.yml{Style.RESET_ALL}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


def _create_env_file(path):
    """Create .env file"""
    content = """# Noia Aegis - Environment Configuration

# Android SDK Path
ANDROID_SDK_ROOT=C:/Env/Android/Sdk
ANDROID_HOME=C:/Env/Android/Sdk

# Build Tools (optional - will use latest if not specified)
ANDROID_BUILD_TOOLS_VERSION=36.0.0

# Java/JDK Path (optional)
# JAVA_HOME=C:/Program Files/Java/jdk-17

# Tool Paths (override if needed)
# APKSIGNER_PATH=C:/Env/Android/Sdk/build-tools/36.0.0/apksigner.bat
# ZIPALIGN_PATH=C:/Env/Android/Sdk/build-tools/36.0.0/zipalign.exe
"""
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    click.echo(f"{Fore.GREEN}✓ Created: {path}{Style.RESET_ALL}")


def _create_toml_file(path):
    """Create aegis.toml file"""
    content = """# Noia Aegis - Tool Configuration

[tools]
apktool = "tools/apktool.jar"
uber_apk_signer = "tools/uber-apk-signer.jar"

[android_sdk]
root = "C:/Env/Android/Sdk"
build_tools_version = "36.0.0"  # or "latest"

[paths]
output_dir = "output"
apk_output = "output/apks"

[logging]
verbose = false
keep_temp = false
"""
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    click.echo(f"{Fore.GREEN}✓ Created: {path}{Style.RESET_ALL}")

@cli.command()
@click.argument('output_path', type=click.Path(), default='signing-config.yml')
@click.option('--production', is_flag=True, help='Generate production config template')
@click.option('--debug', is_flag=True, help='Generate debug config template')
def init_signing(output_path, production, debug):
    """
    Generate signing configuration template
    
    Examples:
        aegis init-signing
        aegis init-signing production-config.yml --production
        aegis init-signing debug-config.yml --debug
    """
    try:
        output_file = Path(output_path)
        
        if output_file.exists():
            if not click.confirm(f"\n{Fore.YELLOW}File exists. Overwrite?{Style.RESET_ALL}", default=False):
                click.echo(f"\n{Fore.YELLOW}⚠️  Cancelled{Style.RESET_ALL}\n")
                return
        
        # Determine template type
        if production:
            template_type = "production"
        elif debug:
            template_type = "debug"
        else:
            template_type = "default"
        
        # Generate template
        if template_type == "production":
            template = """# Noia Aegis - Production Configuration

apk:
  input: "android/app/build/outputs/apk/release/app-release.apk"
  output: "app-release-protected.apk"

signing:
  use_custom: true
  keystore: "release.keystore"
  keystore_password: "env:AEGIS_KS_PASS"  # Use environment variable
  key_alias: "release"
  key_password: "env:AEGIS_KEY_PASS"      # Use environment variable

shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true
  integrity_check: false

obfuscation:
  enable: true
  
behavior:
  show_toast: true
  exit_on_threat: true
  log_threats: false

messages:
  root_detected: "🔓 Security threat detected"
  emulator_detected: "🖥️ Security threat detected"
  debug_detected: "🐛 Security threat detected"
  developer_detected: "⚙️ Security threat detected"

options:
  verbose: false
  keep_temp: false
"""
        elif template_type == "debug":
            template = """# Noia Aegis - Debug Configuration

apk:
  input: "android/app/build/outputs/apk/debug/app-debug.apk"
  output: "app-debug-protected.apk"

signing:
  use_custom: false  # Use debug keystore

shields:
  root_detection: false      # Allow rooted devices
  emulator_detection: false  # Allow emulators
  debug_detection: false     # Allow debugging
  developer_options: false   # Allow dev options

behavior:
  show_toast: true
  exit_on_threat: false  # Don't exit, just warn
  log_threats: true      # Log to logcat

messages:
  root_detected: "⚠️ Running on rooted device"
  emulator_detected: "⚠️ Running on emulator"
  debug_detected: "⚠️ Debugger detected"
  developer_detected: "⚠️ Developer mode active"

options:
  verbose: true
  keep_temp: true  # Keep for debugging
"""
        else:
            template = """# Noia Aegis - Configuration File
# Use with: aegis protect signing-config.yml

apk:
  input: "path/to/your/app.apk"
  output: "app-protected.apk"

signing:
  # Set to true for production, false for debug
  use_custom: true
  
  # Keystore configuration (required if use_custom: true)
  keystore: "your-release.keystore"
  keystore_password: "your_password"
  key_alias: "your_alias"
  key_password: "your_password"
  
  # Recommended: Use environment variables for security
  # keystore_password: "env:AEGIS_KS_PASS"
  # key_password: "env:AEGIS_KEY_PASS"

shields:
  root_detection: true
  emulator_detection: true
  debug_detection: true
  developer_options: true
  integrity_check: false

obfuscation:
  enable: true

behavior:
  show_toast: true
  exit_on_threat: true
  log_threats: false

messages:
  root_detected: "🔓 Root detected!"
  emulator_detected: "🖥️ Emulator detected!"
  debug_detected: "🐛 Debug mode detected!"
  developer_detected: "⚙️ Developer options enabled!"

options:
  verbose: false
  keep_temp: false
"""
        
        # Write template
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        click.echo(f"\n{Fore.GREEN}✓ Config template created: {output_file}{Style.RESET_ALL}")
        
        if template_type == "production":
            click.echo(f"\n{Fore.CYAN}Production config created!{Style.RESET_ALL}")
            click.echo(f"\n{Fore.YELLOW}Before using:{Style.RESET_ALL}")
            click.echo(f"  1. Edit config file and update paths")
            click.echo(f"  2. Set environment variables:")
            click.echo(f"     {Fore.CYAN}export AEGIS_KS_PASS='your_password'{Style.RESET_ALL}")
            click.echo(f"     {Fore.CYAN}export AEGIS_KEY_PASS='your_password'{Style.RESET_ALL}")
            click.echo(f"  3. Run: {Fore.CYAN}aegis protect {output_file}{Style.RESET_ALL}")
        elif template_type == "debug":
            click.echo(f"\n{Fore.CYAN}Debug config created!{Style.RESET_ALL}")
            click.echo(f"  All shields disabled for testing")
            click.echo(f"  Run: {Fore.CYAN}aegis protect {output_file}{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
            click.echo(f"  1. Edit: {Fore.YELLOW}{output_file}{Style.RESET_ALL}")
            click.echo(f"  2. Update APK paths and keystore info")
            click.echo(f"  3. Run: {Fore.CYAN}aegis protect {output_file}{Style.RESET_ALL}")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


# ============================================================================
# 🆕 NEW: Tool Management Commands (v1.3.0)
# ============================================================================

@cli.group()
def tools():
    """
    Manage external tools (apktool, uber-apk-signer)
    
    Examples:
        aegis tools list      # List installed tools
        aegis tools update    # Update to latest versions
        aegis tools clean     # Remove all tools
    """
    pass


@tools.command('list')
def tools_list():
    """
    List installed tools and their versions
    
    Example:
        aegis tools list
    """
    try:
        from noia_aegis.core.tool_manager import ToolManager
        
        tool_manager = ToolManager(verbose=True)
        tool_manager.list_tools()
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


@tools.command('clean')
@click.confirmation_option(prompt='Are you sure you want to remove all tools?')
def tools_clean():
    """
    Remove all downloaded tools
    
    Example:
        aegis tools clean
    """
    try:
        from noia_aegis.core.tool_manager import ToolManager
        
        click.echo(f"\n{Fore.YELLOW}🗑️  Cleaning tools...{Style.RESET_ALL}\n")
        
        tool_manager = ToolManager()
        tool_manager.clean_tools()
        
        click.echo(f"\n{Fore.GREEN}✓ Tools cleaned successfully{Style.RESET_ALL}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


@tools.command('update')
def tools_update():
    """
    Update all tools to latest versions
    
    Example:
        aegis tools update
    """
    try:
        from noia_aegis.core.tool_manager import ToolManager
        
        click.echo(f"\n{Fore.CYAN}🔄 Updating tools...{Style.RESET_ALL}\n")
        
        tool_manager = ToolManager(verbose=True)
        tool_manager.update_tools()
        
        click.echo(f"\n{Fore.GREEN}✓ All tools updated{Style.RESET_ALL}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


@tools.command('download')
def tools_download():
    """
    Download all required tools (if missing)
    
    Example:
        aegis tools download
    """
    try:
        from noia_aegis.core.tool_manager import ToolManager
        
        click.echo(f"\n{Fore.CYAN}📥 Downloading tools...{Style.RESET_ALL}\n")
        
        tool_manager = ToolManager(verbose=True)
        tool_manager.ensure_tools()
        
        click.echo(f"\n{Fore.GREEN}✓ All tools ready{Style.RESET_ALL}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


@tools.command('path')
def tools_path():
    """
    Show tools directory path
    
    Example:
        aegis tools path
    """
    try:
        from noia_aegis.core.tool_manager import ToolManager
        
        tool_manager = ToolManager()
        
        click.echo(f"\n{Fore.CYAN}Tools Directory:{Style.RESET_ALL}")
        click.echo(f"  {tool_manager.tools_dir}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


# ============================================================================


@cli.command()
def about():
    """
    About Noia Aegis
    """
    click.echo(LOGO)
    click.echo(f"""
{Fore.CYAN}Noia Aegis - APK Security Injection Tool{Style.RESET_ALL}

{Fore.YELLOW}Features:{Style.RESET_ALL}
  • Root Detection
  • Emulator Detection
  • Debug Protection
  • Developer Options Detection
  • React Native Support
  • Configurable Shields
  • Custom Keystore Signing
  • 🆕 Auto-Download Tools (v1.2.0)

{Fore.YELLOW}Commands:{Style.RESET_ALL}
  • shield       - Protect APK (full control)
  • protect      - Protect APK (config file)
  • scan         - Analyze APK structure
  • init-config  - Generate .aegis.yml
  • init-signing - Generate signing config
  • tools        - Manage external tools 🆕

{Fore.YELLOW}Version:{Style.RESET_ALL} {__version__}
{Fore.YELLOW}Author:{Style.RESET_ALL} Rizaldy

{Fore.CYAN}Quick Start:{Style.RESET_ALL}
  aegis init-signing production-config.yml --production
  aegis protect production-config.yml

{Fore.CYAN}Tool Management:{Style.RESET_ALL}
  aegis tools list    # List installed tools
  aegis tools update  # Update to latest
  aegis tools clean   # Remove all tools

{Fore.CYAN}Documentation:{Style.RESET_ALL}
  https://github.com/arr-code/noia-aegis
""")


if __name__ == '__main__':
    cli()