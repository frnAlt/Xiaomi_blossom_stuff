# 🚑 Xiaomi Blossom (Redmi 9A / 9C / 9 Activ) Anti-Brick & Emergency Unbrick Guide

This safety manual explains the **hardware protection architecture** of Xiaomi Blossom (MediaTek MT6762G / MT6765 / MT6765G), how to guarantee **zero brick risk**, and how to recover from any softbrick or bootloop.

---

## 🛡️ 1. Anti-Brick Safety Architecture

### Critical Protected Partitions (NEVER Overwritten in Our Ports)
Our porting engine, flasher scripts, and GitHub Actions workflow strictly isolate and protect these partitions:

| Protected Partition | Function | Protection Status in Our Kit |
|---|---|---|
| **`preloader`** | Primary Bootloader (ROM Bootloader in MTK SoC) | 🔒 **100% Protected** (Never touched) |
| **`lk` / `lk2`** | LittleKernel Bootloader (Provides Fastboot mode) | 🔒 **100% Protected** (Never touched) |
| **`nvram` / `nvdata`** | Hardware IMEI, Baseband calibration & MAC address | 🔒 **100% Protected** (Never touched) |
| **`proinfo` / `nvcfg`** | Serial number & factory device provisioning | 🔒 **100% Protected** (Never touched) |
| **`tee1` / `tee2`** | TrustZone & Secure OS | 🔒 **100% Protected** (Never touched) |
| **`spmfw` / `sspm`** | System Power Management firmware | 🔒 **100% Protected** (Never touched) |
| **`md1img` / `md1dsp`** | Cellular Modem Baseband DSP firmware | 🔒 **100% Protected** (Never touched) |

> 💡 **Why this guarantees safety:** As long as `preloader` and `lk` remain intact, a MediaTek phone **CANNOT be hard-bricked**. You can always access Fastboot, Recovery, or BROM mode to restore your system.

---

## 🧯 2. Emergency Recovery Methods

### Method 1: Recovery via Fastboot (Phone can enter Fastboot mode)
If your phone is stuck in a bootloop or boots to Fastboot mode (Hold **Power + Volume Down**):

1. **Reflash Stock Kernel & Clean VBMeta**:
   ```bash
   fastboot flash boot boot.img
   fastboot flash dtbo dtbo.img
   fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img
   fastboot reboot
   ```
2. **Reboot to FastbootD & Reflash Super**:
   ```bash
   fastboot reboot fastboot
   fastboot flash super super.img
   fastboot -w
   fastboot reboot
   ```

---

### Method 2: Emergency Unbrick via MTKClient (Black Screen / BROM Mode)
If your phone won't turn on or bootloops before reaching Fastboot, you can use the open-source **`mtkclient`** tool (works on Linux, Windows, macOS without authorized Mi Account):

#### Step 1: Install MTKClient on PC
```bash
git clone https://github.com/bkerler/mtkclient.git
cd mtkclient
pip3 install -r requirements.txt
```

#### Step 2: Connect Phone in BROM Mode
1. Turn off phone completely.
2. Hold **Volume Up + Volume Down** buttons together and plug in the USB cable to PC.
3. `mtkclient` will detect the MediaTek MT6765/MT6762 SoC and bypass the SLA/DA auth.

#### Step 3: Flash Kernel or Unbrick
```bash
# Read / Backup NVRAM & IMEI (Recommended safety step)
python3 mtk r nvram,nvdata nvram.img,nvdata.img

# Write clean stock boot and vbmeta
python3 mtk w boot boot.img
python3 mtk w vbmeta vbmeta.img

# Wipe cache and metadata
python3 mtk e metadata,userdata

# Reboot phone
python3 mtk reset
```

---

## 💾 3. Backing Up Your IMEI & NVRAM (Recommended Best Practice)

Before flashing experimental ports, backup your IMEI and calibration data:

### Via TWRP / OrangeFox Recovery:
1. Boot into TWRP / OrangeFox.
2. Tap **Backup** -> Select **NVRAM** and **NVDATA** partitions.
3. Swipe to backup to MicroSD card or PC via USB OTG.

### Via ADB Root:
```bash
adb root
adb shell "dd if=/dev/block/by-name/nvram of=/sdcard/nvram_backup.img"
adb shell "dd if=/dev/block/by-name/nvdata of=/sdcard/nvdata_backup.img"
adb pull /sdcard/nvram_backup.img ./
adb pull /sdcard/nvdata_backup.img ./
```

---

## 🔍 4. Pre-Flash Anti-Brick Safety Guard Tool

You can verify any ROM package or script before flashing using our built-in safety auditor ([`tools/unbrick_safety_guard.py`](tools/unbrick_safety_guard.py)):

```bash
# Audit a ROM package for dangerous partition files
python3 tools/unbrick_safety_guard.py --rom-zip MyPortedROM.zip

# Audit a flashing script
python3 tools/unbrick_safety_guard.py --script flash_all.sh
```

---

## 📄 License & Credits
- Xiaomi Blossom Safety Architecture maintained by [crDroid Android](https://github.com/crdroidandroid) & [LineageOS](https://github.com/LineageOS).
- MTKClient by B. Kerler (`bkerler`).
- Apache 2.0 License.
