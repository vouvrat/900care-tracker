# Lessons

(Rempli au fil des corrections — format : [date] | ce qui a mal tourné | règle pour l'éviter)

[2026-09-17] | `Jinja2Templates.TemplateResponse("name.html", {"request": request, ...})` (ancien style) plante avec `TypeError: unhashable type: 'dict'` sur Starlette récent (1.x) | Toujours utiliser la signature moderne `templates.TemplateResponse(request, "name.html", {...})` (request en 1er argument positionnel, hors du dict de contexte).

[2026-09-17] | Un `<select>` HTML avec une option `value=""` envoyée vers un paramètre FastAPI typé `int`/`Optional[int]` (Form ou query) déclenche une 422 car `""` n'est pas castable en int | Typer ces champs en `str = Form("")` / `str = ""` côté handler puis convertir manuellement (`int(x) if x.strip() else None`) quand une valeur vide doit être acceptée.

