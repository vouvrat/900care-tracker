# Déploiement

Trois façons de faire tourner l'outil, de la plus simple à la plus "en
production" :

1. [Développement local sans Docker](#1-développement-local-sans-docker)
2. [Docker en local](#2-docker-en-local)
3. [Docker Hub + NAS Synology](#3-publier-sur-docker-hub-et-déployer-sur-synology)

Dans tous les cas, les données vivent dans un unique fichier SQLite —
sauvegarder ce fichier suffit à sauvegarder tout l'historique (voir
[Sauvegarde](#sauvegarde-et-restauration) en bas de page).

## 1. Développement local sans Docker

Utile pour tester rapidement une modification du code sans reconstruire
d'image.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DB_PATH=./900care.db uvicorn app.main:app --reload
```

L'app est alors sur `http://localhost:8000`.

## 2. Docker en local

```bash
docker compose up --build -d
```

- L'app est accessible sur `http://localhost:8000` (ou l'IP de la machine).
- Les données SQLite sont persistées dans le volume Docker nommé
  `900care_data`, qui survit aux redémarrages/rebuilds.

Arrêter :

```bash
docker compose down
```

`docker compose down` ne supprime pas le volume par défaut. Pour tout
réinitialiser (⚠️ perte de données) :

```bash
docker compose down -v
```

## 3. Publier sur Docker Hub et déployer sur Synology

Objectif : construire l'image une fois sur un poste de dev, la publier sur
Docker Hub (`vouvrat/900care-tracker`), puis la faire tourner sur un NAS
Synology (testé visé : DS1515+, architecture **x86_64/amd64**) via Container
Manager, sans jamais avoir besoin d'installer d'outils de build sur le NAS.

### 3.1 Construire et pousser l'image (depuis le poste de dev)

Ces commandes se lancent **en local sur ta machine**, jamais depuis un
environnement tiers : `docker login` demande tes identifiants Docker Hub, qui
ne doivent jamais transiter ailleurs.

```bash
docker login
docker compose build
docker compose push
```

Ceci construit et pousse `vouvrat/900care-tracker:latest` (le tag `image:`
est déjà défini dans `docker-compose.yml`).

⚠️ **Attention à l'architecture CPU.** Si ton poste de dev est en ARM (Mac
Apple Silicon M1/M2/M3, PC ARM) et que la cible est en x86_64/amd64 (c'est le
cas du DS1515+), un build classique produirait une image incompatible qui ne
démarrera pas sur le NAS. Dans ce cas, construire explicitement en amd64 :

```bash
docker login
docker buildx build --platform linux/amd64 -t vouvrat/900care-tracker:latest --push .
```

Si le poste de dev est déjà x86_64/amd64 (PC Windows/Linux classique, Mac
Intel), la commande standard (`docker compose build` + `push`) suffit.

### 3.2 Préparer le NAS

Créer le dossier de données, par exemple en SSH sur le NAS :

```bash
mkdir -p /volume1/docker/900care/data
```

(ou via l'interface **File Station**, en créant les sous-dossiers `docker`
→ `900care` → `data` dans le volume partagé).

### 3.3 Déployer via Container Manager

1. Ouvrir **Container Manager** (ou **Docker** sur DSM plus ancien).
2. Aller dans l'onglet **Projet** → **Créer**.
3. Nommer le projet (ex. `900care`), choisir un chemin sur le NAS pour les
   fichiers du projet.
4. Dans l'éditeur de compose intégré, coller le contenu de
   [`docker-compose.synology.yml`](../docker-compose.synology.yml).
5. Lancer la création : Container Manager télécharge automatiquement
   `vouvrat/900care-tracker:latest` depuis Docker Hub (image publique, pas
   d'identifiants nécessaires).
6. Une fois le conteneur démarré, l'app est accessible sur
   `http://<ip-du-nas>:8000`.

### 3.4 Mettre à jour après une nouvelle version

Après un nouveau `docker compose push` depuis le poste de dev :

- **Via Container Manager** : Projet → **Actions** → **Arrêter**, puis
  **Actions** → **Mettre à jour** (ou re-télécharger l'image) →
  **Démarrer**.
- **Via SSH sur le NAS** :

```bash
docker compose -f docker-compose.synology.yml pull
docker compose -f docker-compose.synology.yml up -d
```

## Variables d'environnement

| Variable | Défaut | Rôle |
|---|---|---|
| `DB_PATH` | `/data/900care.db` (dans le conteneur) | Chemin du fichier SQLite |

## Sauvegarde et restauration

Toute la donnée applicative (membres, produits, événements, avis) vit dans
le fichier SQLite pointé par `DB_PATH`. Le sauvegarder suffit :

- **Déploiement Synology** : sauvegarder le dossier
  `/volume1/docker/900care/data` (inclure ce dossier dans Hyper Backup ou une
  tâche de sauvegarde planifiée DSM classique).
- **Déploiement Docker local (volume nommé)** :

```bash
docker run --rm -v 900care_data:/data -v "$PWD":/backup alpine \
  tar czf /backup/900care-backup.tar.gz -C /data .
```

Pour restaurer, arrêter le conteneur, extraire l'archive dans le
dossier/volume de données, puis redémarrer.
