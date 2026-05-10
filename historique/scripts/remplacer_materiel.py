import pandas as pd

# Chemin du fichier source
fichier_source = r"data\raw\produits_surveillance_alarmewithcategorie.csv"
# Chemin du fichier de sortie
fichier_sortie = r"exports\produits_surveillance_alarmewithcategorie_corrige.csv"

# Lire le CSV
df = pd.read_csv(fichier_source, sep=';', encoding='utf-8')

# Remplacer partout dans tout le DataFrame
df = df.replace('Materiel Securite', 'Matériel Sécurité', regex=True)

# Sauvegarder le résultat
df.to_csv(fichier_sortie, sep=';', encoding='utf-8', index=False)

print("✅ Remplacement terminé. Nouveau fichier créé :", fichier_sortie)
