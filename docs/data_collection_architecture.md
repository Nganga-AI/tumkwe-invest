# Architecture du système de collecte de données

Ce document décrit l'architecture du système de collecte de données financières de Tumkwe Invest.

## Vue d'ensemble

Le système est conçu pour collecter, valider et stocker des données financières provenant de diverses sources. Ces données seront utilisées ultérieurement pour l'analyse et la génération de conseils d'investissement.

```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
|  Sources externes |     |  Collecteurs de   |     |  Stockage local   |
|  (APIs, Web)      | --> |  données          | --> |  (Fichiers JSON,  |
|                   |     |                   |     |   CSV)            |
+-------------------+     +-------------------+     +-------------------+
                                   |
                                   v
                          +-------------------+
                          |                   |
                          |  Validation des   |
                          |  données          |
                          |                   |
                          +-------------------+
```

## Composants principaux

### 1. Modèles de données (models.py)

Définit les structures de données pour stocker les différents types d'informations financières:

- `StockPrice`: Prix d'actions historiques
- `FinancialStatement`: États financiers (compte de résultat, bilan, flux de trésorerie)
- `CompanyProfile`: Informations sur l'entreprise
- `KeyMetrics`: Indicateurs financiers clés
- `NewsArticle`: Articles de presse et actualités
- `SECFiling`: Documents déposés auprès de la SEC

### 2. Collecteurs spécialisés

Modules qui se connectent à différentes sources de données:

- `yahoo_finance.py`: Collecte des prix d'actions et états financiers via Yahoo Finance
- `sec_edgar.py`: Collecte des documents officiels auprès de la SEC
- `yahoo_news.py`: Collecte des actualités via Yahoo Finance
- `news_collector.py`: Collecte des actualités via News API
- `financial_metrics.py`: Collecte des indicateurs financiers avancés

### 3. Validation des données (validation.py)

Vérifie la qualité et la cohérence des données:

- Détection des valeurs aberrantes dans les prix d'actions
- Vérification de la cohérence des états financiers
- Validation des dates et des périodes
- Vérification de l'exhaustivité des données

### 4. Gestionnaire de collecte (collector_manager.py)

Coordonne le processus de collecte:

- Planifie les tâches de collecte selon différentes fréquences
- Gère les mises à jour automatiques
- Stocke les données de manière cohérente
- Fournit des rapports de validation

## Flux de travail typique

1. L'utilisateur spécifie les symboles d'actions à surveiller
2. Le gestionnaire de collecte crée des tâches pour chaque type de données
3. Les collecteurs spécialisés récupèrent les données auprès des différentes sources
4. Les données sont validées pour détecter les problèmes potentiels
5. Les données validées sont stockées localement dans un format standardisé
6. Les mises à jour sont programmées selon la fréquence appropriée

## Contraintes et optimisations

- **Limites d'API**: Le système respecte les limites de requêtes des APIs gratuites
- **Mise en cache**: Les données sont mises en cache pour réduire les appels aux APIs
- **Tolérance aux erreurs**: Les erreurs de collecte sont consignées et n'arrêtent pas le processus
- **Validation automatique**: Les problèmes de qualité de données sont détectés et signalés

## Extension du système

Pour ajouter une nouvelle source de données:

1. Créer un nouveau collecteur dans le dossier `collectors/`
2. Adapter les données collectées aux modèles existants
3. Ajouter des règles de validation spécifiques si nécessaire
4. Intégrer le nouveau collecteur dans le gestionnaire de collecte
