"""Seed brands and catalog rows with images scraped from public brand store pages.

Run:
  cd backend && .venv/bin/python -m app.seed

Requires:
  pip install -r requirements.txt
"""
from __future__ import annotations

import argparse
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Brand, Garment, Gender, Occasion
from .services.brand_scrape import fetch_image_urls_for_brand, fetch_og_image_url


BRANDS = [
    {
        "name": "Khaadi",
        "slug": "khaadi",
        "description": "Contemporary Pakistani fashion known for vibrant prints.",
        "website": "https://pk.khaadi.com",
    },
    {
        "name": "Sapphire",
        "slug": "sapphire",
        "description": "Modern silhouettes with rich textures.",
        "website": "https://pk.sapphireonline.pk",
    },
    {
        "name": "Gul Ahmed",
        "slug": "gul-ahmed",
        "description": "Heritage textile house with everyday and festive wear.",
        "website": "https://www.gulahmedshop.com",
    },
    {
        "name": "Alkaram Studio",
        "slug": "alkaram",
        "description": "Premium prints and embroidered collections.",
        "website": "https://www.alkaramstudio.com",
    },
    {
        "name": "Outfitters",
        "slug": "outfitters",
        "description": "High-street western and fusion wear.",
        "website": "https://outfitters.com.pk",
    },
    {
        "name": "Bonanza Satrangi",
        "slug": "bonanza-satrangi",
        "description": "Festive and formal eastern wear.",
        "website": "https://bonanzasatrangi.com",
    },
    {
        "name": "J.",
        "slug": "junaid-jamshed",
        "description": "Classic eastern menswear and womenswear.",
        "website": "https://www.junaidjamshed.com",
    },
]

# Public listing or category pages (server-rendered HTML). Tweak if a site
# changes layout; prefer URLs that list products with <img> or JSON-LD.
# Listing/home URLs that return HTML in your region. If a line 404s, swap in
# a working category or homepage for that brand (see README).
CATALOG_SEED_URLS: dict[str, list[str]] = {
    "khaadi": [
        "https://pk.khaadi.com/",
    ],
    "sapphire": [
        "https://pk.sapphireonline.pk/",
    ],
    "gul-ahmed": [
        "https://www.gulahmedshop.com/collections/women",
        "https://www.gulahmedshop.com/collections/all",
        "https://www.gulahmedshop.com/",
    ],
    "alkaram": [
        "https://www.alkaramstudio.com/collections/winter-25",
    ],
    "outfitters": [
        "https://outfitters.com.pk/collections/all",
        "https://outfitters.com.pk/collections",
        "https://outfitters.com.pk/",
    ],
    "bonanza-satrangi": [
        "https://bonanzasatrangi.com/collections/ready-to-wear",
    ],
    "junaid-jamshed": [
        "https://www.junaidjamshed.com/",
    ],
}


