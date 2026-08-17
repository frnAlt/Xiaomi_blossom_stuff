#!/usr/bin/env python3
"""
Xiaomi Blossom Automated End-to-End ROM Porting Engine.
Handles automatic downloading, partition extraction, merging, overlay/shim injection,
repacking, and upload for GitHub Actions and local developers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ensure tools directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent))
from port_helper import BlossomPortEngine

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AutoPorter")


class AutoPorter:
    """Automated ROM Porting orchestrator for Xiaomi Blossom."""

    def __init__(
        self,
        work_dir: Path,
        repo_root: Optional[Path] = None,
        variant: str = "blossom",
        rom_type: str = "MIUI"
    ) -> None:
        self.work_dir = work_dir
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.variant = variant
        self.rom_type = rom_type

        self.base_dir = self.work_dir / "base"
        self.port_dir = self.work_dir / "port"
        self.out_dir = self.work_dir / "output"
        self.build_dir = self.work_dir / "build_root"

        for d in [self.base_dir, self.port_dir, self.out_dir, self.build_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.engine = BlossomPortEngine(root_dir=self.repo_root)

    def download_file(self, url: str, dest_dir: Path, filename_hint: str = "rom_package") -> Path:
        """Downloads a ROM archive using aria2c or curl."""
        logger.info(f"Downloading from: {url}")
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Detect filename from URL or default
        url_clean = url.split("?")[0]
        name = Path(url_clean).name or f"{filename_hint}.zip"
        target_file = dest_dir / name

        if shutil.which("aria2c"):
            cmd = [
                "aria2c", "-x", "16", "-s", "16", "-j", "16",
                "-k", "1M", "--check-certificate=false",
                "-d", str(dest_dir), "-o", target_file.name,
                url
            ]
        else:
            cmd = ["curl", "-L", "-k", "-o", str(target_file), url]

        logger.info(f"Running download command: {' '.join(cmd[:3])}...")
        subprocess.run(cmd, check=True)
        logger.info(f"Downloaded: {target_file.name} ({target_file.stat().st_size} bytes)")
        return target_file

    def extract_archive(self, archive_path: Path, extract_to: Path) -> None:
        """Extracts archives (.zip, .tgz, .tar.gz, .7z, .tar)."""
        logger.info(f"Extracting {archive_path.name} to {extract_to}...")
        extract_to.mkdir(parents=True, exist_ok=True)

        ext = archive_path.suffix.lower()
        if ext == ".tgz" or archive_path.name.endswith(".tar.gz"):
            subprocess.run(["tar", "-xzf", str(archive_path), "-C", str(extract_to)], check=True)
        elif ext == ".tar":
            subprocess.run(["tar", "-xf", str(archive_path), "-C", str(extract_to)], check=True)
        elif ext == ".zip":
            if shutil.which("7z"):
                subprocess.run(["7z", "x", "-y", f"-o{extract_to}", str(archive_path)], check=True)
            else:
                subprocess.run(["unzip", "-q", "-o", str(archive_path), "-d", str(extract_to)], check=True)
        else:
            # Fallback 7z
            subprocess.run(["7z", "x", "-y", f"-o{extract_to}", str(archive_path)], check=True)

    def extract_payload_if_present(self, search_dir: Path, target_dir: Path) -> bool:
        """Extracts payload.bin if found inside search_dir."""
        payload_bin = None
        for p in search_dir.rglob("payload.bin"):
            payload_bin = p
            break

        if not payload_bin:
            return False

        logger.info(f"Found payload.bin at {payload_bin}. Extracting with payload-dumper-go...")
        target_dir.mkdir(parents=True, exist_ok=True)

        if shutil.which("payload-dumper-go"):
            subprocess.run(["payload-dumper-go", "-o", str(target_dir), str(payload_bin)], check=True)
            return True
        else:
            logger.warning("payload-dumper-go not found in PATH! Attempting 7z extraction...")
            subprocess.run(["7z", "x", "-y", f"-o{target_dir}", str(payload_bin)], check=True)
            return True

    def assemble_ported_firmware(self) -> Path:
        """
        Merges Blossom Base hardware components with Port ROM system/UI components,
        injects overlays, shims, carrier configs, and builds the flashable package.
        """
        logger.info("==================================================")
        logger.info(" ASSEMBLE PORTED FIRMWARE FOR XIAOMI BLOSSOM")
        logger.info("==================================================")

        # 1. Prepare build root structure
        merged_system = self.build_dir / "system"
        merged_vendor = self.build_dir / "vendor"
        merged_product = self.build_dir / "product"
        merged_system_ext = self.build_dir / "system_ext"

        for d in [merged_system, merged_vendor, merged_product, merged_system_ext]:
            d.mkdir(parents=True, exist_ok=True)

        # 2. Copy Base Hardware partitions (boot.img, dtbo, vendor)
        logger.info("Copying Blossom Base Hardware components (boot.img, vendor)...")
        # Search for boot.img
        boot_img = None
        for p in self.base_dir.rglob("boot.img"):
            boot_img = p
            shutil.copy2(p, self.build_dir / "boot.img")
            logger.info(f"  -> Preserved Base Kernel: {p.name}")
            break

        for dtbo in self.base_dir.rglob("dtbo.img"):
            shutil.copy2(dtbo, self.build_dir / "dtbo.img")
            logger.info("  -> Preserved Base DTBO")
            break

        # Search for vendor files in base
        base_vendor_src = None
        for candidate in ["vendor", "vendor_extracted", "images/vendor"]:
            cand_path = self.base_dir / candidate
            if cand_path.is_dir() and any(cand_path.iterdir()):
                base_vendor_src = cand_path
                break

        if base_vendor_src:
            shutil.copytree(base_vendor_src, merged_vendor, symlinks=True, dirs_exist_ok=True)
            logger.info(f"  -> Preserved Base Vendor from {base_vendor_src}")
        else:
            logger.info("  -> Copying vendor templates from Blossom Porting Kit...")
            if (self.repo_root / "xmls").exists():
                shutil.copytree(self.repo_root / "xmls", merged_vendor / "etc", symlinks=True, dirs_exist_ok=True)

        # 3. Copy Port ROM System/Product partitions
        logger.info("Copying Port ROM System, Product, System_ext components...")
        for part in ["system", "product", "system_ext"]:
            for cand in [self.port_dir / part, self.port_dir / f"{part}_extracted", self.port_dir / "images" / part]:
                if cand.is_dir():
                    target_dest = self.build_dir / part
                    shutil.copytree(cand, target_dest, symlinks=True, dirs_exist_ok=True)
                    logger.info(f"  -> Injected Port {part} from {cand}")
                    break

        # 4. Run Blossom Port Engine to inject overlays, shims, configs, props
        logger.info("Running Blossom Port Engine injection...")
        self.engine.run_port_pipeline(self.build_dir, variant=self.variant)

        # 5. Add Magisk module and rootdir scripts to output
        logger.info("Embedding Blossom Magisk Notch Fix module...")
        magisk_zip = self.repo_root / "Blossom_Notch_Fix_Magisk.zip"
        if magisk_zip.exists():
            shutil.copy2(magisk_zip, self.build_dir / "Blossom_Notch_Fix_Magisk.zip")

        # 6. Package final flashable archive
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        package_name = f"Blossom_Port_{self.rom_type}_{self.variant}_{timestamp}.zip"
        output_zip = self.out_dir / package_name

        logger.info(f"Packaging final Port ROM archive: {output_zip.name}...")
        with shutil.ZipFile if hasattr(shutil, 'ZipFile') else zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(self.build_dir.rglob("*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.build_dir)
                    zf.write(file_path, arcname)

        # Compute Checksums
        sha256 = hashlib.sha256(output_zip.read_bytes()).hexdigest()
        md5 = hashlib.md5(output_zip.read_bytes()).hexdigest()

        meta = {
            "device": "Xiaomi Blossom",
            "variant": self.variant,
            "rom_type": self.rom_type,
            "filename": output_zip.name,
            "size_bytes": output_zip.stat().st_size,
            "sha256": sha256,
            "md5": md5,
            "timestamp": timestamp
        }

        meta_file = self.out_dir / f"{package_name}.json"
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        logger.info("==================================================")
        logger.info(" ✅ PORTING COMPLETED SUCCESSFULLY!")
        logger.info(f"  • Output ROM: {output_zip.name}")
        logger.info(f"  • Size: {output_zip.stat().st_size / (1024 * 1024):.2f} MB")
        logger.info(f"  • SHA256: {sha256}")
        logger.info("==================================================")
        return output_zip

    def upload_custom_url(self, file_path: Path, upload_url: str) -> None:
        """Uploads completed ROM to a custom HTTP/HTTPS upload URL or Webhook."""
        logger.info(f"Uploading {file_path.name} to custom URL: {upload_url}...")
        try:
            cmd = ["curl", "-T", str(file_path), upload_url]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Upload response:\n{res.stdout}")
        except Exception as e:
            logger.error(f"Failed to upload to custom URL: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Xiaomi Blossom Automated ROM Porter")
    parser.add_argument("--base-url", type=str, help="Direct download URL for Base ROM (Stock Blossom Fastboot / ZIP)")
    parser.add_argument("--port-url", type=str, help="Direct download URL for Port ROM (Target ROM to port)")
    parser.add_argument("--base-file", type=Path, help="Local file path to Base ROM (if already downloaded)")
    parser.add_argument("--port-file", type=Path, help="Local file path to Port ROM (if already downloaded)")
    parser.add_argument("--variant", choices=["blossom", "dandelion", "angelica", "angelican", "cattail"], default="blossom", help="Device variant")
    parser.add_argument("--rom-type", default="CustomROM", help="Name/Type of ROM (MIUI, HyperOS, PixelOS, AOSP, etc.)")
    parser.add_argument("--work-dir", type=Path, default=Path("/tmp/blossom_auto_port"), help="Working directory")
    parser.add_argument("--upload-url", type=str, help="Optional custom upload URL (curl -T)")

    args = parser.parse_args()
    porter = AutoPorter(
        work_dir=args.work_dir,
        variant=args.variant,
        rom_type=args.rom_type
    )

    # 1. Get Base ROM
    if args.base_url:
        base_archive = porter.download_file(args.base_url, porter.work_dir / "base_downloads", "base_rom")
    elif args.base_file:
        base_archive = args.base_file
    else:
        logger.info("No Base ROM specified; using Blossom repository templates as base.")
        base_archive = None

    if base_archive and base_archive.exists():
        porter.extract_archive(base_archive, porter.base_dir)
        porter.extract_payload_if_present(porter.base_dir, porter.base_dir)

    # 2. Get Port ROM
    if args.port_url:
        port_archive = porter.download_file(args.port_url, porter.work_dir / "port_downloads", "port_rom")
    elif args.port_file:
        port_archive = args.port_file
    else:
        logger.error("Error: You must specify --port-url or --port-file!")
        sys.exit(1)

    if port_archive and port_archive.exists():
        porter.extract_archive(port_archive, porter.port_dir)
        porter.extract_payload_if_present(porter.port_dir, porter.port_dir)

    # 3. Assemble and build
    out_rom = porter.assemble_ported_firmware()

    # 4. Optional custom upload
    if args.upload_url:
        porter.upload_custom_url(out_rom, args.upload_url)


if __name__ == "__main__":
    import zipfile
    main()
