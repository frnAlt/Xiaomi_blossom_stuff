# Xiaomi Blossom (Redmi 9A / 9C / 9 Activ) Overlays, Configs & Porting Kit

Complete extracted & compiled display overlays, decompiled XML trees, vendor libraries, shims, sepolicies, and device tree assets for **Xiaomi Blossom** (Redmi 9A, Redmi 9C, Redmi 9 Activ, Poco C3 / MT6762G, MT6765, MT6765G).

Designed for **Custom ROM developers**, **GSI (Generic System Image) builders**, and **Treble maintainers**.

> 📖 **Looking for step-by-step instructions on how to port MIUI / HyperOS, build AOSP ROMs, or fix Treble GSIs?**  
> Check out the complete **[PORTING GUIDE (PORTING_GUIDE.md)](PORTING_GUIDE.md)** for file-to-destination mapping tables, installation steps, and bug fixes!

---

## 📱 Device Specifications & Target Models

| Parameter | Specification |
|---|---|
| **Codename** | `blossom` (`dandelion`, `angelica`, `angelican`, `cattail`) |
| **Devices** | Redmi 9A, Redmi 9C, Redmi 9 Activ, Redmi 9 India, Poco C3 |
| **Platform / SoC** | MediaTek Helio G25 / G35 (MT6762G / MT6765 / MT6765G) |
| **Display Resolution** | 720 x 1600 (HD+ 20:9) |
| **Display Cutout Notch** | Waterdrop Notch (`M 0,0 H -64 V 60 H 64 V 0 H 0 Z`) |
| **Status Bar Height** | `56.0px` (Portrait), `24.0dp` (Landscape) |
| **Rounded Corners** | `33dp` |

---

## 📁 Repository Structure

```text
├── PORTING_GUIDE.md                      # 📖 Comprehensive Porting Guide (MIUI, HyperOS, AOSP, Treble GSI)
├── apks/                                 # Compiled, Zipaligned, and Signed APKs
│   ├── FrameworksResOverlayBlossom.apk   # Full framework-res overlay (Cutout, Brightness, Doze, Power)
│   ├── DisplayOverlayBlossom.apk         # Dedicated Display Cutout & Statusbar overlay
│   ├── display_overlay.apk               # Drop-in display overlay binary
│   ├── SystemUIOverlayBlossom.apk        # SystemUI statusbar paddings, headers & icons
│   ├── SettingsOverlayBlossom.apk        # Settings UI customizations
│   ├── CarrierConfigOverlayBlossom.apk   # VoLTE / IMS / Carrier provisioning
│   ├── WifiResOverlayBlossom.apk         # Wi-Fi resources and channels
│   ├── DialerOverlayBlossom.apk          # Dialer & in-call UI overlays
│   ├── TelephonyOverlayBlossom.apk       # Telephony stack overlays
│   ├── LauncherOverlayBlossom.apk        # Launcher3 grid & icon configs
│   ├── treble_gsi/                       # Treble GSI Notch Overlays
│   │   └── treble-overlay-xiaomi-blossom.apk
│   └── vendor_overlay_prebuilts/         # Standard /vendor/overlay/ prebuilts
│       ├── framework-res__auto_generated_rro_vendor.apk
│       ├── SystemUI__auto_generated_rro_vendor.apk
│       ├── Settings__auto_generated_rro_vendor.apk
│       ├── CarrierConfig__auto_generated_rro_vendor.apk
│       ├── WifiRes__auto_generated_rro_vendor.apk
│       └── Telephony__auto_generated_rro_vendor.apk
│
├── extracted_display_overlay_xml/        # 🎯 Decompiled & Extracted XMLs directly from display_overlay.apk
│   ├── AndroidManifest.xml               # Target package & overlay priority definition
│   ├── display_cutout_notch.xml          # Clean standalone Notch Path + Statusbar Height + Rounded Corners
│   ├── display_dimens.xml                # Extracted dimension resources (status_bar_height, rounded corners)
│   ├── display_strings.xml               # Extracted string resources (config_mainBuiltInDisplayCutout)
│   ├── display_bools.xml                 # Extracted boolean flags (config_fillMainBuiltInDisplayCutout)
│   ├── brightness_arrays.xml             # Auto-brightness lux & nits calibration curves
│   ├── power_profile.xml                 # Extracted battery drain & power profile specs
│   ├── display_overlay_decompiled/       # Full apktool decompiled tree of display_overlay.apk
│   ├── frameworks_overlay_decompiled/    # Full apktool decompiled tree of FrameworksResOverlayBlossom.apk
│   └── treble_gsi_overlay_decompiled/    # Full apktool decompiled tree of treble-overlay-xiaomi-blossom.apk
│
├── xmls/                                 # Extracted & Categorized XML / JSON Configs
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
├── rro_overlays/                         # Source RRO Overlays (with Android.bp & AndroidManifest.xml)
├── device_tree_overlay/                  # Traditional AOSP overlay structure (overlay/frameworks/base/...)
├── port_libs_and_shims/                  # Essential Porting Libraries & Shims
│   ├── vndk/                             # libui-v32.so, android.hardware.*-ndk_platform.so
│   ├── libshims/                         # libshim_ui, libshim_vtservice, libshim_beanpod, libshim_audio
│   ├── lights/                           # Lights HAL C++ source & service XML
│   ├── audio/                            # Audio service init rc & makefiles
│   ├── init/                             # init_blossom.cpp (Variant detection: dandelion vs angelica)
│   └── public.libraries.vendor.txt
├── rootdir/                              # Init scripts (init.mt6765.rc, init.mt6762.rc) & fstabs
├── sepolicy/                             # SELinux policies (vendor & private)
├── props/                                # Props (system.prop, vendor.prop, product.prop, odm.prop)
├── build_makefiles/                      # BoardConfig.mk, device.mk, patches, extract-files.sh
└── magisk_overlay_module/                # Flashable Magisk / KernelSU module for Treble GSIs
```

