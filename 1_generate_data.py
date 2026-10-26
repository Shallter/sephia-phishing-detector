import pandas as pd
import numpy as np
import random

def generate_robust_dataset(n_samples=5000):
    print(f"🚀 Memulai Generasi {n_samples} Data Realistis (Dengan Noise)...")
    
    data = []
    brand_db = {
        'paypal': 'paypal.com', 'google': 'google.com', 'facebook': 'facebook.com',
        'netflix': 'netflix.com', 'bca': 'klikbca.com', 'bri': 'bri.co.id',
        'mandiri': 'bankmandiri.co.id', 'instagram': 'instagram.com',
        'whatsapp': 'whatsapp.com', 'dana': 'dana.id', 'gopay': 'gojek.com',
        'bni': 'bni.co.id'
    }

    for _ in range(n_samples):
        label = np.random.choice([0, 1], p=[0.5, 0.5])
        row = {}
        
        if label == 0: # --- WEBSITE AMAN (LEGITIMATE) ---
            row['label'] = 0
            row['url_length'] = int(np.random.normal(30, 15))
            row['has_ip'] = 1 if random.random() > 0.98 else 0 # 2% web aman pakai IP
            row['count_dash'] = int(np.random.poisson(1)) # Kadang ada strip
            row['count_at'] = 1 if random.random() > 0.99 else 0
            row['is_https'] = 1 if random.random() > 0.05 else 0 # 5% web aman lupa HTTPS
            
            # HTML: Sebagian kecil web aman juga agak berantakan (Noise)
            row['external_link_ratio'] = np.random.uniform(0.0, 0.5) 
            row['null_link_ratio'] = np.random.uniform(0.0, 0.15) 
            row['has_password_field'] = 1 if random.random() > 0.5 else 0
            
            # Brand Check (Valid)
            if random.random() > 0.5:
                row['has_brand_name'] = 1
                row['domain_match'] = 1 
            else:
                row['has_brand_name'] = 0
                row['domain_match'] = 0 

        else: # --- WEBSITE JAHAT (PHISHING) ---
            row['label'] = 1
            row['url_length'] = int(np.random.normal(65, 25))
            row['has_ip'] = 1 if random.random() > 0.7 else 0
            row['count_dash'] = int(np.random.poisson(3))
            row['count_at'] = 1 if random.random() > 0.85 else 0
            row['is_https'] = 1 if random.random() > 0.3 else 0 # Banyak hacker sekarang pakai HTTPS
            
            # HTML: Sebagian hacker bikin web yang sangat rapi (Noise)
            if random.random() > 0.2: 
                row['external_link_ratio'] = np.random.uniform(0.5, 1.0)
                row['null_link_ratio'] = np.random.uniform(0.2, 0.8)
            else: # Hacker cerdas (web rapi)
                row['external_link_ratio'] = np.random.uniform(0.1, 0.4)
                row['null_link_ratio'] = np.random.uniform(0.0, 0.1)

            row['has_password_field'] = 1 if random.random() > 0.1 else 0
            
            # Brand Check (Mencurigakan)
            if random.random() > 0.3:
                row['has_brand_name'] = 1 
                row['domain_match'] = 0 
            else:
                row['has_brand_name'] = 0
                row['domain_match'] = 0

        # Cleaning data minus
        row['url_length'] = max(10, row['url_length'])
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv('dataset_skripsi.csv', index=False)
    print(f"✅ Dataset Realistis Selesai: 'dataset_skripsi.csv' ({len(df)} data).")

if __name__ == "__main__":
    generate_robust_dataset()