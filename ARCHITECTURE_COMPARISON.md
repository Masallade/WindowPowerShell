# WindowSupport - Architecture Comparison

## 🏗️ Three-Layer Protection Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Layer 3: Guardian (Optional)                    │
│         Windows Service or Scheduled Task (SYSTEM)          │
│    • Monitors main EXE every 30 seconds                     │
│    • Restarts if stopped                                    │
│    • System-level protection                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ monitors
                       ↓
┌─────────────────────────────────────────────────────────────┐
│        Layer 2: Scheduled Task (Per-User, Auto-Restart)     │
│              Created by WindowPowerShellProvider             │
│    • Auto-starts at user login                              │
│    • Restarts 999 times if crashed (1-min interval)         │
│    • Hidden, high priority                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ starts
                       ↓
┌─────────────────────────────────────────────────────────────┐
│       Layer 1: WindowPowerShellProvider.exe (Main App)      │
│                 Runs in user session                         │
│    • Internal watchdog thread (restarts if stalled)         │
│    • Health checks every 10 iterations                      │
│    • Auto-restart on 5 consecutive errors                   │
│    • Captures screenshots                                   │
│    • Sends to API                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ monitors
                       ↓
                  User Activity
```

---

## 📊 Comparison: With vs Without Guardian

### **Setup 1: WITHOUT Guardian (Current)**

```
User Login
   ↓
Scheduled Task starts WindowPowerShellProvider.exe
   ↓
Main EXE runs (with internal watchdog)
   ↓
If crashed: Scheduled Task auto-restarts (1 min delay)
```

**Protection:**
- ✅ Internal watchdog thread
- ✅ Auto-restart via scheduled task (999 times)
- ✅ Health checks
- ❌ If scheduled task disabled: NO PROTECTION

**Reliability:** ~95%

---

### **Setup 2: WITH Guardian (Recommended)**

```
Windows Boot
   ↓
Guardian Service/Task starts (SYSTEM level)
   ↓
User Login
   ↓
Scheduled Task starts WindowPowerShellProvider.exe
   ↓
Main EXE runs (with internal watchdog)
   ↓
Guardian monitors every 30 seconds
   ↓
If main EXE stops: Guardian restarts it
   ↓
