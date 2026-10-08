import streamlit as st
import pandas as pd

st.title("Cart2Insights")
st.write("E-Commerce Analytics Dashboard")

customers = pd.read_csv("cleaned/olist_customers_dataset_cleaned.csv")
orders = pd.read_csv("cleaned/olist_orders_dataset_cleaned.csv")
order_items = pd.read_csv("cleaned/olist_order_items_dataset_cleaned.csv")
payments = pd.read_csv("cleaned/olist_order_payments_dataset_cleaned.csv")
reviews = pd.read_csv("cleaned/olist_order_reviews_dataset_cleaned.csv")
products = pd.read_csv("cleaned/olist_products_dataset_cleaned.csv")
sellers = pd.read_csv("cleaned/olist_sellers_dataset_cleaned.csv")
category_translation = pd.read_csv(
    "cleaned/product_category_name_translation_cleaned.csv"
)

st.success("All datasets loaded successfully!")

# Step 3: Dataset information

st.header("Dataset Information")

st.write("Customers:", customers.shape[0])
st.write("Orders:", orders.shape[0])
st.write("Order Items:", order_items.shape[0])
st.write("Payments:", payments.shape[0])
st.write("Reviews:", reviews.shape[0])
st.write("Products:", products.shape[0])
st.write("Sellers:", sellers.shape[0])
st.write("Category Translation:", category_translation.shape[0])

st.header("Business Overview")

# Total Revenue
total_revenue = order_items["price"].sum()

# Total Orders
total_orders = orders["order_id"].nunique()

# Total Customers
total_customers = customers["customer_id"].nunique()

st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
st.metric("Total Orders", total_orders)
st.metric("Total Customers", total_customers)

# More Business Overview metrics

# Total Sellers
total_sellers = sellers["seller_id"].nunique()

# Average Order Value
average_order_value = total_revenue / total_orders

# Average Review Score
average_review_score = reviews["review_score"].mean()

st.metric("Total Sellers", total_sellers)
st.metric("Average Order Value", f"₹{average_order_value:,.2f}")
st.metric("Average Review Score", f"{average_review_score:.2f}")

#Sales Analysis

st.header("Sales Analysis")

# Prepare order value
order_value = order_items.copy()

order_value["total_value"] = (
    order_value["price"] + order_value["freight_value"]
)

# Monthly Revenue
orders["order_purchase_Date"] = pd.to_datetime(
    orders["order_purchase_Date"]
)

monthly_revenue = orders.merge(
    order_value.groupby("order_id")["total_value"].sum().reset_index(),
    on="order_id",
    how="left"
)

monthly_revenue["month"] = (
    monthly_revenue["order_purchase_Date"].dt.to_period("M").astype(str)
)

monthly_revenue = (
    monthly_revenue.groupby("month")["total_value"]
    .sum()
    .reset_index()
)

st.subheader("Monthly Revenue Trend")

st.line_chart(
    monthly_revenue.set_index("month")["total_value"]
)

# Revenue by Category

category_sales = order_items.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left"
)

category_sales["revenue"] = (
    category_sales["price"] +
    category_sales["freight_value"]
)

