#!/usr/bin/env python3
"""Convert story-only DOCX files to PDFs and report exact rendered page counts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def pdf_pages(pdfinfo: Path, pdf: Path) -> int:
    result = subprocess.run([str(pdfinfo), str(pdf)], check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
    if not match:
        raise ValueError(f"cannot read page count: {pdf}")
    return int(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--soffice", type=Path, required=True)
    parser.add_argument("--pdfinfo", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for index, docx in enumerate(sorted(args.input_dir.glob("*.docx")), start=1):
        profile = args.out_dir / f"lo_profile_{index:02d}"
        profile.mkdir(parents=True, exist_ok=True)
        uri = profile.resolve().as_uri()
        subprocess.run(
            [str(args.soffice), f"-env:UserInstallation={uri}", "--headless", "--convert-to", "pdf:writer_pdf_Export", "--outdir", str(args.out_dir), str(docx.resolve())],
            check=True,
            capture_output=True,
        )
        pdf = args.out_dir / (docx.stem + ".pdf")
        pages = pdf_pages(args.pdfinfo, pdf)
        files.append({"docx": docx.name, "pdf": pdf.name, "pages": pages, "pdf_bytes": pdf.stat().st_size})
    report = {"status": "pass", "files": files, "total_pages": sum(item["pages"] for item in files)}
    (args.out_dir / "story_only_page_counts.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