---

## 🎯 Extracted Display Overlay XML Details (`extracted_display_overlay_xml/`)

The folder [`extracted_display_overlay_xml/`](extracted_display_overlay_xml/) contains the human-readable XML resources directly extracted and decompiled from `display_overlay.apk`.

### 1. [`display_cutout_notch.xml`](extracted_display_overlay_xml/display_cutout_notch.xml)
Contains the exact SVG path and geometry required by the Android SurfaceFlinger / WindowManager for Xiaomi Blossom's teardrop/waterdrop notch:
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Waterdrop Notch SVG Cutout Path -->
    <string translatable="false" name="config_mainBuiltInDisplayCutout">M 0,0 H -64 V 60 H 64 V 0 H 0 Z</string>
    <bool name="config_fillMainBuiltInDisplayCutout">true</bool>

    <!-- Status Bar Heights & Rounded Corners -->
    <dimen name="status_bar_height_default">56.0px</dimen>
    <dimen name="status_bar_height_portrait">56.0px</dimen>
    <dimen name="status_bar_height_landscape">24.0dp</dimen>
    <dimen name="rounded_corner_radius">33dp</dimen>
</resources>
```

### 2. [`display_dimens.xml`](extracted_display_overlay_xml/display_dimens.xml)
Status bar and rounded corner dimensions:
- `status_bar_height_default`: `56.0px`
- `status_bar_height_portrait`: `56.0px`
- `status_bar_height_landscape`: `24.0dp`
- `rounded_corner_radius`: `33.0dp`

### 3. [`brightness_arrays.xml`](extracted_display_overlay_xml/brightness_arrays.xml)
Auto-brightness lux and nits mappings for smooth backlight transitions without sudden jumps on MTK panels.

---

## 🚀 Quick Start for Porting (See [PORTING_GUIDE.md](PORTING_GUIDE.md) for Full Details)

- **For MIUI / HyperOS Ports**: Push `apks/DisplayOverlayBlossom.apk` to `/system_ext/overlay/` or `/product/overlay/`, and set `ro.miui.notch=1` in `build.prop`.
- **For AOSP / Custom ROM Trees**: Place `rro_overlays/` in your device tree root and add `PRODUCT_PACKAGES += FrameworksResOverlayBlossom SystemUIOverlayBlossom` to `device.mk`.
- **For Treble GSIs**: Push `apks/treble_gsi/treble-overlay-xiaomi-blossom.apk` to `/system/product/overlay/` or flash [`magisk_overlay_module/`](magisk_overlay_module/) in Magisk / KernelSU.

---

## 📄 License & Credits
- Xiaomi Blossom Device Tree maintained by [crDroid Android](https://github.com/crdroidandroid) & [LineageOS](https://github.com/LineageOS).
- Apache 2.0 License.
