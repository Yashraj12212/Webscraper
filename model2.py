'''
This model is a better version of model1.py
This model scrolls the page to load more products till it reaches the limit(limit can we given by user or can be the max limit) 
and then scrapes the details like Brand,Name,MRP,Price,Discount,Tag,Image,URL from nnnnow website.
The model also checks for duplicate URLs and avoids adding them to the final list.

Working:
1. Opens the nnnnow website and closes any popups.
2. Searches for the product given by the user.
3. Scrolls the page to load more products until the end of the page or until the user-defined limit is reached.
4. Scrapes the required details from each product and stores them in a dictionary.
5. Exports the data to a CSV file named "Productlist_<product_name>.csv".

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
                continue  # Skip duplicates
            seen_urls.add(url)

            brand = product.find_element(By.CSS_SELECTOR, "h3.nw-productview-brandtxt").text.strip()
            name = product.find_element(By.CSS_SELECTOR, "div.nw-productview-producttitle").text.strip()

            tag = ""
            try:
                tag = product.find_element(By.CSS_SELECTOR, "span.nw-producttags-text").text.strip()
            except:
                pass

            mrp = ""
            try:
                mrp = product.find_element(By.CSS_SELECTOR, "del.nw-priceblock-mrp").text.strip()
            except:
                pass

            price = ""
            try:
                price = product.find_element(By.CSS_SELECTOR, "span.nw-priceblock-sellingprice").text.strip()
            except:
                pass

            discount = ""
            try:
                discount = product.find_element(By.CSS_SELECTOR, "span.nw-priceblock-discount").text.strip()
            except:
                pass

            img = ""
            try:
                img = product.find_element(By.CSS_SELECTOR, "img.nwc-lazyimg").get_attribute("src")
            except:
                pass

            data.append({
                "Brand": brand,
                "Name": name,
                "MRP": mrp,
                "Price": price,
                "Discount": discount,
                "Tag": tag,
                "Image": img,
                "URL": url
            })

            # Stop if reached the requested number
            if product_number != -1 and len(data) >= product_number:
                break

        except Exception as e:
            print("Skipped one product:", e)
            continue

    # Stop if reached limit
    if product_number != -1 and len(data) >= product_number:
        break

    # Scroll down
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
    time.sleep(scroll_pause)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break  # End of page
    last_height = new_height

# Export to CSV
df = pd.DataFrame(data)
df.to_csv(f"Productlist_{product_name}.csv", index=False, encoding="utf-8")
print(f"\n✅ Saved {len(data)} products to Productlist_{product_name}.csv")

driver.quit()
