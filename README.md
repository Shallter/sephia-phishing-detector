# SEPHIA: Phishing Website Detection Using Hybrid URL Features and HTML Content Analysis

**SEPHIA** (System for Ensemble Phishing & HTML Intelligent Analysis) detects phishing websites by combining lexical URL features with structural features from a page's HTML, classified by an ensemble of Random Forest and XGBoost.

This project is my final project (thesis) for the S1 Informatics Engineering program at Universitas Islam Sultan Agung, 2026.

## Why this project

URL-only detection is easy to bypass: attackers use clean-looking URLs and hide fake login pages in invisible iframes or in forms that post to foreign servers. SEPHIA analyzes both the URL and the structure of the page.

## How it works

1. **Input:** the user pastes a URL into the Streamlit web app.
2. **Hybrid feature extraction**
   - URL-based features: URL length, raw IP address presence, and special symbol count (`@`, `-`, `//`).
   - HTML-based features: `iframe` presence, form action validity, external script presence, and the ratios of broken (null) and external links. The HTML is fetched with `requests` and parsed with BeautifulSoup4.
3. **Classification:** Random Forest and XGBoost are combined in a **soft voting** ensemble, which averages the confidence of both models to make the final decision (phishing or legitimate).
4. **Extra safeguards in the app**
   - **Brand veto (rule-based layer):** compares brand keywords in the URL with the actual root domain to catch typosquatting.
   - **Heuristic fallback:** if the target server is dead or the crawl fails, a suspicion penalty is applied instead of treating missing HTML features as safe.

## Dataset

- Phishing URLs: [OpenPhish](https://openphish.com)
- Legitimate URLs: [Majestic Million](https://majestic.com/reports/majestic-million)
- Both sources were merged into one dataset. Duplicate, empty, and invalid URLs were removed, and each URL was labeled as legitimate (0) or phishing (1).

## Results (test set)

| Metric | Result |
| --- | --- |
| Accuracy | 99.50% |
| Precision (phishing) | 100% |
| Recall (phishing) | 99% |
| F1-score (phishing) | 1.00 |

The web app was also tested with four scenarios: a legitimate website, a lexical attack (IP-based URL), typosquatting (brand veto activated), and a dead phishing link (heuristic fallback activated).

## App interface

The Streamlit app has a URL input and a "Pindai Website" (scan website) button, and shows the analysis in three tabs:

- **Brand validation (veto protocol):** matches brand keywords in the URL against the root domain.
- **HTML structure:** shows behavior metrics such as the broken-link and external-link ratios.
- **ML debug data:** shows the raw feature matrix that is fed into the model.

## Tech stack

Python, pandas, scikit-learn, XGBoost, requests, BeautifulSoup4, Streamlit, Matplotlib, Seaborn, and Pickle/Joblib for model serialization. Model training was done in Google Colab and the web app was built in VS Code.

## Limitations and future work

- The model was evaluated on a combined OpenPhish and Majestic Million dataset, so performance on other data sources should be validated.
- HTML analysis depends on the target server being reachable (partly handled by the heuristic fallback).
- Future work: turn SEPHIA into a browser extension (Chrome/Firefox) for real-time blocking.

## Author

Muhammad Maulana Fathul Muin
Informatics Engineering, Universitas Islam Sultan Agung
Batam, Indonesia | mmaulana1003@gmail.com
