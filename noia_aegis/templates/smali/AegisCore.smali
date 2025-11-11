.class public Lcom/noiaegis/AegisCore;
.super Ljava/lang/Object;

.method public static protect(Landroid/content/Context;)V
    .locals 3

    # Check root
    invoke-static {}, Lcom/noiaegis/RootShield;->isRooted()Z
    move-result v0
    
    if-eqz v0, :check_emulator
    
    const-string v1, "🔓 Root detected!"
    const/4 v2, 0x1
    invoke-static {p0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v1
    invoke-virtual {v1}, Landroid/widget/Toast;->show()V
    
    const/4 v0, 0x0
    invoke-static {v0}, Ljava/lang/System;->exit(I)V
    
    :check_emulator
    invoke-static {}, Lcom/noiaegis/EmulatorShield;->isEmulator()Z
    move-result v0
    
    if-eqz v0, :check_debug
    
    const-string v1, "🖥️ Emulator detected!"
    const/4 v2, 0x1
    invoke-static {p0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v1
    invoke-virtual {v1}, Landroid/widget/Toast;->show()V
    
    const/4 v0, 0x0
    invoke-static {v0}, Ljava/lang/System;->exit(I)V
    
    :check_debug
    invoke-static {}, Lcom/noiaegis/DebugShield;->isDebuggable()Z
    move-result v0
    
    if-eqz v0, :protected
    
    const-string v1, "🐛 Debug mode detected!"
    const/4 v2, 0x1
    invoke-static {p0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v1
    invoke-virtual {v1}, Landroid/widget/Toast;->show()V
    
    const/4 v0, 0x0
    invoke-static {v0}, Ljava/lang/System;->exit(I)V
    
    :protected
    return-void
.end method