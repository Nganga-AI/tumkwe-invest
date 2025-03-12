# Tumkwe Invest

Application de conseils financiers basée sur l'analyse des données d'entreprise.

## Configuration initiale

1. Créez un environnement virtuel Python:

   ```
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```
2. Installez les dépendances:

   ```
   pip install -r requirements.txt
   ```
3. Configurez les clés API:

   ```
   cp .env.example .env
   # Modifiez le fichier .env pour ajouter vos clés API
   ```

## Collecte de données

La première étape du projet consiste à collecter les données financières, boursières et textuelles nécessaires pour analyser les entreprises.

### Sources de données:

- Yahoo Finance (via yfinance) - données boursières et financières
- Alpha Vantage API - données financières supplémentaires
- News API - articles de presse et actualités
- Yahoo Finance News - actualités (gratuit)
- SEC EDGAR - documents officiels déposés auprès de la SEC

### Méthodes de collecte:

#### 1. Collecteur unifié (recommandé):

```
python unified_data_collection.py AAPL MSFT GOOGL
```

Options supplémentaires:

- `--file symbols.txt` : Charger les symboles d'actions depuis un fichier
- `--scheduler` : Exécuter en arrière-plan et actualiser les données automatiquement
- `--validate` : Valider uniquement les données existantes sans collecter de nouvelles données

#### 2. Script d'échantillon simplifié:

```
python sample_collection.py
```

Ce script collectera des données pour quelques entreprises de démonstration (Apple, Microsoft, Google) et les enregistrera dans le dossier `collected_data/`.

#### 3. Collecte d'actualités Yahoo Finance:

```
python sample_yahoo_news.py
```

### Structure des données collectées:

- `profile.json` - Informations sur l'entreprise
- `stock_prices.csv` - Historique des prix boursiers
- `income_statement.json` - États financiers (compte de résultat)
- `balance_sheet.json` - États financiers (bilan)
- `cash_flow.json` - États financiers (flux de trésorerie)
- `quarterly_*.json` - États financiers trimestriels
- `key_metrics.json` - Indicateurs clés (P/E, ROE, etc.)
- `news_articles.csv` - Liste d'articles de presse récents
- `articles/*.txt` - Contenu complet des articles de presse
- `sec_filings_metadata.csv` - Liste des documents déposés auprès de la SEC
- `sec_filings/*.txt` - Contenu des documents officiels (10-K, 10-Q)

### Architecture du système de collecte de données

Le système est conçu pour être robuste, flexible et capable de s'adapter à différentes sources de données:

1. **Modèles de données**: Classes qui représentent les différentes entités financières (prix d'actions, états financiers, etc.)
2. **Collecteurs spécialisés**: Modules qui se connectent à différentes APIs et sources de données
3. **Gestionnaire de collecte**: Coordonne les tâches de collecte et gère les mises à jour automatiques
4. **Validation des données**: Vérifie la qualité et la cohérence des données collectées

Les données sont automatiquement validées et les problèmes potentiels sont signalés dans les journaux d'exécution.

### Contraintes techniques

- Le système est conçu pour respecter les limites des APIs gratuites
- Les données sont mises en cache localement pour réduire les appels aux APIs
- Les mises à jour sont programmées selon différentes fréquences en fonction du type de données

## Prochaines étapes

1. Analyse des données collectées
2. Modélisation et génération de conseils
3. Création d'une interface utilisateur
