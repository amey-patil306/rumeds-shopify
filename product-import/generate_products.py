"""Generate Shopify product import CSV for Rumeds scrubs catalog."""
import csv
from pathlib import Path

OUTPUT = Path(__file__).parent / "rumeds-products.csv"

HEADERS = [
    "Title",
    "URL handle",
    "Description",
    "Vendor",
    "Product category",
    "Type",
    "Tags",
    "Published on online store",
    "Status",
    "SKU",
    "Barcode",
    "Option1 name",
    "Option1 value",
    "Option1 LinkedTo",
    "Option2 name",
    "Option2 value",
    "Option2 LinkedTo",
    "Price",
    "Price / International",
    "Compare-at price",
    "Compare-at price / International",
    "Cost per item",
    "Charge tax",
    "Inventory tracker",
    "Inventory quantity",
    "Continue selling when out of stock",
    "Weight value (grams)",
    "Weight unit for display",
    "Requires shipping",
    "Fulfillment service",
    "Product image URL",
    "Image position",
    "Image alt text",
    "Variant image URL",
    "Gift card",
    "SEO title",
    "SEO description",
    "Google Shopping / Google Product Category",
]

COLORS = ["Navy", "Ceil Blue", "Black", "Graphite Grey", "Wine"]
MENS_SIZES = ["S", "M", "L", "XL", "XXL"]
WOMENS_SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
UNISEX_SIZES = ["S", "M", "L", "XL", "XXL"]

SCRUB_BODY = """<p>Premium medical scrub engineered for long hospital shifts. Rumeds Pro Flex fabric delivers 4-way stretch, antimicrobial protection, and moisture-wicking comfort.</p>
<ul>
<li>4-way stretch for full range of motion</li>
<li>Antimicrobial and odor-resistant finish</li>
<li>Moisture-wicking, breathable weave</li>
<li>Ergonomic pocket placement for rounds</li>
<li>Machine washable and fade-resistant</li>
</ul>"""

SET_BODY = """<p>Complete scrub set (top + pants) for doctors, residents, and nurses. Save with the Rumeds Essential bundle in our signature Pro Flex fabric.</p>
<ul>
<li>Includes matching scrub top and pants</li>
<li>4-way stretch with antimicrobial finish</li>
<li>Moisture-wicking for 12–24 hour shifts</li>
<li>Coordinated color and professional fit</li>
</ul>"""


def color_code(color: str) -> str:
    return {
        "Navy": "NVY",
        "Ceil Blue": "CBL",
        "Black": "BLK",
        "Graphite Grey": "GRY",
        "Wine": "WIN",
    }[color]


def variant_rows(
    handle: str,
    title: str,
    description: str,
    product_type: str,
    tags: str,
    sizes: list[str],
    price: str,
    compare: str,
    cost: str,
    weight_g: str,
    sku_prefix: str,
    seo_title: str,
    seo_desc: str,
    google_category: str,
):
    rows = []
    first = True
    for color in COLORS:
        for size in sizes:
            sku = f"{sku_prefix}-{color_code(color)}-{size}"
            row = {h: "" for h in HEADERS}
            row["URL handle"] = handle
            if first:
                row["Title"] = title
                row["Description"] = description
                row["Vendor"] = "Rumeds"
                row["Product category"] = "Apparel & Accessories > Clothing > Uniforms > Scrubs"
                row["Type"] = product_type
                row["Tags"] = tags
                row["Published on online store"] = "true"
                row["Status"] = "active"
                row["SEO title"] = seo_title
                row["SEO description"] = seo_desc
                row["Google Shopping / Google Product Category"] = google_category
                first = False
            row["SKU"] = sku
            row["Option1 name"] = "Color"
            row["Option1 value"] = color
            row["Option2 name"] = "Size"
            row["Option2 value"] = size
            row["Price"] = price
            row["Compare-at price"] = compare
            row["Cost per item"] = cost
            row["Charge tax"] = "true"
            row["Inventory tracker"] = "shopify"
            row["Inventory quantity"] = "50"
            row["Continue selling when out of stock"] = "deny"
            row["Weight value (grams)"] = weight_g
            row["Weight unit for display"] = "g"
            row["Requires shipping"] = "true"
            row["Fulfillment service"] = "manual"
            row["Gift card"] = "false"
            rows.append(row)
    return rows


