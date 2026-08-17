# Xiaomi Blossom (Redmi 9A / 9C / 9 Activ) Overlays, Configs & Complete Porting Kit

A complete, production-ready, **anti-brick guaranteed** repository containing extracted & compiled display overlays, decompiled XML trees, vendor libraries, MediaTek shims, SELinux policies, init/fstab scripts, backend automation tools, **AI Porting Diagnostics Assistant**, **Pre-Flash Safety Guard**, **GitHub Actions Cloud Auto-Porter Workflow**, and comprehensive guides for **Xiaomi Blossom** (`dandelion`, `angelica`, `angelican`, `cattail` — MediaTek MT6762G, MT6765, MT6765G).

Designed for **GSI (Generic System Image) Porters**, **MIUI / HyperOS Porters**, **DnA Android Kitchen Porters**, **AOSP / Custom ROM Developers**, and **Treble Maintainers**.

> 🛡️ **100% Anti-Brick & Safe Architecture:**  
> Our porting engine and flasher scripts strictly isolate and protect all bootloader (`preloader`, `lk`) and IMEI/NVRAM partitions (`nvram`, `nvdata`, `proinfo`, `tee`). Read the full **[Emergency Unbrick & Safety Manual (EMERGENCY_UNBRICK_GUIDE.md)](EMERGENCY_UNBRICK_GUIDE.md)**!

