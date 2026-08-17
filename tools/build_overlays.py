#!/usr/bin/env python3
"""
Xiaomi Blossom RRO Overlay Automated Compiler and Signer.
Compiles RRO overlays using aapt, aligns with zipalign, and signs with apksigner.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("OverlayBuilder")


class OverlayCompiler:
    """Compiles Android Runtime Resource Overlays (RRO) into signed APKs."""

    def __init__(
        self,
        framework_res: Path = Path("/usr/share/android-framework-res/framework-res.apk"),
        keystore: Optional[Path] = None,
        ks_pass: str = "android",
        key_alias: str = "androiddebugkey"
    ) -> None:
        self.framework_res = framework_res
        self.keystore = keystore or Path.home() / "test.keystore"
        self.ks_pass = ks_pass
        self.key_alias = key_alias
        self._validate_tools()

    def _validate_tools(self) -> None:
        for tool in ["aapt", "zipalign", "apksigner"]:
            if not shutil.which(tool):
                raise RuntimeError(f"Required Android build tool '{tool}' not found in PATH.")

    def compile_rro(self, source_dir: Path, output_apk: Path) -> bool:
        """Compiles a source RRO folder into a signed, aligned overlay APK."""
        manifest = source_dir / "AndroidManifest.xml"
        res_dir = source_dir / "res"

        if not manifest.exists() or not res_dir.exists():
            logger.warning(f"Skipping {source_dir.name}: missing AndroidManifest.xml or res/ directory.")
            return False

        logger.info(f"Building RRO Overlay: {source_dir.name} -> {output_apk.name}")
        output_apk.parent.mkdir(parents=True, exist_ok=True)
        unaligned_apk = output_apk.parent / f"{output_apk.stem}.unaligned.apk"

        # 1. Compile with aapt
        aapt_cmd: List[str] = [
            "aapt", "package", "-f",
            "-M", str(manifest),
            "-S", str(res_dir),
            "-I", str(self.framework_res),
            "-F", str(unaligned_apk)
        ]
        res = subprocess.run(aapt_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"aapt failed for {source_dir.name}:\n{res.stderr}")
            return False

        # 2. Align with zipalign (4-byte alignment)
        if output_apk.exists():
            output_apk.unlink()

        zipalign_cmd = ["zipalign", "-v", "4", str(unaligned_apk), str(output_apk)]
        res = subprocess.run(zipalign_cmd, capture_output=True, text=True)
        unaligned_apk.unlink(missing_ok=True)
        if res.returncode != 0:
            logger.error(f"zipalign failed for {output_apk.name}:\n{res.stderr}")
            return False

        # 3. Sign with apksigner (v1 + v2 + v3 scheme)
        sign_cmd = [
            "apksigner", "sign",
            "--ks", str(self.keystore),
            "--ks-pass", f"pass:{self.ks_pass}",
            "--ks-key-alias", self.key_alias,
            "--key-pass", f"pass:{self.ks_pass}",
            str(output_apk)
        ]
        res = subprocess.run(sign_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"apksigner failed for {output_apk.name}:\n{res.stderr}")
            return False

        logger.info(f"Successfully compiled, aligned, and signed: {output_apk.name}")
        return True

    def build_all(self, rro_root: Path, out_dir: Path) -> None:
        """Recursively builds all overlays found inside rro_root."""
        for item in rro_root.iterdir():
            if item.is_dir() and (item / "AndroidManifest.xml").exists():
                out_apk = out_dir / f"{item.name}.apk"
                self.compile_rro(item, out_apk)


def main() -> None:
    parser = argparse.ArgumentParser(description="Xiaomi Blossom Overlay Automated Builder")
    parser.add_argument("--rro-dir", type=Path, default=Path(__file__).parent.parent / "rro_overlays", help="Path to rro_overlays directory")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent.parent / "apks", help="Output directory for compiled APKs")
    args = parser.parse_args()

    compiler = OverlayCompiler()
    compiler.build_all(args.rro_dir, args.output_dir)


if __name__ == "__main__":
    main()
