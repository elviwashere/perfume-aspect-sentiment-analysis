import os
import pandas as pd

from scraper import scrape_product
from products import products

os.makedirs("output", exist_ok=True)

all_reviews = []

for product in products:

    print("=" * 60)
    print(f"Scraping {product['brand']} - {product['product']}")
    print("=" * 60)

    df = scrape_product(
    product["brand"],
    product["product"],
    product["url"]
    )

    all_reviews.append(df)

result = pd.concat(all_reviews, ignore_index=True)

result.to_csv(
    "output/review_tokopedia.csv",
    index=False,
    encoding="utf-8-sig"
)

print(result)

print("SELESAI")