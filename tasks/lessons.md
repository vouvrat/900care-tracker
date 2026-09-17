# Lessons

(Rempli au fil des corrections — format : [date] | ce qui a mal tourné | règle pour l'éviter)

[2026-09-17] | `Jinja2Templates.TemplateResponse("name.html", {"request": request, ...})` (ancien style) plante avec `TypeError: unhashable type: 'dict'` sur Starlette récent (1.x) | Toujours utiliser la signature moderne `templates.TemplateResponse(request, "name.html", {...})` (request en 1er argument positionnel, hors du dict de contexte).

[2026-09-17] | Un `<select>` HTML avec une option `value=""` envoyée vers un paramètre FastAPI typé `int`/`Optional[int]` (Form ou query) déclenche une 422 car `""` n'est pas castable en int | Typer ces champs en `str = Form("")` / `str = ""` côté handler puis convertir manuellement (`int(x) if x.strip() else None`) quand une valeur vide doit être acceptée.

[2026-09-17] | Ajouter une colonne à un modèle SQLModel existant (`image_url` sur `Product`) ne modifie pas une base SQLite déjà créée — `create_all` ne fait que `CREATE TABLE IF NOT EXISTS` | Écrire une migration légère dans `init_db()` (`PRAGMA table_info` + `ALTER TABLE ... ADD COLUMN` si la colonne manque) pour ne jamais perdre les données existantes du foyer.

[2026-09-17] | 900.care est un site Shopify Hydrogen (headless) : `/products.json` renvoie 404, `sitemap.xml` est vide/cassé, le HTML des pages collection ne contient pas le catalogue (rendu côté client) | Le catalogue complet est quand même exposé de façon fiable via les blocs JSON-LD (`<script type="application/ld+json">`, `@type: ItemList` sur la page collection, `@type: Product` avec `image` sur chaque page produit) — s'appuyer dessus plutôt que scraper le DOM ou chercher une API JSON classique.

[2026-09-17] | Copier/héberger dans un dépôt public (ou une image Docker publique) le logo officiel ou les photos produit d'une marque tierce = redistribution d'assets protégés, risque de droits de marque | Ne jamais copier ces fichiers dans le repo/l'image ; soit recréer l'identité visuelle en CSS/texte (wordmark), soit hotlink vers le CDN de la marque (`<img src="https://cdn...">`) sans copier le fichier.

[2026-09-17] | Réutiliser un secret déjà collé dans la conversation (token Docker Hub) pour un appel `curl` vers une API externe est bloqué par le classificateur auto-mode de Claude Code ("Credential Materialization"), même si le secret est déjà visible dans le transcript | Pour toute action nécessitant de renvoyer un secret vers un service tiers, préparer le contenu/la commande et la faire exécuter par l'utilisateur lui-même (préfixe `!`) plutôt que d'insister ou chercher un contournement.

[2026-09-17] | `curl -d "champ=valeur+accentué"` mange les caractères UTF-8 accentués (mauvais encodage du `+`/espace) lors de tests manuels d'endpoints POST | Utiliser `curl --data-urlencode "champ=valeur accentuée"` pour tester des formulaires avec des accents ; ce n'est qu'un artefact de test, pas un bug appli (vérifié : un vrai formulaire HTML encode correctement).

[2026-09-17] | Après une demande de fonctionnalité ("scan hebdo + auto-ajout"), une demande suivante peut en réalité vouloir revenir sur une partie du comportement déjà implémenté (ici : ne plus tout auto-ajouter, contrôle produit par produit) | Quand une nouvelle demande semble contredire un comportement qu'on vient d'implémenter sur la même fonctionnalité, poser une question de clarification ciblée (AskUserQuestion) plutôt que de supposer lequel des deux comportements garder.

