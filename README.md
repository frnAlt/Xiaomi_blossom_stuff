# Xiaomi Blossom (Redmi 9A / 9C / 9 Activ) Overlays, Configs & Porting Kit

Complete extracted & compiled display overlays, XML configuration trees, vendor libraries, shims, sepolicies, and device tree assets for **Xiaomi Blossom** (Redmi 9A, Redmi 9C, Redmi 9 Activ, Poco C3 / MT6762G, MT6765, MT6765G).

Designed for **Custom ROM developers**, **GSI (Generic System Image) builders**, and **Treble maintainers**.

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
├── xmls/                                 # Extracted & Organized XML / JSON Configs
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

## 🛠️ Display & Cutout Technical Reference

### Notch SVG Path (`config_mainBuiltInDisplayCutout`)
```xml
<string translatable="false" name="config_mainBuiltInDisplayCutout">M 0,0 H -64 V 60 H 64 V 0 H 0 Z</string>
<bool name="config_fillMainBuiltInDisplayCutout">true</bool>
```

### Dimensions
```xml
<dimen name="status_bar_height_default">56.0px</dimen>
<dimen name="status_bar_height_portrait">56.0px</dimen>
<dimen name="status_bar_height_landscape">24.0dp</dimen>
<dimen name="rounded_corner_radius">33dp</dimen>
<dimen name="status_bar_padding_start">8dp</dimen>
<dimen name="status_bar_padding_top">10.0px</dimen>
<dimen name="status_bar_padding_end">0dp</dimen>
```

---

## 🚀 How to Use for ROM Porting & Treble GSIs

### Option 1: Using on Treble GSIs (Phh / AOSP / PixelExperience GSI)
1. Push `apks/treble_gsi/treble-overlay-xiaomi-blossom.apk` or `apks/DisplayOverlayBlossom.apk` to `/system/product/overlay/` or `/product/overlay/` with permissions `0644`.
2. Or flash the pre-configured `magisk_overlay_module` via Magisk / KernelSU / APatch.

### Option 2: Using in Custom ROM Device Trees (AOSP / LineageOS / crDroid)
- **Soong RRO Overlays**: Copy `rro_overlays/` directly into your device tree root and reference `PRODUCT_PACKAGES += FrameworksResOverlayBlossom SystemUIOverlayBlossom SettingsOverlayBlossom CarrierConfigOverlayBlossom WifiResOverlayBlossom TelephonyOverlayBlossom` in `device.mk`.
- **Traditional Overlay**: Set `DEVICE_PACKAGE_OVERLAYS += $(DEVICE_PATH)/device_tree_overlay` in `device.mk`.

### Option 3: MediaTek Shims & VNDK Fixes
- Copy `port_libs_and_shims/libshims` and `port_libs_and_shims/vndk` into your device tree or vendor tree to resolve `libui-v32.so` and `GraphicBufferMapper` symbol incompatibilities on Android 12 through Android 16.

---

## 📤 Pushing to Your GitHub Repository

To push this entire structured package to your own GitHub repository:

```bash
cd /home/ffjisan804/blossom_overlays_and_configs

# Initialize git repository (if not already initialized)
git init -b main

# Stage all files
git add .

# Create initial commit
git commit -m "blossom: Add extracted overlays, XML configs, porting libs, and shims"

# Add your GitHub repository as remote origin
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git

# Push to GitHub
git push -u origin main
```

---

## 📄 License & Credits
- Xiaomi Blossom Device Tree maintained by [crDroid Android](https://github.com/crdroidandroid) & [LineageOS](https://github.com/LineageOS).
- Apache 2.0 License.
