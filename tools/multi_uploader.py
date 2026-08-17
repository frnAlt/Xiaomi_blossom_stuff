#!/usr/bin/env python3
"""
Xiaomi Blossom Multi-Mirror ROM Uploader.
Uploads built ROMs to high-speed cloud mirrors (Pixeldrain, GoFile, Transfer.sh, Custom URL)
and generates a structured markdown download table with checksums.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MultiUploader")


class MultiMirrorUploader:
    """Uploads ROM artifacts to multiple public and custom mirrors."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        if not self.file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        self.size_mb = self.file_path.stat().st_size / (1024 * 1024)
        self.sha256 = hashlib.sha256(self.file_path.read_bytes()).hexdigest()
        self.md5 = hashlib.md5(self.file_path.read_bytes()).hexdigest()

    def upload_pixeldrain(self) -> Optional[str]:
        """Uploads file to Pixeldrain API."""
        logger.info("Uploading to Pixeldrain...")
        try:
            cmd = [
                "curl", "-s", "-X", "POST",
                "-F", f"file=@{self.file_path}",
                "https://pixeldrain.com/api/file"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            if data.get("success"):
                file_id = data["id"]
                url = f"https://pixeldrain.com/u/{file_id}"
                logger.info(f"✅ Pixeldrain link: {url}")
                return url
        except Exception as e:
            logger.warning(f"Pixeldrain upload failed: {e}")
        return None

    def upload_transfer_sh(self) -> Optional[str]:
        """Uploads file to Transfer.sh."""
        logger.info("Uploading to Transfer.sh...")
        try:
            cmd = [
                "curl", "-s", "--upload-file", str(self.file_path),
                f"https://transfer.sh/{self.file_path.name}"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            url = res.stdout.strip()
            if url.startswith("http"):
                logger.info(f"✅ Transfer.sh link: {url}")
                return url
        except Exception as e:
            logger.warning(f"Transfer.sh upload failed: {e}")
        return None

    def upload_custom(self, custom_url: str) -> Optional[str]:
        """Uploads to custom user-provided endpoint."""
        logger.info(f"Uploading to custom URL: {custom_url}...")
        try:
            cmd = ["curl", "-s", "-T", str(self.file_path), custom_url]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"✅ Custom upload completed.")
            return custom_url
        except Exception as e:
            logger.warning(f"Custom upload failed: {e}")
        return None

    def generate_markdown_summary(self, mirrors: Dict[str, str]) -> str:
        """Creates a formatted markdown summary table with download mirrors and checksums."""
        lines = [
            f"## 📦 ROM Download & Integrity Summary",
            f"- **Filename:** `{self.file_path.name}`",
            f"- **Size:** `{self.size_mb:.2f} MB`",
            f"- **MD5:** `{self.md5}`",
            f"- **SHA256:** `{self.sha256}`\n",
            "| Mirror Provider | Download Link | Status |",
            "|---|---|---|"
        ]

        for provider, link in mirrors.items():
            lines.append(f"| **{provider}** | [Download Here]({link}) | ✅ Live |")

        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Mirror ROM Uploader")
    parser.add_argument("--file", type=Path, required=True, help="Path to ROM archive to upload")
    parser.add_argument("--custom-url", type=str, help="Optional custom upload endpoint")
    parser.add_argument("--output-md", type=Path, help="Output markdown summary file")

    args = parser.parse_args()
    uploader = MultiMirrorUploader(args.file)
    mirrors: Dict[str, str] = {}

    # Upload to mirrors
    if args.custom_url:
        custom_res = uploader.upload_custom(args.custom_url)
        if custom_res:
            mirrors["Custom Endpoint"] = custom_res

    pd_url = uploader.upload_pixeldrain()
    if pd_url:
        mirrors["Pixeldrain"] = pd_url

    tr_url = uploader.upload_transfer_sh()
    if tr_url:
        mirrors["Transfer.sh"] = tr_url

    summary = uploader.generate_markdown_summary(mirrors)
    print(summary)

    if args.output_md:
        args.output_md.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
