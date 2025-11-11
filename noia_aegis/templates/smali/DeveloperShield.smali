.class public Lcom/noiaegis/DeveloperShield;
.super Ljava/lang/Object;

# Check if developer options or USB debugging enabled
.method public static isDeveloperMode(Landroid/content/Context;)Z
    .locals 5

    :try_start
    invoke-virtual {p0}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;
    move-result-object v0
    
    # Check ADB enabled
    const-string v1, "adb_enabled"
    const/4 v2, 0x0
    invoke-static {v0, v1, v2}, Landroid/provider/Settings$Global;->getInt(Landroid/content/ContentResolver;Ljava/lang/String;I)I
    move-result v3
    
    const/4 v4, 0x1
    if-ne v3, v4, :check_dev_settings
    const/4 v0, 0x1
    return v0
    
    :check_dev_settings
    # Check development settings enabled
    const-string v1, "development_settings_enabled"
    invoke-static {v0, v1, v2}, Landroid/provider/Settings$Global;->getInt(Landroid/content/ContentResolver;Ljava/lang/String;I)I
    move-result v3
    
    if-ne v3, v4, :check_stay_awake
    const/4 v0, 0x1
    return v0
    
    :check_stay_awake
    # Check stay awake while charging
    const-string v1, "stay_on_while_plugged_in"
    invoke-static {v0, v1, v2}, Landroid/provider/Settings$Global;->getInt(Landroid/content/ContentResolver;Ljava/lang/String;I)I
    move-result v3
    
    if-eqz v3, :not_dev_mode
    const/4 v0, 0x1
    return v0
    :try_end
    
    .catch Ljava/lang/Exception; {:try_start .. :try_end} :catch_ex
    
    :catch_ex
    :not_dev_mode
    const/4 v0, 0x0
    return v0
.end method