import os
import pandas as pd

from playwright.sync_api import sync_playwright

from scraper import scrape_product
from products import products

os.makedirs("output", exist_ok=True)

all_reviews = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for product in products:

        print("=" * 60)
        print(f"Scraping {product['brand']} - {product['product']}")
        print("=" * 60)

        df = scrape_product(
            page,
            product["brand"],
            product["product"],
            product["url"]
        )

        all_reviews.append(df)

    browser.close()

result = pd.concat(
    all_reviews,
    ignore_index=True
)

result.to_csv(
    "output/review_tokopedia.csv",
    index=False,
    encoding="utf-8-sig"
)

print(result)

print("SELESAI")