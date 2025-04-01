import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Path to ChromeDriver
CHROMEDRIVER_PATH = "chromedriver.exe"

# Setting up Selenium WebDriver
print("Setting up ChromeDriver path...")
options = webdriver.ChromeOptions()  # Create an instance of ChromeOptions for browser settings
options.add_argument("--start-maximized")  # Start the browser in full-screen mode
service = Service(CHROMEDRIVER_PATH)  # Set up the service with the path to ChromeDriver
driver = webdriver.Chrome(service=service, options=options)  # Launch ChromeDriver with options
print("Selenium setup complete.")

# Target URL for the website to scrape
url = "https://vintagepens.in/collections/parker"
print("Target URL:", url)

# Open the target website
driver.get(url)  # Navigate to the target URL
print("Opening website...")
time.sleep(3)  # Wait for the page to load completely
print("Website opened.")

# Scroll to the bottom of the page to load all products
print("Scrolling to the bottom of the page...")
while True:
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get the current page height
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
    print("Scrolling...")
    time.sleep(3)  # Wait for new content to load (if any)
    new_height = driver.execute_script("return document.body.scrollHeight")  # Check the new page height
    if new_height == last_height:  # If the height hasn't changed, all products are loaded
        print("Reached the bottom of the page.")
        break

# Extract the page source and parse it using BeautifulSoup
print("Extracting page source...")
soup = BeautifulSoup(driver.page_source, "html.parser")  # Parse the page source with BeautifulSoup
product_list = soup.select("li.grid__item")  # Find all product elements (list items with class `grid__item`)
print("Page source extracted.")

# Initialize an empty list to collect product data
print("Collecting product data...")
data = []

# Loop through each product in the list
for product in product_list:
    try:
        # Extract basic product information from the main page
        name = product.select_one("a.full-unstyled-link").text.strip()  # Product name
        url_suffix = product.select_one("a.full-unstyled-link")["href"]  # Relative URL to the product page
        url = f"https://vintagepens.in{url_suffix}"  # Build the full URL
        price = product.select_one("span.money").text.strip()  # Product price

        # Navigate to the product page to fetch detailed information
        driver.get(url)  # Go to the product's URL
        print(f"Fetching product details for {name}...")
        time.sleep(2)  # Wait for the page to load completely

        # Parse the product page using BeautifulSoup
        product_soup = BeautifulSoup(driver.page_source, "html.parser")
        description_div = product_soup.find("div", class_="product__description rte quick-add-hidden")  # Locate the description block

        # Initialize attributes for detailed product information
        brand = type_ = condition = model = nib_material = nib_size = body_material = color = trim = filling_mechanism = additional_description = None

        # Extract detailed product information if the description block exists
        if description_div:
            paragraphs = description_div.find_all("p")  # Find all <p> tags within the description block
            for paragraph in paragraphs:
                text = paragraph.get_text(strip=True)  # Get the text inside the <p> tag
                # Match each detail based on the label at the start of the paragraph
                if text.startswith("Brand:"):
                    brand = text.replace("Brand:", "").strip()
                elif text.startswith("Type:"):
                    type_ = text.replace("Type:", "").strip()
                elif text.startswith("Condition:"):
                    condition = text.replace("Condition:", "").strip()
                elif text.startswith("Model:"):
                    model = text.replace("Model:", "").strip()
                elif text.startswith("Nib Material:"):
                    nib_material = text.replace("Nib Material:", "").strip()
                elif text.startswith("Nib Size:"):
                    nib_size = text.replace("Nib Size:", "").strip()
                elif text.startswith("Body Material:"):
                    body_material = text.replace("Body Material:", "").strip()
                elif text.startswith("Color:"):
                    color = text.replace("Color:", "").strip()
                elif text.startswith("Trim:"):
                    trim = text.replace("Trim:", "").strip()
                elif text.startswith("Filling Mechanism:"):
                    filling_mechanism = text.replace("Filling Mechanism:", "").strip()
                else:
                    # For any additional details, append them to a general description field
                    additional_description = text if additional_description is None else f"{additional_description} {text}"

        # Append the extracted data as a dictionary to the list
        data.append({
            "Name": name,
            "Price": price,
            "URL": url,
            "Brand": brand,
            "Type": type_,
            "Condition": condition,
            "Model": model,
            "Nib Material": nib_material,
            "Nib Size": nib_size,
            "Body Material": body_material,
            "Color": color,
            "Trim": trim,
            "Filling Mechanism": filling_mechanism,
            "Additional Description": additional_description
        })
        print(f"Details for {name} fetched and stored.")

    except Exception as e:
        print(f"Error processing product: {e}")  # Print error if something goes wrong

# Convert the collected data into a Pandas DataFrame
print("Saving data to Pandas DataFrame...")
df = pd.DataFrame(data)  # Create a DataFrame from the list of dictionaries
print("Data saved to DataFrame.")

# Save the DataFrame as a CSV file
print("Saving data to CSV...")
df.to_csv("pens_data_detailed.csv", index=False)  # Save the data to a CSV file
print("Data saved to pens_data_detailed.csv")

# Close the browser
print("Closing browser...")
driver.quit()  # Quit the Selenium WebDriver
print("Browser closed.")
