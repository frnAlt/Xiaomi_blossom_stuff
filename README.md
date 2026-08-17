# Xiaomi Blossom (Redmi 9A / 9C / 9 Activ) Overlays, Configs, and Porting Kit

A production-ready repository containing extracted and compiled display overlays, decompiled XML trees, vendor libraries, MediaTek shims, SELinux policies, init/fstab scripts, backend automation tools, AI Porting Diagnostics Assistant, Pre-Flash Safety Guard, GitHub Actions Cloud Auto-Porter Workflow, and porting documentation for Xiaomi Blossom (`dandelion`, `angelica`, `angelican`, `cattail` — MediaTek MT6762G, MT6765, MT6765G).

Target platforms: Generic System Images (GSI), MIUI / HyperOS ports, DnA Android Kitchen workflows, AOSP / Custom ROM trees, and Treble environments.

---

## Device Specifications

| Parameter | Specification |
|---|---|
| Codename | `blossom` (`dandelion`, `angelica`, `angelican`, `cattail`) |
| Target Devices | Xiaomi Redmi 9A, Redmi 9C, Redmi 9 Activ, Redmi 9 India, Poco C3 |
| Platform / SoC | MediaTek Helio G25 / G35 (MT6762G / MT6765 / MT6765G) |
| Architecture | ARM64 (`arm64-v8a`) |
| Display Resolution | 720 x 1600 (HD+ 20:9 Aspect Ratio) |
| Display Cutout Notch | Waterdrop Notch (`M 0,0 H -64 V 60 H 64 V 0 H 0 Z`) |
| Status Bar Height | `56.0px` (Portrait), `24.0dp` (Landscape) |
| Rounded Corners Radius | `33dp` |
| Treble Architecture | System-as-Root (SAR), VNDK 30/31/32, Dynamic Partitions (VAB/Retrofit) |

---

## Anti-Brick Protected Partition Architecture

| Protected Partition | Function | Protection Policy |
|---|---|---|
| `preloader` | Primary SoC Bootloader | Read-only / Excluded from flash targets |
| `lk` / `lk2` | LittleKernel Fastboot Bootloader | Read-only / Preserves Fastboot recovery access |
| `nvram` / `nvdata` | Hardware IMEI, Baseband calibration, Wi-Fi MAC | Read-only / Preserves network credentials |
| `proinfo` / `nvcfg` | Serial number and device provisioning | Read-only |
| `tee1` / `tee2` | TrustZone and secure OS execution | Read-only |
| `md1img` / `md1dsp` | Cellular Modem DSP Firmware | Read-only |

For full unbrick instructions, see [EMERGENCY_UNBRICK_GUIDE.md](EMERGENCY_UNBRICK_GUIDE.md).

---

## Cloud Auto-Porter (GitHub Actions Workflow)

Automated cloud porting pipeline available at [`.github/workflows/auto_port.yml`](.github/workflows/auto_port.yml):

```mermaid
graph LR
    A[Input Port ROM URL] --> B[GitHub Actions Runner]
    B --> C[Multi-threaded Download via aria2c]
    C --> D[Extract payload.bin / super.img]
    D --> E[Auto-Patcher: Overlays, Shims, AVB Bypass]
    E --> F[Anti-Brick Safety Guard Verification]
    F --> G[AI Assistant: Diagnostics & Summary]
    G --> H[Package Flashable ZIP + SHA256]
    H --> I[Upload to GitHub Releases & Mirrors]
```

### Execution Steps
1. Navigate to the GitHub repository: `https://github.com/frnAlt/Xiaomi_blossom_stuff`
2. Open the **Actions** tab.
3. Select **Automatic ROM Porter for Xiaomi Blossom**.
4. Click **Run workflow** and provide the following parameters:
   - `port_rom_url`: Direct download URL of the target ROM package.
   - `base_rom_url` (Optional): Direct link to stock Blossom Fastboot ROM.
   - `target_variant`: Select `blossom`, `dandelion`, `angelica`, or `cattail`.
   - `rom_type`: Name or category (e.g., `HyperOS`, `MIUI14`, `PixelOS`).
   - `custom_upload_url` (Optional): Custom HTTP server or `https://transfer.sh/` endpoint.
5. Click **Run workflow**.

---

## Repository Structure

