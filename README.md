                                 Optometry Clinical Intelligence & Practice Analytics Platform

An integrated healthcare informatics prototype combining clinical analytics, practice operations, revenue-cycle insights, and AI-assisted information exploration.

## Project Overview

This project demonstrates how optometry-related clinical and operational data can be organized, queried, analyzed, and visualized to support informed practice management. It combines three complementary components into a single portfolio project:

1. Healthcare Operations Dashboard — practice activity, monthly trends, daily operations, and operational KPIs.
2. Revenue Cycle Analytics — preliminary invoice trends and service-related financial analysis.
3. Ophthalmology Clinical Intelligence Platform — refractive analytics and AI-assisted exploration of clinical and operational information.

This project demonstrates an integrated healthcare informatics solution combining optometry clinical intelligence, operational analytics, revenue cycle analysis, and locally integrated LLM-powered assistance. The platform demonstrates the practical application of Python, MySQL, Streamlit, Power BI, and AI in healthcare analytics.

## Key Features

- Practice operations: monthly activity trends, daily records, weekday activity summaries, and interactive year filtering.
- Financial analytics: preliminary monthly invoice trends and KPI summaries; service-level analysis where compatible source fields are available.
- Refractive analytics: spherical power (SPH), cylindrical power (CYL), and lens-utilization patterns.
- Clinical intelligence: interactive views of ophthalmic data and exploratory summaries.
- AI-assisted exploration: locally integrated Qwen 2.5 model for prototype information exploration.
- Multiple reporting interfaces: Streamlit applications and a complementary Power BI dashboard.
- SQL-driven analytics: structured MySQL tables and SQL queries for extracting and aggregating practice data.

## Technology Stack

| Layer | Technology |
| --- | --- |
| Database and queries | MySQL, SQL |
| Data processing | Python, Pandas |
| Interactive applications | Streamlit |
| Business intelligence | Microsoft Power BI |
| AI exploration | Local Qwen 2.5 LLM |
| Development | Visual Studio Code |

## Architecture

```text
Preliminary clinical and operational data extracts
                       |
                       v
          MySQL / Structured CSV Data
                       |
                       v
              Python + Pandas
                       |
          +------------+-------------+
          |                          |
          v                          v
  Streamlit applications      Power BI reporting
          |
          v
   Clinical, operational,
   and financial insights

Local Qwen 2.5 supports AI-assisted exploration in the clinical application.
```

## Application Components

### 1. Healthcare Operations Dashboard

Explores practice activity using monthly and daily summaries. Includes trend visualizations, weekday comparisons, and interactive filtering where supported by the available data.

### 2. Revenue Cycle Analytics

Demonstrates preliminary invoice analytics and business KPI reporting. The figures are illustrative analytical extracts and should not be interpreted as reconciled revenue, cash collections, or audited financial results.

### 3. Ophthalmology Clinical Intelligence Platform

Explores ophthalmic and refractive information, including SPH/CYL distributions and lens categories. Lens-entry counts are not equivalent to unique patient counts. The prototype also demonstrates local LLM-assisted information exploration.

## Repository Files

The development project includes these primary Python entry points:

- `app.py` — ophthalmology clinical intelligence Streamlit application.
- `business_dashboard.py` — MySQL-connected operations and business analytics Streamlit application.

The application integrates Python-based clinical analytics, MySQL-driven business intelligence, interactive Streamlit dashboards, Power BI visualizations, and a locally integrated LLM.

## Running the Applications

Install the dependencies used by the relevant application in a local Python environment, configure access to your **own permitted test database or synthetic dataset**, and run:

```bash
python -m streamlit run app.py
```

For the business analytics application, use a separate terminal:

```bash
python -m streamlit run business_dashboard.py --server.port 8502
```

The business analytics dashboard connects to a MySQL database to retrieve and analyze clinical operations, revenue, and practice activity data. Python and Streamlit enable interactive visualization and reporting.

## Data Privacy and Limitations

- The platform utilizes preliminary analytical datasets to demonstrate integrated clinical, operational, and financial analytics.
- Analytical results are subject to further refinement and validation as part of continuous development.
- The project emphasizes responsible healthcare data management, with appropriate consideration for data privacy, confidentiality, and secure information handling.
- Publicly shared resources are limited to appropriately de-identified and authorized data.
## Potential Future Enhancements

- Validated and documented data pipelines.
- Expanded data-quality and reconciliation checks.
- Role-based access controls and audit logging.
- Standardized healthcare data interfaces and secure deployment.
- Evaluation and guardrails for AI-assisted outputs.

## Project Focus

This project demonstrates the integration of **clinical domain expertise, MySQL, Python, interactive Streamlit dashboards, Power BI, and locally integrated LLM-powered AI assistance** to support clinical intelligence, operational analytics, revenue cycle analysis, and data-driven decision-making in optometry practice management.
