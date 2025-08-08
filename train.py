import pandas as pd
import joblib
import os
import json
import re
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# --- Konfigurasi ---
os.makedirs("model", exist_ok=True)
DATASET_PATH = "dataset/dataset_filled_status_promo.xlsx"
CUSTOMER_ID_PATH = "dataset/datasets_Customer_ID.xlsx"
CONVERSATION_FLOW_PATH = "model/conversation_flow.json"
VECTORIZER_PATH = "model/vectorizer.pkl"
CUSTOMER_ID_LIST_PATH = "model/customer_ids.pkl"

# --- Fungsi untuk Memuat dan Menyimpan Customer ID ---
def load_and_save_customer_ids():
    """Memuat daftar Customer ID dan menyimpannya untuk validasi di app."""
    print("\nMemuat daftar Customer ID...")
    try:
        df_customers = pd.read_excel(CUSTOMER_ID_PATH)
        customer_ids = df_customers['Customer_ID'].astype(str).tolist()
        
        # Simpan sebagai set untuk validasi cepat
        customer_id_set = set(customer_ids)
        joblib.dump(customer_id_set, CUSTOMER_ID_LIST_PATH)
        
        print(f"✅ Berhasil memuat {len(customer_ids)} Customer ID dari '{CUSTOMER_ID_PATH}'.")
        print(f"✅ Daftar Customer ID disimpan di '{CUSTOMER_ID_LIST_PATH}'.")
        
        # Tampilkan sample
        sample_ids = customer_ids[:5]
        print(f"Sample Customer ID: {sample_ids}")
        
        return customer_id_set
        
    except Exception as e:
        print(f"❌ Error memuat Customer ID: {e}")
        return set()

# --- Fungsi untuk Membangun Alur Percakapan ---
def build_conversation_flow(df):
    """Membangun struktur percakapan dari DataFrame dan menyimpannya sebagai JSON."""
    print("\nMembangun alur percakapan...")
    flow = {}
    
    # Deteksi kolom pertanyaan dan jawaban secara dinamis
    pertanyaan_cols = sorted([col for col in df.columns if col.startswith('Pertanyaan_CS.')], key=lambda x: int(x.split('.')[-1]))
    jawaban_cols = sorted([col for col in df.columns if col.startswith('Jawaban_Pelanggan.')], key=lambda x: int(x.split('.')[-1]))
    
    # Pastikan setiap pertanyaan punya pasangan jawaban
    max_depth = min(len(pertanyaan_cols), len(jawaban_cols))
    
    for _, row in df.iterrows():
        mode = row.get('Mode')
        if not mode or pd.isna(mode):
            continue

        # Inisialisasi mode jika belum ada
        if mode not in flow:
            flow[mode] = {}

        # Pointer untuk menelusuri struktur JSON
        current_level = flow[mode]

        # Iterasi melalui setiap pasangan pertanyaan-jawaban
        for i in range(max_depth):
            pertanyaan_col = pertanyaan_cols[i]
            jawaban_col = jawaban_cols[i]
            
            pertanyaan = row[pertanyaan_col]
            jawaban = row[jawaban_col]

            # Lewati jika pertanyaan atau jawaban kosong
            if pd.isna(pertanyaan) or not pertanyaan or pd.isna(jawaban) or not jawaban:
                break 

            # Jika pertanyaan belum ada di level ini, tambahkan
            if pertanyaan not in current_level:
                current_level[pertanyaan] = {}

            # Pindah ke level berikutnya (jawaban)
            current_level = current_level[pertanyaan]
            
            # Jika jawaban belum ada, inisialisasi untuk pertanyaan selanjutnya
            if jawaban not in current_level:
                current_level[jawaban] = {}
            
            # Pindah ke level selanjutnya untuk iterasi berikutnya
            current_level = current_level[jawaban]

    # Simpan ke file JSON
    with open(CONVERSATION_FLOW_PATH, 'w', encoding='utf-8') as f:
        json.dump(flow, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Alur percakapan berhasil disimpan di '{CONVERSATION_FLOW_PATH}'.")
    return flow

# --- Fungsi untuk melatih dan menyimpan model ---
def train_and_save_model(df, vectorizer, label_col, model_filename):
    """Fungsi generik untuk melatih model klasifikasi."""
    print(f"\nMelatih model untuk '{label_col}'...")
    
    # Filter data yang memiliki label
    df_sub = df.dropna(subset=[label_col, 'gabungan_interaksi'])
    if df_sub.empty:
        print(f"⚠️ Data kosong untuk target '{label_col}', model tidak dilatih.")
        return

    X = vectorizer.transform(df_sub['gabungan_interaksi'])
    y = df_sub[label_col]
    
    model = MultinomialNB()
    model.fit(X, y)
    
    joblib.dump(model, f"model/{model_filename}")
    print(f"✅ Model '{label_col}' berhasil disimpan sebagai 'model/{model_filename}'.")

# --- Proses Utama ---
if __name__ == "__main__":
    print(f"Memuat dataset dari {DATASET_PATH}...")
    try:
        df = pd.read_excel(DATASET_PATH)
    except FileNotFoundError:
        print(f"❌ Error: File dataset tidak ditemukan di {DATASET_PATH}.")
        exit()

    # Gabungkan semua interaksi menjadi satu kolom teks untuk training
    pertanyaan_cols = [col for col in df.columns if col.startswith("Pertanyaan_CS")]
    jawaban_cols = [col for col in df.columns if col.startswith("Jawaban_Pelanggan")]
    
    for col in pertanyaan_cols + jawaban_cols:
        df[col] = df[col].fillna('')
    
    df['gabungan_interaksi'] = df[pertanyaan_cols + jawaban_cols].astype(str).apply(lambda row: ' '.join(row), axis=1)
    print("✅ Berhasil menggabungkan teks interaksi untuk training.")

    # 1. Muat dan simpan daftar Customer ID
    load_and_save_customer_ids()

    # 2. Bangun dan simpan alur percakapan
    build_conversation_flow(df)

    # 3. Latih dan simpan Vectorizer
    print("\nMembuat dan melatih vectorizer...")
    vectorizer = TfidfVectorizer()
    vectorizer.fit(df['gabungan_interaksi'])
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"✅ Vectorizer berhasil disimpan sebagai '{VECTORIZER_PATH}'.")

    # 4. Latih dan simpan semua model prediksi
    train_and_save_model(df, vectorizer, 'Status', 'model_status.pkl')  # Gunakan 'Status' bukan 'status'
    train_and_save_model(df, vectorizer, 'Jenis_Promo', 'model_promo.pkl')
    train_and_save_model(df, vectorizer, 'Mode', 'model_mode.pkl')

    print("\n--- Proses Selesai ---")
    print("Semua model (Status, Jenis_Promo, Mode), vectorizer, Customer ID, dan alur percakapan telah berhasil dibuat.")
    print("ℹ️  Estimasi Pembayaran menggunakan ekstraksi real-time dari jawaban pelanggan, bukan model prediksi.")