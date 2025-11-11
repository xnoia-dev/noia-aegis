.class public Lcom/noiaegis/EmulatorShield;
.super Ljava/lang/Object;

.method public static isEmulator()Z
    .locals 3

    # Check Build.FINGERPRINT
    sget-object v0, Landroid/os/Build;->FINGERPRINT:Ljava/lang/String;
    const-string v1, "generic"
    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v2
    if-eqz v2, :check_model
    const/4 v0, 0x1
    return v0
    
    :check_model
    sget-object v0, Landroid/os/Build;->MODEL:Ljava/lang/String;
    const-string v1, "sdk"
    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v2
    if-eqz v2, :check_brand
    const/4 v0, 0x1
    return v0
    
    :check_brand
    sget-object v0, Landroid/os/Build;->BRAND:Ljava/lang/String;
    const-string v1, "generic"
    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v2
    if-eqz v2, :check_hardware
    const/4 v0, 0x1
    return v0
    
    :check_hardware
    sget-object v0, Landroid/os/Build;->HARDWARE:Ljava/lang/String;
    const-string v1, "goldfish"
    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v2
    if-eqz v2, :not_emulator
    const/4 v0, 0x1
    return v0
    
    :not_emulator
    const/4 v0, 0x0
    return v0
.end method