import pandas as pd
#import numpy as np
#import math
#from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns   
# Load dataset
df = pd.read_excel(r"C:\Users\VICTUS\Downloads\customer_shopping_behavior.xlsx")

# Basic Info
print(df.head())
print(df.tail())
print(len(df))
print(df.shape)

print(df.describe())
print(df.describe(include="all"))
df.info()

print(df.isnull().sum())

# ---------------- DATA CLEANING ---------------- #

# Mapping categories
correct_mapping = {
    "Sunglasses": "Accessories", "Gloves": "Accessories", "Jewelry": "Accessories",
    "Hat": "Accessories", "Handbag": "Accessories", "Backpack": "Accessories",
    "Belt": "Accessories", "Scarf": "Accessories", "Bag": "Accessories",

    "T-shirt": "Clothing", "Shirt": "Clothing", "Shorts": "Clothing",
    "Hoodie": "Clothing", "Pants": "Clothing", "Socks": "Clothing",
    "Jeans": "Clothing", "Blouse": "Clothing", "Skirt": "Clothing",
    "Sweater": "Clothing", "Dress": "Clothing",

    "Laptop": "Electronics", "Phone": "Electronics",
    "Headphones": "Electronics", "Watch": "Electronics",

    "Shoes": "Footwear", "Sandals": "Footwear",
    "Sneakers": "Footwear", "Boots": "Footwear",

    "Coat": "Outerwear", "Jacket": "Outerwear"
}

df["Category"] = df["Item Purchased"].map(correct_mapping)

# Handle Size column
df.loc[df['Category'] == 'Electronics', 'Size'] = "Not applicable"
df.loc[df['Category'] == 'Accessories', 'Size'] = "Free Size"
df.loc[df['Category'] == 'Footwear', 'Size'] = "Not Available"

df.loc[
    (df['Category'] == 'Clothing') & (df['Size'].isnull()),
    'Size'
] = df[df['Category'] == 'Clothing']['Size'].mode()[0]

# Fill missing values
df['Review Rating'] = df['Review Rating'].fillna(
    df.groupby('Item Purchased')['Review Rating'].transform("mean")
)

df['Previous Purchases'] = df['Previous Purchases'].fillna(0)

df['Purchase Amount (USD)'] = df['Purchase Amount (USD)'].fillna(
    df.groupby("Item Purchased")['Purchase Amount (USD)'].transform("mean")
)

# Remove duplicates
df = df.drop_duplicates(subset=['Customer ID'], keep='first')

# Rename columns
df.columns = df.columns.str.replace(" ", "_").str.lower()
df = df.rename(columns={"purchase_amount_(usd)": "purchase_amount"})

# ---------------- BUSINESS INSIGHTS ---------------- #

# 1. Revenue by category
revenue_by_category = (
    df.groupby("category")["purchase_amount"]
    .sum()
    .round(2)
    .sort_values(ascending=False)
    .reset_index(name="highest_revenue")
)
print(revenue_by_category)

# 2. Discount impact
revenue_with_discount = df.groupby("discount_applied").agg(
    total_revenue=("purchase_amount", "sum"),
    avg_revenue=("purchase_amount", "mean")
).round(2)
print(revenue_with_discount)

# 3. Revenue by gender
revenue_by_gender = (
    df.groupby("gender")["purchase_amount"]
    .sum()
    .round(2)
    .sort_values(ascending=False)
    .reset_index(name="highest_revenue")
)
print(revenue_by_gender)

# 4. High-value discount customers
avg_value = df["purchase_amount"].mean()

result = (
    df[(df["discount_applied"] == "Yes") &
       (df["purchase_amount"] > avg_value)]
    .sort_values(by="purchase_amount", ascending=False)
    [["customer_id", "purchase_amount", "discount_applied"]]
    .head(10)
)
print(result)

# 5. Top & low rated products
top_rated = (
    df.groupby("item_purchased")["review_rating"]
    .mean().round(2)
    .sort_values(ascending=False)
    .head(5)
    .reset_index(name="avg_ratings")
)

low_rated = (
    df.groupby("item_purchased")["review_rating"]
    .mean().round(2)
    .sort_values()
    .head(5)
    .reset_index(name="avg_ratings")
)

print(top_rated)
print(low_rated)

# 6. Shipping analysis
avg_purchase_by_shipping_type = (
    df.groupby("shipping_type").agg(
        order_placed=("customer_id", "nunique"),
        avg_purchase=("purchase_amount", "mean"),
        revenue=("purchase_amount", "sum")
    ).round(2).reset_index()
)
print(avg_purchase_by_shipping_type)

# ---------------- VISUALIZATION ---------------- #

plt.style.use('seaborn-v0_8')

# Revenue by category
plt.figure(figsize=(8,5))
plt.bar(revenue_by_category["category"], revenue_by_category["highest_revenue"])
plt.xticks(rotation=45)
plt.title("Revenue by Category")
plt.show()

# Discount analysis
revenue_with_discount.plot(kind="bar", title="Discount Analysis")
plt.show()

# Gender pie chart
plt.pie(
    revenue_by_gender["highest_revenue"],
    labels=revenue_by_gender["gender"],
    autopct="%1.1f%%"
)
plt.title("Revenue by Gender")
plt.show()

# Top rated
plt.figure()
plt.bar(top_rated["item_purchased"], top_rated["avg_ratings"])
plt.xticks(rotation=45)
plt.title("Top Rated Products")
plt.show()

# Correlation heatmap
corr = df.corr(numeric_only=True)

plt.figure(figsize=(8,5))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Heatmap")
plt.show()

# Scatter plot
plt.figure()
plt.scatter(df['purchase_amount'], df['review_rating'], alpha=0.6)
plt.xlabel("Purchase Amount")
plt.ylabel("Review Rating")
plt.title("Purchase vs Review Rating")
plt.show()