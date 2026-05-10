from __future__ import annotations

import pandas as pd

from .config import settings


def generate_seo_descriptions(df: pd.DataFrame, limit: int | None = None) -> pd.DataFrame:
    """Generate short and long SEO descriptions when OPENAI_API_KEY is configured."""
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env before generating descriptions.")

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    enriched = df.copy()
    for column in ["short_description", "long_description"]:
        if column not in enriched.columns:
            enriched[column] = ""

    indexes = enriched.index if limit is None else enriched.index[:limit]
    for index in indexes:
        name = enriched.at[index, "name"]
        brand = enriched.at[index, "marque"] if "marque" in enriched.columns else ""

        enriched.at[index, "short_description"] = _ask_openai(
            client,
            f"Redige une description courte, commerciale et naturelle en francais pour ce produit: {name} {brand}.",
            max_tokens=120,
        )
        enriched.at[index, "long_description"] = _ask_openai(
            client,
            (
                "Redige une description longue SEO en francais pour une fiche produit WooCommerce. "
                f"Produit: {name} {brand}. Style professionnel, clair, sans promesses non verifiables."
            ),
            max_tokens=450,
        )

    return enriched


def _ask_openai(client: object, prompt: str, max_tokens: int) -> str:
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
