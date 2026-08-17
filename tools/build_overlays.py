#!/usr/bin/env python3
"""
Xiaomi Blossom Overlay Build & Sign Backend Tool.
Automates compilation, zip-alignment, and cryptographic signing of RRO Overlays.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BuildOverlays")


class OverlayBuilder:
    """Backend engine for compiling and signing Android RRO overlays."""

    def __init__(
        self,
        framework_res: Path,
        keystore_path: Path,
        keystore_pass: str = "android",
        key_alias: str = "androiddebugkey",
        key_pass: str = "android"
    ) -> None:
        self.framework_res = framework_res
        self.keystore_path = keystore_path
        self.keystore_pass = keystore_pass
        self.key_alias = key_alias
        self.key_pass = key_pass

        self._verify_dependencies()
        self._ensure_keystore()

    def _verify_dependencies(self) -> None:
        """Verifies that all required binary dependencies are present in PATH."""
        required_tools = ["aapt", "zipalign", "apksigner", "keytool"]
        for tool in required_tools:
            if shutil.which(tool) is None:
                logger.error(f"Missing required tool: {tool}. Please install it.")
                sys.exit(1)

        if not self.framework_res.exists():
            logger.error(f"Framework resource APK not found at: {self.framework_res}")
            sys.exit(1)

    def _ensure_keystore(self) -> None:
        """Generates a debug RSA keystore if one does not already exist."""
        if not self.keystore_path.exists():
            logger.info(f"Generating debug keystore at {self.keystore_path}...")
            cmd = [
                "keytool", "-genkey", "-v",
                "-keystore", str(self.keystore_path),
                "-alias", self.key_alias,
                "-storepass", self.keystore_pass,
                "-keypass", self.key_pass,
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-dname", "CN=Android Debug,O=Android,C=US"
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Debug keystore generated successfully.")

    def compile_overlay(
        self,
        manifest_path: Path,
        res_dir: Optional[Path],
        output_apk: Path
    ) -> bool:
        """
        Compiles an overlay package into an APK, aligns it to 4-byte boundaries,
        and cryptographically signs it.
        """
        temp_dir = Path("/tmp/overlay_build")
        temp_dir.mkdir(parents=True, exist_ok=True)

        unaligned_apk = temp_dir / f"{output_apk.stem}_unaligned.apk"
        aligned_apk = temp_dir / f"{output_apk.stem}_aligned.apk"

        # Step 1: aapt package
        aapt_cmd = [
            "aapt", "package", "-f",
            "-M", str(manifest_path),
            "-I", str(self.framework_res),
            "-F", str(unaligned_apk)
        ]
        if res_dir and res_dir.exists():
            aapt_cmd.extend(["-S", str(res_dir)])

        logger.debug(f"Running aapt: {' '.join(aapt_cmd)}")
        res = subprocess.run(aapt_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"aapt failed for {output_apk.name}:\n{res.stderr}")
            return False

        # Step 2: zipalign
        zipalign_cmd = ["zipalign", "-p", "-f", "4", str(unaligned_apk), str(aligned_apk)]
        subprocess.run(zipalign_cmd, check=True)

        # Step 3: apksigner
        output_apk.parent.mkdir(parents=True, exist_ok=True)
        apksigner_cmd = [
            "apksigner", "sign",
            "--ks", str(self.keystore_path),
            "--ks-pass", f"pass:{self.keystore_pass}",
            "--key-pass", f"pass:{self.key_pass}",
            "--out", str(output_apk),
            str(aligned_apk)
        ]
        subprocess.run(apksigner_cmd, check=True)

        logger.info(f"Generated: {output_apk.name} ({output_apk.stat().st_size} bytes)")
        return True

    def build_all(self, rro_dir: Path, output_dir: Path) -> Dict[str, bool]:
        """Builds all overlay folders discovered in the given directory."""
        results: Dict[str, bool] = {}
        for item in sorted(rro_dir.iterdir()):
            if item.is_dir():
                manifest = item / "AndroidManifest.xml"
                res = item / "res"
                out_apk = output_dir / f"{item.name}.apk"
                if manifest.exists():
                    logger.info(f"Building overlay: {item.name}")
                    success = self.compile_overlay(manifest, res if res.exists() else None, out_apk)
                    results[item.name] = success
        return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Xiaomi Blossom Overlay Build Tool")
    parser.add_argument("--rro-dir", type=Path, default=Path(__file__).parent.parent / "rro_overlays", help="Path to rro_overlays directory")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent.parent / "apks", help="Output directory for signed APKs")
    parser.add_argument("--framework-res", type=Path, default=Path("/usr/share/android-framework-res/framework-res.apk"), help="Path to base framework-res.apk")
    parser.add_argument("--keystore", type=Path, default=Path.home() / "test.keystore", help="Path to keystore")

    args = parser.parse_args()
    builder = OverlayBuilder(
        framework_res=args.framework_res,
        keystore_path=args.keystore
    )
    builder.build_all(args.rro_dir, args.output_dir)


if __name__ == "__main__":
    main()
