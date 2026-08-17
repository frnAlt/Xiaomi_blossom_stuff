#!/usr/bin/env python3
"""
Xiaomi Blossom Flashable Magisk / KernelSU Module Packager.
Compresses and validates the GSI Notch & Overlay Fix module into a flashable ZIP.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
import zipfile
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MagiskPackager")


def build_magisk_zip(module_dir: Path, output_zip: Path) -> bool:
    """Packages module directory into a standard flashable ZIP."""
    if not module_dir.exists():
        logger.error(f"Module directory not found: {module_dir}")
        return False

    prop_file = module_dir / "module.prop"
    if not prop_file.exists():
        logger.error("module.prop is missing from module directory!")
        return False

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Creating Magisk flashable ZIP: {output_zip}...")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root_path, _, file_names in sorted(module_dir.walk() if hasattr(module_dir, 'walk') else []):
            pass
        # Fallback for Python < 3.12 compatibility
        for file_path in sorted(module_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(module_dir)
                zf.write(file_path, arcname)
                logger.debug(f"  Added: {arcname}")

    # Calculate SHA256
    hasher = hashlib.sha256()
    with open(output_zip, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)

    logger.info(f"✅ Successfully built: {output_zip.name}")
    logger.info(f"  -> Size: {output_zip.stat().st_size} bytes")
    logger.info(f"  -> SHA256: {hasher.hexdigest()}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Blossom Magisk Overlay Module ZIP")
    parser.add_argument("--module-dir", type=Path, default=Path(__file__).parent.parent / "magisk_overlay_module", help="Path to magisk module source folder")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent.parent / "Blossom_Notch_Fix_Magisk.zip", help="Path for output ZIP file")

    args = parser.parse_args()
    success = build_magisk_zip(args.module_dir, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