def cap_rows():
    rows = []
    first = True
    for color in COLORS:
        row = {h: "" for h in HEADERS}
        row["URL handle"] = "rumeds-surgical-scrub-cap"
        if first:
            row["Title"] = "Rumeds Surgical Scrub Cap"
            row["Description"] = (
                "<p>Lightweight surgical scrub cap with moisture-wicking fabric. "
                "Keeps hair secure and comfortable through long procedures.</p>"
            )
            row["Vendor"] = "Rumeds"
            row["Product category"] = "Apparel & Accessories > Clothing > Uniforms > Scrubs"
            row["Type"] = "Scrub Cap"
            row["Tags"] = "scrubs, accessories, or-essentials, unisex"
            row["Published on online store"] = "true"
            row["Status"] = "active"
            row["SEO title"] = "Rumeds Surgical Scrub Cap | OR Essentials"
            row["SEO description"] = "Moisture-wicking surgical scrub cap for doctors and surgeons."
            first = False
        row["SKU"] = f"RM-CAP-{color_code(color)}-OS"
        row["Option1 name"] = "Color"
        row["Option1 value"] = color
        row["Option2 name"] = "Size"
        row["Option2 value"] = "One Size"
        row["Price"] = "399.00"
        row["Compare-at price"] = "499.00"
        row["Cost per item"] = "180.00"
        row["Charge tax"] = "true"
        row["Inventory tracker"] = "shopify"
        row["Inventory quantity"] = "100"
        row["Continue selling when out of stock"] = "deny"
        row["Weight value (grams)"] = "40"
        row["Weight unit for display"] = "g"
        row["Requires shipping"] = "true"
        row["Fulfillment service"] = "manual"
        row["Gift card"] = "false"
        rows.append(row)
    return rows


