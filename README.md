# 900 Care — Suivi conso & avis famille

Outil web self-hosted pour un foyer abonné à [900 Care](https://900.care) :
il suit qui consomme quel produit et à quel rythme, centralise les avis de
chaque membre, et calcule automatiquement les quantités à commander la
prochaine fois.

- **Pourquoi et comment l'utiliser au quotidien** → [`docs/GUIDE_UTILISATEUR.md`](docs/GUIDE_UTILISATEUR.md)
- **Comment le déployer** (local, Docker, Docker Hub + Synology) → [`docs/DEPLOIEMENT.md`](docs/DEPLOIEMENT.md)
- **Comment il est construit** (stack, modèle de données, logique de calcul) → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Démarrage rapide

```bash
docker compose up --build -d
```

Puis ouvrir `http://localhost:8000`. Détails et autres méthodes de
déploiement (Docker Hub, NAS Synology) dans
[`docs/DEPLOIEMENT.md`](docs/DEPLOIEMENT.md).

## Fonctionnalités

- Foyer configurable : nombre de membres et prénoms personnalisables
- Catalogue de produits libre (nom, catégorie, unité)
- Journal de consommation par membre (début/fin d'utilisation d'un produit)
- Avis internes par membre (note + commentaire), ou avis "foyer"
- Dashboard : consommation par produit × membre, rythme mensuel estimé
- Suggestion automatique des quantités pour la prochaine commande
- Historique complet filtrable par membre/produit

## Stack

Python (FastAPI + SQLModel/SQLite) + Jinja2, conteneurisé avec Docker — pas
de dépendance externe, pas de build frontend. Détails dans
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
