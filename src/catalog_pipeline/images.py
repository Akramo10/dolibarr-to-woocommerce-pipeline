from __future__ import annotations

from pathlib import Path
import os

import pandas as pd


def download_product_images(
    df: pd.DataFrame,
    image_dir: str | Path,
    max_images_per_product: int = 1,
) -> pd.DataFrame:
    """Download product images using the product name and SKU as the search query."""
    from icrawler.builtin import GoogleImageCrawler

    target = Path(image_dir)
    target.mkdir(parents=True, exist_ok=True)
    updated = df.copy()

    if "local_image_path" not in updated.columns:
        updated["local_image_path"] = ""

    for index, row in updated.iterrows():
        sku = str(row["sku"]).strip()
        name = str(row["name"]).strip()
        expected = target / f"{sku}.jpg"

        if expected.exists():
            updated.at[index, "local_image_path"] = str(expected)
            continue

        before = set(os.listdir(target))
        crawler = GoogleImageCrawler(storage={"root_dir": str(target)})
        crawler.crawl(keyword=f"{sku} {name}", max_num=max_images_per_product)
        after = set(os.listdir(target))

        new_files = [target / filename for filename in after - before]
        if new_files:
            downloaded = max(new_files, key=lambda file: file.stat().st_mtime)
            final_path = target / f"{sku}{downloaded.suffix}"
            downloaded.rename(final_path)
            updated.at[index, "local_image_path"] = str(final_path)

    return updated
