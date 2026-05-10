import pandas as pd
import os
from icrawler.builtin import GoogleImageCrawler

# Charger le CSV
df = pd.read_csv("TOUT les produit traitemnet en mass.csv", encoding="utf-8", sep=";")

# Dossier de destination des images
dossier_images = r"data\images"
os.makedirs(dossier_images, exist_ok=True)

# Ajouter la colonne image_url si elle n'existe pas
if 'image_url' not in df.columns:
    df['image_url'] = ""

# Pour chaque produit, chercher et télécharger l'image
for idx, row in df.iterrows():
    nom_produit = str(row['name'])
    sku = str(row['sku'])
    chemin_image = os.path.join(dossier_images, f"{sku}.jpg")
    if not os.path.exists(chemin_image):  # Évite de retélécharger si déjà présent
        try:
            google_crawler = GoogleImageCrawler(storage={'root_dir': dossier_images})
            google_crawler.crawl(keyword=nom_produit, max_num=1, file_idx_offset=0)
            # Renommer la première image téléchargée en sku.jpg
            for file in os.listdir(dossier_images):
                if file.endswith('.jpg') and not file.startswith(sku):
                    os.rename(os.path.join(dossier_images, file), chemin_image)
                    break
        except Exception as e:
            print(f"Erreur pour {nom_produit}: {e}")
    # Mettre le chemin local dans image_url
    df.at[idx, 'image_url'] = chemin_image

# Sauvegarder le CSV
df.to_csv("TOUT les produit traitemnet en mass.csv", index=False, encoding="utf-8", sep=";")
print("Traitement terminé ! Images téléchargées et CSV mis à jour.")
