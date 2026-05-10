import pandas as pd

fichier_excel = r"data\raw\teledistribution_sonorisation.xlsx"
fichier_csv = "Télédistribution_Sonorisation.csv"

df = pd.read_excel(fichier_excel)
df.to_csv(fichier_csv, index=False, encoding='utf-8')

print("Conversion terminée !")
