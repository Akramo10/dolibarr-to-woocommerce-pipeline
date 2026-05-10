import pandas as pd
import os
from icrawler.builtin import GoogleImageCrawler

# Charger le fichier Excel
df = pd.read_excel("Télédistribution & Sonorisation.xlsx")

col_nom = "name"      # colonne du nom du produit
col_sku = "sku"       # colonne de la référence/SKU

# Liste des marques à détecter (en minuscules pour la comparaison)
marques = [
    "aiwa", "ajax", "apple", "asus", "azatech", "cable solution", "canon", "dahua", "dell",
    "digital print", "epson", "eurotoner", "ezviz", "gigabyte", "hiksemi", "hikvision", "hilook",
    "hp", "imou", "king d’home"
]
marques_set = set(marques)

# Ajouter la colonne image_url si elle n'existe pas
dossier = r"data\images\teledistribution_sonorisation"
os.makedirs(dossier, exist_ok=True)
if "image_url" not in df.columns:
    df["image_url"] = ""
# Ajouter la colonne marque si elle n'existe pas
if "marque" not in df.columns:
    df["marque"] = ""

def detecter_marque(nom):
    nom_lower = nom.lower()
    # D'abord, chercher les marques composées (avec espace)
    for marque in marques:
        if marque in nom_lower:
            return marque.title()
    # Sinon, split et chercher les mots simples
    for mot in nom_lower.split():
        if mot in marques_set:
            return mot.title()
    return ""

for idx, row in df.iterrows():
    nom = str(row[col_nom])
    sku = str(row[col_sku])
    # Détection de la marque
    marque = detecter_marque(nom)
    df.at[idx, "marque"] = marque
    # Ne chercher une image que si la case image_url est vide
    if not row.get("image_url", ""):  # vide ou NaN
        requete = f"{nom} {sku}"
        print(f"Téléchargement image pour : {requete}")
        try:
            # Télécharger 1 image directement dans le dossier final
            google_crawler = GoogleImageCrawler(storage={'root_dir': dossier})
            google_crawler.crawl(keyword=requete, max_num=1, file_idx_offset=idx)
            # Chercher le dernier fichier ajouté dans le dossier
            fichiers = sorted([f for f in os.listdir(dossier) if os.path.isfile(os.path.join(dossier, f))], key=lambda x: os.path.getctime(os.path.join(dossier, x)), reverse=True)
            if fichiers:
                dernier_fichier = fichiers[0]
                ext = os.path.splitext(dernier_fichier)[1]
                chemin_image = os.path.join(dossier, f"{sku}{ext}")
                os.rename(os.path.join(dossier, dernier_fichier), chemin_image)
                df.at[idx, "image_url"] = chemin_image
            else:
                print(f"Aucune image trouvée pour : {requete}")
                df.at[idx, "image_url"] = ""
        except Exception as e:
            print(f"Erreur pour {requete} : {e}")
            df.at[idx, "image_url"] = ""
    else:
        print(f"Image déjà présente pour : {sku}, on ne cherche pas.")

# Sauvegarder le fichier Excel avec la colonne image_url et marque
df.to_excel("produits_surveillance_alarme.xlsx", index=False)
print("Lien des images ajouté dans la colonne 'image_url' et marque détectée dans la colonne 'marque'.")