If scheduled task disabled: Guardian still works
```

**Protection:**
- ✅ Internal watchdog thread
- ✅ Auto-restart via scheduled task (999 times)
- ✅ Health checks
- ✅ Guardian monitoring (independent)
- ✅ Works even if scheduled task disabled

**Reliability:** ~99.5%

---

## 🎯 What Each Layer Protects Against

| Failure Scenario | Layer 1 (Main) | Layer 2 (Task) | Layer 3 (Guardian) |
|------------------|----------------|----------------|-------------------|
| **Application crash** | ✅ Restarts self | ✅ Restarts (1 min) | ✅ Restarts (30 sec) |
| **Main loop stall** | ✅ Watchdog detects | ❌ | ✅ Detects & restarts |
| **Out of memory** | ✅ Health check | ✅ Restarts | ✅ Restarts |
| **Network issues** | ✅ Retries | ❌ | ❌ |
| **Manual kill (Task Manager)** | ❌ | ✅ Auto-restarts | ✅ Detects & restarts |
| **Scheduled task disabled** | ❌ | ❌ | ✅ Still works |
| **Antivirus quarantine** | ❌ | ❌ | ❌ (needs exclusions) |
| **Windows Update** | ❌ | ✅ Restarts after | ✅ Restarts after |

---

## 🔄 Restart Flow Examples

### **Scenario 1: Application Crashes**

**Without Guardian:**
```
1. App crashes
2. Wait 1 minute (scheduled task interval)
3. Scheduled task detects failure
4. Restarts app
Total downtime: ~1 minute
```

**With Guardian:**
```
1. App crashes
2. Wait up to 30 seconds (guardian check interval)
3. Guardian detects and restarts immediately
Total downtime: ~30 seconds
```

---

### **Scenario 2: User Kills Process Manually**

**Without Guardian:**
```
1. User kills via Task Manager
2. Wait 1 minute
3. Scheduled task restarts
Total downtime: ~1 minute
```

**With Guardian:**
```
1. User kills via Task Manager
2. Guardian detects within 30 seconds
3. Guardian triggers scheduled task OR starts directly
Total downtime: ~30 seconds
```

---

### **Scenario 3: Scheduled Task Disabled by Admin**

**Without Guardian:**
```
1. Admin disables scheduled task
2. App crashes
3. NO RESTART - app stays down
Total downtime: PERMANENT until manual intervention
```

**With Guardian:**
```
1. Admin disables scheduled task
2. App crashes
3. Guardian detects and starts directly
Total downtime: ~30 seconds
```

---

## 💡 When to Use Each Setup

### **Use WITHOUT Guardian if:**
- ✅ Simple deployment (1-2 users)
- ✅ Non-critical monitoring
- ✅ Can tolerate 1-minute downtime
- ✅ No system-level access available

### **Use WITH Guardian if:**
- ✅ Critical monitoring (many users)
- ✅ Need maximum uptime (99%+)
- ✅ Want protection against task scheduler issues
- ✅ Have system admin access
- ✅ Enterprise deployment

---

## 📈 Reliability Comparison

### **Without Guardian:**
```
Uptime: ~95-97%
MTTR (Mean Time To Recovery): 1-2 minutes
Single Point of Failure: Scheduled Task
```

### **With Guardian (Python Service):**
```
Uptime: ~99.5-99.9%
MTTR (Mean Time To Recovery): 30-60 seconds
Redundant Protection: Multiple layers
```

### **With Guardian (Batch File):**
```
Uptime: ~98-99%
MTTR (Mean Time To Recovery): 30-90 seconds
Redundant Protection: Multiple layers
```

---

## 🔐 Security Considerations

### **Scheduled Task (Layer 2):**
- Runs as current user
- User-level permissions
- Per-user isolation
- Can't monitor other users

### **Guardian Service (Layer 3 - Python):**
- Runs as SYSTEM
- System-level permissions
- Can monitor all users
- More powerful but more risk

### **Guardian Task (Layer 3 - Batch):**
- Runs as SYSTEM
- System-level permissions
- Simpler, less attack surface

---

## 💰 Resource Usage

### **Main App Alone:**
```
CPU: ~1-3% (idle), 5-10% (screenshot)
Memory: ~50-150 MB
Disk: ~5 MB logs (rotated)
Network: Minimal (API calls only)
```

### **+ Guardian Service:**
```
Additional CPU: ~0.5%
Additional Memory: ~10-20 MB
Total overhead: <1% system resources
```

### **+ Guardian Batch:**
```
Additional CPU: ~0.1%
Additional Memory: ~5 MB
Total overhead: <0.5% system resources
```

---

## 🎓 Best Practices

### **For Testing/Development:**
1. Start with main app only (no guardian)
2. Test scheduled task auto-restart
3. Monitor logs for issues
4. Add guardian if needed

### **For Production:**
1. Deploy main app with scheduled task
2. Add guardian (service or batch)
3. Configure antivirus exclusions
4. Monitor via Event Logs
5. Set up alerting for failures

### **For Enterprise:**
1. Use Python Service guardian
2. Deploy via GPO (Group Policy)
3. Centralized logging
4. Monitoring dashboard
5. Automated deployment scripts

---

## 📋 Quick Setup Guide

### **Minimal Setup (Good for most users):**
```powershell
1. Deploy WindowPowerShellProvider.exe
2. Run once to create scheduled task
3. Add antivirus exclusions
4. Done!
```

### **Maximum Protection Setup (Recommended):**
```powershell
1. Deploy WindowPowerShellProvider.exe
2. Run once to create scheduled task
3. Add antivirus exclusions
4. Install Guardian (Python Service OR Batch File)
5. Test by killing main process
6. Verify auto-restart
7. Done!
```

---

## 🚀 Deployment Order

**Correct order:**
1. ✅ Main app (WindowPowerShellProvider.exe)
2. ✅ Run to create scheduled task
3. ✅ Set staff_id (get_your_staff_id.py)
4. ✅ Add antivirus exclusions
5. ✅ Install Guardian (optional but recommended)
6. ✅ Test everything

**Don't:**
- ❌ Install guardian before main app
- ❌ Skip antivirus exclusions
- ❌ Forget to set staff_id
- ❌ Deploy without testing

---

**Conclusion:** The Guardian is an optional but highly valuable addition that provides enterprise-grade reliability. Choose based on your uptime requirements and available resources.

---

**Version:** 1.0  
**Last Updated:** 2025-10-21



