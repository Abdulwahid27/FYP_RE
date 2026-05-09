"""Seed brands + catalogue from real Shopify collection JSON (multi-brand).

Run:
  cd backend && .venv/bin/python -m app.seed

Each garment row is a real product (title, price, image, product URL) from the
brand's storefront. Bottoms / bags / socks are dropped at seed time. Winter
knitwear is *kept* in the DB but hidden at request time when the client passes
``feels_like_c`` from OpenWeather (see ``GET /api/garments``).
"""
from __future__ import annotations

import argparse
from collections import deque
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Brand, Garment, Gender, Event, Style
from .services.catalog_filters import is_upper_body_shopify_product
from .services.shopify_catalog import (
    ShopifyProduct,
    dict_to_shopify_product,
    fetch_collection_raw_products,
)


BRANDS: list[dict[str, str]] = [
    {
        "name": "J.",
        "slug": "junaid-jamshed",
        "description": "Men + women eastern; Cast & Crew / Sync.C western lines.",
        "website": "https://www.junaidjamshed.com",
    },
    {
        "name": "Gul Ahmed",
        "slug": "gul-ahmed",
        "description": "Men's eastern shalwar kameez & kurta; women's Ideas pret.",
        "website": "https://www.gulahmedshop.com",
    },
    {
        "name": "Outfitters",
        "slug": "outfitters",
        "description": "Men + women western shirts & tees.",
        "website": "https://outfitters.com.pk",
    },
    {
        "name": "Diners",
        "slug": "diners",
        "description": "Men's western shirts & polos.",
        "website": "https://www.diners.com.pk",
    },
    {
        "name": "Limelight",
        "slug": "limelight",
        "description": "Women's eastern tops & western tops.",
        "website": "https://www.limelight.pk",
    },
    {
        "name": "Beechtree",
        "slug": "beechtree",
        "description": "Women's western tops & dresses.",
        "website": "https://www.beechtree.pk",
    },
]

BRAND_BASE: dict[str, str] = {b["slug"]: b["website"] for b in BRANDS}

# (gender, style, event) → list of (brand_slug, shopify_collection_handle)
BUCKET_SOURCES: dict[tuple[Gender, Style, Event], list[tuple[str, str]]] = {
    (Gender.male, Style.eastern, Event.office_wear): [
        ("gul-ahmed", "mens-clothes-eastern-shalwar-kameez"),
        ("junaid-jamshed", "mens-kameez-shalwar-formal"),
    ],
    (Gender.male, Style.eastern, Event.hangouts): [
        ("gul-ahmed", "mens-clothes-eastern-gents-kurta"),
        ("junaid-jamshed", "mens-kurta-casual"),
    ],
    (Gender.male, Style.eastern, Event.religious): [
        ("junaid-jamshed", "mens-kurta-pajama"),
        ("gul-ahmed", "mens-clothes-eastern-gents-kurta"),
    ],
    (Gender.male, Style.eastern, Event.family_gatherings): [
        ("junaid-jamshed", "mens-kameez-shalwar-exclusive"),
        ("gul-ahmed", "mens-clothes-eastern-shalwar-kameez"),
    ],
    (Gender.male, Style.western, Event.office_wear): [
        ("outfitters", "men-shirts"),
        ("diners", "diners-formal-shirts"),
        ("diners", "diners-semi-formal-shirts"),
    ],
    (Gender.male, Style.western, Event.hangouts): [
        ("outfitters", "men-t-shirts"),
        ("diners", "diners-men-polo"),
        ("diners", "casual-printed-shirt"),
    ],
    (Gender.male, Style.western, Event.religious): [
        ("outfitters", "men-shirts"),
        ("diners", "black-white-shirts"),
        ("diners", "formal-check-shirts"),
    ],
    (Gender.male, Style.western, Event.family_gatherings): [
        ("outfitters", "men-t-shirts"),
        ("diners", "casual-classic-shirts"),
        ("diners", "autograph-shirts"),
    ],
    (Gender.female, Style.eastern, Event.office_wear): [
        ("junaid-jamshed", "womens-stitched-2-piece"),
        ("gul-ahmed", "women-ideas-pret-9-to-5"),
    ],
    (Gender.female, Style.eastern, Event.hangouts): [
        ("junaid-jamshed", "womens-stitched-kurti"),
        ("limelight", "daily-wear-without-embroidery-eastern-top"),
    ],
    (Gender.female, Style.eastern, Event.religious): [
        ("junaid-jamshed", "womens-stitched-3-piece"),
        ("gul-ahmed", "women-ideas-pret-essentials-3-piece"),
    ],
    (Gender.female, Style.eastern, Event.family_gatherings): [
        ("junaid-jamshed", "womens-stitched-co-ord-set"),
        ("gul-ahmed", "women-ideas-pret-signature-3-piece"),
    ],
    (Gender.female, Style.western, Event.office_wear): [
        ("limelight", "all-season-tops"),
        ("limelight", "dyed-western-top"),
        ("outfitters", "women-shirts"),
        ("beechtree", "btk-tops"),
    ],
    (Gender.female, Style.western, Event.hangouts): [
        ("limelight", "dyed-summer-tops"),
        ("outfitters", "women-t-shirts"),
        ("beechtree", "absolute-denim-tops-w22"),
    ],
    (Gender.female, Style.western, Event.religious): [
        ("outfitters", "women-shirts"),
        ("limelight", "all-season-tops"),
        ("beechtree", "btk-tops"),
    ],
    (Gender.female, Style.western, Event.family_gatherings): [
        ("limelight", "embroidered-pret"),
        ("beechtree", "western-dresses"),
        ("outfitters", "women-t-shirts"),
    ],
}

