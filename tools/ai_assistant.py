#!/usr/bin/env python3
"""
Xiaomi Blossom AI Porting Assistant & Diagnostic Engine.
Performs real-time error analysis, root-cause identification, and automated troubleshooting
for ROM builds, bootloops, and logcat logs.
Supports both intelligent offline rule-based diagnostics and online LLM reasoning (Gemini / OpenAI API).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AIAssistant")


class BlossomAIAssistant:
    """Intelligent Porting Diagnostics & AI Advisor for Xiaomi Blossom."""

    KNOWLEDGE_BASE: List[Dict[str, str]] = [
        {
            "pattern": r"(undefined symbol: _ZN7android19GraphicBufferMapper|GraphicBufferMapper)",
            "issue": "MediaTek Camera/Graphics HAL symbol missing (GraphicBufferMapper)",
            "root_cause": "The ported system framework uses modern GraphicBufferMapper symbols that differ from MediaTek's proprietary HAL.",
            "solution": "Inject 'libshim_ui.so' into system/lib64 and register it in vendor/etc/public.libraries.vendor.txt."
        },
        {
            "pattern": r"(Fatal signal 11 \(SIGSEGV\).*SurfaceFlinger|surfaceflinger.*crash)",
            "issue": "SurfaceFlinger Crash / Black Screen",
            "root_cause": "Display cutout path is unparsable or missing VNDK libui.so symbol.",
            "solution": "Apply DisplayOverlayBlossom.apk to product/overlay and inject libui-v32.so into system/lib64/vndk-v32."
        },
        {
            "pattern": r"(avc: denied|SELinux.*denied|enforcing.*blocked)",
            "issue": "SELinux Access Vector Cache (AVC) Denial",
            "root_cause": "SELinux policy in the ported ROM is blocking vendor HAL initialization.",
            "solution": "Merge sepolicy/vendor rules or add 'androidboot.selinux=permissive' to boot.img kernel cmdline for testing."
        },
        {
            "pattern": r"(dm-verity.*verification failed|vbmeta.*signature mismatch|verify error)",
            "issue": "Android Verified Boot (AVB) dm-verity Bootloop",
            "root_cause": "System partition was modified, causing AVB 2.0 signature check to abort boot.",
            "solution": "Flash patched vbmeta.img with '--disable-verity --disable-verification' using tools/super_tools.py."
        },
        {
            "pattern": r"(AudioPolicyService.*cannot find|android\.hardware\.audio.*dead)",
            "issue": "Audio Server Panic / No Sound",
            "root_cause": "Aurisys parameter mismatch between MTK audio HAL and port audio policy.",
            "solution": "Restore base vendor/etc/audio_policy_configuration.xml and aurisys_config.xml from xmls/audio/."
        },
        {
            "pattern": r"(Total partitions size exceeds main group limit|lpmake.*exceeds)",
            "issue": "Super Partition Group Overflow",
            "root_cause": "Combined size of system, vendor, product, and system_ext exceeds 4.5GB (4829741056 bytes).",
            "solution": "Debloat unnecessary apps or resize partitions to fit within Blossom's main dynamic partition group."
        },
        {
            "pattern": r"(failed to mount.*userdata|encryption.*failed)",
            "issue": "Fstab Forced Encryption Rejection",
            "root_cause": "Ported ROM kernel expects hardware-backed FBE while user partition is formatted differently.",
            "solution": "Run tools/auto_patcher.py to remove 'fileencryption=' flags and set 'encryptable=userdata' in fstab."
        }
    ]

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

    def analyze_log_content(self, log_text: str) -> List[Dict[str, str]]:
        """Scans log content against expert rule-based knowledge base."""
        matched_issues: List[Dict[str, str]] = []
        for rule in self.KNOWLEDGE_BASE:
            if re.search(rule["pattern"], log_text, re.IGNORECASE):
                matched_issues.append(rule)
        return matched_issues

    def call_online_ai(self, prompt: str) -> Optional[str]:
        """Calls Google Gemini API for deep generative diagnostics if API key is provided."""
        if not self.api_key:
            return None

        logger.info("Connecting to Gemini AI for deep diagnostic reasoning...")
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": (
                                    "You are an expert Android ROM developer specialized in MediaTek MT6762/MT6765 "
                                    "and Xiaomi Blossom (Redmi 9A/9C). Diagnose the following ROM build/boot log and "
                                    f"provide exact root cause and actionable fix:\n\n{prompt[:8000]}"
                                )
                            }
                        ]
                    }
                ]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.warning(f"Online AI request failed: {e}. Falling back to offline engine.")
            return None

    def generate_report(self, log_path: Path, output_md: Optional[Path] = None) -> str:
        """Generates a complete markdown diagnosis report from a log file."""
        if not log_path.exists():
            return f"Log file not found: {log_path}"

        log_content = log_path.read_text(encoding="utf-8", errors="ignore")
        detected = self.analyze_log_content(log_content)
        ai_response = self.call_online_ai(log_content)

        lines: List[str] = [
            "# Xiaomi Blossom AI Porting Assistant Report",
            f"- Target Device: Xiaomi Blossom (dandelion / angelica / cattail)",
            f"- Log File: `{log_path.name}` ({log_path.stat().st_size} bytes)",
            f"- Diagnostic Status: {'Issues Detected' if detected else 'No Fatal Errors Found'}\n",
            "---"
        ]

        if detected:
            lines.append("## Detected Issues & Automated Solutions\n")
            for idx, item in enumerate(detected, 1):
                lines.append(f"### {idx}. {item['issue']}")
                lines.append(f"- Root Cause: {item['root_cause']}")
                lines.append(f"- Recommended Fix: {item['solution']}\n")
        else:
            lines.append("## Diagnostic Health Check")
            lines.append("No critical MediaTek HAL crashes, AVB signature mismatches, or partition overflow errors were detected in the analyzed log.\n")

        if ai_response:
            lines.append("## Generative AI Reasoning Analysis\n")
            lines.append(ai_response)
            lines.append("\n")

        lines.append("---")
        lines.append("*Generated automatically by Xiaomi Blossom AI Porting Assistant.*")

        report_str = "\n".join(lines)
        if output_md:
            output_md.write_text(report_str, encoding="utf-8")
            logger.info(f"Report written to: {output_md}")

        return report_str


def main() -> None:
    parser = argparse.ArgumentParser(description="Blossom AI Porting Assistant")
    parser.add_argument("--log-file", type=Path, required=True, help="Path to build log, extraction log, or logcat file")
    parser.add_argument("--output-md", type=Path, help="Output markdown report file path (e.g. $GITHUB_STEP_SUMMARY)")

    args = parser.parse_args()
    assistant = BlossomAIAssistant()
    report = assistant.generate_report(args.log_file, args.output_md)
    print(report)


if __name__ == "__main__":
    main()
