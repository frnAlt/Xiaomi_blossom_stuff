#!/usr/bin/env python3
"""
Xiaomi Blossom Automated ROM Porting Backend Engine.
Designed for DnA Android Kitchen, CRB, and manual ROM porting workflows.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("PortHelper")


class BlossomPortEngine:
    """Backend engine to inject Blossom overlays, shims, configs, and properties into a Port ROM."""

    DEVICE_MODELS: Dict[str, Dict[str, str]] = {
        "dandelion": {
            "model": "Redmi 9A",
            "device": "dandelion",
            "name": "dandelion",
            "market_name": "Redmi 9A",
            "fingerprint": "false"
        },
        "angelica": {
            "model": "Redmi 9C",
            "device": "angelica",
            "name": "angelica",
            "market_name": "Redmi 9C",
            "fingerprint": "true"
        },
        "angelican": {
            "model": "Redmi 9C NFC",
            "device": "angelican",
            "name": "angelican",
            "market_name": "Redmi 9C NFC",
            "fingerprint": "true"
        },
        "cattail": {
            "model": "Redmi 9 Activ",
            "device": "cattail",
            "name": "cattail",
            "market_name": "Redmi 9 Activ",
            "fingerprint": "true"
        },
        "blossom": {
            "model": "Redmi 9A / 9C / 9 Activ",
            "device": "blossom",
            "name": "blossom",
            "market_name": "Xiaomi Blossom Series",
            "fingerprint": "auto"
        }
    }

    REQUIRED_PROPS: Dict[str, str] = {
        # Notch & Display
        "ro.miui.notch": "1",
        "ro.miui.has_real_notch": "1",
        "ro.vendor.display.type": "1",
        # Telephony & RIL
        "persist.vendor.radio.mtk_ps4_support": "1",
        "ro.vendor.mtk_telephony_add_on_policy": "0",
        "persist.vendor.radio.smart.data.switch": "1",
        # MediaTek Performance & Touch
        "ro.vendor.pref_scale_enable": "1",
        "ro.vendor.perf_touch_boost": "1",
        "ro.vendor.qti.va_aosp.support": "0",
        # Audio routing
        "ro.vendor.audio.sdk.fluencetype": "none",
        "ro.vendor.audio.sdk.ssr": "false",
    }

    def __init__(self, root_dir: Optional[Path] = None) -> None:
        self.root_dir = root_dir or Path(__file__).parent.parent
        self.apks_dir = self.root_dir / "apks"
        self.port_libs_dir = self.root_dir / "port_libs_and_shims"
        self.xmls_dir = self.root_dir / "xmls"

    def inject_overlays(self, port_dir: Path) -> None:
        """Injects compiled RRO overlay APKs into the target Port ROM partitions."""
        logger.info("Injecting Blossom Display & System overlays...")

        product_overlay = port_dir / "product" / "overlay"
        vendor_overlay = port_dir / "vendor" / "overlay"
        system_ext_overlay = port_dir / "system_ext" / "overlay"

        product_overlay.mkdir(parents=True, exist_ok=True)
        vendor_overlay.mkdir(parents=True, exist_ok=True)

        # 1. Display Notch Overlay -> product/overlay
        disp_apk = self.apks_dir / "DisplayOverlayBlossom.apk"
        if disp_apk.exists():
            shutil.copy2(disp_apk, product_overlay / "DisplayOverlayBlossom.apk")
            logger.info("  -> Copied DisplayOverlayBlossom.apk to product/overlay/")

        # 2. Framework & SystemUI overlays -> vendor/overlay
        for overlay_name in [
            "FrameworksResOverlayBlossom.apk",
            "SystemUIOverlayBlossom.apk",
            "CarrierConfigOverlayBlossom.apk",
            "SettingsOverlayBlossom.apk",
            "WifiResOverlayBlossom.apk",
            "TelephonyOverlayBlossom.apk"
        ]:
            src_apk = self.apks_dir / overlay_name
            if src_apk.exists():
                shutil.copy2(src_apk, vendor_overlay / overlay_name)
                logger.info(f"  -> Copied {overlay_name} to vendor/overlay/")

    def inject_shims_and_vndk(self, port_dir: Path) -> None:
        """Injects MediaTek shims and VNDK libraries into system and vendor paths."""
        logger.info("Injecting MediaTek GraphicBufferMapper & VNDK shims...")

        system_lib64 = port_dir / "system" / "lib64"
        vendor_lib64 = port_dir / "vendor" / "lib64"
        vndk_v32 = port_dir / "system" / "lib64" / "vndk-v32"

        vndk_v32.mkdir(parents=True, exist_ok=True)
        system_lib64.mkdir(parents=True, exist_ok=True)

        # VNDK libui-v32
        libui_src = self.port_libs_dir / "vndk" / "libui-v32.so"
        if libui_src.exists():
            shutil.copy2(libui_src, vndk_v32 / "libui.so")
            logger.info("  -> Injected libui-v32 to system/lib64/vndk-v32/libui.so")

        # Public vendor libraries
        pub_libs = self.port_libs_dir / "public.libraries.vendor.txt"
        vendor_etc = port_dir / "vendor" / "etc"
        vendor_etc.mkdir(parents=True, exist_ok=True)
        if pub_libs.exists():
            shutil.copy2(pub_libs, vendor_etc / "public.libraries.vendor.txt")
            logger.info("  -> Synchronized public.libraries.vendor.txt")

    def inject_carrier_and_audio_configs(self, port_dir: Path) -> None:
        """Synchronizes carrier, audio, and thermal XML definitions."""
        logger.info("Synchronizing Carrier, Audio, and Thermal XML configurations...")

        vendor_carrier = port_dir / "vendor" / "etc" / "carrier"
        vendor_carrier.mkdir(parents=True, exist_ok=True)

        for xml_file in ["vendor_miui.xml", "vendor_device.xml", "vendor.xml"]:
            src = self.xmls_dir / "carrier" / xml_file
            if src.exists():
                shutil.copy2(src, vendor_carrier / xml_file)
                logger.info(f"  -> Copied carrier config: {xml_file}")

        # Thermal
        thermal_src = self.xmls_dir / "thermal" / "thermal_info_config.json"
        if thermal_src.exists():
            shutil.copy2(thermal_src, port_dir / "vendor" / "etc" / "thermal_info_config.json")
            logger.info("  -> Synchronized thermal_info_config.json")

    def patch_build_properties(self, port_dir: Path, variant: str = "blossom") -> None:
        """Patches build.prop files with device identifiers and MediaTek specific flags."""
        logger.info(f"Patching build.prop properties for variant: {variant}...")

        target_props = self.REQUIRED_PROPS.copy()
        if variant in self.DEVICE_MODELS:
            v_info = self.DEVICE_MODELS[variant]
            target_props["ro.product.model"] = v_info["model"]
            target_props["ro.product.device"] = v_info["device"]
            target_props["ro.product.name"] = v_info["name"]
            target_props["ro.build.product"] = v_info["device"]
            target_props["ro.product.marketname"] = v_info["market_name"]

        prop_files = [
            port_dir / "system" / "build.prop",
            port_dir / "system" / "system" / "build.prop",
            port_dir / "vendor" / "build.prop"
        ]

        for prop_path in prop_files:
            if not prop_path.exists():
                continue

            logger.info(f"  -> Updating {prop_path.relative_to(port_dir)}...")
            content = prop_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            existing_keys: Set[str] = set()

            new_lines: List[str] = []
            for line in lines:
                match = re.match(r"^([a-zA-Z0-9._]+)=(.*)$", line)
                if match:
                    key = match.group(1)
                    existing_keys.add(key)
                    if key in target_props:
                        new_lines.append(f"{key}={target_props[key]}")
                        continue
                new_lines.append(line)

            # Append missing props
            new_lines.append("\n# Added by Blossom Port Engine")
            for k, v in target_props.items():
                if k not in existing_keys:
                    new_lines.append(f"{k}={v}")

            prop_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    def run_port_pipeline(
        self,
        port_dir: Path,
        variant: str = "blossom"
    ) -> bool:
        """Runs the entire porting and patch pipeline on the given port directory."""
        logger.info(f"Starting Blossom Port Pipeline on {port_dir} (Variant: {variant})...")
        if not port_dir.exists():
            logger.error(f"Port directory does not exist: {port_dir}")
            return False

        self.inject_overlays(port_dir)
        self.inject_shims_and_vndk(port_dir)
        self.inject_carrier_and_audio_configs(port_dir)
        self.patch_build_properties(port_dir, variant)

        logger.info("✅ Blossom Port Pipeline completed successfully!")
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Xiaomi Blossom Automated ROM Port Engine")
    parser.add_argument("--port-dir", type=Path, required=True, help="Path to extracted Port ROM directory (containing system, vendor, product)")
    parser.add_argument("--variant", choices=["blossom", "dandelion", "angelica", "angelican", "cattail"], default="blossom", help="Hardware SKU variant")

    args = parser.parse_args()
    engine = BlossomPortEngine()
    success = engine.run_port_pipeline(args.port_dir, args.variant)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
