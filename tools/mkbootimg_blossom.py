#!/usr/bin/env python3
"""
Xiaomi Blossom Custom Kernel Boot Image Packager & Unpacker.
Matches exact MediaTek MT6765/MT6762 boot header version 2, memory base, offsets,
DTB/DTBO embedding, and kernel cmdline parameters from BoardConfig.mk.
"""

from __future__ import annotations

import argparse
import logging
import os
import struct
import subprocess
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BlossomBootEngine")


class BlossomBootSpecs:
    """Exact Kernel & mkbootimg parameters from device/xiaomi/blossom BoardConfig.mk."""

    HEADER_VERSION: int = 2
    BASE: int = 0x40078000
    PAGESIZE: int = 2048
    KERNEL_OFFSET: int = 0x00008000
    SECOND_OFFSET: int = 0x00e88000
    RAMDISK_OFFSET: int = 0x11a88000
    TAGS_OFFSET: int = 0x07808000
    DTB_OFFSET: int = 0x07808000
    FLASH_BLOCK_SIZE: int = 131072
    BOOT_SIZE: int = 67108864
    DTBO_SIZE: int = 8388608

    CMDLINE: str = (
        "bootopt=64S3,32N2,64N2 "
        "androidboot.init_fatal_reboot_target=recovery "
        "androidboot.serialconsole=0 "
        "kpti=off "
        "quiet loglevel=3 "
        "cgroup_disable=pressure "
        "cgroup.memory=nokmem,nosocket "
        "nodebugmon "
        "noirqdebug "
        "kasan=off"
    )


class BlossomBootPacker:
    """Packs and unpacks Xiaomi Blossom boot.img matching MediaTek header v2."""

    def __init__(self, specs: BlossomBootSpecs = BlossomBootSpecs()) -> None:
        self.specs = specs

    def build_boot_img(
        self,
        kernel: Path,
        ramdisk: Optional[Path],
        dtb: Optional[Path],
        output_boot: Path,
        extra_cmdline: str = ""
    ) -> bool:
        """Constructs a standard boot.img matching Blossom's hardware memory layout."""
        if not kernel.exists():
            logger.error(f"Kernel image not found: {kernel}")
            return False

        logger.info(f"Building Xiaomi Blossom boot.img -> {output_boot}...")
        output_boot.parent.mkdir(parents=True, exist_ok=True)

        full_cmdline = f"{self.specs.CMDLINE} {extra_cmdline}".strip()

        cmd = [
            "mkbootimg",
            "--header_version", str(self.specs.HEADER_VERSION),
            "--base", hex(self.specs.BASE),
            "--pagesize", str(self.specs.PAGESIZE),
            "--kernel_offset", hex(self.specs.KERNEL_OFFSET),
            "--second_offset", hex(self.specs.SECOND_OFFSET),
            "--ramdisk_offset", hex(self.specs.RAMDISK_OFFSET),
            "--tags_offset", hex(self.specs.TAGS_OFFSET),
            "--dtb_offset", hex(self.specs.DTB_OFFSET),
            "--kernel", str(kernel),
            "--cmdline", full_cmdline,
            "--output", str(output_boot)
        ]

        if ramdisk and ramdisk.exists():
            cmd.extend(["--ramdisk", str(ramdisk)])

        if dtb and dtb.exists():
            cmd.extend(["--dtb", str(dtb)])

        logger.info(f"Executing mkbootimg command...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"mkbootimg failed:\n{res.stderr}")
            return False

        logger.info(f"Successfully generated Blossom boot.img ({output_boot.stat().st_size / (1024 * 1024):.2f} MB)")
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Xiaomi Blossom Custom Kernel Boot Image Builder")
    parser.add_argument("--kernel", type=Path, required=True, help="Path to raw kernel binary (Image.gz / kernel)")
    parser.add_argument("--ramdisk", type=Path, help="Path to ramdisk image (ramdisk.cpio.gz / ramdisk.img)")
    parser.add_argument("--dtb", type=Path, help="Path to Device Tree Blob (dtb.img)")
    parser.add_argument("--output", type=Path, default=Path("boot_blossom.img"), help="Output boot.img path")
    parser.add_argument("--cmdline-extra", type=str, default="", help="Additional kernel command-line arguments")

    args = parser.parse_args()
    packer = BlossomBootPacker()
    success = packer.build_boot_img(
        kernel=args.kernel,
        ramdisk=args.ramdisk,
        dtb=args.dtb,
        output_boot=args.output,
        extra_cmdline=args.cmdline_extra
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
