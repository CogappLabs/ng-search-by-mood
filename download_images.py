import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from tqdm import tqdm

IMAGES_DIR = pathlib.Path("data/images")
WORKERS = 16  # concurrent downloads - this is network-bound, not CPU-bound


def download_one(uid, url):
    """Download a single painting's image to data/images/<uid>.jpg.
    Skips the request entirely if we already have a non-empty file for this
    uid, so re-running the script after a partial run just fills in gaps."""
    dest = IMAGES_DIR / f"{uid}.jpg"
    if dest.exists() and dest.stat().st_size > 0:
        return uid, True
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return uid, True
    except Exception:
        return uid, False


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet("data/colour_features.parquet")
    df = df.dropna(subset=["image_url"])

    failures = []
    # fan the downloads out across a thread pool - each one just waits on a
    # network request, so threads (not processes) are the right tool here
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {
            ex.submit(download_one, row.uid, row.image_url): row.uid
            for row in df.itertuples()
        }
        for fut in tqdm(as_completed(futures), total=len(futures)):
            uid, ok = fut.result()
            if not ok:
                failures.append(uid)

    print(f"done. {len(failures)} failures")
    if failures:
        pathlib.Path("data/download_failures.txt").write_text("\n".join(failures))


if __name__ == "__main__":
    main()