```text
├── .github/workflows/
│   └── auto_port.yml                     # GitHub Actions Cloud Auto-Porter Workflow
│
├── tools/                                # Backend Automation & CLI Porting Suite
│   ├── unbrick_safety_guard.py           # Pre-Flash Safety Validator
│   ├── ai_assistant.py                   # Porting Diagnostics & Error Root-Cause Analyzer
│   ├── auto_patcher.py                   # Automated Hardware & Framework Patcher
│   ├── auto_porter.py                    # End-to-End CLI Porter (Download, Extract, Merge, Package)
│   ├── multi_uploader.py                 # Multi-Mirror Cloud Uploader
│   ├── port_helper.py                    # ROM Injection Engine (Overlays, Shims, Props, Carrier)
│   ├── super_tools.py                    # Dynamic Super Partition Engine (lpmake, AVB verity, Flasher)
│   ├── build_overlays.py                 # RRO Compiler and Signer (aapt + apksigner)
│   ├── create_magisk_module.py           # Magisk/KernelSU ZIP Packager
│   └── verify_tree.py                    # Tree Diagnostic Validator
│
├── EMERGENCY_UNBRICK_GUIDE.md            # Emergency Unbrick & MTKClient Recovery Manual
├── DNA_KITCHEN_PORTING_GUIDE.md          # DnA Kitchen Step-by-Step Manual
├── PORTING_GUIDE.md                      # Standalone Comprehensive Porting Manual
├── Blossom_Notch_Fix_Magisk.zip          # Flashable Magisk/KernelSU Notch Fix Module
│
├── apks/                                 # Compiled, Zipaligned, and Signed Overlay APKs
│   ├── FrameworksResOverlayBlossom.apk   # Framework Overlay (Notch, Brightness, Doze, Power)
│   ├── DisplayOverlayBlossom.apk         # Display Cutout and Statusbar Overlay
│   ├── display_overlay.apk               # Drop-in binary display overlay
│   ├── SystemUIOverlayBlossom.apk        # SystemUI paddings and icon offsets
│   ├── SettingsOverlayBlossom.apk        # Settings UI customizations
│   ├── CarrierConfigOverlayBlossom.apk   # VoLTE / IMS Carrier configurations
│   ├── WifiResOverlayBlossom.apk         # Wi-Fi 2.4/5GHz channel resources
│   ├── DialerOverlayBlossom.apk          # Dialer and in-call UI overlays
│   ├── TelephonyOverlayBlossom.apk       # Telephony stack overlays
│   ├── LauncherOverlayBlossom.apk        # Launcher grid and icon configs
│   ├── treble_gsi/                       # Treble GSI Specific Overlays
│   │   └── treble-overlay-xiaomi-blossom.apk
│   └── vendor_overlay_prebuilts/         # Standard /vendor/overlay/ prebuilts
│
├── extracted_display_overlay_xml/        # Decompiled XML resources from display_overlay.apk
│   ├── AndroidManifest.xml               # Target package declaration and priority
│   ├── display_cutout_notch.xml          # Cutout SVG Path, Statusbar, and Corner Radii
│   ├── display_dimens.xml                # Dimension resources
│   ├── display_strings.xml               # String definitions
│   ├── display_bools.xml                 # Boolean configurations
│   ├── brightness_arrays.xml             # Lux/nits auto-brightness spline calibration
│   ├── power_profile.xml                 # Battery consumption specifications
│   ├── display_overlay_decompiled/       # Full decompiled apktool tree
│   ├── frameworks_overlay_decompiled/    # Full decompiled FrameworksRes overlay tree
│   └── treble_gsi_overlay_decompiled/    # Full decompiled Treble GSI overlay tree
│
├── xmls/                                 # Categorized XML and JSON configurations
│   ├── display/                          # Cutout SVG paths and brightness curves
│   ├── systemui/                         # Status bar dimensions and margins
│   ├── settings/                         # Settings layout and features
│   ├── power/                            # power_profile.xml, powerhint.json, task_profiles.json
│   ├── audio/                            # audio_policy_configuration.xml, aurisys, effects
│   ├── media/                            # media_codecs.xml, c2, profiles, performance
│   ├── thermal/                          # thermal_info_config.json
│   ├── carrier/                          # vendor.xml, vendor_device.xml, vendor_miui.xml
│   ├── permissions/                      # MediaTek framework and privapp permissions
│   └── vintf_manifests/                  # manifest.xml, compatibility matrices, lights
│
├── rro_overlays/                         # Source RRO overlays with Android.bp & AndroidManifest.xml
├── device_tree_overlay/                  # Traditional AOSP overlay structure
├── port_libs_and_shims/                  # Porting libraries and shims
│   ├── vndk/                             # libui-v32.so, android.hardware.*-ndk_platform.so
│   ├── libshims/                         # libshim_ui, libshim_vtservice, libshim_beanpod, libshim_audio
│   ├── lights/                           # Lights HAL C++ source and service XML
│   ├── audio/                            # Audio service init rc and makefiles
│   ├── init/                             # init_blossom.cpp (Variant detection: dandelion vs angelica)
│   └── public.libraries.vendor.txt
├── rootdir/                              # Init scripts (init.mt6765.rc, init.mt6762.rc) and fstabs
├── sepolicy/                             # SELinux vendor and private policies
├── props/                                # Props (system.prop, vendor.prop, product.prop, odm.prop)
└── build_makefiles/                      # BoardConfig.mk, device.mk, patches, extract-files.sh
```

