import pandas as pd

# Load the CSV
df = pd.read_csv("Productlist_jeans.csv")

# Check for duplicate URLs
duplicates = df[df.duplicated(subset=["URL"], keep=False)]

if not duplicates.empty:
    print(f"Found {len(duplicates)} duplicate entries based on URL:")
    print(duplicates[["Brand","Name","URL"]])
else:
    print("No duplicate URLs found.")