PRODUCTS_PER_BUCKET = 5
RAW_PER_COLLECTION = 45


def _ensure_brands(db: Session) -> dict[str, Brand]:
    slug_to_brand: dict[str, Brand] = {}
    for b in BRANDS:
        existing = db.execute(select(Brand).where(Brand.slug == b["slug"])).scalar_one_or_none()
        if existing:
            for k, v in b.items():
                setattr(existing, k, v)
            slug_to_brand[b["slug"]] = existing
        else:
            row = Brand(**b)
            db.add(row)
            db.flush()
            slug_to_brand[b["slug"]] = row
    return slug_to_brand


def _ingest_bucket(
    db: Session,
    *,
    brand: Brand,
    gender: Gender,
    style: Style,
    event: Event,
    products: Iterable[ShopifyProduct],
) -> tuple[int, int]:
    inserted = 0
    refreshed = 0
    for p in products:
        tags = (p.tags or "")[:800] if p.tags else None
        ex = db.execute(
            select(Garment).where(
                Garment.brand_id == brand.id,
                Garment.product_url == p.product_url,
            )
        ).scalar_one_or_none()
        if ex:
            ex.title = p.title
            ex.image_url = p.image_url
            ex.price = p.price
            ex.color = p.color
            ex.product_type = p.product_type
            ex.tags = tags
            ex.gender = gender
            ex.style = style
            ex.event = event
            refreshed += 1
        else:
            db.add(
                Garment(
                    brand_id=brand.id,
                    title=p.title,
                    gender=gender,
                    event=event,
                    style=style,
                    image_url=p.image_url,
                    product_url=p.product_url,
                    product_type=p.product_type,
                    tags=tags,
                    price=p.price,
                    color=p.color,
                )
            )
            inserted += 1
    return inserted, refreshed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Only ensure brands exist; skip pulling catalogue from storefronts.",
    )
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        slug_to_brand = _ensure_brands(db)
        db.commit()

        if args.no_fetch:
            print("Brands ready (--no-fetch: skipped catalogue refresh).")
            return

        print("Pulling real products (Shopify, multi-brand, upper-body only)…")
        total_inserted = total_refreshed = 0

        for bucket in sorted(BUCKET_SOURCES.keys(), key=lambda k: (k[0].value, k[1].value, k[2].value)):
            gender, style, event = bucket
            seen: set[str] = set()

            # Per-source queues + **round-robin** merge so every brand in the bucket
            # gets representation (Outfitters alone must not consume all 5 slots).
            deques: list[tuple[str, deque[ShopifyProduct]]] = []
            for slug, handle in BUCKET_SOURCES[bucket]:
                base = BRAND_BASE[slug]
                q: deque[ShopifyProduct] = deque()
                for raw in fetch_collection_raw_products(base, handle, limit=RAW_PER_COLLECTION):
                    if not is_upper_body_shopify_product(raw):
                        continue
                    sp = dict_to_shopify_product(base, raw)
                    if not sp or not sp.product_url or sp.product_url in seen:
                        continue
                    seen.add(sp.product_url)
                    q.append(sp)
                    if len(q) >= 12:
                        break
                if q:
                    deques.append((slug, q))

            merged: list[tuple[str, ShopifyProduct]] = []
            while len(merged) < PRODUCTS_PER_BUCKET:
                active = [(s, d) for s, d in deques if d]
                if not active:
                    break
                before = len(merged)
                for slug, d in active:
                    if len(merged) >= PRODUCTS_PER_BUCKET:
                        break
                    merged.append((slug, d.popleft()))
                if len(merged) == before:
                    break

            slice_ = merged[:PRODUCTS_PER_BUCKET]
            if not slice_:
                print(f"  WARNING empty bucket {gender.value} {style.value} {event.value}")
                continue

            for slug, sp in slice_:
                brand = slug_to_brand[slug]
                ins, ref = _ingest_bucket(
                    db,
                    brand=brand,
                    gender=gender,
                    style=style,
                    event=event,
                    products=[sp],
                )
                total_inserted += ins
                total_refreshed += ref

            print(
                f"  {gender.value:6s} · {style.value:7s} · {event.value:18s} "
                f"→ {len(slice_)} item(s)"
            )

        db.commit()
        print(f"\nDone. {total_inserted} new garments, {total_refreshed} refreshed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
