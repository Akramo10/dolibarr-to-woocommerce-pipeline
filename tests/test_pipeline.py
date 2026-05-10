import pandas as pd

from src.catalog_pipeline.pipeline import build_wordpress_image_url, clean_products


def test_clean_products_separates_duplicates_and_missing_prices():
    df = pd.DataFrame(
        [
            {"sku": "SKU-1", "name": "Camera IP Hikvision", "regular_price": 100, "categorie": ""},
            {"sku": "SKU-1", "name": "Camera IP Hikvision", "regular_price": 110, "categorie": ""},
            {"sku": "SKU-2", "name": "Switch reseau", "regular_price": "", "categorie": ""},
            {"sku": "SKU-3", "name": "Routeur Wifi TP-Link", "regular_price": 250, "categorie": ""},
        ]
    )

    ready, duplicates, missing_price = clean_products(df)

    assert len(ready) == 2
    assert len(duplicates) == 2
    assert len(missing_price) == 1
    assert "categories_wordpress" in ready.columns
    assert "short_description" in ready.columns
    assert "long_description" in ready.columns


def test_build_wordpress_image_url_uses_sku_as_filename():
    assert build_wordpress_image_url("DS-2FA1208-C16").endswith("/DS-2FA1208-C16.webp")
