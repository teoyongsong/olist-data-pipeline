# Executive Presentation Outline (10 min + 5 min Q&A)

**Ready-to-present deck:** Open `presentation_slides.html` in a browser to present (Reveal.js). Use arrow keys or click to advance.

Use this outline to build a custom slide deck (e.g. PowerPoint or Google Slides). Keep slides visual and high-level; avoid code.

---

## Slide 1 – Title
- **Title**: Olist E-Commerce Data Pipeline – From Raw Data to Business Insights
- **Subtitle**: Data Engineering Project | [Your Team/Date]

---

## Slide 2 – Executive Summary (2–3 min)
- **Problem**: Need reliable, timely analytics on e-commerce sales, customers, and operations.
- **Solution**: End-to-end pipeline: ingest Olist data → PostgreSQL warehouse → star schema → quality checks → analysis.
- **Impact**:
  - Single source of truth for revenue, orders, and customer value.
  - Trusted metrics (e.g. monthly trends, top categories, customer segments, delivery performance).
  - Foundation for BI and data science.

---

## Slide 3 – Business Value
- **Revenue**: Identify top categories and high-CLV segments for targeted campaigns.
- **Operations**: Late-delivery metrics to improve logistics and SLAs.
- **Strategy**: Reusable pipeline for more data sources and markets.

**Visual**: 2–3 KPIs or a simple “value chain” graphic (Data → Insights → Decisions).

---

## Slide 4 – Architecture (One Picture)
- **Diagram**: Source CSVs → Python ingest → PostgreSQL (`raw_olist`) → dbt (staging → star schema `dw`) → Quality (dbt + script) → Analysis (Python/BI).
- **Caption**: “Single pipeline from raw data to analysis-ready star schema.”

---

## Slide 5 – Star Schema (Simple)
- **Fact**: Order items (revenue, units, late delivery, first order).
- **Dimensions**: Customer, Product, Seller, Date.
- **Why**: Fast, intuitive queries for business questions; easy to extend.

**Visual**: Simple star diagram (one central “Sales” fact, four dimension boxes).

---

## Slide 6 – Key Insights (Charts)
- **Chart 1**: Monthly revenue trend (from notebook).
- **Chart 2**: Top product categories by revenue.
- **Chart 3**: Customer segments (e.g. tenure or CLV) and revenue share.
- **Optional**: Late delivery rate.

**Talking point**: “These metrics are now reproducible and validated by our pipeline.”

---

## Slide 7 – Data Quality & Trust
- **What we do**: Automated checks after each run (dbt tests + custom checks on raw data).
- **What we catch**: Missing keys, invalid numbers, broken references.
- **Message**: “Quality gates ensure we can trust the numbers we present.”

---

## Slide 8 – Risks and Mitigations
- **Data quality**: Automated tests and alerts.
- **Scaling**: Same design can move to cloud warehouse (e.g. BigQuery) if needed.
- **Operational**: Optional orchestration (e.g. scheduled runs) for regular refreshes.

---

## Slide 9 – Next Steps / Recommendations
- **Short term**: Use current metrics for monthly business reviews; add one or two dashboards.
- **Medium term**: Schedule pipeline (e.g. weekly); add more dimensions (e.g. region) if data allows.
- **Long term**: Extend to other sources (e.g. marketing, returns) using the same pattern.

---

## Slide 10 – Q&A
- **Title**: Questions & Discussion
- **Reminder**: Balance technical depth with business language; have one technical and one business spokesperson for Q&A.

---

## Suggested Q&A Prep

| Question | Suggested answer |
|----------|------------------|
| Why star schema? | Fewer joins, clear grain, easy for business users and BI tools; supports our main KPIs. |
| How do we know the data is correct? | dbt tests (uniqueness, FKs, nulls) plus data-quality checks on raw data; we can add more rules as needed. |
| Can we add more data sources? | Yes; same pattern: ingest to raw → staging → marts. We’d add new tables and models. |
| What if data volume grows? | PostgreSQL can scale; we can also move to a cloud warehouse (BigQuery/Snowflake) with minimal change to dbt and analysis code. |
