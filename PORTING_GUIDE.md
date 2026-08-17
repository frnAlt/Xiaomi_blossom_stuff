# Xiaomi Blossom (Redmi 9A / 9C / 9 Activ) Complete Porting Guide

This guide is a complete technical manual for ROM porters, developers, and maintainers working with **Xiaomi Blossom** (`dandelion`, `angelica`, `angelican`, `cattail` — MT6762G, MT6765, MT6765G).

Whether you are porting **MIUI / HyperOS**, building **AOSP / Custom ROMs from source**, or fixing **Treble GSIs**, this guide maps every file in this repository to its exact destination and explains how to resolve common porting bugs.

---

## 🗺️ Master File & Destination Mapping Table

| Source in this Repository | Destination in MIUI / HyperOS Port | Destination in AOSP / Custom ROM Tree | Destination in Treble GSI |
|---|---|---|---|
| **`apks/display_overlay.apk`** | `/product/overlay/display_overlay.apk` | N/A (Builds from source) | `/system/product/overlay/display_overlay.apk` |
| **`apks/FrameworksResOverlayBlossom.apk`** | `/vendor/overlay/FrameworksResOverlayBlossom.apk` | `PRODUCT_PACKAGES += FrameworksResOverlayBlossom` | `/vendor/overlay/FrameworksResOverlayBlossom.apk` |
| **`apks/SystemUIOverlayBlossom.apk`** | `/vendor/overlay/SystemUIOverlayBlossom.apk` | `PRODUCT_PACKAGES += SystemUIOverlayBlossom` | `/vendor/overlay/SystemUIOverlayBlossom.apk` |
| **`apks/CarrierConfigOverlayBlossom.apk`** | `/vendor/overlay/CarrierConfigOverlayBlossom.apk` | `PRODUCT_PACKAGES += CarrierConfigOverlayBlossom` | `/vendor/overlay/CarrierConfigOverlayBlossom.apk` |
| **`apks/treble_gsi/treble-overlay-xiaomi-blossom.apk`** | N/A | N/A | `/system/product/overlay/treble-overlay-xiaomi-blossom.apk` |
| **`extracted_display_overlay_xml/display_cutout_notch.xml`** | Decompile `framework-res.apk` -> `res/values/config.xml` & `dimens.xml` | `overlay/frameworks/base/core/res/res/values/config.xml` | Included in GSI overlay APK |
| **`xmls/carrier/vendor_miui.xml`** | `/vendor/etc/carrier/vendor_miui.xml` | `rro_overlays/CarrierConfigOverlayBlossom/res/xml/vendor_miui.xml` | `/vendor/etc/carrier/` |
| **`xmls/audio/*.xml`** | `/vendor/etc/audio/` & `/vendor/etc/audio_policy_configuration.xml` | `device/xiaomi/blossom/configs/audio/` | Stock vendor retains this |
| **`xmls/media/*.xml`** | `/vendor/etc/media_codecs*.xml` & `/vendor/etc/media_profiles_V1_0.xml` | `device/xiaomi/blossom/configs/media/` | Stock vendor retains this |
| **`xmls/power/power_profile.xml`** | `framework-res.apk` -> `res/xml/power_profile.xml` | `overlay/frameworks/base/core/res/res/xml/power_profile.xml` | Overlaid via framework-res overlay |
| **`xmls/power/powerhint.json`** | `/vendor/etc/powerhint.json` | `device/xiaomi/blossom/configs/powerhint.json` | `/vendor/etc/powerhint.json` |
| **`xmls/thermal/thermal_info_config.json`** | `/vendor/etc/thermal_info_config.json` | `device/xiaomi/blossom/configs/thermal/thermal_info_config.json` | `/vendor/etc/thermal_info_config.json` |
| **`port_libs_and_shims/vndk/libui-v32.so`** | `/system/lib64/vndk-v32/libui.so` | `device/xiaomi/blossom/vndk/libui-v32.so` | Handled by VNDK APEX |
| **`port_libs_and_shims/libshims/`** | `/system/lib64/libshim_*.so` or `/vendor/lib64/` | `device/xiaomi/blossom/libshims/` | Injected into `/system/lib64/` if needed |
| **`port_libs_and_shims/lights/`** | `/vendor/bin/hw/android.hardware.light-service.blossom` | `device/xiaomi/blossom/lights/` | Stock vendor service |
| **`port_libs_and_shims/init/init_blossom.cpp`** | N/A (MIUI uses build.prop) | `device/xiaomi/blossom/init/init_blossom.cpp` | N/A |
| **`rootdir/etc/*`** | `/vendor/etc/init/hw/*` | `device/xiaomi/blossom/rootdir/etc/*` | Stock vendor ramdisk / vendor |
| **`sepolicy/*`** | Merged into `/vendor/etc/selinux/` | `device/xiaomi/blossom/sepolicy/` | Stock vendor sepolicy |
| **`props/*.prop`** | Append to `/system/build.prop` & `/vendor/build.prop` | Included via `system.prop` in device tree | Append to `system.prop` |

---

## 📱 1. Porting MIUI / HyperOS ROMs

When porting a MIUI or HyperOS ROM from another MediaTek device (e.g. Helio G80/G85/G88 or higher) to Xiaomi Blossom:

### Step 1: Fix Display Cutout & Status Bar Overlap
1. Push `apks/DisplayOverlayBlossom.apk` to `/system_ext/overlay/` or `/product/overlay/` with permissions `chmod 644`.
2. Ensure the following properties exist in `/system/build.prop` or `/system_ext/build.prop`:
   ```properties
   ro.miui.notch=1
   ro.miui.has_real_notch=1
   ro.vendor.display.type=1
   ```
