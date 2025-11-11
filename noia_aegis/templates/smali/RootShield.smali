.class public Lcom/noiaegis/RootShield;
.super Ljava/lang/Object;

.method public static isRooted()Z
    .locals 2

    # Check /system/bin/su
    const-string v0, "/system/bin/su"
    invoke-static {v0}, Lcom/noiaegis/RootShield;->fileExists(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :check_xbin
    const/4 v0, 0x1
    return v0
    
    :check_xbin
    const-string v0, "/system/xbin/su"
    invoke-static {v0}, Lcom/noiaegis/RootShield;->fileExists(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :check_sbin
    const/4 v0, 0x1
    return v0
    
    :check_sbin
    const-string v0, "/sbin/su"
    invoke-static {v0}, Lcom/noiaegis/RootShield;->fileExists(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :check_magisk
    const/4 v0, 0x1
    return v0
    
    :check_magisk
    const-string v0, "/system/app/Magisk"
    invoke-static {v0}, Lcom/noiaegis/RootShield;->fileExists(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :not_rooted
    const/4 v0, 0x1
    return v0
    
    :not_rooted
    const/4 v0, 0x0
    return v0
.end method

.method private static fileExists(Ljava/lang/String;)Z
    .locals 2

    :try_start
    new-instance v0, Ljava/io/File;
    invoke-direct {v0, p0}, Ljava/io/File;-><init>(Ljava/lang/String;)V
    invoke-virtual {v0}, Ljava/io/File;->exists()Z
    move-result v1
    return v1
    :try_end
    
    .catch Ljava/lang/Exception; {:try_start .. :try_end} :catch_ex
    
    :catch_ex
    const/4 v0, 0x0
    return v0
.end method