PRODUCTS = [
    {
        "handle": "rumeds-pro-flex-mens-scrub-top",
        "title": "Rumeds Pro Flex Men's Scrub Top",
        "description": SCRUB_BODY,
        "product_type": "Scrub Top",
        "tags": "men, scrubs, tops, pro-flex, medical-apparel",
        "sizes": MENS_SIZES,
        "price": "1899.00",
        "compare": "2299.00",
        "cost": "850.00",
        "weight_g": "280",
        "sku_prefix": "RM-MTOP",
        "seo_title": "Rumeds Pro Flex Men's Scrub Top | 4-Way Stretch Scrubs",
        "seo_desc": "Premium men's scrub top with 4-way stretch, antimicrobial finish, and moisture-wicking fabric for long hospital shifts.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-pro-flex-mens-scrub-pants",
        "title": "Rumeds Pro Flex Men's Scrub Pants",
        "description": SCRUB_BODY.replace("top", "pants").replace("Top", "Pants"),
        "product_type": "Scrub Pants",
        "tags": "men, scrubs, pants, pro-flex, medical-apparel",
        "sizes": MENS_SIZES,
        "price": "1899.00",
        "compare": "2299.00",
        "cost": "900.00",
        "weight_g": "380",
        "sku_prefix": "RM-MPNT",
        "seo_title": "Rumeds Pro Flex Men's Scrub Pants | Stretch Medical Pants",
        "seo_desc": "Comfortable men's scrub pants with yoga-inspired waistband, 4-way stretch, and antimicrobial fabric.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-pro-flex-womens-scrub-top",
        "title": "Rumeds Pro Flex Women's Scrub Top",
        "description": (
            "<p>Tailored women's scrub top with a flattering fit and Rumeds Pro Flex performance fabric. "
            "Designed for female doctors and residents who need style and function on long shifts.</p>"
            "<ul><li>Fitted silhouette with side slits for mobility</li>"
            "<li>4-way stretch and antimicrobial finish</li>"
            "<li>Moisture-wicking, breathable fabric</li>"
            "<li>Multiple utility pockets</li></ul>"
        ),
        "product_type": "Scrub Top",
        "tags": "women, scrubs, tops, pro-flex, medical-apparel",
        "sizes": WOMENS_SIZES,
        "price": "1899.00",
        "compare": "2299.00",
        "cost": "850.00",
        "weight_g": "260",
        "sku_prefix": "RM-WTOP",
        "seo_title": "Rumeds Pro Flex Women's Scrub Top | Fitted Medical Scrubs",
        "seo_desc": "Fitted women's scrub top with 4-way stretch and antimicrobial fabric. Built for long hospital shifts.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-pro-flex-womens-scrub-pants",
        "title": "Rumeds Pro Flex Women's Scrub Pants",
        "description": (
            "<p>Women's scrub pants with a mid-rise yoga waistband and tapered leg. "
            "Pro Flex fabric moves with you through rounds, codes, and 24-hour calls.</p>"
            "<ul><li>Yoga-style waistband for all-day comfort</li>"
            "<li>4-way stretch with antimicrobial finish</li>"
            "<li>Moisture-wicking and breathable</li>"
            "<li>Cargo and hip pockets</li></ul>"
        ),
        "product_type": "Scrub Pants",
        "tags": "women, scrubs, pants, pro-flex, medical-apparel",
        "sizes": WOMENS_SIZES,
        "price": "1899.00",
        "compare": "2299.00",
        "cost": "900.00",
        "weight_g": "360",
        "sku_prefix": "RM-WPNT",
        "seo_title": "Rumeds Pro Flex Women's Scrub Pants | Yoga Waist Scrubs",
        "seo_desc": "Women's scrub pants with yoga waistband, 4-way stretch, and antimicrobial moisture-wicking fabric.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-essential-mens-scrub-set",
        "title": "Rumeds Essential Men's Scrub Set",
        "description": SET_BODY,
        "product_type": "Scrub Set",
        "tags": "men, scrubs, sets, bundle, pro-flex, best-value",
        "sizes": MENS_SIZES,
        "price": "3499.00",
        "compare": "4199.00",
        "cost": "1600.00",
        "weight_g": "650",
        "sku_prefix": "RM-MSET",
        "seo_title": "Rumeds Essential Men's Scrub Set | Top + Pants Bundle",
        "seo_desc": "Save on a complete men's scrub set. Pro Flex top and pants with 4-way stretch and antimicrobial finish.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-essential-womens-scrub-set",
        "title": "Rumeds Essential Women's Scrub Set",
        "description": SET_BODY,
        "product_type": "Scrub Set",
        "tags": "women, scrubs, sets, bundle, pro-flex, best-value",
        "sizes": WOMENS_SIZES,
        "price": "3499.00",
        "compare": "4199.00",
        "cost": "1600.00",
        "weight_g": "620",
        "sku_prefix": "RM-WSET",
        "seo_title": "Rumeds Essential Women's Scrub Set | Top + Pants Bundle",
        "seo_desc": "Complete women's scrub set with fitted top and yoga-waist pants in Pro Flex antimicrobial fabric.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-performance-underscrub-tee",
        "title": "Rumeds Performance Underscrub Tee",
        "description": (
            "<p>Base-layer underscrub tee worn beneath your Rumeds scrubs. "
            "Ultra-soft, breathable, and moisture-wicking for layered comfort in the OR and on the ward.</p>"
            "<ul><li>Lightweight stretch jersey</li>"
            "<li>Moisture-wicking and quick-dry</li>"
            "<li>Tagless for irritation-free wear</li></ul>"
        ),
        "product_type": "Underscrub",
        "tags": "underscrub, base-layer, unisex, accessories",
        "sizes": UNISEX_SIZES,
        "price": "899.00",
        "compare": "1099.00",
        "cost": "400.00",
        "weight_g": "150",
        "sku_prefix": "RM-UND",
        "seo_title": "Rumeds Performance Underscrub Tee | Base Layer for Scrubs",
        "seo_desc": "Moisture-wicking underscrub tee for doctors and nurses. Soft base layer under medical scrubs.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-or-warm-up-jacket",
        "title": "Rumeds OR Warm-Up Jacket",
        "description": (
            "<p>Lightweight warm-up jacket for cold ORs and night shifts. "
            "Snap-front closure layers easily over scrubs without bulk.</p>"
            "<ul><li>Soft fleece-lined interior</li>"
            "<li>4-way stretch outer shell</li>"
            "<li>Multiple pockets for essentials</li>"
            "<li>Antimicrobial-treated fabric</li></ul>"
        ),
        "product_type": "Warm-Up Jacket",
        "tags": "jacket, or-essentials, unisex, outerwear, pro-flex",
        "sizes": UNISEX_SIZES,
        "price": "2499.00",
        "compare": "2999.00",
        "cost": "1100.00",
        "weight_g": "450",
        "sku_prefix": "RM-JKT",
        "seo_title": "Rumeds OR Warm-Up Jacket | Medical Scrub Jacket",
        "seo_desc": "Warm-up jacket for operating rooms and hospital shifts. Layers over scrubs with stretch and antimicrobial fabric.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Scrubs",
    },
    {
        "handle": "rumeds-classic-lab-coat",
        "title": "Rumeds Classic Lab Coat",
        "description": (
            "<p>Professional lab coat for rounds, clinics, and teaching. "
            "Crisp tailored look with stain-resistant, easy-care fabric.</p>"
            "<ul><li>Mid-length professional cut</li>"
            "<li>Stain-resistant finish</li>"
            "<li>Three-button closure with chest pocket</li>"
            "<li>Side access slits for scrub pockets</li></ul>"
        ),
        "product_type": "Lab Coat",
        "tags": "lab-coat, unisex, professional, clinic",
        "sizes": UNISEX_SIZES,
        "price": "2199.00",
        "compare": "2699.00",
        "cost": "950.00",
        "weight_g": "520",
        "sku_prefix": "RM-LAB",
        "seo_title": "Rumeds Classic Lab Coat | Professional Medical Coat",
        "seo_desc": "Tailored lab coat for doctors and medical students. Stain-resistant professional coat for clinic and rounds.",
        "google_category": "Apparel & Accessories > Clothing > Uniforms > Lab Coats",
    },
]


def main():
    all_rows = []
    for p in PRODUCTS:
        all_rows.extend(variant_rows(**p))
    all_rows.extend(cap_rows())

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    product_count = len(PRODUCTS) + 1  # + scrub cap
    print(f"Wrote {len(all_rows)} variant rows ({product_count} products) to {OUTPUT}")


if __name__ == "__main__":
    main()
