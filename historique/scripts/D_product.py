import os

import google.generativeai as genai
import pandas as pd


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY manquante. Ajoutez-la dans vos variables d'environnement.")

genai.configure(api_key=GOOGLE_API_KEY)

fichier = "produits_surveillance_alarme.xlsx"
df = pd.read_excel(fichier)

if "description_longue_seo" not in df.columns:
    df["description_longue_seo"] = ""
if "description_courte" not in df.columns:
    df["description_courte"] = ""

model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-pro"))

for i in range(min(10, len(df))):
    nom = df.loc[i, "name"]
    print(f"Generation pour : {nom}")

    prompt_long = (
        f"Redige une description longue optimisee SEO pour le produit suivant : {nom}. "
        "Utilise un style vendeur, professionnel, et inclus des mots-cles pertinents."
    )

    try:
        response_long = model.generate_content(prompt_long)
        df.loc[i, "description_longue_seo"] = response_long.text.strip()
        print("Description longue generee.")
    except Exception as e:
        print(f"Erreur description longue : {e}")
        df.loc[i, "description_longue_seo"] = "Erreur de generation"

    prompt_court = f"Redige une description courte et attractive pour le produit suivant : {nom}."

    try:
        response_court = model.generate_content(prompt_court)
        df.loc[i, "description_courte"] = response_court.text.strip()
        print("Description courte generee.")
    except Exception as e:
        print(f"Erreur description courte : {e}")
        df.loc[i, "description_courte"] = "Erreur de generation"

df.to_excel(fichier, index=False)
print("Descriptions generees et enregistrees.")
