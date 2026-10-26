import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

def train_model():
    print("\n🚀 Memulai Training Model Ensemble (RF + XGBoost)...")
    
    # 1. Load Dataset
    try:
        df = pd.read_csv('dataset_skripsi.csv')
    except FileNotFoundError:
        print("❌ Dataset tidak ditemukan! Jalankan '1_generate_data.py' dulu.")
        return

    # 2. Pisahkan Fitur dan Label
    X = df.drop(columns=['label'])
    y = df['label']
    
    # Simpan nama kolom untuk referensi Aplikasi (Biar gak error urutan)
    feature_columns = list(X.columns)
    
    # 3. Split Data (80% Latih, 20% Uji)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Define Models
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    
    # 5. Ensemble (Soft Voting)
    ensemble = VotingClassifier(estimators=[('rf', rf), ('xgb', xgb)], voting='soft')
    
    print("⏳ Sedang melatih model... (Tunggu sebentar)")
    ensemble.fit(X_train, y_train)
    
    # 6. Evaluasi
    y_pred = ensemble.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Training Selesai! Akurasi Model: {acc*100:.2f}%")
    print("\nLaporan Klasifikasi:")
    print(classification_report(y_test, y_pred))
    
    # 7. Simpan Model & Kolom
    # Kita simpan dictionary berisi model DAN urutan kolomnya
    model_data = {
        'model': ensemble,
        'features': feature_columns
    }
    joblib.dump(model_data, 'model_final.pkl')
    print("💾 Model tersimpan sebagai 'model_final.pkl'")

if __name__ == "__main__":
    train_model()