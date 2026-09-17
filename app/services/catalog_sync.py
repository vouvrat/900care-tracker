"""Synchronisation du catalogue produits avec https://900.care.

Récupère la liste des produits publiée par le site (via les données
structurées JSON-LD des pages publiques — aucune clé API, aucun scraping
du JS client) et met à jour le cache local CatalogItem : nom, catégorie,
image. Ne touche jamais à la table Product — c'est l'utilisateur qui
choisit, produit par produit, ce qu'il suit réellement (voir toggle_product
dans app/routers/products.py). Les images restent hébergées sur le CDN
900.care et sont affichées par lien direct, jamais copiées.
"""

import json
import re
import urllib.error
import urllib.request
from datetime import datetime

from sqlmodel import Session, select

from app.catalog_900care import CATALOG_900CARE
from app.models import CatalogItem, CatalogSyncLog

CATALOG_URL = "https://900.care/collections/all"
USER_AGENT = "Mozilla/5.0 (900Care-Tracker self-hosted catalog sync)"
REQUEST_TIMEOUT = 15

_CATEGORY_BY_NAME = {c["name"].strip().lower(): c["category"] for c in CATALOG_900CARE}


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read().decode("utf-8", "ignore")


def _extract_ld_json_blocks(html: str):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            yield json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            continue


def fetch_live_catalog() -> list[dict]:
    """Interroge 900.care et retourne [{name, category, image_url}, ...].

    Lève une exception si le site est injoignable ou si sa structure a
    changé au point de ne plus exposer les données attendues — à l'appelant
    de décider du repli (voir refresh_catalog_cache).
    """
    html = _fetch(CATALOG_URL)

    item_list = None
    for block in _extract_ld_json_blocks(html):
        blocks = block if isinstance(block, list) else [block]
        for b in blocks:
            if isinstance(b, dict) and b.get("@type") == "ItemList":
                item_list = b
                break
        if item_list:
            break

    if not item_list or not item_list.get("itemListElement"):
        raise ValueError("Structure inattendue : aucun ItemList JSON-LD trouvé sur la page catalogue")

    catalog = []
    for entry in item_list["itemListElement"]:
        name = entry.get("name")
        url = entry.get("url")
        if not name or not url:
            continue

        image_url = ""
        try:
            product_html = _fetch(url)
            for block in _extract_ld_json_blocks(product_html):
                if isinstance(block, dict) and block.get("@type") == "Product":
                    image_url = block.get("image", "")
                    break
        except (urllib.error.URLError, TimeoutError):
            pass  # on garde le produit même sans image plutôt que de le perdre

        category = _CATEGORY_BY_NAME.get(name.strip().lower(), "")
        catalog.append({"name": name, "category": category, "image_url": image_url})

    return catalog


def seed_catalog_cache_if_empty(session: Session) -> None:
    """Amorce le cache avec la copie statique au tout premier démarrage,
    pour que les toggles soient utilisables avant la première synchro."""
    if session.exec(select(CatalogItem)).first():
        return
    for item in CATALOG_900CARE:
        session.add(CatalogItem(
            name=item["name"],
            category=item["category"],
            image_url=item["image_url"],
        ))
    session.commit()


def refresh_catalog_cache(session: Session) -> CatalogSyncLog:
    """Récupère le catalogue (live, avec repli sur la copie statique) et
    met à jour le cache CatalogItem (ajoute les nouveautés, rafraîchit
    catégorie/image des entrées existantes). Journalise le résultat."""
    try:
        catalog = fetch_live_catalog()
        source = "live"
        error = ""
    except Exception as exc:  # réseau down, site changé, etc. — on ne casse pas l'appli
        catalog = CATALOG_900CARE
        source = "fallback"
        error = str(exc)[:500]

    existing = {c.name.strip().lower(): c for c in session.exec(select(CatalogItem))}

    added = 0
    now = datetime.utcnow()
    for item in catalog:
        key = item["name"].strip().lower()
        current = existing.get(key)
        if current:
            current.category = item.get("category", "") or current.category
            current.image_url = item.get("image_url", "") or current.image_url
            current.updated_at = now
            session.add(current)
        else:
            session.add(CatalogItem(
                name=item["name"],
                category=item.get("category", ""),
                image_url=item.get("image_url", ""),
                updated_at=now,
            ))
            added += 1

    log = CatalogSyncLog(ran_at=now, source=source, added_count=added, error=error)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
