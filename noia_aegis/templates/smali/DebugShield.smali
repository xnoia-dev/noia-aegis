.class public Lcom/noiaegis/DebugShield;
.super Ljava/lang/Object;

# Check if debugger is connected
.method public static isDebuggable()Z
    .locals 4

    # Check if debugger connected
    invoke-static {}, Landroid/os/Debug;->isDebuggerConnected()Z
    move-result v0
    
    if-eqz v0, :check_waiting
    const/4 v0, 0x1
    return v0
    
    :check_waiting
    # Check if waiting for debugger
    invoke-static {}, Landroid/os/Debug;->waitingForDebugger()Z
    move-result v0
    
    if-eqz v0, :check_build_flags
    const/4 v0, 0x1
    return v0
    
    :check_build_flags
    # Check ApplicationInfo flags for debuggable
    :try_start
    invoke-static {}, Landroid/app/ActivityThread;->currentApplication()Landroid/app/Application;
    move-result-object v1
    
    if-nez v1, :get_app_info
    const/4 v0, 0x0
    return v0
    
    :get_app_info
    invoke-virtual {v1}, Landroid/app/Application;->getApplicationInfo()Landroid/content/pm/ApplicationInfo;
    move-result-object v2
    
    iget v3, v2, Landroid/content/pm/ApplicationInfo;->flags:I
    and-int/lit8 v3, v3, 0x2
    
    if-eqz v3, :not_debuggable
    const/4 v0, 0x1
    return v0
    :try_end
    
    .catch Ljava/lang/Exception; {:try_start .. :try_end} :catch_ex
    
    :catch_ex
    :not_debuggable
    const/4 v0, 0x0
    return v0
.end method

# Check if developer options enabled
.method public static isDeveloperOptionsEnabled(Landroid/content/Context;)Z
    .locals 5

    :try_start
    # Get ContentResolver
    invoke-virtual {p0}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;
    move-result-object v0
    
    # Check ADB enabled (Settings.Global.ADB_ENABLED)
    const-string v1, "adb_enabled"
    const/4 v2, 0x0
    invoke-static {v0, v1, v2}, Landroid/provider/Settings$Global;->getInt(Landroid/content/ContentResolver;Ljava/lang/String;I)I
    move-result v3
    
    const/4 v4, 0x1
    if-ne v3, v4, :check_dev_settings
    const/4 v0, 0x1
    return v0
    
    :check_dev_settings
    # Check development_settings_enabled
    const-string v1, "development_settings_enabled"
    invoke-static {v0, v1, v2}, Landroid/provider/Settings$Global;->getInt(Landroid/content/ContentResolver;Ljava/lang/String;I)I
    move-result v3
    
    if-ne v3, v4, :not_enabled
    const/4 v0, 0x1
    return v0
    :try_end
    
    .catch Ljava/lang/Exception; {:try_start .. :try_end} :catch_ex
    
    :catch_ex
    :not_enabled
    const/4 v0, 0x0
    return v0
.end method