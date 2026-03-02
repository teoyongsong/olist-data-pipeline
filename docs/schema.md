# Database Schema Reference

PostgreSQL schemas and tables used in this project. Deployed schema names depend on the dbt profile: marts appear in **`dw_dw`**, staging in **`dw_stg_olist`**, raw in **`raw_olist`**.

---

## 1. Raw layer — `raw_olist`

Loaded from CSV by `ingestion/ingest_raw_olist.py`. One table per Kaggle CSV; column names match the source files.

| Table | Source CSV | Description |
|-------|------------|-------------|
| `customers` | olist_customers_dataset.csv | Customer IDs and location |
| `orders` | olist_orders_dataset.csv | Order headers and timestamps |
| `order_items` | olist_order_items_dataset.csv | Line items (product, seller, price, freight) |
| `order_payments` | olist_order_payments_dataset.csv | Payment type and value per order |
| `products` | olist_products_dataset.csv | Product attributes and category |
| `sellers` | olist_sellers_dataset.csv | Seller IDs and location |
| `geolocation` | olist_geolocation_dataset.csv | Zip code / geo data |
| `order_reviews` | olist_order_reviews_dataset.csv | Review scores and comments |

---

## 2. Staging layer — `dw_stg_olist`

Views built by dbt; clean and cast columns from `raw_olist`. Used only as input to marts.

### `stg_customers`

| Column | Type | Description |
|--------|------|-------------|
| customer_id | text | PK |
| customer_unique_id | text | Unique customer (can have multiple IDs) |
| customer_zip_code_prefix | text | Zip prefix |
| customer_city | text | City |
| customer_state | text | State |

### `stg_orders`

| Column | Type | Description |
|--------|------|-------------|
| order_id | text | PK |
| customer_id | text | FK to customers |
| order_ts | timestamp | Purchase timestamp |
| order_approved_ts | timestamp | Approval time |
| shipped_ts | timestamp | Delivered to carrier |
| delivered_ts | timestamp | Delivered to customer |
| estimated_delivery_ts | timestamp | Estimated delivery |
| order_status | text | Status |

### `stg_order_items`

| Column | Type | Description |
|--------|------|-------------|
| order_id | text | PK part 1 |
| order_item_id | int | PK part 2 |
| product_id | text | FK to products |
| seller_id | text | FK to sellers |
| price | numeric(12,2) | Unit price |
| freight_value | numeric(12,2) | Freight |

### `stg_products`

| Column | Type | Description |
|--------|------|-------------|
| product_id | text | PK |
| product_category_name | text | Category |
| product_name_length | int | Name length |
| product_description_length | int | Description length |
| product_photos_qty | int | Photo count |
| product_weight_g | int | Weight (g) |
| product_length_cm | int | Length (cm) |
| product_height_cm | int | Height (cm) |
| product_width_cm | int | Width (cm) |

### `stg_sellers`

| Column | Type | Description |
|--------|------|-------------|
| seller_id | text | PK |
| seller_zip_code_prefix | text | Zip prefix |
| seller_city | text | City |
| seller_state | text | State |

---

## 3. Data warehouse (star schema) — `dw_dw`

Marts built by dbt. Use these for reporting and the EDA notebook.

### `dim_customer`

| Column | Type | Description |
|--------|------|-------------|
| customer_key | int | Surrogate PK |
| customer_id | text | Business key |
| customer_unique_id | text | Unique customer |
| customer_city | text | City |
| customer_state | text | State |
| first_order_date | date | First order |
| last_order_date | date | Last order |
| total_orders | int | Order count |
| total_revenue | numeric | Sum of order value |
| customer_lifetime_value | numeric | Same as total_revenue |
| tenure_segment | text | 'No orders' \| 'New' \| 'Established' \| 'Loyal' |

### `dim_product`

| Column | Type | Description |
|--------|------|-------------|
| product_key | int | Surrogate PK |
| product_id | text | Business key |
| product_category_name | text | Category |
| product_name_length | int | Name length |
| product_description_length | int | Description length |
| product_photos_qty | int | Photo count |
| product_weight_g | int | Weight (g) |
| product_length_cm | int | Length (cm) |
| product_height_cm | int | Height (cm) |
| product_width_cm | int | Width (cm) |

### `dim_seller`

| Column | Type | Description |
|--------|------|-------------|
| seller_key | int | Surrogate PK |
| seller_id | text | Business key |
| seller_zip_code_prefix | text | Zip prefix |
| seller_city | text | City |
| seller_state | text | State |

### `dim_date`

| Column | Type | Description |
|--------|------|-------------|
| date_key | date | PK (2016-01-01 to 2018-12-31) |
| date_day | date | Same as date_key |
| year | int | Year |
| month | int | Month (1–12) |
| day_of_month | int | Day |
| month_name | text | Month name |
| week_of_year | int | Week number |
| day_of_week | int | Day of week (0–6) |
| day_name | text | Day name |

### `fact_order_items`

| Column | Type | Description |
|--------|------|-------------|
| order_item_key | int | Surrogate PK |
| order_id | text | Order business key |
| order_item_id | int | Item id within order |
| customer_key | int | FK → dim_customer.customer_key |
| product_key | int | FK → dim_product.product_key |
| seller_key | int | FK → dim_seller.seller_key |
| order_date_key | date | Order date |
| delivery_date_key | date | Delivery date (nullable) |
| price | numeric | Unit price |
| freight_value | numeric | Freight |
| total_item_value | numeric | price + freight_value |
| is_late_delivery | boolean | delivered_ts > estimated_delivery_ts |
| is_first_order | boolean | Order date = customer first_order_date |

---

## 4. Star schema diagram (text)

```
                    dim_customer
                          │
                          │ customer_key
                          ▼
dim_date ◄──── order_date_key ──── fact_order_items ──── product_key ────► dim_product
                          │
                          │ seller_key
                          ▼
                    dim_seller

                delivery_date_key (optional link to dim_date)
```

**Grain of `fact_order_items`:** One row per order item (order_id + order_item_id).
