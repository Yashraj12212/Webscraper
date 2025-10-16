# Shopping Website Product Scraper

A Selenium-based web scraper to extract product details from [NNNOW](https://www.nnnow.com/) website.  
This project was developed iteratively, gradually adding features for more detailed product scraping.

---

## Project Overview

The scraper allows you to:

- Search for a product on NNNOW.
- Scrape product listings.
- Visit each product page for detailed information.
- Collect prices, sale prices, images, material, description, available sizes, product category, and more.
- Export data to CSV.

This project started simple and progressively gained more features as follows:

---

### Step-by-Step Feature Development

1. **Initial Product Listing Scraper**
   - Started with scraping product names and URLs from search results.
   - Used Selenium to scroll through the page and load products dynamically.
   - Avoided duplicates using a `seen_urls` set.
   - Allowed scraping a specific number of products or all products.

2. **Product Page Scraping**
   - Added a `product_scrape(url)` function.
   - Opened each product URL in a new tab and scraped:
     - Brand
     - Product title
     - Price
     - Main image
     - Tags

3. **Extended Product Details**
   - Added scraping for:
     - `material` → From `<ul class="nw-pdp-desktopaccordiondetailsul li">`.
     - `description` → From `<div class="nw-pdp-desktopaccordiondetailssection"><ul><li>` (product specs).
     - `additional_image_link` → Carousel images on product page.
     - `sale_price` → Extracted separately from HTML if discounted.

4. **Stock & Size Availability**
   - Extracted size options and stock availability directly from HTML without clicking buttons.
   - Created a readable sentence listing only in-stock sizes.
   ```python
   sizes = driver.find_elements(By.CSS_SELECTOR, "button.nwc-btn.nw-size-chip")
   available_sizes = [s.text.strip() for s in sizes if "OutOfStock" not in s.get_attribute("outerHTML")]
   availability = f"Available sizes: {', '.join(available_sizes)}"


5. **Product Category**

Combined brand and product title to generate a product_category.
```bash
brand = driver.find_element(By.CSS_SELECTOR, "span.nw-product-brandtxt").text.strip()
title = driver.find_element(By.CSS_SELECTOR, "span.nw-product-title").text.strip()
product_category = f"{brand} > {title}"
```

6. **CSV Export**

Exported all collected data into a CSV file using pandas.
```bash
df = pd.DataFrame(data)
df.to_csv(f"Productlist_{product_name}.csv", index=False, encoding="utf-8")
```

## Installation

### Clone the repository:

git clone <repo_url>


### Install dependencies:

pip install selenium pandas webdriver-manager


### Make sure you have Google Chrome installed.

## Usage

```bash

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# User input
product_name = input("Enter Product: ")
product_number = int(input("Enter number of products to scrape (-1 for all): "))

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.nnnow.com/")
time.sleep(5)

# Close popup if it exists
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "crossIcon"))
    ).click()
except:
    pass

# Search product
search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input.nwc-inp.nw-searchbar-input"))
)
search_input.clear()
search_input.send_keys(product_name)
search_input.send_keys(Keys.RETURN)
time.sleep(5)

data = []
seen_urls = set()
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_pause = 2

# Collect product URLs
while True:
    products = driver.find_elements(By.CSS_SELECTOR, "div.nw-productlist-eachproduct")
    for product in products:
        try:
            url = product.find_element(By.CSS_SELECTOR, "a.nw-productview").get_attribute("href")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            if product_number != -1 and len(seen_urls) >= product_number:
                break
        except:
            continue

    if product_number != -1 and len(seen_urls) >= product_number:
        break

    driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Function to scrape each product page
def product_scrape(url):
    driver.execute_script(f"window.open('{url}','_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    try:
        brand = driver.find_element(By.CSS_SELECTOR, "span.nw-product-brandtxt").text.strip()
        title = driver.find_element(By.CSS_SELECTOR, "span.nw-product-title").text.strip()
        price = driver.find_element(By.CSS_SELECTOR, "span.nw-priceblock-sellingprice").text.strip()
        materials = driver.find_elements(By.CSS_SELECTOR, "ul.nw-pdp-desktopaccordiondetailsul li")
        material = ", ".join([m.text.strip() for m in materials if "%" in m.text])
        specs = driver.find_elements(By.CSS_SELECTOR, "div.nw-pdp-desktopaccordiondetailssection ul li")
        description = ", ".join([s.text.strip() for s in specs])
        sizes = driver.find_elements(By.CSS_SELECTOR, "button.nwc-btn.nw-size-chip")
        available_sizes = [s.text.strip() for s in sizes if "OutOfStock" not in s.get_attribute("outerHTML")]
        availability = f"Available sizes: {', '.join(available_sizes)}"
        product_category = f"{brand} > {title}"

        img = driver.find_element(By.CSS_SELECTOR, "img.nwc-lazyimg").get_attribute("src")
        additional_images = [i.get_attribute("src") for i in driver.find_elements(By.CSS_SELECTOR, "div.nwc-carousel img")]

        data.append({
            "id": url,  # Can hash if needed
            "title": title,
            "description": description,
            "link": url,
            "product_category": product_category,
            "brand": brand,
            "material": material,
            "availability": availability,
            "image_link": img,
            "additional_image_link": additional_images,
            "price": price,
            # "sale_price": "",  # Can extract if discounted
        })

    except Exception as e:
        print(f"Failed scraping {url}: {e}")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

# Scrape each product URL
for url in list(seen_urls):
    product_scrape(url)

# Export to CSV
df = pd.DataFrame(data)
df.to_csv(f"Productlist_{product_name}.csv", index=False, encoding="utf-8")
driver.quit()

``` 

## Notes
    Stock availability is read directly from HTML; no clicking needed.
    Weight, age_group, and some fields may be missing in HTML and can be inferred.
    Incrementally added features: URLs → Product Page Details → Material → Description → Images → Sizes → Category → CSV.

## Known Issues / Possible Errors During Scraping

    Missing Data Fields: Some products may lack descriptions, weight, or material fields, resulting in empty strings.
    Out-of-Stock Sizes: Sizes marked disabled in HTML are considered out-of-stock and won’t be counted as available.
    Dynamic Content Loading: Some images or elements might load slowly; adding time.sleep() or WebDriverWait is recommended.
    Duplicate URLs: Already handled by seen_urls set, but dynamic page updates may occasionally add duplicates.
    Network Issues: Temporary connection issues or slow responses may break the scraper.
    Website Structure Changes: If NNNOW updates their HTML/CSS, selectors in the scraper may fail, causing exceptions.

## Error Handling Recommendations
    Use try-except blocks for each element extraction to continue scraping even if some fields fail.
    Wrap network-dependent operations with retries and timeouts to handle intermittent connection issues.
    Log errors with the product URL to revisit failed items later.
    Periodically update CSS selectors to match website changes.
