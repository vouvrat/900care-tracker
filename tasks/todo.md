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
- [ ] À faire par l'utilisateur : `docker login`, build/push depuis sa machine,
      créer `/volume1/docker/900care/data` sur le NAS, créer le projet dans
      Container Manager avec `docker-compose.synology.yml`
