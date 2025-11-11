import re
import shutil
from pathlib import Path
from noia_aegis.core.config import AegisConfig


class AegisInjector:
    def __init__(self, work_dir, verbose=False, config=None):
        self.work_dir = Path(work_dir)
        self.smali_dir = self.work_dir / "smali"
        self.templates_dir = Path(__file__).parent.parent / "templates" / "smali"
        self.verbose = verbose
        self.config = config or AegisConfig()
    
    def analyze(self):
        """Analyze APK structure"""
        is_react_native = self._is_react_native()
        app_class = self._find_application_class()
        activities = self._find_activities()
        main_activity = self._find_main_activity()
        
        return {
            'app_type': 'React Native' if is_react_native else 'Native Android',
            'has_application': app_class is not None,
            'activity_count': len(activities),
            'activities': [str(a.relative_to(self.work_dir)) for a in activities],
            'has_main_activity': main_activity is not None,
            'package': self._get_package_name()
        }
    
    def forge_aegis(self):
        """Inject Aegis protection based on config"""
        # Copy only enabled shields
        shields_copied = self._copy_shields()
        
        # Generate AegisCore based on config
        self._generate_aegis_core()
        
        # Find injection points
        app_class = self._find_application_class()
        main_activity = self._find_main_activity()
        
        injection_count = 0
        
        # Inject to Application
        if app_class:
            if self._inject_to_application(app_class):
                injection_count += 1
        
        # Inject to MainActivity
        if main_activity:
            if self._inject_or_create_oncreate(main_activity):
                injection_count += 1
        
        return {
            'classes_added': shields_copied,
            'injection_count': injection_count,
            'success_rate': 100 if injection_count > 0 else 0,
            'enabled_shields': self._get_enabled_shields()
        }
    
    def _get_enabled_shields(self):
        """Get list of enabled shields"""
        shields = []
        if self.config.is_shield_enabled('root_detection'):
            shields.append('Root Detection')
        if self.config.is_shield_enabled('emulator_detection'):
            shields.append('Emulator Detection')
        if self.config.is_shield_enabled('debug_detection'):
            shields.append('Debug Detection')
        if self.config.is_shield_enabled('developer_options'):
            shields.append('Developer Options Detection')
        if self.config.is_shield_enabled('integrity_check'):
            shields.append('Integrity Check')
        return shields
    
    def _copy_shields(self):
        """Copy only enabled shield smali files"""
        aegis_dir = self.smali_dir / "com" / "noiaegis"
        aegis_dir.mkdir(parents=True, exist_ok=True)
        
        shields_map = {
            'root_detection': 'RootShield.smali',
            'emulator_detection': 'EmulatorShield.smali',
            'debug_detection': 'DebugShield.smali',
            'developer_options': 'DeveloperShield.smali',
        }
        
        copied = 0
        for shield_key, shield_file in shields_map.items():
            if self.config.is_shield_enabled(shield_key):
                src = self.templates_dir / shield_file
                dst = aegis_dir / shield_file
                if src.exists():
                    shutil.copy(src, dst)
                    copied += 1
        
        # AegisCore is always copied
        copied += 1
        
        return copied
    
    def _generate_aegis_core(self):
        """Generate AegisCore.smali based on enabled shields"""
        aegis_dir = self.smali_dir / "com" / "noiaegis"
        aegis_dir.mkdir(parents=True, exist_ok=True)
        
        # Build dynamic AegisCore
        smali_code = self._build_aegis_core_smali()
        
        with open(aegis_dir / "AegisCore.smali", 'w', encoding='utf-8') as f:
            f.write(smali_code)
    
    def _build_aegis_core_smali(self):
        """Build AegisCore.smali dynamically based on config"""
        header = """.class public Lcom/noiaegis/AegisCore;
    .super Ljava/lang/Object;

    .method public static protect(Landroid/content/Context;)V
        .locals 3

    """
        
        checks = []
        label_counter = 0
        
        # Root detection
        if self.config.is_shield_enabled('root_detection'):
            next_label = f"check_{label_counter + 1}"
            message = self.config.get_message('root_detected')
            checks.append(self._generate_check_code(
                'RootShield', 'isRooted', message, next_label, use_context=False
            ))
            label_counter += 1
        
        # Emulator detection
        if self.config.is_shield_enabled('emulator_detection'):
            next_label = f"check_{label_counter + 1}"
            message = self.config.get_message('emulator_detected')
            checks.append(self._generate_check_code(
                'EmulatorShield', 'isEmulator', message, next_label,
                label=f"check_{label_counter}", use_context=False
            ))
            label_counter += 1
        
        # Debug detection
        if self.config.is_shield_enabled('debug_detection'):
            next_label = f"check_{label_counter + 1}"
            message = self.config.get_message('debug_detected')
            checks.append(self._generate_check_code(
                'DebugShield', 'isDebuggable', message, next_label,
                label=f"check_{label_counter}", use_context=False
            ))
            label_counter += 1
        
        # Developer options detection
        if self.config.is_shield_enabled('developer_options'):
            next_label = "protected"
            message = self.config.get_message('developer_detected')
            checks.append(self._generate_check_code(
                'DeveloperShield', 'isDeveloperMode', message, next_label,
                label=f"check_{label_counter}", use_context=True
            ))
            label_counter += 1
        
        footer = """
        :protected
        return-void
    .end method
    """
        
        # If no checks enabled, just return
        if not checks:
            return header + "    return-void\n.end method\n"
        
        return header + "\n".join(checks) + footer
    
    def _generate_check_code(self, shield_class, method, message, next_label, label=None, use_context=False):
        """Generate smali code for a shield check"""
        exit_behavior = """
        const/4 v0, 0x0
        invoke-static {v0}, Ljava/lang/System;->exit(I)V
    """ if self.config.should_exit_on_threat() else ""
        
        show_toast = f"""
        const-string v1, "{message}"
        const/4 v2, 0x1
        invoke-static {{p0, v1, v2}}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
        move-result-object v1
        invoke-virtual {{v1}}, Landroid/widget/Toast;->show()V
    """ if self.config.should_show_toast() else ""
        
        label_line = f"    :{label}\n" if label else ""
        
        # Method call with or without context parameter
        if use_context:
            method_call = f"invoke-static {{p0}}, Lcom/noiaegis/{shield_class};->{method}(Landroid/content/Context;)Z"
        else:
            method_call = f"invoke-static {{}}, Lcom/noiaegis/{shield_class};->{method}()Z"
        
        return f"""{label_line}    {method_call}
        move-result v0
        
        if-eqz v0, :{next_label}
    {show_toast}{exit_behavior}
    """

    def _inject_to_application(self, app_file):
        """Inject to Application.onCreate()"""
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "AEGIS INJECTED" in content:
            return False
        
        pattern = r'(\.method\s+public\s+onCreate\(\)V\s*\.locals\s+\d+)'
        injection = '\n    # AEGIS INJECTED\n    invoke-static {p0}, Lcom/noiaegis/AegisCore;->protect(Landroid/content/Context;)V\n'
        
        if re.search(pattern, content):
            modified = re.sub(pattern, r'\1' + injection, content, count=1)
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(modified)
            return True
        
        return False
    
    def _inject_or_create_oncreate(self, activity_file):
        """Inject or create onCreate in MainActivity"""
        with open(activity_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "AEGIS INJECTED" in content:
            return False
        
        has_oncreate = bool(re.search(r'\.method.*onCreate\(Landroid/os/Bundle;\)V', content))
        
        if has_oncreate:
            pattern = r'(\.method\s+(?:public|protected)\s+onCreate\(Landroid/os/Bundle;\)V\s*\.locals\s+\d+)'
            injection = '\n    # AEGIS INJECTED\n    invoke-static {p0}, Lcom/noiaegis/AegisCore;->protect(Landroid/content/Context;)V\n'
            
            modified = re.sub(pattern, r'\1' + injection, content, count=1)
            with open(activity_file, 'w', encoding='utf-8') as f:
                f.write(modified)
            return True
        else:
            super_match = re.search(r'\.super\s+(L[^;]+;)', content)
            if not super_match:
                return False
            
            super_class = super_match.group(1)
            
            new_method = f'''

# AEGIS INJECTED
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 0

    invoke-static {{p0}}, Lcom/noiaegis/AegisCore;->protect(Landroid/content/Context;)V
    invoke-super {{p0, p1}}, {super_class}->onCreate(Landroid/os/Bundle;)V

    return-void
.end method
'''
            
            pattern = r'(\.super\s+' + re.escape(super_class) + ')'
            modified = re.sub(pattern, r'\1' + new_method, content, count=1)
            
            with open(activity_file, 'w', encoding='utf-8') as f:
                f.write(modified)
            return True
        
        return False
    
    def _is_react_native(self):
        """Check if React Native app"""
        react_files = list(self.smali_dir.rglob("*ReactActivity.smali"))
        return len(react_files) > 0
    
    def _find_application_class(self):
        """Find Application class"""
        for smali_file in self.smali_dir.rglob("*Application.smali"):
            if "com/facebook/react" in str(smali_file):
                continue
            
            with open(smali_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if re.search(r'\.super\s+L(?:android/app/Application|com/facebook/react/ReactApplication|androidx/multidex/MultiDexApplication);', content):
                return smali_file
        
        return None
    
    def _find_main_activity(self):
        """Find MainActivity"""
        for smali_file in self.smali_dir.rglob("*MainActivity.smali"):
            if "com/facebook/react" in str(smali_file):
                continue
            return smali_file
        return None
    
    def _find_activities(self):
        """Find all Activity classes"""
        activities = []
        
        for smali_file in self.smali_dir.rglob("*.smali"):
            with open(smali_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if re.search(r'\.super\s+L(?:android/app/Activity|androidx/appcompat/app/AppCompatActivity|com/facebook/react/ReactActivity);', content):
                activities.append(smali_file)
        
        return activities
    
    def _get_package_name(self):
        """Get package name from AndroidManifest"""
        manifest = self.work_dir / "AndroidManifest.xml"
        if manifest.exists():
            with open(manifest, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'package="([^"]+)"', content)
            if match:
                return match.group(1)
        return "Unknown"