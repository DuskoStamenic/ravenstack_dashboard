# Ravenstack Dashboard

A SaaS churn analytics dashboard built as a personal learning project, exploring two years of subscription and churn data through Python, Pandas, Plotly, and Streamlit. The full long-form write-up lives on the author's blog — this repository is the working code, data, and exported artifacts.

## Overview

RavenStack is a fictional SaaS company used to frame a real churn analytics exercise on the "SaaS Subscription & Churn Analytics Dataset by Rivalytics" from Kaggle. The dashboard is designed for an executive and leadership audience, structured around a clear narrative: **How much → When → Why → What it costs → What to do next**. The goal is to turn raw subscription events into a decision-ready view of retention health.

## Features

- KPI strip with headline retention and revenue metrics
- Monthly churn trends over the two-year window
- Churn reason breakdown
- Customer feedback themes
- Pre-churn signals
- Refund analysis
- Reason-vs-feedback heatmap
- Quarterly trend table
- 10-slide executive presentation derived from the dashboard

## Tech Stack

- Python
- Pandas
- Plotly
- Streamlit

## Project Structure

```
app.py                            Streamlit app entrypoint
charts.py                         Plotly chart definitions
data.py                           Data loading and processing
requirements.txt                  Python dependencies
ravenstack_churn_events.csv       Source data
ravenstack_churn_dashboard.html   Exported dashboard
ravenstack_churn_slides.html      Exported presentation
ravenstack_churn_review.pptx      PowerPoint version of slides
Images/                           Assets
```

## Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Design Notes

The visual language is dark and industrial, inspired by trading terminals and mission-control interfaces. A near-black background (`#0d0f14`) is paired with a lime-acid accent (`#e8ff47`), using Syne for headlines and DM Mono for labels. The layout favors a dense grid, sharp edges, and no rounded corners — every pixel earns its place.

## Dataset

"SaaS Subscription & Churn Analytics Dataset by Rivalytics" — available on Kaggle.

## Status

Personal learning project exploring data analysis as a complement to product design.
