# SEPHIA: Phishing Website Detection Using Hybrid URL Features and HTML Content Analysis

**SEPHIA** (System for Ensemble Phishing & HTML Intelligent Analysis) detects phishing websites by combining lexical URL features with structural features from a page's HTML, classified by an ensemble of Random Forest and XGBoost. This project is my final project (thesis) for the S1 Informatics Engineering program at Universitas Islam Sultan Agung, 2026.

## Why this project
URL-only detection is easy to bypass: attackers use clean-looking URLs and hide fake login pages in invisible iframes or forms that post to foreign servers. SEPHIA looks at both the URL and the page structure.

## How it works
1. **Input:** the user pastes a URL into the Streamlit app.
2. **Feature extraction (hybrid):**
   - URL-based: URL length, raw IP address presence, special symbol count (`@`, `-`, `//`).
   - HTML-based: `iframe` presence, form action validity, external script presence, and ratios of broken (null) and external links. The HTML is fetched with `requests` and parsed with BeautifulSoup4.
3. **Classification:** Random Forest and XGBoost are combined with a **soft voting** ensemble.
4. **Extra safeguards in the app:**
   - **Brand veto (rule-based layer):** compares brand keywords in the URL with the actual root domain to catch typosquatting.
   - **Heuristic fallback:** if the target server is dead or the crawl fails, a suspicion penalty is applied instead of treating missing HTML features as safe.

## Dataset
- Phishing URLs: [OpenPhish](https://openphish.com)
- Legitimate URLs: [Majestic Million](https://majestic.com/reports/majestic-million)
- Duplicates and invalid URLs removed, then labeled (0 = legitimate, 1 = phishing).
- Size: [number of phishing URLs] phishing and [number of legitimate URLs] legitimate. Train/test split: [e.g. 80/20].

## Results (test set)
| Metric | Result |
| --- | --- |
| Accuracy | 99.50% |
| Precision (phishing) | 100% |
| Recall (phishing) | 99% |
| F1-score (phishing) | 1.00 |

The app was also tested with four scenarios: a legitimate site, lexical attacks (IP-based URL), typosquatting (brand veto), and a dead phishing link (heuristic fallback).

## Tech stack
Python, pandas, scikit-learn, XGBoost, requests, BeautifulSoup4, Streamlit, Matplotlib, Seaborn, Pickle/Joblib. Model training in Google Colab, app built in VS Code.

## Screenshots
![Main interface](screenshots/main.png)
![Typosquatting detection](screenshots/typosquatting.png)

## Run locally
```bash
git clone https://github.com/[your-username]/[repo-name].git
cd [repo-name]
pip install -r requirements.txt
streamlit run [app-file].py
```

## Limitations and future work
- The model was evaluated on a combined OpenPhish + Majestic Million dataset; performance on other data sources should be validated.
- HTML analysis depends on the target server being reachable (partly handled by the heuristic fallback).
- Future work: turn SEPHIA into a browser extension (Chrome/Firefox) for real-time blocking.

## Author
Muhammad Maulana Fathul Muin  
Informatics Engineering, Universitas Islam Sultan Agung  
Batam, Indonesia | [LinkedIn URL] | mmaulana1003@gmail.com
