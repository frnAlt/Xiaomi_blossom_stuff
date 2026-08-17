# Xiaomi Blossom Kernel, Hardware Architecture, and Code Logic

This document details the hardware specifications, kernel memory layouts, mkbootimg parameters, CPU scheduler configurations, and variant detection logic derived from the official Xiaomi Blossom device and kernel trees (`device/xiaomi/blossom` and `kernel/xiaomi/blossom`).

---

## 1. Platform and SoC Architecture

Xiaomi Blossom is a unified platform targeting low-power MediaTek Helio G25 and G35 SoCs.

| Parameter | MediaTek Helio G25 (MT6762G) | MediaTek Helio G35 (MT6765 / MT6765G) |
|---|---|---|
| Target Devices | Redmi 9A (`dandelion`), Poco C30 | Redmi 9C (`angelica`), Redmi 9C NFC (`angelican`), Redmi 9 Activ (`cattail`), Poco C3 |
| CPU Cores | 8x ARM Cortex-A53 | 8x ARM Cortex-A53 |
| CPU Cluster 0 (LITTLE) | 4x Cortex-A53 up to 1.5 GHz | 4x Cortex-A53 up to 1.8 GHz |
| CPU Cluster 1 (big) | 4x Cortex-A53 up to 2.0 GHz | 4x Cortex-A53 up to 2.3 GHz |
| GPU | IMG PowerVR GE8320 @ 650 MHz | IMG PowerVR GE8320 @ 680 MHz |
| Memory Architecture | LPDDR4X (Dual Channel) @ 1600 MHz | LPDDR4X (Dual Channel) @ 1600 MHz |
| Storage Interface | eMMC 5.1 | eMMC 5.1 |

---

## 2. Kernel Memory Layout and mkbootimg Parameters

The boot image format uses Android Boot Image Header Version 2 with embedded Device Tree Blobs (DTB).

### BoardConfig.mk Memory Parameters
```makefile
BOARD_BOOT_HEADER_VERSION := 2
BOARD_KERNEL_BASE         := 0x40078000
BOARD_KERNEL_PAGESIZE     := 2048
BOARD_KERNEL_OFFSET       := 0x00008000
BOARD_SECOND_OFFSET       := 0x00e88000
BOARD_RAMDISK_OFFSET      := 0x11a88000
BOARD_KERNEL_TAGS_OFFSET  := 0x07808000
BOARD_DTB_OFFSET          := 0x07808000
BOARD_FLASH_BLOCK_SIZE    := 131072
BOARD_BOOTIMAGE_PARTITION_SIZE     := 67108864  # 64 MB
BOARD_DTBOIMG_PARTITION_SIZE       := 8388608   # 8 MB
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 67108864  # 64 MB
```

### Kernel Command Line (cmdline)
```text
bootopt=64S3,32N2,64N2 androidboot.init_fatal_reboot_target=recovery androidboot.serialconsole=0 kpti=off quiet loglevel=3 cgroup_disable=pressure cgroup.memory=nokmem,nosocket nodebugmon noirqdebug kasan=off
```

### Kernel Flag Rationale
- `kpti=off`: Disables Kernel Page Table Isolation to avoid severe CPU overhead on Cortex-A53 cores.
- `cgroup.memory=nokmem,nosocket`: Disables socket and kernel memory cgroup accounting to reduce RAM pressure on 2GB/3GB RAM models.
- `cgroup_disable=pressure`: Disables PSI pressure stall information collection to save CPU cycles.

---

## 3. Dynamic Partition Geometry (super.img)

```makefile
BOARD_SUPER_PARTITION_SIZE := 4831838208  # 4608 MiB (Total flash super block)
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_SIZE := 4829741056             # SUPER_SIZE - 2 MiB metadata overhead
BOARD_MAIN_PARTITION_LIST := system vendor product odm system_ext
```

