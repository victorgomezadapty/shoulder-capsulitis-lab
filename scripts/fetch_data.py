"""Copy or download the two official Mendeley Data files and stop on any sha256 mismatch.

Usage (from the project root):
    .venv/bin/python scripts/fetch_data.py            # copy from a local verified cache if present, else download
    .venv/bin/python scripts/fetch_data.py --download # always download from Mendeley Data

Files already present and verified are left untouched. Nothing is ever moved or deleted at the source.
"""
from __future__ import annotations

import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shoulder_capsulitis_lab import data as D  # noqa: E402

URLS = {
    "spiral": "https://data.mendeley.com/public-files/datasets/hnvhm376hg/files/40e39950-75ec-4807-a922-f2c64fc6d175/file_downloaded",
    "magneto": "https://data.mendeley.com/public-files/datasets/khdtg3rzmp/files/2e37ea10-cdd8-424e-8090-25826b93e1b1/file_downloaded",
}
LOCAL_CACHE = {
    "spiral": [Path("/workspace/dsverify/shoulder-lic/fresh_hnvhm376hg.sav"), Path("/workspace/dsverify/dl_hnvhm376hg")],
    "magneto": [Path("/workspace/dsverify/shoulder-lic/fresh_khdtg3rzmp.xlsx"), Path("/workspace/dsverify/dl_khdtg3rzmp")],
}


def ok(p: Path, t) -> bool:
    return p.exists() and p.stat().st_size == t.size and D.sha256sum(p) == t.sha256


def main(force_download: bool = False) -> int:
    D.RAW_DIR.mkdir(parents=True, exist_ok=True)
    for k, t in D.TRIALS.items():
        dest = D.RAW_DIR / t.file_name
        if ok(dest, t):
            print(f"ok {t.file_name}")
            continue
        src = None if force_download else next((c for c in LOCAL_CACHE[k] if ok(c, t)), None)
        tmp = dest.with_suffix(dest.suffix + ".part")
        if src:
            shutil.copy2(src, tmp)
        else:
            req = urllib.request.Request(URLS[k], headers={"User-Agent": "shoulder-capsulitis-lab/0.1"})
            with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as fh:
                fh.write(r.read())
        if not ok(tmp, t):
            tmp.unlink(missing_ok=True)
            print(f"sha256 mismatch for {t.file_name}; stopped")
            return 1
        tmp.replace(dest)
        print(f"fetched {t.file_name} ({'copy' if src else 'download'})")
    D.verify_raw()
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--download" in sys.argv))
