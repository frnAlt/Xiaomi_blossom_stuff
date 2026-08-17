# Xiaomi Blossom (Redmi 9A / 9C / 9 Activ) Overlays, Configs & Complete Porting Guide

A complete, production-ready repository containing extracted & compiled display overlays, decompiled XML trees, vendor libraries, MediaTek shims, SELinux policies, init/fstab scripts, and comprehensive guides for **Xiaomi Blossom** (`dandelion`, `angelica`, `angelican`, `cattail` — MediaTek MT6762G, MT6765, MT6765G).

Designed for **GSI (Generic System Image) Porters**, **MIUI / HyperOS Porters**, **AOSP / Custom ROM Developers**, and **Treble Maintainers**.

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

## 📁 Repository Structure

```text
├── PORTING_GUIDE.md                      # 📖 Standalone Comprehensive Porting Manual
├── apks/                                 # 📦 Compiled, Zipaligned, and Signed Overlay APKs
│   ├── FrameworksResOverlayBlossom.apk   # Full framework overlay (Notch, Brightness, Doze, Power)
│   ├── DisplayOverlayBlossom.apk         # Dedicated Display Cutout & Statusbar overlay
│   ├── display_overlay.apk               # Drop-in display overlay binary for ROMs/GSIs
│   ├── SystemUIOverlayBlossom.apk        # SystemUI statusbar paddings, headers & system icons
│   ├── SettingsOverlayBlossom.apk        # Settings UI customizations
│   ├── CarrierConfigOverlayBlossom.apk   # VoLTE / IMS / Carrier provisioning
│   ├── WifiResOverlayBlossom.apk         # Wi-Fi 2.4/5GHz resources and channels
│   ├── DialerOverlayBlossom.apk          # Dialer & in-call UI overlays
│   ├── TelephonyOverlayBlossom.apk       # Telephony stack overlays
│   ├── LauncherOverlayBlossom.apk        # Launcher3 grid & icon configs
│   ├── treble_gsi/                       # ⚡ Treble GSI Specific Overlays
│   │   └── treble-overlay-xiaomi-blossom.apk
│   └── vendor_overlay_prebuilts/         # 📁 Standard /vendor/overlay/ prebuilts
│       ├── framework-res__auto_generated_rro_vendor.apk
│       ├── SystemUI__auto_generated_rro_vendor.apk
│       ├── Settings__auto_generated_rro_vendor.apk
│       ├── CarrierConfig__auto_generated_rro_vendor.apk
│       ├── WifiRes__auto_generated_rro_vendor.apk
│       └── Telephony__auto_generated_rro_vendor.apk
│
├── extracted_display_overlay_xml/        # 🎯 Decompiled & Extracted XMLs from display_overlay.apk
│   ├── AndroidManifest.xml               # Target package ("android") & overlay priority
│   ├── display_cutout_notch.xml          # Clean standalone Notch Path + Statusbar + Corners
│   ├── display_dimens.xml                # Extracted dimension resources (status_bar_height, corners)
│   ├── display_strings.xml               # Extracted string resources (config_mainBuiltInDisplayCutout)
│   ├── display_bools.xml                 # Extracted boolean flags (config_fillMainBuiltInDisplayCutout)
│   ├── brightness_arrays.xml             # Auto-brightness lux & nits calibration curves
│   ├── power_profile.xml                 # Extracted battery drain & power profile specs
│   ├── display_overlay_decompiled/       # Full apktool decompiled tree of display_overlay.apk
│   ├── frameworks_overlay_decompiled/    # Full apktool decompiled tree of FrameworksResOverlayBlossom.apk
│   └── treble_gsi_overlay_decompiled/    # Full apktool decompiled tree of treble-overlay-xiaomi-blossom.apk
│
├── xmls/                                 # 🛠️ Extracted & Categorized XML / JSON Configs
│   ├── display/                          # Cutout SVG paths, Brightness curves, AOD/Doze
│   ├── systemui/                         # Status bar paddings, carrier margins
│   ├── settings/                         # Settings layout & features
│   ├── power/                            # power_profile.xml, powerhint.json, task_profiles.json
│   ├── audio/                            # audio_policy_configuration.xml, aurisys, effects
│   ├── media/                            # media_codecs.xml, c2, profiles, performance
│   ├── thermal/                          # thermal_info_config.json
│   ├── carrier/                          # vendor.xml, vendor_device.xml, vendor_miui.xml
│   ├── permissions/                      # Mediatek framework & IMS privapp permissions
│   └── vintf_manifests/                  # manifest.xml, compatibility matrices, lights
│
├── rro_overlays/                         # 🌳 Source RRO Overlays (with Android.bp & AndroidManifest.xml)
├── device_tree_overlay/                  # 📂 Traditional AOSP overlay structure (overlay/frameworks/base/...)
├── port_libs_and_shims/                  # ⚙️ Essential Porting Libraries & Shims
│   ├── vndk/                             # libui-v32.so, android.hardware.*-ndk_platform.so
│   ├── libshims/                         # libshim_ui, libshim_vtservice, libshim_beanpod, libshim_audio
│   ├── lights/                           # Lights HAL C++ source & service XML
│   ├── audio/                            # Audio service init rc & makefiles
│   ├── init/                             # init_blossom.cpp (Variant detection: dandelion vs angelica)
│   └── public.libraries.vendor.txt
├── rootdir/                              # 📜 Init scripts (init.mt6765.rc, init.mt6762.rc) & fstabs
├── sepolicy/                             # 🔒 SELinux policies (vendor & private)
├── props/                                # ⚙️ Props (system.prop, vendor.prop, product.prop, odm.prop)
├── build_makefiles/                      # 🏗️ BoardConfig.mk, device.mk, patches, extract-files.sh
└── magisk_overlay_module/                # ⚡ Flashable Magisk / KernelSU module for Treble GSIs
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
| **`xmls/carrier/vendor_miui.xml`** | `/vendor/etc/carrier/vendor_miui.xml` | `rro_overlays/CarrierConfigOverlayBlossom/res/xml/vendor_miui.xml` | `/vendor/etc/carrier/vendor_miui.xml` |
| **`xmls/audio/*.xml`** | `/vendor/etc/audio/` & `/vendor/etc/audio_policy_configuration.xml` | `device/xiaomi/blossom/configs/audio/` | Stock vendor retains this |
| **`xmls/media/*.xml`** | `/vendor/etc/media_codecs*.xml` & `/vendor/etc/media_profiles_V1_0.xml` | `device/xiaomi/blossom/configs/media/` | Stock vendor retains this |
| **`xmls/power/power_profile.xml`** | `framework-res.apk` -> `res/xml/power_profile.xml` | `overlay/frameworks/base/core/res/res/xml/power_profile.xml` | Overlaid via framework-res overlay |
| **`xmls/power/powerhint.json`** | `/vendor/etc/powerhint.json` | `device/xiaomi/blossom/configs/powerhint.json` | `/vendor/etc/powerhint.json` |
| **`xmls/thermal/thermal_info_config.json`** | `/vendor/etc/thermal_info_config.json` | `device/xiaomi/blossom/configs/thermal/thermal_info_config.json` | `/vendor/etc/thermal_info_config.json` |
| **`port_libs_and_shims/vndk/libui-v32.so`** | `/system/lib64/vndk-v32/libui.so` | `device/xiaomi/blossom/vndk/libui-v32.so` | Handled by VNDK APEX |
| **`port_libs_and_shims/libshims/`** | `/system/lib64/libshim_*.so` or `/vendor/lib64/` | `device/xiaomi/blossom/libshims/` | Injected into `/system/lib64/` if needed |
| **`port_libs_and_shims/lights/`** | `/vendor/bin/hw/android.hardware.light-service.blossom` | `device/xiaomi/blossom/lights/` | Stock vendor service |
| **`port_libs_and_shims/init/init_blossom.cpp`** | N/A (Build props) | `device/xiaomi/blossom/init/init_blossom.cpp` | N/A |
| **`rootdir/etc/*`** | `/vendor/etc/init/hw/*` | `device/xiaomi/blossom/rootdir/etc/*` | Stock vendor ramdisk / vendor |
| **`sepolicy/*`** | Merged into `/vendor/etc/selinux/` | `device/xiaomi/blossom/sepolicy/` | Stock vendor sepolicy |
| **`props/*.prop`** | Append to `/system/build.prop` & `/vendor/build.prop` | Included via `system.prop` in device tree | Append to `system.prop` |

---

## ⚡ 1. Complete Treble GSI Porting & Usage Guide

If you are running or installing a **Generic System Image (GSI)** (such as Phh AOSP, PixelExperience GSI, crDroid GSI, LineageOS GSI, EvolutionX GSI, etc.) on Xiaomi Blossom:

### A. Flashing a GSI via Fastboot
1. Download an **`arm64_bvN`** or **`arm64_bgN`** (ARM64 A/B) GSI image.
2. Reboot phone to FastbootD mode:
   ```bash
   adb reboot fastboot
   # Or from bootloader: fastboot reboot fastboot
   ```
3. Flash the GSI system image:
   ```bash
   fastboot erase system
   fastboot flash system <gsi_image_name>.img
   fastboot -w
   fastboot reboot
   ```

### B. Installing the Notch & Display Overlay Fix on GSI
Without this overlay, GSI status bar icons will overlap under the waterdrop notch and brightness might jump abruptly.

#### Option 1: Direct Push via ADB (Root / TWRP / OrangeFox)
```bash
adb root
adb remount
adb push apks/treble_gsi/treble-overlay-xiaomi-blossom.apk /system/product/overlay/
adb shell chmod 644 /system/product/overlay/treble-overlay-xiaomi-blossom.apk
adb reboot
```

#### Option 2: Flash via Magisk / KernelSU Module
1. Zip the [`magisk_overlay_module/`](magisk_overlay_module/) folder:
   ```bash
   cd magisk_overlay_module
   zip -r ../Blossom_Notch_Fix.zip ./*
   ```
2. Open **Magisk** or **KernelSU** -> Modules -> Install from storage -> Select `Blossom_Notch_Fix.zip` -> Reboot.

### C. Fixing Common GSI Bugs on MediaTek MT6762/MT6765
- **Fix Bluetooth Audio**: Go to `Settings -> Phh Treble Settings -> Audio -> Enable "Disable Bluetooth A2DP offload"`.
- **Fix Minimum Brightness**: In Phh Settings, enable `"Set backlight scale"` or use the brightness arrays from [`extracted_display_overlay_xml/brightness_arrays.xml`](extracted_display_overlay_xml/brightness_arrays.xml).
- **Fix In-Call Audio / Low Mic**: Go to `Phh Treble Settings -> Audio -> Enable "Use alternate audio policy"`.

---

## 📱 2. Complete MIUI & HyperOS Porting Guide

When porting a MIUI (MIUI 12.5 / 13 / 14) or Xiaomi HyperOS ROM from another device (like Redmi 9, Redmi Note 9, Redmi 10) to Blossom:

### Step 1: Notch & Display Alignment
1. Push `apks/DisplayOverlayBlossom.apk` to `/system_ext/overlay/` or `/product/overlay/`.
2. Add the following lines to `/system/build.prop` or `/system_ext/build.prop`:
   ```properties
   ro.miui.notch=1
   ro.miui.has_real_notch=1
   ro.vendor.display.type=1
   ```
3. Inject the exact Waterdrop SVG cutout from [`extracted_display_overlay_xml/display_cutout_notch.xml`](extracted_display_overlay_xml/display_cutout_notch.xml) into your base `framework-res.apk`:
   ```xml
   <string translatable="false" name="config_mainBuiltInDisplayCutout">M 0,0 H -64 V 60 H 64 V 0 H 0 Z</string>
   <dimen name="status_bar_height_portrait">56.0px</dimen>
   <dimen name="status_bar_height_default">56.0px</dimen>
   <dimen name="status_bar_height_landscape">24.0dp</dimen>
   <dimen name="rounded_corner_radius">33dp</dimen>
   ```

### Step 2: VoLTE & MIUI Carrier Provisioning
- Copy `xmls/carrier/vendor_miui.xml` and `xmls/carrier/vendor_device.xml` to `/vendor/etc/carrier/`.
- Install `apks/CarrierConfigOverlayBlossom.apk` to `/vendor/overlay/` to ensure Dual 4G VoLTE and Wi-Fi calling icons initialize correctly.

### Step 3: MediaTek Shims & VNDK Compatibility
If camera, video playback, or SurfaceFlinger crash on newer bases due to missing `GraphicBufferMapper` symbols:
- Place `port_libs_and_shims/libshims/libshim_ui/` into your vendor library path.
- Add `libshim_ui.so` to `/vendor/etc/public.libraries.vendor.txt`.

---

## 🛠️ 3. Complete AOSP / Custom ROM Source Porting Guide

To port LineageOS, crDroid, PixelOS, DerpFest, CherishOS, or EvolutionX from source:

### Step 1: Set Up Device Tree Layout
Copy the required components into your Android build tree under `device/xiaomi/blossom/`:
```text
device/xiaomi/blossom/
├── rro_overlays/             <- Source RRO overlays from rro_overlays/
├── configs/                  <- XML configs (audio, media, thermal, power) from xmls/
├── rootdir/                  <- Init scripts and fstabs from rootdir/
├── sepolicy/                 <- SELinux rules from sepolicy/
├── libshims/                 <- Shims from port_libs_and_shims/libshims/
├── lights/                   <- Lights HAL C++ from port_libs_and_shims/lights/
├── init/                     <- Variant init cpp from port_libs_and_shims/init/
├── vndk/                     <- VNDK prebuilts from port_libs_and_shims/vndk/
├── BoardConfig.mk            <- Build config from build_makefiles/BoardConfig.mk
└── device.mk                 <- Device makefile from build_makefiles/device.mk
```

### Step 2: Include Overlays in `device.mk`
```makefile
# RRO Overlays for Blossom
PRODUCT_PACKAGES += \
    CarrierConfigOverlayBlossom \
    DialerOverlayBlossom \
    FrameworksResOverlayBlossom \
    LauncherOverlayBlossom \
    SettingsOverlayBlossom \
    SystemUIOverlayBlossom \
    TelephonyOverlayBlossom \
    WifiResOverlayBlossom

# Or traditional overlay path
DEVICE_PACKAGE_OVERLAYS += $(LOCAL_PATH)/device_tree_overlay
```

### Step 3: Dynamic Variant Handling (Redmi 9A vs 9C vs 9 Activ)
The file `port_libs_and_shims/init/init_blossom.cpp` dynamically identifies hardware SKUs:
- **`dandelion`** (Redmi 9A — Single rear camera, no fingerprint sensor)
- **`angelica`** (Redmi 9C — Triple rear camera, rear fingerprint sensor)
- **`angelican`** (Redmi 9C NFC — Triple rear camera, fingerprint, NXP NFC)
- **`cattail`** (Redmi 9 Activ — Helio G35 platform)

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
- Apache 2.0 License.