### Filesystem Allocation
- `system`, `vendor`, `product`, `system_ext`, `odm`: `ext4` (Read-only, logical, first-stage mount).
- `userdata`: `f2fs` with `fileencryption=aes-256-xts:aes-256-cts` (Stock) or `encryptable=userdata` (Custom/Ported).
- `metadata`: `/dev/block/by-name/md_udc` mounted at `/metadata` (`ext4`).

---

## 4. Hardware SKU & Variant Detection Logic (`libinit_blossom`)

The Blossom device tree supports 4 distinct hardware variants using a single unified build tree. The native initialization library (`libinit_blossom`) reads `/proc/bootconfig` or `ro.boot.hwname` at runtime:

```cpp
void set_variant_props(const std::string& hwname) {
    if (hwname == "dandelion") {
        // Redmi 9A: Single camera, no fingerprint sensor
        set_ro_build_prop("model", "Redmi 9A");
        set_ro_build_prop("product", "dandelion");
        set_ro_build_prop("device", "dandelion");
        set_ro_build_prop("name", "dandelion");
        property_override("ro.product.marketname", "Redmi 9A");
        property_override("ro.hardware.fingerprint", "none");
    } else if (hwname == "angelica") {
        // Redmi 9C: Triple camera, rear capacitive fingerprint
        set_ro_build_prop("model", "Redmi 9C");
        set_ro_build_prop("product", "angelica");
        set_ro_build_prop("device", "angelica");
        set_ro_build_prop("name", "angelica");
        property_override("ro.product.marketname", "Redmi 9C");
        property_override("ro.hardware.fingerprint", "goodix");
    } else if (hwname == "angelican") {
        // Redmi 9C NFC: Triple camera, fingerprint, NXP PN553 NFC
        set_ro_build_prop("model", "Redmi 9C NFC");
        set_ro_build_prop("product", "angelican");
        set_ro_build_prop("device", "angelican");
        set_ro_build_prop("name", "angelican");
        property_override("ro.product.marketname", "Redmi 9C NFC");
        property_override("ro.hardware.nfc", "nxp");
    } else if (hwname == "cattail") {
        // Redmi 9 Activ: Helio G35, Dual camera, fingerprint
        set_ro_build_prop("model", "Redmi 9 Activ");
        set_ro_build_prop("product", "cattail");
        set_ro_build_prop("device", "cattail");
        set_ro_build_prop("name", "cattail");
        property_override("ro.product.marketname", "Redmi 9 Activ");
    }
}
```

---

## 5. Memory Management & Low RAM Tuning

Due to 2GB and 3GB RAM constraints on base Blossom hardware:

- **Jemalloc Tuning**: `MALLOC_LOW_MEMORY := true` reduces heap arena fragmentation.
- **ZRAM Configuration**: `zramsize=55%,max_comp_streams=8` compressed via LZ4 algorithm.
- **SurfaceFlinger Decoupling**: SurfaceFlinger runs with 1 frame buffer latency decoupling to smooth 60Hz UI rendering without dropped frames.

---

## 6. Display Cutout & Status Bar Specifications

- Waterdrop Cutout Path: `M 0,0 H -64 V 60 H 64 V 0 H 0 Z`
- Default Status Bar Height: `56.0px`
- Landscape Status Bar Height: `24.0dp`
- Display Corner Radius: `33dp`
- Fill Built-in Cutout Flag: `config_fillMainBuiltInDisplayCutout=true`

---

## 7. MediaTek Shims and VNDK Interface

- **`libui-v32.so`**: Provides Android 12/12.1/13 VNDK libui compatibility for MediaTek camera and display HALs.
- **`libshim_ui.so`**: Shims missing `GraphicBufferMapper` symbols:
  - `_ZN7android19GraphicBufferMapper9lockYCbCrEPK13native_handlejRKNS_4RectEP13android_ycbcr`
- **`libshim_vtservice.so`**: Shims MediaTek Video Telephony (ViLTE) service entry points.

---

## License
- Xiaomi Blossom Device and Kernel Architecture maintained by crDroid Android and LineageOS.
- Apache 2.0 License.