> 🚀 **Automate Everything on GitHub Actions:**  
> Want to port any ROM in the cloud without downloading gigabytes of files locally?  
> Use our **[GitHub Actions Auto-Port Workflow](#-cloud-auto-port-github-actions-workflow)**! Paste any Port ROM URL -> Click Run -> Real-time AI logs diagnostic -> Download your ready-to-flash Blossom ROM from GitHub Releases & Mirrors!

---

## 📱 Device Specifications & Target Models

| Parameter | Specification |
|---|---|
| **Codename** | `blossom` (`dandelion`, `angelica`, `angelican`, `cattail`) |
| **Target Devices** | Xiaomi Redmi 9A, Redmi 9C, Redmi 9 Activ, Redmi 9 India, Poco C3 |
| **Platform / SoC** | MediaTek Helio G25 / G35 (MT6762G / MT6765 / MT6765G) |
| **Architecture** | ARM64 (`arm64-v8a`) |
| **Display Resolution** | 720 x 1600 (HD+ 20:9 Aspect Ratio) |
| **Display Cutout Notch** | Waterdrop Notch (`M 0,0 H -64 V 60 H 64 V 0 H 0 Z`) |
| **Status Bar Height** | `56.0px` (Portrait), `24.0dp` (Landscape) |
| **Rounded Corners Radius** | `33dp` |
| **Treble Architecture** | System-as-Root (SAR), VNDK 30/31/32, Dynamic Partitions (VAB/Retrofit) |

---

## 🛡️ Anti-Brick & Protected Partition Architecture

| Protected Partition | Function | Protection Status |
|---|---|---|
| **`preloader`** | Primary SoC Bootloader | 🔒 **100% Protected** (Never touched / zero brick risk) |
| **`lk` / `lk2`** | LittleKernel Fastboot Bootloader | 🔒 **100% Protected** (Guarantees Fastboot access) |
| **`nvram` / `nvdata`** | Hardware IMEI, Baseband, Wi-Fi MAC | 🔒 **100% Protected** (Prevents baseband/network loss) |
| **`tee1` / `tee2`** | TrustZone & Hardware Security | 🔒 **100% Protected** |
| **`md1img` / `md1dsp`** | Cellular Modem DSP Firmware | 🔒 **100% Protected** |

---

## 🚀 Cloud Auto-Port (GitHub Actions Workflow)

You can automatically port any ROM directly in GitHub Cloud using our automated workflow ([`.github/workflows/auto_port.yml`](.github/workflows/auto_port.yml)):

```mermaid
graph LR
    A[Enter Port ROM URL in GitHub] --> B[GitHub Actions Cloud Runner]
    B --> C[Fast Multi-threaded Download aria2c]
    C --> D[Extract payload.bin / super.img]
    D --> E[Auto-Patcher: Overlays, Shims, AVB Bypass]
    E --> F[Anti-Brick Safety Guard Verification]
    F --> G[AI Assistant: Real-time Diagnostics]
    G --> H[Package Flashable ZIP + SHA256]
    H --> I[Upload to GitHub Releases & Multi-Mirrors]
```

### How to Run the Cloud Auto-Porter:
1. Go to your GitHub Repository: **`https://github.com/frnAlt/Xiaomi_blossom_stuff`**
2. Click on the **Actions** tab at the top.
3. In the left sidebar, click **"🚀 Automatic ROM Porter for Xiaomi Blossom"**.
4. Click the **"Run workflow"** button on the right.
5. Fill in the input fields:
   - **Port ROM URL**: Direct download link of the target ROM (e.g. HyperOS from Redmi Note 11, PixelOS, OneUI, etc.).
   - **Base ROM URL** *(Optional)*: Direct link to stock Blossom Fastboot ROM (leave empty to use repository stock templates).
   - **Target Variant**: Select `blossom` (All models), `dandelion` (9A), `angelica` (9C), or `cattail` (9 Activ).
   - **ROM Name / Type**: Enter name (e.g. `HyperOS`, `MIUI14`, `PixelOS`).
   - **Custom Upload URL** *(Optional)*: Enter a custom server URL or `https://transfer.sh/` to upload the finished build.
6. Click **"Run workflow"**.
7. The workflow automatically produces:
   - **GitHub Release** with flashable ZIPs, SHA256 checksums, and flashing scripts (`flash_all.bat` / `flash_all.sh`).
   - **Anti-Brick Safety Audit Report**.
   - **AI Diagnostic Report** in the workflow summary.
   - **Multi-mirror links** (Pixeldrain, Transfer.sh, Custom endpoint).
   - **Complete build logs and diagnostics artifacts**.

---

## 📁 Repository Structure

```text
├── .github/workflows/
│   └── auto_port.yml                     # 🚀 GitHub Actions Cloud Auto-Porter Workflow (with AI Diagnostics)
│
├── tools/                                # ⚙️ Backend Automation & CLI Porting Suite
│   ├── unbrick_safety_guard.py           # 🛡️ Anti-Brick Safety Guard & Pre-Flash Validator
│   ├── ai_assistant.py                   # 🤖 AI Diagnostics & Error Root-Cause Analyzer (Offline + Gemini API)
│   ├── auto_patcher.py                   # 🛠️ Automated Patcher (Fstab Encryption Bypass, AVB Verity, Audio)
│   ├── auto_porter.py                    # ⚡ End-to-End CLI Porter (Download -> Extract -> Merge -> Package)
│   ├── port_helper.py                    # 🔧 ROM Injection Engine (Overlays, Shims, Props, Carrier)
│   ├── super_tools.py                    # 🧩 Dynamic Super Partition Engine (lpmake, AVB flags, Flasher scripts)
│   ├── multi_uploader.py                 # 🌐 Multi-Mirror Cloud Uploader (Pixeldrain, Transfer.sh, Custom)
│   ├── build_overlays.py                 # 🔨 RRO Compiler & Signer (aapt + apksigner)
│   ├── create_magisk_module.py           # 📦 Flashable Magisk/KernelSU ZIP Packager
│   └── verify_tree.py                    # 🔍 Tree Integrity & Port Diagnostic Validator
│
├── EMERGENCY_UNBRICK_GUIDE.md            # 🚑 Emergency Unbrick & MTKClient Recovery Manual
├── DNA_KITCHEN_PORTING_GUIDE.md          # 🍳 Complete Guide for Porting with DnA Kitchen (Base -> Port)
├── PORTING_GUIDE.md                      # 📖 Standalone Comprehensive Porting Manual
├── Blossom_Notch_Fix_Magisk.zip          # ⚡ Ready-to-flash Magisk / KernelSU Notch Fix Module
│
├── apks/                                 # 📦 Compiled, Zipaligned, and Signed Overlay APKs
├── extracted_display_overlay_xml/        # 🎯 Decompiled & Extracted XMLs from display_overlay.apk
├── xmls/                                 # 🛠️ Audio, Media, Thermal, Carrier & VINTF XMLs
├── port_libs_and_shims/                  # ⚙️ Essential Porting Libraries & Shims
├── rootdir/                              # 📜 Init scripts (init.mt6765.rc, init.mt6762.rc) & fstabs
├── sepolicy/                             # 🔒 SELinux policies (vendor & private)
├── props/                                # ⚙️ Props (system.prop, vendor.prop, product.prop, odm.prop)
└── build_makefiles/                      # 🏗️ BoardConfig.mk, device.mk, patches, extract-files.sh
```

---

## ⚙️ Backend Automation CLI Tools

Run all porting, patching, safety audit, AI diagnostic, and packaging tasks locally:

### 1. Pre-Flash Anti-Brick Safety Guard (`tools/unbrick_safety_guard.py`)
Scans any ROM package or script to ensure no dangerous bootloader or IMEI partitions are targeted:
```bash
python3 tools/unbrick_safety_guard.py --rom-zip Blossom_Port_HyperOS_dandelion.zip
```

### 2. AI Porting Assistant & Diagnostic Engine (`tools/ai_assistant.py`)
Analyzes build logs, extraction errors, or bootloop logcats and outputs exact root causes and fixes:
```bash
python3 tools/ai_assistant.py --log-file /path/to/bootlog_or_build.log
```

### 3. Automated Hardware & Framework Patcher (`tools/auto_patcher.py`)
Bypasses forced encryption in fstabs, disables dm-verity panics, and configures MediaTek shims:
```bash
python3 tools/auto_patcher.py --port-dir /path/to/extracted_port_rom
```

### 4. End-to-End Automated ROM Porter (`tools/auto_porter.py`)
Downloads, unpacks `payload.bin`/`super.img`, merges Base + Port partitions, injects fixes, and packages a flashable ZIP:
```bash
python3 tools/auto_porter.py \
  --port-url "https://example.com/hyperos_port.zip" \
  --variant dandelion \
  --rom-type HyperOS
```

### 5. Dynamic Super Partition & Flasher Generator (`tools/super_tools.py`)
Patches `vbmeta.img` flags and builds cross-platform fastboot flashing scripts (`flash_all.bat` & `flash_all.sh`):
```bash
python3 tools/super_tools.py --patch-vbmeta vbmeta.img --gen-scripts ./output_folder
```

### 6. Multi-Mirror Uploader (`tools/multi_uploader.py`)
Uploads built ROMs to high-speed cloud mirrors (Pixeldrain, Transfer.sh, Custom URL):
```bash
python3 tools/multi_uploader.py --file Blossom_Port_HyperOS_dandelion.zip
```

---

## 🗺️ Master File-to-Destination Mapping Table

| Source File / Folder in this Repository | Destination in MIUI / HyperOS Port | Destination in AOSP / Custom ROM Tree | Destination in Treble GSI |
|---|---|---|---|
| **`apks/display_overlay.apk`** | `/product/overlay/display_overlay.apk` | N/A (Builds from source) | `/system/product/overlay/display_overlay.apk` |
| **`apks/FrameworksResOverlayBlossom.apk`** | `/vendor/overlay/FrameworksResOverlayBlossom.apk` | `PRODUCT_PACKAGES += FrameworksResOverlayBlossom` | `/vendor/overlay/FrameworksResOverlayBlossom.apk` |
| **`apks/SystemUIOverlayBlossom.apk`** | `/vendor/overlay/SystemUIOverlayBlossom.apk` | `PRODUCT_PACKAGES += SystemUIOverlayBlossom` | `/vendor/overlay/SystemUIOverlayBlossom.apk` |
| **`apks/CarrierConfigOverlayBlossom.apk`** | `/vendor/overlay/CarrierConfigOverlayBlossom.apk` | `PRODUCT_PACKAGES += CarrierConfigOverlayBlossom` | `/vendor/overlay/CarrierConfigOverlayBlossom.apk` |
| **`apks/treble_gsi/treble-overlay-xiaomi-blossom.apk`** | N/A | N/A | `/system/product/overlay/treble-overlay-xiaomi-blossom.apk` |
| **`extracted_display_overlay_xml/display_cutout_notch.xml`** | Decompile `framework-res.apk` -> Inject into `res/values/config.xml` & `dimens.xml` | `overlay/frameworks/base/core/res/res/values/config.xml` | Overlaid via GSI overlay APK |
| **`xmls/carrier/vendor_miui.xml`** | `/vendor/etc/carrier/vendor_miui.xml` | `rro_overlays/CarrierConfigOverlayBlossom/res/xml/` | `/vendor/etc/carrier/vendor_miui.xml` |
| **`xmls/audio/*.xml`** | `/vendor/etc/audio/` & `/vendor/etc/audio_policy_configuration.xml` | `device/xiaomi/blossom/configs/audio/` | Stock vendor retains this |
| **`xmls/media/*.xml`** | `/vendor/etc/media_codecs*.xml` & `/vendor/etc/media_profiles_V1_0.xml` | `device/xiaomi/blossom/configs/media/` | Stock vendor retains this |
| **`xmls/power/power_profile.xml`** | `framework-res.apk` -> `res/xml/power_profile.xml` | `overlay/frameworks/base/core/res/res/xml/power_profile.xml` | Overlaid via framework-res overlay |
| **`xmls/power/powerhint.json`** | `/vendor/etc/powerhint.json` | `device/xiaomi/blossom/configs/powerhint.json` | `/vendor/etc/powerhint.json` |
| **`xmls/thermal/thermal_info_config.json`** | `/vendor/etc/thermal_info_config.json` | `device/xiaomi/blossom/configs/thermal/` | `/vendor/etc/thermal_info_config.json` |
| **`port_libs_and_shims/vndk/libui-v32.so`** | `/system/lib64/vndk-v32/libui.so` | `device/xiaomi/blossom/vndk/libui-v32.so` | Handled by VNDK APEX |
| **`port_libs_and_shims/libshims/`** | `/system/lib64/libshim_*.so` or `/vendor/lib64/` | `device/xiaomi/blossom/libshims/` | Injected into `/system/lib64/` if needed |
| **`port_libs_and_shims/lights/`** | `/vendor/bin/hw/android.hardware.light-service.blossom` | `device/xiaomi/blossom/lights/` | Stock vendor service |
| **`port_libs_and_shims/init/init_blossom.cpp`** | N/A (Build props) | `device/xiaomi/blossom/init/init_blossom.cpp` | N/A |
| **`rootdir/etc/*`** | `/vendor/etc/init/hw/*` | `device/xiaomi/blossom/rootdir/etc/*` | Stock vendor ramdisk / vendor |
| **`sepolicy/*`** | Merged into `/vendor/etc/selinux/` | `device/xiaomi/blossom/sepolicy/` | Stock vendor sepolicy |
| **`props/*.prop`** | Append to `/system/build.prop` & `/vendor/build.prop` | Included via `system.prop` in device tree | Append to `system.prop` |

---

## ⚡ Complete Treble GSI Porting & Usage Guide

If you are running or installing a **Generic System Image (GSI)** (such as Phh AOSP, PixelExperience GSI, crDroid GSI, LineageOS GSI, EvolutionX GSI, etc.) on Xiaomi Blossom:

### A. Flashing a GSI via Fastboot
1. Download an **`arm64_bvN`** or **`arm64_bgN`** (ARM64 A/B) GSI image.
2. Reboot phone to FastbootD mode:
   ```bash
   adb reboot fastboot
   ```
3. Flash the GSI system image:
   ```bash
   fastboot erase system
   fastboot flash system <gsi_image_name>.img
   fastboot -w
   fastboot reboot
   ```

### B. Installing the Notch & Display Overlay Fix on GSI
Simply flash the prebuilt [`Blossom_Notch_Fix_Magisk.zip`](Blossom_Notch_Fix_Magisk.zip) directly in the Magisk or KernelSU app and reboot!

---

## 🔧 Troubleshooting Common Blossom Porting Bugs

| Symptom / Bug | Root Cause | Fix / Solution |
|---|---|---|
| **Status bar icons overlap under notch** | Missing `config_mainBuiltInDisplayCutout` or wrong statusbar height. | Install `DisplayOverlayBlossom.apk` or inject SVG path `M 0,0 H -64 V 60 H 64 V 0 H 0 Z` and set status bar height to `56px`. |
| **Brightness slider has no effect or jumps** | Missing lux-to-nits spline interpolation arrays on MTK panel. | Apply [`extracted_display_overlay_xml/brightness_arrays.xml`](extracted_display_overlay_xml/brightness_arrays.xml) into framework-res. |
| **Camera app crashes on launch** | Missing `GraphicBufferMapper` symbol in MTK camera HAL. | Add `port_libs_and_shims/libshims/libshim_ui` to the build or vendor libs. |
| **No In-Call Audio / Bluetooth Headset Audio** | MTK Aurisys DSP parameter mismatch. | Use `xmls/audio/aurisys_config.xml` and `xmls/audio/audio_policy_configuration.xml`. |
| **Fingerprint settings missing or crashing on 9A** | Redmi 9A (`dandelion`) lacks fingerprint hardware; ROM tried loading biometric HAL. | Use `port_libs_and_shims/init/init_blossom.cpp` to dynamically disable fingerprint props on `dandelion`. |

---

## 🎯 Display Cutout Technical Reference

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Waterdrop Notch Path for Xiaomi Redmi 9A / 9C / 9 Activ -->
<resources>
    <string translatable="false" name="config_mainBuiltInDisplayCutout">M 0,0 H -64 V 60 H 64 V 0 H 0 Z</string>
    <bool name="config_fillMainBuiltInDisplayCutout">true</bool>
    <dimen name="status_bar_height_default">56.0px</dimen>
    <dimen name="status_bar_height_portrait">56.0px</dimen>
    <dimen name="status_bar_height_landscape">24.0dp</dimen>
    <dimen name="rounded_corner_radius">33dp</dimen>
</resources>
```

---

## 📄 License & Credits
- Xiaomi Blossom Device Tree maintained by [crDroid Android](https://github.com/crdroidandroid) & [LineageOS](https://github.com/LineageOS).
- DnA Android Kitchen by the DnA Developer Team.
- Apache 2.0 License.
