from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

import pandas as pd

from .config import settings


BRANDS = [
    "aiwa", "ajax", "apple", "asus", "azatech", "canon", "dahua", "dell",
    "epson", "eurotoner", "ezviz", "gigabyte", "hiksemi", "hikvision",
    "hilook", "hp", "imou", "lg", "logitech", "mercusys", "phonic",
    "ruijie", "samsung", "sandisk", "tapo", "tenda", "tp-link", "uniview",
    "western digital", "xiaomi",
]

CATEGORY_KEYWORDS = {
    "Materiel Securite": {
        "Camera Surveillance": ["camera", "surveillance", "video", "dome", "bullet", "ptz"],
        "Camera IP": [" ip ", "poe", "reseau", "network"],
        "Camera Analogique": ["analogique", "analog", "cvi", "tvi", "ahd"],
        "Systeme D'alarme": ["alarme", "detecteur", "sirene", "centrale", "capteur"],
        "Accessoires camera": ["dvr", "nvr", "alimentation", "cable", "disque", "hdd", "ups"],
    },
    "Equipement de reseaux": {
        "Switch": ["switch"],
        "Routeur Wifi": ["routeur", "router", "wifi"],
        "Point d'acces": ["point d'acces", "access point", "ap "],
        "Armoire": ["armoire", "rack"],
    },
    "Materiel Informatique": {
        "PC Portable": ["pc portable", "laptop"],
        "PC Bureau": ["pc bureau", "desktop"],
        "Imprimante": ["imprimante", "printer", "photocopieur"],
        "Stockage": ["disque dur", "ssd", "hdd"],
        "Accessoires": ["clavier", "souris", "ram"],
    },
    "Teledistribution & Sonorisation": {
        "Sonorisation": ["haut parleur", "amplificateur", "phonic", "micro"],
        "Teledistribution": ["satellite", "antenne", "recepteur"],
    },
}


@dataclass
class PipelineResult:
    ready: pd.DataFrame
    duplicates: pd.DataFrame
    missing_price: pd.DataFrame
    output_dir: Path


def read_products(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if source.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(source)
    return pd.read_csv(source, sep=_detect_separator(source), encoding="utf-8")


def clean_products(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = normalize_columns(df)
    require_columns(df, ["sku", "name"])
    df = drop_legacy_image_link_columns(df)

    df["sku"] = df["sku"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()

    if "regular_price" not in df.columns:
        df["regular_price"] = pd.NA

    df = df[df["sku"].ne("") & df["sku"].ne("nan")].copy()
    duplicates = df[df.duplicated("sku", keep=False)].sort_values("sku").copy()
    missing_price = df[df["regular_price"].isna() | (df["regular_price"].astype(str).str.strip() == "")].copy()

    ready = df.drop_duplicates("sku", keep="first").copy()
    ready = ready[~(ready["regular_price"].isna() | (ready["regular_price"].astype(str).str.strip() == ""))].copy()
    ready["marque"] = ready.apply(detect_brand, axis=1)
    ready["categories_wordpress"] = ready.apply(categorize_row, axis=1)
    ready["image_url"] = ready["sku"].apply(build_wordpress_image_url)

    if "short_description" not in ready.columns:
        ready["short_description"] = ""
    if "long_description" not in ready.columns:
        ready["long_description"] = ""

    return ready, duplicates, missing_price


def export_result(
    ready: pd.DataFrame,
    duplicates: pd.DataFrame,
    missing_price: pd.DataFrame,
    output_dir: str | Path,
) -> PipelineResult:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    ready.to_csv(target / "products_ready.csv", sep=";", encoding="utf-8", index=False)
    duplicates.to_csv(target / "products_duplicates.csv", sep=";", encoding="utf-8", index=False)
    missing_price.to_csv(target / "products_missing_price.csv", sep=";", encoding="utf-8", index=False)
    write_report(target, ready, duplicates, missing_price)

    return PipelineResult(ready=ready, duplicates=duplicates, missing_price=missing_price, output_dir=target)


def process_file(input_path: str | Path, output_dir: str | Path) -> PipelineResult:
    ready, duplicates, missing_price = clean_products(read_products(input_path))
    return export_result(ready, duplicates, missing_price, output_dir)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [
        strip_accents(str(column)).strip().lower().replace(" ", "_")
        for column in normalized.columns
    ]
    normalized = normalized.rename(columns={"categorie_": "categorie", "prix_ttc": "price_ttc"})
    return normalized


def drop_legacy_image_link_columns(df: pd.DataFrame) -> pd.DataFrame:
    legacy_columns = [column for column in df.columns if column.startswith("link_image_cloud")]
    return df.drop(columns=legacy_columns) if legacy_columns else df


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Colonnes obligatoires manquantes: {', '.join(missing)}")


def detect_brand(row: pd.Series) -> str:
    current = str(row.get("marque", "")).strip()
    if current and current.lower() != "nan":
        return current.title()

    text = normalize_text(row.get("name", ""))
    for brand in sorted(BRANDS, key=len, reverse=True):
        if brand in text:
            return brand.title()
    return ""


def categorize_row(row: pd.Series) -> str:
    text = normalize_text(f"{row.get('name', '')} {row.get('description', '')} {row.get('categorie', '')}")
    best_category = str(row.get("categorie", "")).strip()
    best_subcategory = ""
    best_score = 0

    for category, subcategories in CATEGORY_KEYWORDS.items():
        for subcategory, keywords in subcategories.items():
            score = sum(1 for keyword in keywords if normalize_text(keyword) in text)
            if score > best_score:
                best_category = category
                best_subcategory = subcategory
                best_score = score

    parts = [best_category or "Catalogue"]
    if best_subcategory:
        parts.append(best_subcategory)
    return ", ".join(clean_wordpress_category(part) for part in parts if part)


def build_wordpress_image_url(sku: str, extension: str = "webp") -> str:
    safe_sku = str(sku).strip()
    base = settings.wordpress_upload_base_url.rstrip("/")
    return f"{base}/{safe_sku}.{extension}"


def clean_wordpress_category(value: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(value)).strip()


def normalize_text(value: object) -> str:
    text = strip_accents(str(value).lower())
    return f" {re.sub(r'[^a-z0-9]+', ' ', text)} "


def strip_accents(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def _detect_separator(path: Path) -> str:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:2048]
    return ";" if sample.count(";") >= sample.count(",") else ","


def write_report(
    output_dir: Path,
    ready: pd.DataFrame,
    duplicates: pd.DataFrame,
    missing_price: pd.DataFrame,
) -> None:
    report = f"""# Rapport de traitement

- Produits prets pour import: {len(ready)}
- Lignes en doublon par SKU: {len(duplicates)}
- Produits sans prix: {len(missing_price)}

Fichiers generes:

- products_ready.csv
- products_duplicates.csv
- products_missing_price.csv
"""
    (output_dir / "products_report.md").write_text(report, encoding="utf-8")
