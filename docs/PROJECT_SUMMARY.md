# Resume Portfolio

## Contexte

Une entreprise disposait d'un catalogue produit issu de Dolibarr, mais les donnees n'etaient pas directement exploitables pour une boutique WooCommerce : doublons, prix manquants, categories incompletes, images absentes et descriptions produit non optimisees.

## Mission

Construire un pipeline de traitement capable de transformer les exports CRM en fichiers importables dans WordPress / WooCommerce, avec enrichissement automatique des fiches produits.

## Travail realise

1. Import des donnees depuis les exports Dolibarr en Excel / CSV.
2. Nettoyage des colonnes et normalisation des SKU.
3. Detection des doublons produit par SKU.
4. Separation des produits sans prix dans un fichier de controle.
5. Categorisation des produits par mots-cles.
6. Detection automatique des marques depuis les noms produit.
7. Recherche et telechargement d'images produit a partir du SKU et du nom.
8. Renommage des images avec la convention `{SKU}.{extension}`.
9. Generation des liens WordPress au format `https://example-store.com/wp-content/uploads/2025/07/{SKU}.webp`.
10. Ajout de descriptions courtes et longues avec l'API OpenAI.
11. Export d'un fichier final pret pour l'import en masse WooCommerce.

## Impact

- Reduction du travail manuel sur le catalogue.
- Meilleure qualite des fiches produits.
- Import WooCommerce plus fiable.
- Donnees separees pour faciliter la correction des anomalies.
- Projet reutilisable pour de nouveaux exports Dolibarr.

## Competences demontrees

- Data cleaning avec Python et Pandas.
- Automatisation de processus metier.
- Integration API IA.
- Preparation de donnees pour e-commerce.
- Gestion de fichiers CSV / Excel.
- Structuration d'un projet technique presentable en portfolio.
