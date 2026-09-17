# TODO — Outil suivi conso & avis 900 Care

Plan complet : /home/Vincent/.claude/plans/refactored-floating-orbit.md

## Étapes

- [x] Structure de dossiers (app/, tasks/)
- [x] tasks/todo.md, tasks/lessons.md
- [x] requirements.txt
- [x] app/db.py (engine SQLite + session)
- [x] app/models.py (Member, HouseholdSettings, Product, ConsumptionEvent, Review)
- [x] app/services/consumption.py (calcul rythme conso)
- [x] app/services/suggestions.py (calcul quantités suggérées)
- [x] app/routers/dashboard.py
- [x] app/routers/members.py
- [x] app/routers/products.py
- [x] app/routers/consumption.py
- [x] app/routers/reviews.py
- [x] app/routers/history.py
- [x] app/main.py (assemble app, init DB au démarrage)
- [x] templates/ (base.html, dashboard.html, members.html, products.html, log.html, reviews.html, history.html)
- [x] static/style.css
- [x] Dockerfile
- [x] docker-compose.yml
- [x] README.md
- [x] Vérification : app testée en local (uvicorn direct, pas de Docker dispo dans ce sandbox) —
      parcours complet validé : réglage foyer (4 membres) → renommage → ajout produit →
      3 événements de conso à des dates différentes → dashboard calcule bien le rythme
      (0.97/mois) et la suggestion (2 unités pour 2 mois de couverture) → avis (avec et
      sans membre) → historique filtrable. Tous les statuts HTTP à 200/303 comme attendu.

## Reste à faire par l'utilisateur

- [ ] Lancer `docker compose up --build -d` sur sa propre machine (Docker non disponible
      dans ce sandbox de dev, donc le build Docker lui-même n'a pas pu être testé ici —
      seul le Dockerfile/compose ont été relus, pas exécutés)

## Publication Docker Hub + déploiement Synology DS1515+ (2026-09-17)

- [x] `docker-compose.yml` : ajout du tag `image: vouvrat/900care-tracker:latest`
      (permet `docker compose build` + `docker compose push`)
- [x] `docker-compose.synology.yml` créé : pull-only, volume bind sur
      `/volume1/docker/900care/data` (au lieu du volume nommé, pour usage NAS)
- [x] README : section build/push Docker Hub (avec avertissement architecture
      ARM host → amd64 cible, DS1515+ = x86_64) + section déploiement via
      Container Manager
- [x] `docker login` (via token Docker Hub, --password-stdin)
- [x] `docker compose build` + `docker compose push` — image `vouvrat/900care-tracker:latest`
      publiée sur Docker Hub (2026-09-17)
- [ ] À faire par l'utilisateur sur le NAS : créer `/volume1/docker/900care/data`,
      créer le projet dans Container Manager avec `docker-compose.synology.yml`

## Session UI/UX + charte + catalogue (2026-09-17)

Toutes les étapes ci-dessous ont été testées de bout en bout (curl, vérification
DB, nettoyage des données de test) puis commit + push GitHub + push Docker Hub
à chaque étape. Dernier commit : `1b0e946`. Image Docker Hub à jour.

- [x] Description bilingue FR/EN pour Docker Hub (`DOCKERHUB_DESCRIPTION.md`,
      à coller manuellement dans l'onglet Description du repo Docker Hub)
- [x] Identité git locale configurée (Vincent Ouvrat / v.ouvrat@gmail.com,
      `git config` sans `--global`, ce repo uniquement)
- [x] Rendu mobile : tableaux dans `.grid-wrap` (scroll horizontal contenu),
      media queries <600px
- [x] Charte graphique 900 Care : rose `#f32aa4`, vert `#2ea957`, police
      Poppins (relevés depuis le CSS public du site) ; wordmark "900.care
      tracker" recréé en CSS/texte (pas de copie du logo officiel)
- [x] Menu hamburger mobile (checkbox CSS, sans JS)
- [x] Notation par étoiles (widget radio+CSS) au lieu du `<select>` pour les avis
- [x] Import du catalogue officiel 900 Care (18 produits, noms/catégories/images
      relevés via JSON-LD des pages publiques — voir lessons.md) :
      - `app/catalog_900care.py` : copie statique de secours
      - `app/services/catalog_sync.py` : fetch live + repli automatique
      - `app/scheduler.py` (APScheduler) : rafraîchit le cache catalogue chaque
        dimanche 4h (Europe/Paris) — ne fait qu'actualiser la liste, n'active
        plus rien automatiquement (revu suite au retour utilisateur)
      - Table `CatalogItem` : cache local du catalogue connu
      - Table `CatalogSyncLog` : historique des synchros (source live/fallback,
        nb de nouveautés, erreur éventuelle), affiché sur `/products`
      - Toggle produit par produit (switch CSS) sur `/products` pour activer/
        désactiver le suivi d'un produit du catalogue, au lieu d'un import en masse
      - Bouton "rafraîchir maintenant" pour forcer une synchro manuelle
- [x] Édition inline (catégorie/unité/notes) des produits déjà suivis, avec
      bouton Enregistrer par ligne — nécessaire car les produits importés du
      catalogue héritent d'une unité générique "unité"
- [x] Suppression d'un événement du journal de consommation (bouton Supprimer
      + confirmation, suppression définitive) pour corriger une erreur de saisie

## Reste à faire

- [ ] Utilisateur : coller `DOCKERHUB_DESCRIPTION.md` dans Docker Hub (onglet Description)
- [ ] Utilisateur : révoquer/régénérer le token Docker Hub collé en clair dans une
      conversation précédente (hygiène de sécurité, non bloquant)
- [ ] Utilisateur : finir le déploiement Synology (créer le dossier data, créer
      le projet Container Manager) — cf section précédente
- [ ] Vérifier après le premier dimanche que la synchro catalogue automatique
      tourne bien sur le NAS (le conteneur doit être allumé à 4h le dimanche)
