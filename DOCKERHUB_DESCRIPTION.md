# 900 Care Tracker

Outil web self-hosted de suivi de consommation & avis pour un foyer abonné à [900 Care](https://900.care).
Self-hosted web app to track household consumption & reviews for [900 Care](https://900.care) subscribers.

📖 **Documentation complète / Full documentation** → https://github.com/vouvrat/900care-tracker

---

## 🇫🇷 Français

Suit qui consomme quel produit et à quel rythme, centralise les avis de chaque membre du foyer,
et calcule automatiquement les quantités à commander la prochaine fois.

**Fonctionnalités**
- Foyer configurable (nombre de membres, prénoms personnalisables)
- Catalogue de produits libre (nom, catégorie, unité)
- Journal de consommation par membre
- Avis internes par membre (note + commentaire), ou avis "foyer"
- Dashboard avec rythme de consommation estimé
- Suggestion automatique des quantités pour la prochaine commande
- Historique complet filtrable

**Démarrage rapide**
```bash
docker compose up --build -d
```
Puis ouvrir `http://localhost:8000`.

**Guides**
- Utilisation au quotidien → [docs/GUIDE_UTILISATEUR.md](https://github.com/vouvrat/900care-tracker/blob/main/docs/GUIDE_UTILISATEUR.md)
- Déploiement (local, Docker, Synology NAS) → [docs/DEPLOIEMENT.md](https://github.com/vouvrat/900care-tracker/blob/main/docs/DEPLOIEMENT.md)
- Architecture (stack, modèle de données) → [docs/ARCHITECTURE.md](https://github.com/vouvrat/900care-tracker/blob/main/docs/ARCHITECTURE.md)

---

## 🇬🇧 English

Tracks who consumes which product and at what rate, centralizes reviews from each household member,
and automatically suggests quantities to order next time.

**Features**
- Configurable household (member count, custom names)
- Free-form product catalog (name, category, unit)
- Per-member consumption log
- Per-member reviews (rating + comment), or household-wide reviews
- Dashboard with estimated consumption rate
- Automatic quantity suggestions for the next order
- Fully filterable history

**Quick start**
```bash
docker compose up --build -d
```
Then open `http://localhost:8000`.

**Guides**
- Day-to-day usage → [docs/GUIDE_UTILISATEUR.md](https://github.com/vouvrat/900care-tracker/blob/main/docs/GUIDE_UTILISATEUR.md)
- Deployment (local, Docker, Synology NAS) → [docs/DEPLOIEMENT.md](https://github.com/vouvrat/900care-tracker/blob/main/docs/DEPLOIEMENT.md)
- Architecture (stack, data model) → [docs/ARCHITECTURE.md](https://github.com/vouvrat/900care-tracker/blob/main/docs/ARCHITECTURE.md)

---

## Stack

Python (FastAPI + SQLModel/SQLite) + Jinja2, containerized with Docker — no external dependency, no frontend build.
