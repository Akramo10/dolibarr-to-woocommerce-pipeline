import pandas as pd
import os

# Dictionnaire des catégories et sous-catégories
categories = {
    "Matériel Informatiques": [
        "Clavier", "disque dur", "Pc Bureau", "Pc Portable", "Photocopieur & Imprimantes", "Ram", "Souris"
    ],
    "Equipements de réseaux": [
        "Armoire", "Point d'accès", "Routeur Wifi", "Switch"
    ],
    "Accessoires & Electroniques": [],
    "Consommables & Toner": []
}

# Liste des marques
marques = [
    "aiwa", "Ajax", "Apple", "Asus", "Azatech", "Cable solutiuon", "Canon", "Dahua", "Dell", "Digital print",
    "ECHOSAT", "Epson", "Eurotoner", "Ezviz", "Gigabyte", "Hiksemi", "Hikvision", "Hilook", "HP", "Imou",
    "King d'home", "KOBRA", "LG", "Logitech", "MASTERPLUS", "Mercusys", "Omada", "Phonic", "Reyee", "Ruijie",
    "SAB", "Samsung", "Sandisk", "Shelly", "STARSAT", "Svc", "Tapo", "Tcl", "Tenda", "Tiandy", "Tp-link",
    "Uniview", "Wd-link", "Western digital", "XIAOMI"
]

# Charger le fichier CSV avec le bon séparateur
df = pd.read_csv("TOUT les produit traitemnet en mass.csv", encoding="utf-8", sep=";")

# Afficher les colonnes pour vérification
print("Colonnes trouvées :", df.columns.tolist())

# Nettoyer les noms de colonnes
df.columns = df.columns.str.strip().str.lower()

# Vérifier la présence de la colonne 'categorie'
if 'categorie' not in df.columns:
    raise Exception("La colonne 'categorie' est introuvable. Vérifiez le nom exact dans votre fichier CSV.")

def extraire_categorie_et_souscat(cat):
    if pd.isnull(cat):
        return ("", "")
    for categorie, sous_categories in categories.items():
        for sous_cat in sous_categories:
            # Respecte la casse exacte
            if sous_cat in str(cat):
                return (categorie, sous_cat)
        if categorie in str(cat):
            return (categorie, "")
    return (cat, "")

# Appliquer la fonction et créer deux colonnes
cats = df['categorie'].apply(extraire_categorie_et_souscat)
df['categorie'] = cats.apply(lambda x: x[0])
df['categorie2'] = cats.apply(lambda x: x[1])

# Fonction pour détecter la marque dans le nom du produit
def detecter_marque(nom):
    if pd.isnull(nom):
        return ""
    for marque in marques:
        if marque in str(nom):  # Respecte la casse exacte
            return marque
    return ""

# Ajouter la colonne marque (remplie automatiquement si possible)
if 'marque' not in df.columns:
    df['marque'] = df['name'].apply(detecter_marque)
else:
    # Remplir les valeurs vides uniquement
    df['marque'] = df.apply(lambda row: detecter_marque(row['name']) if pd.isnull(row['marque']) or row['marque']=="" else row['marque'], axis=1)

# Ajout de la colonne link_image_cloud en première position
link_cloud3 = "https://example-store.com/wp-content/uploads/2025/07/{sku}.webp"
df.insert(0, 'link_image_cloud3', df['sku'].apply(lambda sku: link_cloud3.replace('{sku}', str(sku))))

# Sauvegarder le fichier avec le séparateur ;
df.to_csv("TOUT les produit traitemnet en mass.csv", index=False, encoding="utf-8", sep=";")

print("Traitement terminé ! Fichier prêt pour import WordPress.")
