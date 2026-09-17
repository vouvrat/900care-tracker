"""Synchronisation du catalogue produits avec https://900.care.

Récupère la liste des produits publiée par le site (via les données
structurées JSON-LD des pages publiques — aucune clé API, aucun scraping
du JS client) et ajoute automatiquement les produits qui manquent encore
au catalogue local. Les images restent hébergées sur le CDN 900.care et
sont affichées par lien direct, jamais copiées.
"""

import json
import re
import urllib.error
import urllib.request
from datetime import datetime

from sqlmodel import Session, select

from app.catalog_900care import CATALOG_900CARE
from app.models import CatalogSyncLog, Product

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
    de décider du repli (voir sync_catalog).
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


def sync_catalog(session: Session) -> CatalogSyncLog:
    """Récupère le catalogue (live, avec repli sur la copie statique) et
    ajoute les produits manquants. Journalise le résultat et le retourne."""
    try:
        catalog = fetch_live_catalog()
        source = "live"
        error = ""
    except Exception as exc:  # réseau down, site changé, etc. — on ne casse pas l'appli
        catalog = CATALOG_900CARE
        source = "fallback"
        error = str(exc)[:500]

    existing_names = {
        p.name.strip().lower()
        for p in session.exec(select(Product).where(Product.active == True))  # noqa: E712
    }

    added = 0
    for item in catalog:
        key = item["name"].strip().lower()
        if key in existing_names:
            continue
        session.add(Product(
            name=item["name"],
            category=item.get("category", ""),
            unit="unité",
            image_url=item.get("image_url", ""),
        ))
        existing_names.add(key)
        added += 1

    log = CatalogSyncLog(ran_at=datetime.utcnow(), source=source, added_count=added, error=error)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