category_sales = (
    category_sales.groupby("product_category_name")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.subheader("Top 10 Product Categories by Revenue")

st.bar_chart(category_sales)

# Customer Analysis

st.header("Customer Analysis")

# Customer order count
customer_orders = (
    orders.groupby("customer_id")["order_id"]
    .nunique()
    .reset_index()
)

customer_orders.columns = ["customer_id", "order_count"]

# Customer spending
customer_spending = order_items.merge(
    orders[["order_id", "customer_id"]],
    on="order_id",
    how="left"
)

customer_spending["total_spending"] = (
    customer_spending["price"] +
    customer_spending["freight_value"]
)

customer_spending = (
    customer_spending.groupby("customer_id")["total_spending"]
    .sum()
    .reset_index()
)

# Combine customer information
customer_data = customer_orders.merge(
    customer_spending,
    on="customer_id",
    how="left"
)

# Repeat customer
customer_data["repeat_customer"] = (
    customer_data["order_count"] > 1
)

st.subheader("Customer Overview")

st.metric(
    "Customers with Orders",
    customer_data["customer_id"].nunique()
)

st.metric(
    "Repeat Customers",
    customer_data["repeat_customer"].sum()
)

# Top 10 customers by spending
top_customers = (
    customer_data
    .sort_values("total_spending", ascending=False)
    .head(10)
)

st.subheader("Top 10 Customers by Spending")

st.dataframe(
    top_customers[["customer_id", "order_count", "total_spending"]]
)
# Seller & Product Analysis

st.header("Seller & Product Analysis")

# Seller Revenue
seller_sales = order_items.groupby("seller_id")["price"].sum()

st.subheader("Top Sellers")
st.bar_chart(seller_sales.sort_values(ascending=False).head(10))

st.subheader("Seller Revenue")
st.dataframe(
    seller_sales.sort_values(ascending=False).head(10)
)

# Product Category Performance
category_performance = category_sales.sort_values(ascending=False).head(10)

st.subheader("Product/Category Performance")
st.bar_chart(category_performance)

# Seller Ratings
seller_ratings = reviews.merge(
    orders[["order_id"]],
    on="order_id"
)

seller_ratings = seller_ratings["review_score"].mean()

st.subheader("Seller Ratings")
st.metric("Average Seller Rating", f"{seller_ratings:.2f}")

# Delivery Analysis

st.header("Delivery Analysis")

# Calculate delivery time
orders["order_purchase_Date"] = pd.to_datetime(orders["order_purchase_Date"])
orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_Date"]
).dt.days

# Average delivery time
average_delivery = orders["delivery_days"].mean()

st.metric(
    "Average Delivery Time",
    f"{average_delivery:.2f} days"
)

# On-time vs delayed
orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"]
)

orders["delivery_delay"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.days

on_time = (orders["delivery_delay"] <= 0).sum()
delayed = (orders["delivery_delay"] > 0).sum()

st.subheader("On-time vs Delayed Orders")

st.write("On-time orders:", on_time)
st.write("Delayed orders:", delayed)

# Delivery performance by location
location_delivery = orders.merge(
    customers[["customer_id", "customer_state"]],
    on="customer_id",
    how="left"
)

location_delivery = (
    location_delivery.groupby("customer_state")["delivery_days"]
    .mean()
    .sort_values()
)

st.subheader("Delivery Performance by Location")

st.bar_chart(location_delivery)

# Delivery delay vs review score
delivery_review = orders.merge(
    reviews[["order_id", "review_score"]],
    on="order_id",
    how="inner"
)

delay_review = (
    delivery_review.groupby("review_score")["delivery_delay"]
    .mean()
)

st.subheader("Delivery Delay vs Review Score")

st.dataframe(delay_review)

# Customer Experience

st.header("Customer Experience")

# Review Score Distribution
st.subheader("Review Score Distribution")

review_distribution = reviews["review_score"].value_counts().sort_index()

st.bar_chart(review_distribution)


# Reviews by Category
st.subheader("Reviews by Category")

review_category = reviews.merge(
    orders[["order_id"]],
    on="order_id",
    how="inner"
)

review_category = review_category.merge(
    order_items[["order_id", "product_id"]],
    on="order_id",
    how="inner"
)

review_category = review_category.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left"
)

reviews_by_category = (
    review_category
    .groupby("product_category_name")["review_score"]
    .count()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(reviews_by_category)


# Rating vs Delivery Performance
st.subheader("Rating vs Delivery Performance")

rating_delivery = orders.merge(
    reviews[["order_id", "review_score"]],
    on="order_id",
    how="inner"
)

rating_delivery["order_purchase_Date"] = pd.to_datetime(
    rating_delivery["order_purchase_Date"]
)

rating_delivery["order_delivered_customer_date"] = pd.to_datetime(
    rating_delivery["order_delivered_customer_date"]
)

rating_delivery["delivery_days"] = (
    rating_delivery["order_delivered_customer_date"]
    - rating_delivery["order_purchase_Date"]
).dt.days

rating_delivery_summary = (
    rating_delivery
    .groupby("review_score")["delivery_days"]
    .mean()
    .reset_index()
)

st.dataframe(rating_delivery_summary)

st.bar_chart(
    rating_delivery_summary.set_index("review_score")["delivery_days"]
)
st.header("Business Insights")

st.write("""
• On-time deliveries receive much higher review scores than delayed orders, showing that delivery performance strongly affects customer satisfaction.

• Revenue is concentrated in top categories and sellers, so focusing on high-performing products and reliable sellers can support business growth.
""")