3. If building the port manually, inject the SVG cutout from [`extracted_display_overlay_xml/display_cutout_notch.xml`](extracted_display_overlay_xml/display_cutout_notch.xml):
   ```xml
   <string translatable="false" name="config_mainBuiltInDisplayCutout">M 0,0 H -64 V 60 H 64 V 0 H 0 Z</string>
   <dimen name="status_bar_height_portrait">56.0px</dimen>
   <dimen name="status_bar_height_default">56.0px</dimen>
   <dimen name="status_bar_height_landscape">24.0dp</dimen>
   <dimen name="rounded_corner_radius">33dp</dimen>
   ```

### Step 2: Fix VoLTE & MIUI Carrier Configs
- Copy `xmls/carrier/vendor_miui.xml` and `xmls/carrier/vendor_device.xml` to `/vendor/etc/carrier/` or install `apks/CarrierConfigOverlayBlossom.apk` into `/vendor/overlay/`.

### Step 3: MediaTek Graphics & Camera Shims
If the Camera or SurfaceFlinger crashes due to missing `GraphicBufferMapper` symbols on newer Android/MIUI bases:
- Place `port_libs_and_shims/libshims/libshim_ui/` into your vendor library path or compile `libshim_ui.so` and add it to `public.libraries.vendor.txt`.

---

## 🛠️ 2. Building AOSP / Custom ROMs from Source (LineageOS, crDroid, etc.)

### Step 1: Device Tree Placement
Place the components into your device tree `device/xiaomi/blossom/`:
```text
device/xiaomi/blossom/
├── rro_overlays/             <- Copy from this repo's rro_overlays/
├── configs/                  <- Copy audio/, media/, thermal/, power/ from xmls/
├── rootdir/                  <- Copy from rootdir/
├── sepolicy/                 <- Copy from sepolicy/
├── libshims/                 <- Copy from port_libs_and_shims/libshims/
├── lights/                   <- Copy from port_libs_and_shims/lights/
├── init/                     <- Copy from port_libs_and_shims/init/
├── vndk/                     <- Copy from port_libs_and_shims/vndk/
├── BoardConfig.mk            <- Copy from build_makefiles/BoardConfig.mk
└── device.mk                 <- Copy from build_makefiles/device.mk
```

### Step 2: Configure `device.mk`
Ensure your `device.mk` includes the RRO overlay packages:
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

### Step 3: Variant Detection (Redmi 9A vs 9C vs 9 Activ)
`port_libs_and_shims/init/init_blossom.cpp` dynamically detects whether the device is:
- **`dandelion`** (Redmi 9A — Single camera, no fingerprint sensor)
- **`angelica`** (Redmi 9C — Triple camera with fingerprint sensor)
- **`angelican`** (Redmi 9C NFC — NFC hardware enabled)
- **`cattail`** (Redmi 9 Activ — Helio G35 variant)

---

## ⚡ 3. Treble GSI Porting & Notch Fix Guide

If you are running a Generic System Image (GSI) such as Phh-AOSP, PixelExperience GSI, crDroid GSI, or LineageOS GSI:

### Method A: Direct System Injection (Root / TWRP / Recovery)
1. Mount `/system` and `/product` as read-write.
2. Copy `apks/treble_gsi/treble-overlay-xiaomi-blossom.apk` or `apks/DisplayOverlayBlossom.apk` to `/system/product/overlay/`:
   ```bash
   adb root
   adb remount
   adb push apks/treble_gsi/treble-overlay-xiaomi-blossom.apk /system/product/overlay/
   adb shell chmod 644 /system/product/overlay/treble-overlay-xiaomi-blossom.apk
   adb reboot
   ```

### Method B: Flash via Magisk / KernelSU / APatch
1. Zip the folder [`magisk_overlay_module/`](magisk_overlay_module/):
   ```bash
   cd magisk_overlay_module
   zip -r ../Blossom_Notch_Fix_Magisk.zip ./*
   ```
2. Flash `Blossom_Notch_Fix_Magisk.zip` in the Magisk / KernelSU Manager app and reboot.

---

## 🔧 Troubleshooting Common Blossom Porting Bugs

| Symptom | Root Cause | Solution |
|---|---|---|
| **Status bar icons cut off by waterdrop notch** | Missing `config_mainBuiltInDisplayCutout` or incorrect status bar height. | Install `DisplayOverlayBlossom.apk` or inject SVG path `M 0,0 H -64 V 60 H 64 V 0 H 0 Z` and set status bar height to `56px`. |
| **Brightness slider has no effect or jumps abruptly** | Missing lux-to-nits spline interpolation arrays. | Apply [`extracted_display_overlay_xml/brightness_arrays.xml`](extracted_display_overlay_xml/brightness_arrays.xml) into framework-res. |
| **Camera app crashes on open (`undefined symbol: GraphicBufferMapper`)** | MTK proprietary camera HAL requires legacy GraphicBufferMapper symbol. | Add `port_libs_and_shims/libshims/libshim_ui` to the build or vendor libs. |
| **No In-Call Audio / Bluetooth Headset Audio** | MTK Aurisys DSP parameter mismatch. | Use `xmls/audio/aurisys_config.xml` and `xmls/audio/audio_policy_configuration.xml`. |
| **Fingerprint not working on Redmi 9A** | Redmi 9A (`dandelion`) has no fingerprint sensor; build was configured for `angelica`. | Use `port_libs_and_shims/init/init_blossom.cpp` to dynamically toggle biometric properties based on hardware SKU. |

---

## 📄 License & Credits
- Xiaomi Blossom Device Tree maintained by [crDroid Android](https://github.com/crdroidandroid) & [LineageOS](https://github.com/LineageOS).
- Apache 2.0 License.