---

## Backend Automation CLI Tools

### 1. Pre-Flash Anti-Brick Safety Guard (`tools/unbrick_safety_guard.py`)
Scans any ROM package or script to ensure no protected bootloader or NVRAM partitions are targeted:
```bash
python3 tools/unbrick_safety_guard.py --rom-zip Blossom_Port_HyperOS_dandelion.zip
```

### 2. AI Porting Assistant & Diagnostic Engine (`tools/ai_assistant.py`)
Analyzes build logs, extraction errors, or bootloop logcats and outputs root causes and fixes:
```bash
python3 tools/ai_assistant.py --log-file /path/to/bootlog_or_build.log
```

### 3. Automated Hardware & Framework Patcher (`tools/auto_patcher.py`)
Disables forced encryption in fstabs, strips dm-verity panics, and configures MediaTek shims:
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

## Master File-to-Destination Mapping Table

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

## Treble GSI Porting & Installation

When installing a Generic System Image (ARM64 A/B):

### Fastboot Flash Procedure
1. Obtain an `arm64_bvN` or `arm64_bgN` GSI image.
2. Reboot into FastbootD:
   ```bash
   adb reboot fastboot
   ```
3. Flash the system image and wipe:
   ```bash
   fastboot erase system
   fastboot flash system <gsi_image_name>.img
   fastboot -w
   fastboot reboot
   ```

### GSI Notch and Display Cutout Configuration
Flash the prebuilt [`Blossom_Notch_Fix_Magisk.zip`](Blossom_Notch_Fix_Magisk.zip) through Magisk or KernelSU to apply status bar and display cutout alignment.

---

## Troubleshooting Guide

| Issue | Root Cause | Resolution |
|---|---|---|
| Status bar icons overlap under notch | Missing `config_mainBuiltInDisplayCutout` or incorrect status bar height. | Install `DisplayOverlayBlossom.apk` or inject SVG path `M 0,0 H -64 V 60 H 64 V 0 H 0 Z` and set height to `56px`. |
| Brightness slider non-linear or unresponsive | Missing lux-to-nits spline interpolation arrays on MTK panel. | Apply [`extracted_display_overlay_xml/brightness_arrays.xml`](extracted_display_overlay_xml/brightness_arrays.xml) to framework-res. |
| Camera service termination on launch | Missing `GraphicBufferMapper` symbol in MediaTek camera HAL. | Add `port_libs_and_shims/libshims/libshim_ui` to the build or vendor libraries. |
| In-call audio / Bluetooth headset failure | MediaTek Aurisys DSP parameter mismatch. | Use `xmls/audio/aurisys_config.xml` and `xmls/audio/audio_policy_configuration.xml`. |
| Fingerprint settings crashing on Redmi 9A | Redmi 9A (`dandelion`) lacks fingerprint hardware. | Use `port_libs_and_shims/init/init_blossom.cpp` to dynamically disable fingerprint props on `dandelion`. |

---

## Display Cutout Technical Reference

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

## License
- Xiaomi Blossom Device Tree maintained by crDroid Android and LineageOS.
- Apache 2.0 License.
