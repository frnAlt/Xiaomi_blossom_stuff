#!/usr/bin/env python3
"""
Xiaomi Blossom Heavy-Duty Firmware & ROM Dumper Engine.
Comprehensive partition extraction pipeline supporting payload.bin, super.img (lpunpack),
brotli .new.dat.br, EROFS, EXT4, Sparse images, and proprietary archive formats.
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
from typing import Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("RomDumper")


class HeavyRomDumper:
    """Production-grade firmware unpacker and partition analyzer."""

    KNOWN_PARTITIONS: List[str] = [
        "system", "system_ext", "vendor", "product", "odm", "cust",
        "boot", "dtbo", "vbmeta", "vbmeta_system", "vbmeta_vendor",
        "recovery", "persist", "metadata", "userdata"
    ]

    def __init__(self, work_dir: Path, output_dir: Path) -> None:
        self.work_dir = work_dir
        self.output_dir = output_dir
        self.raw_images_dir = self.output_dir / "raw_images"
        self.extracted_fs_dir = self.output_dir / "extracted_partitions"
        self.configs_dir = self.output_dir / "device_configs"

        for d in [self.work_dir, self.output_dir, self.raw_images_dir, self.extracted_fs_dir, self.configs_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def download_rom(self, url: str) -> Path:
        """Downloads ROM file via aria2c or curl."""
        logger.info(f"Downloading firmware package: {url}")
        dest_dir = self.work_dir / "download"
        dest_dir.mkdir(parents=True, exist_ok=True)

        url_clean = url.split("?")[0]
        filename = Path(url_clean).name or "firmware_package.zip"
        dest_file = dest_dir / filename

        if shutil.which("aria2c"):
            cmd = [
                "aria2c", "-x", "16", "-s", "16", "-j", "16",
                "-k", "1M", "--check-certificate=false",
                "-d", str(dest_dir), "-o", dest_file.name,
                url
            ]
        else:
            cmd = ["curl", "-L", "-k", "-o", str(dest_file), url]

        subprocess.run(cmd, check=True)
        logger.info(f"Downloaded: {dest_file.name} ({dest_file.stat().st_size / (1024 * 1024):.2f} MB)")
        return dest_file

    def extract_outer_archive(self, archive_path: Path) -> Path:
        """Extracts top-level container archives (.zip, .tgz, .tar.gz, .7z, .tar)."""
        logger.info(f"Extracting outer archive: {archive_path.name}...")
        stage_dir = self.work_dir / "unpacked_stage"
        stage_dir.mkdir(parents=True, exist_ok=True)

        ext = archive_path.suffix.lower()
        if ext == ".tgz" or archive_path.name.endswith(".tar.gz"):
            subprocess.run(["tar", "-xzf", str(archive_path), "-C", str(stage_dir)], check=True)
        elif ext == ".tar":
            subprocess.run(["tar", "-xf", str(archive_path), "-C", str(stage_dir)], check=True)
        elif ext == ".zip":
            if shutil.which("7z"):
                subprocess.run(["7z", "x", "-y", f"-o{stage_dir}", str(archive_path)], check=True)
            else:
                subprocess.run(["unzip", "-q", "-o", str(archive_path), "-d", str(stage_dir)], check=True)
        else:
            subprocess.run(["7z", "x", "-y", f"-o{stage_dir}", str(archive_path)], check=True)

        return stage_dir

    def extract_payload_bin(self, search_dir: Path) -> bool:
        """Extracts payload.bin if found inside stage directory."""
        payload_file = None
        for p in search_dir.rglob("payload.bin"):
            payload_file = p
            break

        if not payload_file:
            return False

        logger.info(f"Detected OTA payload.bin ({payload_file.stat().st_size / (1024 * 1024):.2f} MB)...")
        if shutil.which("payload-dumper-go"):
            subprocess.run(["payload-dumper-go", "-o", str(self.raw_images_dir), str(payload_file)], check=True)
            return True
        elif shutil.which("7z"):
            subprocess.run(["7z", "x", "-y", f"-o{self.raw_images_dir}", str(payload_file)], check=True)
            return True
        return False

    def unsparse_and_unpack_super(self, search_dir: Path) -> bool:
        """Finds super.img, converts sparse to raw, and unpacks dynamic partitions via lpunpack."""
        super_img = None
        for p in search_dir.rglob("super.img"):
            super_img = p
            break

        if not super_img:
            return False

        logger.info(f"Detected super.img ({super_img.stat().st_size / (1024 * 1024):.2f} MB)...")
        raw_super = self.work_dir / "super.raw.img"

        # Check if sparse
        if shutil.which("simg2img"):
            logger.info("Converting sparse super.img to raw...")
            res = subprocess.run(["simg2img", str(super_img), str(raw_super)], capture_output=True)
            if res.returncode != 0:
                raw_super = super_img
        else:
            raw_super = super_img

        # Unpack with lpunpack
        if shutil.which("lpunpack"):
            logger.info("Unpacking dynamic partitions using lpunpack...")
            subprocess.run(["lpunpack", str(raw_super), str(self.raw_images_dir)], check=True)
            return True
        elif shutil.which("7z"):
            subprocess.run(["7z", "x", "-y", f"-o{self.raw_images_dir}", str(raw_super)], check=True)
            return True

        return False

    def handle_brotli_sdat(self, search_dir: Path) -> None:
        """Converts *.new.dat.br and *.new.dat into raw partition images."""
        for br_file in search_dir.rglob("*.new.dat.br"):
            part_name = br_file.name.replace(".new.dat.br", "")
            logger.info(f"Decompressing brotli partition: {br_file.name}...")
            dat_file = self.work_dir / f"{part_name}.new.dat"
            subprocess.run(["brotli", "-d", str(br_file), "-o", str(dat_file)], check=True)

            transfer_file = search_dir / f"{part_name}.transfer.list"
            if not transfer_file.exists():
                for cand in search_dir.rglob(f"{part_name}.transfer.list"):
                    transfer_file = cand
                    break

            if transfer_file and transfer_file.exists():
                out_img = self.raw_images_dir / f"{part_name}.img"
                logger.info(f"Converting sdat to raw image: {out_img.name}...")
                sdat2img_py = Path(__file__).parent / "sdat2img.py"
                if sdat2img_py.exists():
                    subprocess.run(["python3", str(sdat2img_py), str(transfer_file), str(dat_file), str(out_img)], check=True)

    def extract_filesystem_trees(self) -> None:
        """Extracts filesystem contents from raw images using 7z or erofs/ext4 tools."""
        logger.info("Extracting filesystem trees for partition inspection...")
        for img in self.raw_images_dir.rglob("*.img"):
            part_name = img.stem
            dest = self.extracted_fs_dir / part_name
            dest.mkdir(parents=True, exist_ok=True)

            logger.info(f"Extracting filesystem: {img.name} -> {dest.name}/...")
            if shutil.which("7z"):
                subprocess.run(["7z", "x", "-y", f"-o{dest}", str(img)], capture_output=True)

    def aggregate_build_props(self) -> Path:
        """Collects and aggregates build.prop files from all partitions."""
        logger.info("Aggregating build properties...")
        props_file = self.configs_dir / "all_build_props.prop"
        all_props: List[str] = [
            f"# Aggregated Build Properties",
            f"# Dump Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"# Target Output Directory: {self.output_dir.name}\n"
        ]

        for prop_path in self.output_dir.rglob("build.prop"):
            rel = prop_path.relative_to(self.output_dir)
            all_props.append(f"\n# --- Source: {rel} ---")
            try:
                all_props.append(prop_path.read_text(encoding="utf-8", errors="ignore"))
            except Exception as e:
                logger.warning(f"Could not read {prop_path}: {e}")

        props_file.write_text("\n".join(all_props), encoding="utf-8")
        logger.info(f"Wrote consolidated properties to: {props_file.name}")
        return props_file

    def generate_dump_manifest(self) -> Path:
        """Generates JSON manifest containing file sizes, SHA256 hashes, and partition table."""
        logger.info("Generating dump manifest and checksums...")
        manifest_data = {
            "dump_engine": "Xiaomi Blossom Heavy-Duty Dumper",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "raw_images": {},
            "extracted_partitions": []
        }

        for img in sorted(self.raw_images_dir.glob("*.img")):
            size = img.stat().st_size
            sha256 = hashlib.sha256(img.read_bytes()).hexdigest()
            manifest_data["raw_images"][img.name] = {
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "sha256": sha256
            }

        for part_dir in sorted(self.extracted_fs_dir.iterdir()):
            if part_dir.is_dir():
                manifest_data["extracted_partitions"].append(part_dir.name)

        manifest_file = self.output_dir / "dump_manifest.json"
        manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        return manifest_file

    def package_dump(self, archive_name: str = "blossom_firmware_dump") -> Path:
        """Compresses the full dump output into a high-ratio Zstandard or 7z archive."""
        out_archive = self.work_dir / f"{archive_name}.tar.zst"
        logger.info(f"Packaging firmware dump into {out_archive.name}...")

        if shutil.which("tar") and shutil.which("zstd"):
            cmd = ["tar", "-I", "zstd -T0 -19", "-cf", str(out_archive), "-C", str(self.output_dir.parent), self.output_dir.name]
            subprocess.run(cmd, check=True)
        else:
            out_archive = self.work_dir / f"{archive_name}.7z"
            cmd = ["7z", "a", "-t7z", "-m0=lzma2", "-mx=9", "-mfb=64", "-md=32m", "-ms=on", str(out_archive), str(self.output_dir)]
            subprocess.run(cmd, check=True)

        logger.info(f"Dump package built: {out_archive.name} ({out_archive.stat().st_size / (1024 * 1024):.2f} MB)")
        return out_archive


def main() -> None:
    parser = argparse.ArgumentParser(description="Xiaomi Blossom Heavy-Duty ROM Dumper")
    parser.add_argument("--url", type=str, help="Direct download URL of firmware archive")
    parser.add_argument("--file", type=Path, help="Local firmware package file")
    parser.add_argument("--work-dir", type=Path, default=Path("/tmp/blossom_dumper_work"), help="Working directory")
    parser.add_argument("--out-dir", type=Path, default=Path("/tmp/blossom_dumper_out"), help="Output dump directory")
    parser.add_argument("--package-name", type=str, default="blossom_firmware_dump", help="Archive output name")

    args = parser.parse_args()
    dumper = HeavyRomDumper(work_dir=args.work_dir, output_dir=args.out_dir)

    if args.url:
        archive = dumper.download_rom(args.url)
    elif args.file:
        archive = args.file
    else:
        logger.error("Must provide --url or --file argument.")
        sys.exit(1)

    stage = dumper.extract_outer_archive(archive)
    dumper.extract_payload_bin(stage)
    dumper.unsparse_and_unpack_super(stage)
    dumper.handle_brotli_sdat(stage)

    # Collect any standalone images from stage
    for img in stage.rglob("*.img"):
        target = dumper.raw_images_dir / img.name
        if not target.exists():
            shutil.copy2(img, target)

    dumper.extract_filesystem_trees()
    dumper.aggregate_build_props()
    dumper.generate_dump_manifest()
    packaged = dumper.package_dump(args.package_name)

    print("\n" + "=" * 50)
    print(" FIRMWARE DUMP COMPLETED SUCCESSFULLY")
    print(f" Output Package: {packaged}")
    print("=" * 50)


if __name__ == "__main__":
    main()
