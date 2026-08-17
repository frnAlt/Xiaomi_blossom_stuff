#!/usr/bin/env python3
"""
Xiaomi Blossom Super Partition & AVB Engine.
Developer-grade tools for lpmake / lpunpack, super.img generation,
AVB vbmeta patching (verity bypass), and Fastboot flashing script generation.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SuperTools")


class BlossomPartitionSpecs:
    """Exact partition and hardware geometry from device/xiaomi/blossom BoardConfig.mk."""

    # Partition limits (in bytes)
    SUPER_PARTITION_SIZE: int = 4831838208    # 4608 MiB
    MAIN_GROUP_SIZE: int = 4829741056         # SUPER_SIZE - 2 MiB
    BOOT_PARTITION_SIZE: int = 67108864       # 64 MiB
    DTBO_PARTITION_SIZE: int = 8388608        # 8 MiB
    RECOVERY_PARTITION_SIZE: int = 67108864   # 64 MiB
    BLOCK_SIZE: int = 4096                    # 4 KiB block size
    METADATA_SIZE: int = 65536                # 64 KiB
    METADATA_SLOTS: int = 2


class SuperImageBuilder:
    """Handles unpacking, rebuilding, and sparsing super.img for Xiaomi Blossom."""

    def __init__(self, specs: BlossomPartitionSpecs = BlossomPartitionSpecs()) -> None:
        self.specs = specs

    def patch_vbmeta_disable_verification(self, vbmeta_input: Path, vbmeta_output: Path) -> bool:
        """
        Patches vbmeta.img binary directly to set flags=0x03 (DISABLE_VERITY | DISABLE_VERIFICATION).
        Ensures ported ROM boots without AVB signature mismatch bootloops.
        """
        logger.info(f"Patching AVB flags in {vbmeta_input.name} -> {vbmeta_output.name}...")
        if not vbmeta_input.exists():
            logger.warning(f"vbmeta file {vbmeta_input} does not exist. Generating empty patched vbmeta...")
            self.generate_clean_vbmeta(vbmeta_output)
            return True

        data = bytearray(vbmeta_input.read_bytes())
        magic_offset = data.find(b"AVB0")
        if magic_offset == -1:
            logger.warning("Could not find AVB0 magic in vbmeta image.")
            return False

        flags_offset = magic_offset + 120
        if len(data) >= flags_offset + 4:
            struct.pack_into(">I", data, flags_offset, 3)
            vbmeta_output.parent.mkdir(parents=True, exist_ok=True)
            vbmeta_output.write_bytes(data)
            logger.info("vbmeta patched: dm-verity and verification successfully disabled.")
            return True
        return False

    def generate_clean_vbmeta(self, output_path: Path) -> None:
        """Creates a minimal valid AVB vbmeta image with verification disabled."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        buf = bytearray(65536)
        buf[0:4] = b"AVB0"
        struct.pack_into(">II", buf, 4, 1, 0)
        struct.pack_into(">I", buf, 120, 3)
        output_path.write_bytes(buf)
        logger.info(f"Generated clean disabled vbmeta image at {output_path}")

    def build_super_image(
        self,
        partition_images: Dict[str, Path],
        output_super: Path,
        sparse: bool = True
    ) -> bool:
        """
        Builds a dynamic partition super.img matching Xiaomi Blossom's exact partition table using lpmake.
        """
        logger.info("Constructing super.img with Blossom partition geometry...")
        output_super.parent.mkdir(parents=True, exist_ok=True)

        lpmake_bin = shutil.which("lpmake")
        if not lpmake_bin:
            for cand in ["/usr/local/bin/lpmake", "/usr/bin/lpmake", "./tools/bin/lpmake"]:
                if Path(cand).exists():
                    lpmake_bin = cand
                    break

        if not lpmake_bin:
            logger.error("lpmake is required to build dynamic partition super.img!")
            return False

        cmd = [
            lpmake_bin,
            "--metadata-size", str(self.specs.METADATA_SIZE),
            "--super-name", "super",
            "--metadata-slots", str(self.specs.METADATA_SLOTS),
            "--device", f"super:{self.specs.SUPER_PARTITION_SIZE}",
            "--group", f"main:{self.specs.MAIN_GROUP_SIZE}",
        ]

        if sparse:
            cmd.append("--sparse")

        total_part_size = 0
        for part_name, img_path in partition_images.items():
            if img_path.exists() and img_path.stat().st_size > 0:
                size = img_path.stat().st_size
                total_part_size += size
                cmd.extend([
                    "--partition", f"{part_name}:readonly:{size}:main",
                    "--image", f"{part_name}={img_path}"
                ])
                logger.info(f"  Partition '{part_name}': {size / (1024 * 1024):.2f} MB ({img_path.name})")

        if total_part_size > self.specs.MAIN_GROUP_SIZE:
            logger.error(f"Total partitions size ({total_part_size}) exceeds main group limit ({self.specs.MAIN_GROUP_SIZE})!")
            return False

        cmd.extend(["--output", str(output_super)])

        logger.info("Executing lpmake command...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"lpmake failed:\n{res.stderr}")
            return False

        logger.info(f"super.img created successfully: {output_super.name} ({output_super.stat().st_size / (1024 * 1024):.2f} MB)")
        return True

    def generate_flashing_scripts(self, output_dir: Path, rom_title: str = "Xiaomi Blossom Custom Port") -> None:
        """Generates cross-platform fastboot flashing scripts for Windows (.bat) and Linux/macOS (.sh)."""
        logger.info("Generating Windows & Linux Fastboot flashing automation scripts...")

        # 1. Linux / macOS Bash script
        sh_content = f'''#!/usr/bin/env bash
# ==============================================================================
# {rom_title} - Fastboot Flasher for Xiaomi Blossom (Redmi 9A/9C/9 Activ)
# ==============================================================================

set -e
echo "=================================================================="
echo " Flashing {rom_title} to Xiaomi Blossom"
echo "=================================================================="

if ! fastboot devices | grep -q "fastboot"; then
    echo "Error: No device detected in fastboot mode. Please connect phone in Fastboot mode."
    exit 1
fi

echo ">> 1. Flashing Kernel (boot.img) & DTBO..."
fastboot flash boot boot.img
if [ -f "dtbo.img" ]; then
    fastboot flash dtbo dtbo.img
fi

echo ">> 2. Flashing AVB VBMeta with verity disabled..."
if [ -f "vbmeta.img" ]; then
    fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img
fi
if [ -f "vbmeta_system.img" ]; then
    fastboot flash vbmeta_system --disable-verity --disable-verification vbmeta_system.img || true
fi
if [ -f "vbmeta_vendor.img" ]; then
    fastboot flash vbmeta_vendor --disable-verity --disable-verification vbmeta_vendor.img || true
fi

echo ">> 3. Rebooting into FastbootD (Dynamic Partition Mode)..."
fastboot reboot fastboot
sleep 5

echo ">> 4. Flashing Dynamic Partitions (super.img)..."
if [ -f "super.img" ]; then
    fastboot flash super super.img
fi

echo ">> 5. Wiping Userdata & Cache..."
fastboot -w || true

echo ">> 6. Rebooting into System..."
fastboot reboot

echo "=================================================================="
echo " Flashing Complete! Your device is now rebooting."
echo "=================================================================="
'''
        (output_dir / "flash_all.sh").write_text(sh_content, encoding="utf-8")
        subprocess.run(["chmod", "+x", str(output_dir / "flash_all.sh")], check=False)

        # 2. Windows Batch script
        bat_content = f'''@echo off
:: ==============================================================================
:: {rom_title} - Windows Fastboot Flasher for Xiaomi Blossom
:: ==============================================================================

title {rom_title} Flasher
color 0B

echo ==================================================================
echo  Flashing {rom_title} to Xiaomi Blossom
echo ==================================================================
echo.

fastboot devices
echo.

echo >> 1. Flashing Kernel (boot.img) ^& DTBO...
fastboot flash boot boot.img
if exist dtbo.img fastboot flash dtbo dtbo.img

echo >> 2. Flashing AVB VBMeta with verity disabled...
if exist vbmeta.img fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img
if exist vbmeta_system.img fastboot flash vbmeta_system --disable-verity --disable-verification vbmeta_system.img
if exist vbmeta_vendor.img fastboot flash vbmeta_vendor --disable-verity --disable-verification vbmeta_vendor.img

echo >> 3. Rebooting into FastbootD (Dynamic Partitions)...
fastboot reboot fastboot
timeout /t 5

echo >> 4. Flashing Dynamic Partitions (super.img)...
if exist super.img fastboot flash super super.img

echo >> 5. Formatting Userdata ^& Cache...
fastboot -w

echo >> 6. Rebooting into System...
fastboot reboot

echo.
echo ==================================================================
echo  Flashing Complete! Press any key to exit.
echo ==================================================================
pause
'''
        (output_dir / "flash_all.bat").write_text(bat_content, encoding="utf-8")
        logger.info("  -> Created flash_all.sh and flash_all.bat successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Xiaomi Blossom Super Partition & AVB Tools")
    parser.add_argument("--patch-vbmeta", type=Path, help="Input vbmeta.img to patch with verity disabled")
    parser.add_argument("--out-vbmeta", type=Path, default=Path("vbmeta_patched.img"), help="Output path for patched vbmeta.img")
    parser.add_argument("--gen-scripts", type=Path, help="Directory to generate flash_all.sh and flash_all.bat")

    args = parser.parse_args()
    builder = SuperImageBuilder()

    if args.patch_vbmeta:
        builder.patch_vbmeta_disable_verification(args.patch_vbmeta, args.out_vbmeta)

    if args.gen_scripts:
        builder.generate_flashing_scripts(args.gen_scripts)


if __name__ == "__main__":
    main()
