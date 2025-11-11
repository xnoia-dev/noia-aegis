import click
from colorama import init, Fore, Style
from pathlib import Path
import sys
from datetime import datetime
import json

init(autoreset=True)

__version__ = '1.0.0'

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
    """Noia Aegis - APK Security Injection Tool"""
    pass


@cli.command()
@click.argument('apk_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output APK filename')
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.option('--keep-temp', is_flag=True, help='Keep temporary files')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--no-logo', is_flag=True, help='Hide logo')
def shield(apk_path, output, config, keep_temp, verbose, no_logo):
    """Protect APK with Aegis shield"""
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
        
        # Load config
        aegis_config = AegisConfig(config)
        
        if verbose:
            click.echo(f"{Fore.YELLOW}Config loaded:{Style.RESET_ALL}")
            click.echo(f"  • Root Detection: {aegis_config.is_shield_enabled('root_detection')}")
            click.echo(f"  • Emulator Detection: {aegis_config.is_shield_enabled('emulator_detection')}")
            click.echo(f"  • Debug Detection: {aegis_config.is_shield_enabled('debug_detection')}")
            click.echo()
        
        click.echo(f"{Fore.YELLOW}📱 Input:{Style.RESET_ALL} {apk_path}")
        if output:
            click.echo(f"{Fore.YELLOW}📦 Output:{Style.RESET_ALL} {output}\n")
        
        # Step 1: Decompile
        click.echo(f"{Fore.CYAN}[1/5] 🔍 Decompiling APK...{Style.RESET_ALL}")
        processor = APKProcessor(apk_path, verbose=verbose)
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
        signed_apk = processor.sign(unsigned_apk)
        click.echo(f"{Fore.GREEN}✓ Signed{Style.RESET_ALL}\n")
        
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
@click.argument('output_path', type=click.Path(), default='.aegis.yml')
def init_config(output_path):
    """Generate default config file"""
    try:
        from noia_aegis.core.config import AegisConfig
        
        config = AegisConfig()
        config.save_to_file(output_path)
        
        click.echo(f"\n{Fore.GREEN}✓ Config file created: {output_path}{Style.RESET_ALL}")
        click.echo(f"\n{Fore.CYAN}Edit the file to customize shields:{Style.RESET_ALL}")
        click.echo(f"  {Fore.YELLOW}{output_path}{Style.RESET_ALL}\n")
        
    except Exception as e:
        click.echo(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)


@cli.command()
@click.argument('apk_path', type=click.Path(exists=True))
def scan(apk_path):
    """Scan APK structure"""
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
def about():
    """About Noia Aegis"""
    click.echo(LOGO)
    click.echo(f"""
{Fore.CYAN}Noia Aegis - APK Security Injection Tool{Style.RESET_ALL}

{Fore.YELLOW}Features:{Style.RESET_ALL}
  • Root Detection
  • Emulator Detection
  • Debug Protection
  • React Native Support
  • Configurable Shields

{Fore.YELLOW}Version:{Style.RESET_ALL} {__version__}
{Fore.YELLOW}Author:{Style.RESET_ALL} Rigels Dev
""")


if __name__ == '__main__':
    cli()