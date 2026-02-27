with source as (
    select * from {{ source('raw_olist', 'order_items') }}
),

renamed as (
    select
        order_id,
        order_item_id,
        product_id,
        seller_id,
        cast(price as numeric(12, 2)) as price,
        cast(freight_value as numeric(12, 2)) as freight_value
    from source
)

select * from renamed
