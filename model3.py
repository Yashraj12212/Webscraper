'''
It feels like the model2 does everything but as we need more data for a specific product, so we will have
to go to the product page and scrape more details.

Working:
1. The model first scrapes the product listing page as done in model2.py
2. It collects all unique product URLs.
3. It then visits each product URL to scrape additional details like description, material, images, sizes, and category.
4. Finally, it exports all the collected data to a CSV file.
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
p=input("") #this was added to avoid the code running on import, can be removed if not needed

product_name = input("Enter Product: ")
product_number = int(input("Enter number of products to scrape (-1 for all): "))

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.nnnow.com/")
time.sleep(5)

# Close popup
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "crossIcon"))
    ).click()
except:
    pass

# Search for the product
wait = WebDriverWait(driver, 10)
search_input = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input.nwc-inp.nw-searchbar-input"))
)
search_input.clear()
search_input.send_keys(product_name)
search_input.send_keys(Keys.RETURN)
time.sleep(5)

data = []
seen_urls = set()  # Track unique product URLs
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_pause = 2

while True:
    # Wait for products to load
    products = driver.find_elements(By.CSS_SELECTOR, "div.nw-productlist-eachproduct")
    print(f"Loaded {len(products)} products...")

    # Extract data from visible products
    for product in products:
        try:
            url = product.find_element(By.CSS_SELECTOR, "a.nw-productview").get_attribute("href")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Stop if reached requested number of products
            if product_number != -1 and len(seen_urls) >= product_number:
                break


        except Exception as e:
            print("Skipped one product:", e)
            continue

    # Stop if reached limit
    if product_number != -1 and len(seen_urls) >= product_number:
        break

    # Scroll down
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break  # End of page
    last_height = new_height

#this funtion will go to each product page and scrape more details
import hashlib

def product_scrape(url):
    driver.execute_script(f"window.open('{url}','_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    try:
        title = driver.find_element(By.CSS_SELECTOR, "span.nw-product-title").text.strip()
        brand = driver.find_element(By.CSS_SELECTOR, "span.nw-product-brandtxt").text.strip()

        # try:
        #     description = driver.find_element(By.CSS_SELECTOR, "div.nw-productview-desc").text.strip()
        # except:
        #     description = ""

        materials = driver.find_elements(By.CSS_SELECTOR, "ul.nw-pdp-desktopaccordiondetailsul li")
        if materials:
            material_text = materials[0].text.strip()  # Take only the first <li>
        else:
            material_text = ""

        # Find the Specs section
        specs_list = driver.find_elements(By.CSS_SELECTOR, "div.nw-pdp-desktopaccordiondetailssection h3.nw-pdp-desktopaccordiondetailstitle + ul li")
        # Join all <li> items as a description
        if specs_list:
            description = ", ".join([li.text.strip() for li in specs_list])
        else:
            description = ""


        img = driver.find_element(By.CSS_SELECTOR, "div.nw-maincarousel img").get_attribute("src")
        additional_imgs = driver.find_elements(By.CSS_SELECTOR, "div.nw-thumbnail-image img")
        additional_image_links = [i.get_attribute("src") for i in additional_imgs]

        mrp = driver.find_element(By.CSS_SELECTOR, "del.nw-priceblock-mrp").text.strip()
        selling_price = driver.find_element(By.CSS_SELECTOR, "span.nw-priceblock-sellingprice").text.strip()

        # Find all size buttons
        size_buttons = driver.find_elements(By.CSS_SELECTOR, "div.nw-sizeblock-list button.nw-size-chip")

        # Extract available sizes (not disabled)
        available_sizes = []
        for btn in size_buttons:
            if btn.get_attribute("disabled") is None:  # clickable / available
                available_sizes.append(btn.text.strip())

        # Make a sentence
        if available_sizes:
            availability = "Available sizes: " + ", ".join(available_sizes)
        else:
            availability = "Out of stock"

        product_category = f"{brand} > {title}"

        data.append({
            "id": hashlib.md5(url.encode()).hexdigest(),
            "title": title,
            "description": description,
            "link": url,
            "product_category": product_category,
            "brand": brand,
            "material": material_text,
            "weight": "",
            "age_group": "Adult" if "Men" in title or "Women" in title else "Kids",
            "image_link": img,
            "additional_image_link": additional_image_links,
            "price": mrp,
            "sale_price": selling_price,
            "pricing_trend": "",
            "availability": availability if available_sizes else "out of stock",
            "inventory_quantity": "",
            "variant_options": []
        })

    except Exception as e:
        print(f"Failed scraping {url}: {e}")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


product_urls = list(seen_urls)

for url in product_urls:
    product_scrape(url)


# Export to CSV
df = pd.DataFrame(data)
df.to_csv(f"Productlist_{product_name}.csv", index=False, encoding="utf-8")
print(f"\n✅ Saved {len(data)} products to Productlist_{product_name}.csv")

driver.quit()


