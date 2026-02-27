{{
    config(
        materialized='table',
        schema='dw'
    )
}}
with date_spine as (
    select generate_series(
        '2016-01-01'::date,
        '2018-12-31'::date,
        '1 day'::interval
    )::date as date_day
),

renamed as (
    select
        date_day as date_key,
        date_day,
        extract(year from date_day)::int as year,
        extract(month from date_day)::int as month,
        extract(day from date_day)::int as day_of_month,
        to_char(date_day, 'Month') as month_name,
        extract(week from date_day)::int as week_of_year,
        extract(dow from date_day)::int as day_of_week,
        to_char(date_day, 'Day') as day_name
    from date_spine
)

select * from renamed
