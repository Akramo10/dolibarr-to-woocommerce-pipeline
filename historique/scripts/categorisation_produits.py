import pandas as pd
import re
import unicodedata

def categoriser_produits():
    """
    Catégorise automatiquement les produits en fonction de mots-clés
    en ignorant les majuscules/minuscules et en organisant hiérarchiquement
    """
    # Définition des catégories hiérarchiques avec leurs mots-clés
    categories = {
        "Matériel Sécurité": {
            "mots_cles": ["sécurité", "surveillance", "alarme", "protection", "détection"],
            "sous_categories": {
                "Caméra Surveillance": {
                    "mots_cles": ["caméra", "camera", "surveillance", "vidéo", "video", "ip", "analogique", "wifi", "dome", "bullet", "ptz"],
                    "sous_sous_categories": {
                        "Caméra Analogiques": ["analogique", "analog", "cvi", "tvi", "ahd"],
                        "Caméra IP": ["ip", "internet", "réseau", "reseau", "poe"],
                        "Caméra Wifi": ["wifi", "wireless", "sans fil", "sansfil"]
                    }
                },
                "Accessoires camera": {
                    "mots_cles": ["accessoire", "alimentation", "bloc", "dvr", "nvr", "câble", "cable", "disque", "dur", "onduleur", "ups"],
                    "sous_sous_categories": {
                        "Bloc d'alimentation": ["alimentation", "bloc", "alim", "power", "12v", "24v"],
                        "DVR": ["dvr", "enregistreur", "digital"],
                        "NVR": ["nvr", "network", "réseau", "reseau"],
                        "Onduleur": ["onduleur", "ups", "batterie", "backup"],
                        "Câbles": ["câble", "cable", "connecteur", "rj45", "coaxial"],
                        "Disque Dur": ["disque", "dur", "hdd", "ssd", "stockage"]
                    }
                },
                "Système D'alarme": {
                    "mots_cles": ["alarme", "détecteur", "detecteur", "sirène", "sirene", "centrale", "capteur"],
                    "sous_sous_categories": {
                        "Détecteurs": ["détecteur", "detecteur", "mouvement", "ouverture", "fumée", "fumee"],
                        "Sirènes": ["sirène", "sirene", "sonore", "flash"],
                        "Centrale": ["centrale", "panneau", "clavier", "code"]
                    }
                }
            }
        },
        # ... (autres catégories si besoin)
    }

    def normaliser_texte(texte):
        """Normalise le texte en minuscules et supprime les accents"""
        if pd.isna(texte):
            return ""
        texte = str(texte).lower()
        accents = {'à': 'a', 'â': 'a', 'ä': 'a', 'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
                  'î': 'i', 'ï': 'i', 'ô': 'o', 'ö': 'o', 'ù': 'u', 'û': 'u', 'ü': 'u',
                  'ÿ': 'y', 'ç': 'c', 'ñ': 'n'}
        for accent, lettre in accents.items():
            texte = texte.replace(accent, lettre)
        return texte

    def normaliser_categorie_wordpress(categorie):
        """Supprime les accents et caractères spéciaux pour WordPress"""
        if pd.isna(categorie) or not categorie:
            return ""
        texte = str(categorie)
        texte = unicodedata.normalize('NFKD', texte).encode('ASCII', 'ignore').decode('ASCII')
        texte = ''.join(c for c in texte if c.isalnum() or c in [' ', ','])
        return texte.strip()

    def trouver_categorie(nom_produit, description=""):
        """Trouve la catégorie appropriée pour un produit"""
        texte_complet = f"{nom_produit} {description}"
        texte_normalise = normaliser_texte(texte_complet)
        meilleure_categorie = "Matériel Sécurité"
        meilleure_sous_categorie = ""
        meilleure_sous_sous_categorie = ""
        meilleur_score = 0

        if "Matériel Sécurité" in categories:
            config = categories["Matériel Sécurité"]
            score_categorie = 0
            for mot_cle in config["mots_cles"]:
                if normaliser_texte(mot_cle) in texte_normalise:
                    score_categorie += 1
            if "sous_categories" in config:
                for sous_cat, sous_config in config["sous_categories"].items():
                    score_sous_cat = 0
                    if isinstance(sous_config, dict):
                        mots_cles_sous = sous_config.get("mots_cles", [])
                        sous_sous_cats = sous_config.get("sous_sous_categories", {})
                    else:
                        mots_cles_sous = sous_config
                        sous_sous_cats = {}
                    for mot_cle in mots_cles_sous:
                        if normaliser_texte(mot_cle) in texte_normalise:
                            score_sous_cat += 1
                    meilleure_sous_sous = ""
                    for sous_sous_cat, mots_cles_sous_sous in sous_sous_cats.items():
                        for mot_cle in mots_cles_sous_sous:
                            if normaliser_texte(mot_cle) in texte_normalise:
                                meilleure_sous_sous = sous_sous_cat
                                break
                        if meilleure_sous_sous:
                            break
                    score_total = score_categorie + score_sous_cat
                    if meilleure_sous_sous:
                        score_total += 1
                    if score_total > meilleur_score:
                        meilleur_score = score_total
                        meilleure_sous_categorie = sous_cat
                        meilleure_sous_sous_categorie = meilleure_sous_sous

        return meilleure_categorie, meilleure_sous_categorie, meilleure_sous_sous_categorie

    # Charger le fichier Excel
    try:
        df = pd.read_excel("produits_surveillance_alarme.xlsx")
        print(f"✅ Fichier chargé avec {len(df)} produits")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du fichier: {e}")
        return

    # Ajouter les colonnes de catégorisation
    df['categorie'] = ""
    df['sous_categorie'] = ""
    df['sous_sous_categorie'] = ""
    df['categories_wordpress'] = ""

    # Traiter chaque produit
    for index, row in df.iterrows():
        nom = row.get('name', '')
        marque = row.get('marque', '')
        if pd.isna(nom):
            nom = ""
        if pd.isna(marque):
            marque = ""
        texte_produit = f"{nom} {marque}"
        categorie, sous_cat, sous_sous_cat = trouver_categorie(texte_produit)
        df.at[index, 'categorie'] = categorie
        df.at[index, 'sous_categorie'] = sous_cat
        df.at[index, 'sous_sous_categorie'] = sous_sous_cat
        # Toujours commencer par 'Materiel Securite' sans accent
        categories_wordpress = ["Materiel Securite"]
        if sous_cat:
            categories_wordpress.append(normaliser_categorie_wordpress(sous_cat))
        if sous_sous_cat:
            categories_wordpress.append(normaliser_categorie_wordpress(sous_sous_cat))
        df.at[index, 'categories_wordpress'] = ", ".join(categories_wordpress)

    # Sauvegarder le fichier en CSV UTF-8 avec séparateur ;
    try:
        df.to_csv(r"exports\produits_surveillance_alarmewithcategorie1.csv", sep=';', encoding='utf-8', index=False)
        print("\n✅ Fichier CSV sauvegardé dans le dossier demandé.")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde CSV: {e}")

if __name__ == "__main__":
    categoriser_produits()