SLOTS: list[dict] = [
    {"brand_slug": "khaadi", "title": "Embroidered Lawn Kurta", "gender": Gender.female, "occasion": Occasion.casual, "price": "PKR 4,500", "color": "Mint"},
    {"brand_slug": "khaadi", "title": "Festive Anarkali Top", "gender": Gender.female, "occasion": Occasion.wedding, "price": "PKR 14,900", "color": "Maroon"},
    {"brand_slug": "khaadi", "title": "Office Solid Kurta", "gender": Gender.female, "occasion": Occasion.office, "price": "PKR 5,200", "color": "Charcoal"},
    {"brand_slug": "khaadi", "title": "Party Sequin Top", "gender": Gender.female, "occasion": Occasion.party, "price": "PKR 9,800", "color": "Black"},
    {"brand_slug": "sapphire", "title": "Linen Casual Shirt", "gender": Gender.male, "occasion": Occasion.casual, "price": "PKR 4,200", "color": "Beige"},
    {"brand_slug": "sapphire", "title": "Slim Fit Office Shirt", "gender": Gender.male, "occasion": Occasion.office, "price": "PKR 4,800", "color": "Sky"},
    {"brand_slug": "sapphire", "title": "Festive Embroidered Shirt", "gender": Gender.male, "occasion": Occasion.wedding, "price": "PKR 12,500", "color": "Ivory"},
    {"brand_slug": "sapphire", "title": "Party Black Tee", "gender": Gender.male, "occasion": Occasion.party, "price": "PKR 2,200", "color": "Black"},
    {"brand_slug": "gul-ahmed", "title": "Printed Lawn Kurta", "gender": Gender.female, "occasion": Occasion.casual, "price": "PKR 3,900", "color": "Sky"},
    {"brand_slug": "gul-ahmed", "title": "Bridal Choli Top", "gender": Gender.female, "occasion": Occasion.wedding, "price": "PKR 22,500", "color": "Red"},
    {"brand_slug": "gul-ahmed", "title": "Workwear Tunic", "gender": Gender.female, "occasion": Occasion.office, "price": "PKR 5,500", "color": "Navy"},
    {"brand_slug": "alkaram", "title": "Embroidered Casual Kurta", "gender": Gender.female, "occasion": Occasion.casual, "price": "PKR 4,300", "color": "Pink"},
    {"brand_slug": "alkaram", "title": "Wedding Gota Top", "gender": Gender.female, "occasion": Occasion.wedding, "price": "PKR 17,800", "color": "Gold"},
    {"brand_slug": "alkaram", "title": "Party Chiffon Blouse", "gender": Gender.female, "occasion": Occasion.party, "price": "PKR 8,400", "color": "Wine"},
    {"brand_slug": "outfitters", "title": "Graphic Casual Tee", "gender": Gender.male, "occasion": Occasion.casual, "price": "PKR 1,990", "color": "White"},
    {"brand_slug": "outfitters", "title": "Smart Office Shirt", "gender": Gender.male, "occasion": Occasion.office, "price": "PKR 3,490", "color": "Light Blue"},
    {"brand_slug": "outfitters", "title": "Party Henley", "gender": Gender.male, "occasion": Occasion.party, "price": "PKR 2,890", "color": "Olive"},
    {"brand_slug": "outfitters", "title": "Smart Casual Polo", "gender": Gender.male, "occasion": Occasion.casual, "price": "PKR 2,490", "color": "Navy"},
    {"brand_slug": "bonanza-satrangi", "title": "Bridal Anarkali Top", "gender": Gender.female, "occasion": Occasion.wedding, "price": "PKR 19,500", "color": "Rust"},
    {"brand_slug": "bonanza-satrangi", "title": "Casual Print Kurta", "gender": Gender.female, "occasion": Occasion.casual, "price": "PKR 3,800", "color": "Lilac"},
    {"brand_slug": "bonanza-satrangi", "title": "Office Formal Kurta", "gender": Gender.female, "occasion": Occasion.office, "price": "PKR 4,900", "color": "Stone"},
    {"brand_slug": "junaid-jamshed", "title": "Festive Kurta (Men)", "gender": Gender.male, "occasion": Occasion.wedding, "price": "PKR 8,500", "color": "Cream"},
    {"brand_slug": "junaid-jamshed", "title": "Office Dress Shirt", "gender": Gender.male, "occasion": Occasion.office, "price": "PKR 4,200", "color": "White"},
    {"brand_slug": "junaid-jamshed", "title": "Casual Cotton Kurta", "gender": Gender.male, "occasion": Occasion.casual, "price": "PKR 3,500", "color": "Sand"},
    {"brand_slug": "junaid-jamshed", "title": "Party Shalwar Top", "gender": Gender.male, "occasion": Occasion.party, "price": "PKR 4,800", "color": "Black"},
]


def _ensure_brands(db: Session) -> dict[str, Brand]:
    slug_to_brand: dict[str, Brand] = {}
    for b in BRANDS:
        existing = db.execute(select(Brand).where(Brand.slug == b["slug"])).scalar_one_or_none()
        if existing:
            slug_to_brand[b["slug"]] = existing
        else:
            row = Brand(**b)
            db.add(row)
            db.flush()
            slug_to_brand[b["slug"]] = row
    return slug_to_brand


def _load_images_by_brand() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for b in BRANDS:
        slug = b["slug"]
        pages = CATALOG_SEED_URLS.get(slug, [])
        urls = fetch_image_urls_for_brand(pages, max_images=50)
        if not urls and b.get("website"):
            og = fetch_og_image_url(b["website"])
            if og:
                urls = [og]
        out[slug] = urls
        print(f"  {slug}: {len(out[slug])} image URL(s) from site(s)")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-scrape",
        action="store_true",
        help="Only ensure brands exist; do not refresh garment images (not recommended).",
    )
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        slug_to_brand = _ensure_brands(db)
        db.commit()

        if args.no_scrape:
            print("Brands ready (--no-scrape: skipped garment image refresh).")
            return

        print("Scraping image URLs from brand sites (this may take a minute)…")
        by_slug_images = _load_images_by_brand()

        slots_by: dict[str, list[dict]] = defaultdict(list)
        for s in SLOTS:
            slots_by[s["brand_slug"]].append(s)

        n_insert = 0
        n_update = 0
        for slug, slot_list in slots_by.items():
            brand = slug_to_brand[slug]
            pool = by_slug_images.get(slug) or []
            if not pool:
                print(f"  WARNING: no images for {slug} — add URLs to CATALOG_SEED_URLS in app/seed.py")
                continue
            for i, slot in enumerate(slot_list):
                image_url = pool[i % len(pool)]
                ex = db.execute(
                    select(Garment).where(
                        Garment.brand_id == brand.id,
                        Garment.title == slot["title"],
                    )
                ).scalar_one_or_none()
                if ex:
                    if ex.image_url != image_url:
                        ex.image_url = image_url
                        ex.extracted_path = None
                        n_update += 1
                else:
                    db.add(
                        Garment(
                            brand_id=brand.id,
                            title=slot["title"],
                            gender=slot["gender"],
                            occasion=slot["occasion"],
                            image_url=image_url,
                            price=slot["price"],
                            color=slot["color"],
                        )
                    )
                    n_insert += 1
        db.commit()
        print(f"Done. Garments inserted: {n_insert}, image URLs updated: {n_update}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
