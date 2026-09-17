# Architecture technique

## Stack

- **Backend** : Python + [FastAPI](https://fastapi.tiangolo.com/) + [SQLModel](https://sqlmodel.tiangolo.com/) (ORM sur SQLite)
- **Stockage** : SQLite, fichier unique (`/data/900care.db` dans le conteneur), monté sur un volume Docker persistant
- **Frontend** : rendu serveur avec Jinja2 (pas de build JS/npm), CSS custom dans `app/static/style.css`
- **Conteneurisation** : image Docker unique (`python:3.12-slim`), orchestrée via `docker-compose.yml` (dev/local) ou `docker-compose.synology.yml` (déploiement NAS, pull-only)

Choix volontaire : pas de base de données serveur séparée (Postgres, MySQL...)
ni de build frontend — l'outil doit rester un "micro-serveur" simple à faire
tourner et à sauvegarder pour un usage familial.

## Structure des fichiers

```
900Care/
  app/
    main.py                  # Instancie FastAPI, monte les routers/static, init DB au démarrage
    db.py                    # Engine SQLModel + dépendance de session
    models.py                 # Modèles de données (voir ci-dessous)
    templating.py              # Instance partagée de Jinja2Templates
    services/
      consumption.py           # Calcul du rythme de consommation par produit × membre
      suggestions.py             # Calcul des quantités suggérées pour la commande
      settings.py                 # Paramètres du foyer (singleton) + synchronisation des membres
    routers/
      dashboard.py               # GET /
      members.py                  # /members (CRUD membres, taille foyer, couverture commande)
      products.py                  # /products (CRUD catalogue)
      consumption.py                # /log (saisie et historique récent des événements)
      reviews.py                     # /reviews (avis famille)
      history.py                      # /history (timeline combinée filtrable)
    templates/                        # Gabarits Jinja2 (un par page + base.html)
    static/style.css                   # Styles
  Dockerfile
  docker-compose.yml                    # Build + run local (avec tag image Docker Hub)
  docker-compose.synology.yml            # Déploiement NAS : pull-only, volume bind Synology
  requirements.txt
  docs/                                   # Cette documentation
  tasks/                                   # Suivi de travail (todo.md, lessons.md)
```

## Modèle de données

- **`Member`** : `id`, `name`, `active`, `created_at`
  Un membre désactivé (retiré via la réduction de la taille du foyer)
  conserve son historique de conso/avis mais disparaît des listes actives.

- **`HouseholdSettings`** (singleton, une seule ligne) : `household_size`,
  `order_coverage_months` (par défaut 2.0)

- **`Product`** : `id`, `name`, `category`, `unit`, `notes`, `active`

- **`ConsumptionEvent`** : `id`, `product_id`, `member_id`, `event_type`
  (`"started"` ou `"finished"`), `quantity`, `event_date`

- **`Review`** : `id`, `product_id`, `member_id` (nullable = avis "Foyer"),
  `rating` (1-5), `comment`, `review_date`

## Logique de calcul

### Rythme de consommation (`app/services/consumption.py`)

Pour chaque couple `(produit, membre)`, on récupère les dates de tous les
événements `finished`, triées. S'il y en a au moins deux, l'intervalle moyen
en jours entre événements consécutifs donne le rythme mensuel :

```python
rate = 30.0 / intervalle_moyen_en_jours
```

Avec moins de deux événements, le rythme est `None` ("pas assez de données").

Le **rythme foyer** pour un produit est la somme des rythmes (non nuls) de
tous les membres actifs.

### Suggestion de commande (`app/services/suggestions.py`)

```python
quantité_suggérée = ceil(rythme_foyer_mensuel * order_coverage_months)
```

Seuls les produits avec un rythme foyer strictement positif apparaissent
dans la liste de suggestions, triée par quantité décroissante.

### Taille du foyer (`app/services/settings.py`)

`sync_member_count` ajuste le nombre de membres actifs pour correspondre à
la taille voulue :
- si on augmente, des membres `"Membre N"` sont créés (à renommer ensuite) ;
- si on diminue, les membres excédentaires (les derniers par `id`) sont
  désactivés (`active = False`), jamais supprimés — leur historique reste
  intact et consultable dans `/history`.

## Points d'attention pour la maintenance

- **Signature Jinja2Templates** : ce projet utilise l'API moderne de
  Starlette `templates.TemplateResponse(request, "nom.html", contexte)`
  (le `request` en premier argument positionnel, hors du dict de contexte).
  L'ancienne signature `TemplateResponse("nom.html", {"request": ..., ...})`
  provoque une erreur `TypeError: unhashable type: 'dict'` sur les versions
  récentes de Starlette (voir `tasks/lessons.md`).
- **Champs optionnels de formulaire/query string** : un `<select>` avec une
  option vide (`value=""`) envoyée à un paramètre FastAPI typé `int` ou
  `Optional[int]` provoque une erreur 422. Ces champs (`member_id` optionnel
  dans `/reviews`, filtres de `/history`) sont donc typés `str` côté handler
  puis convertis manuellement.
