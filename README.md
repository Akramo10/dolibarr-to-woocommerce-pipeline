
# CRM to WooCommerce Product Pipeline

Projet de traitement de donnees produits realise pour automatiser la migration d'un catalogue depuis le CRM Dolibarr vers une boutique WordPress / WooCommerce.

Le pipeline nettoie les exports produits, separe les cas a corriger, enrichit les fiches avec des images et des descriptions SEO, puis genere un fichier pret pour l'import en masse dans WooCommerce.
<img width="1046" height="701" alt="image" src="https://github.com/user-attachments/assets/36e35f9b-c246-4480-a2c0-f7aed8ee8e85" />
## Objectif

Transformer un export brut Dolibarr en catalogue e-commerce exploitable :

- suppression et controle des doublons par SKU ;
- separation des produits sans prix dans un fichier dedie ;
- detection des marques et categorisation produit ;
- generation de liens images au format WordPress ;
- telechargement d'images par recherche SKU / nom produit ;
- ajout de descriptions courtes et longues optimisees SEO avec l'API OpenAI ;
- preparation du fichier final pour import WooCommerce.

## Stack technique

- Python
- Pandas
- OpenPyXL
- OpenAI API
- icrawler / scraping image
- CSV / Excel
- WordPress / WooCommerce

## Structure

```text
crm-woocommerce-product-pipeline/
├── src/catalog_pipeline/        # Pipeline propre et reutilisable
├── tests/                       # Tests unitaires du pipeline
├── docs/                        # Description portfolio et workflow
├── historique/                  # Anciens scripts, donnees et exports de travail
├── requirements.txt             # Dependances Python
├── .env.example                 # Variables d'environnement attendues
└── README.md                    # Presentation du projet
```

Les anciens scripts et fichiers de travail sont archives dans `historique`. La version structuree pour portfolio est dans `src/catalog_pipeline`.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Renseigner ensuite `OPENAI_API_KEY` dans `.env` si la generation de descriptions SEO est utilisee.

## Utilisation

Exemple avec le fichier principal :

```powershell
python -m src.catalog_pipeline.cli process `
  --input "chemin/vers/export-produits.csv" `
  --output-dir "exports"
```

Sorties generees :

- `exports/products_ready.csv` : fichier nettoye pret pour WooCommerce ;
- `exports/products_duplicates.csv` : doublons SKU a verifier ;
- `exports/products_missing_price.csv` : produits sans prix ;
- `exports/products_report.md` : resume du traitement.

## Regle image WordPress

Les images sont referencees avec le SKU du produit :

```text
https://example-store.com/wp-content/uploads/2025/07/{SKU}.webp
```

Exemple :

```text
https://example-store.com/wp-content/uploads/2025/07/DS-2FA1208-C16.webp
```

## Resultat

Ce projet montre la capacite a :

- automatiser un workflow data reel ;
- nettoyer des donnees commerciales imparfaites ;
- enrichir un catalogue produit avec IA ;
- preparer un import WooCommerce en masse ;
- structurer un projet Python pour une presentation professionnelle.

## Tests

```powershell
pytest
```
