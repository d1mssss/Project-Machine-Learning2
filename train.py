import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# --- Konfigurasi ---
# Pastikan direktori 'model' dan file dataset sudah ada
os.makedirs("model", exist_ok=True)
DATASET_PATH = "dataset/dataset_filled_status_promo.xlsx"

# --- Memuat dan Memproses Data ---
print(f"Memuat dataset dari {DATASET_PATH}...")
try:
    df = pd.read_excel(DATASET_PATH)
except FileNotFoundError:
    print(f"❌ Error: File dataset tidak ditemukan di {DATASET_PATH}.")
    exit()

# Rename kolom jika perlu
if 'Pertanyaan_CS.0' in df.columns:
    df = df.rename(columns={'Pertanyaan_CS.0': 'Pertanyaan_CS', 'Jawaban_Pelanggan.0': 'Jawaban_Pelanggan'})

# Ambil kolom pertanyaan dan jawaban
pertanyaan_cols = [col for col in df.columns if col.startswith("Pertanyaan_CS")]
jawaban_cols = [col for col in df.columns if col.startswith("Jawaban_Pelanggan")]

# Gabungkan semua interaksi menjadi satu kolom teks
for col in pertanyaan_cols + jawaban_cols:
    df[col] = df[col].fillna('')
df['gabungan_interaksi'] = df[pertanyaan_cols + jawaban_cols].astype(str).apply(lambda row: ' '.join(row), axis=1)
print("✅ Berhasil menggabungkan teks interaksi.")

# --- Melatih dan Menyimpan Vectorizer ---
print("\nMembuat dan melatih vectorizer tunggal...")
vectorizer = TfidfVectorizer()
vectorizer.fit(df['gabungan_interaksi'])
joblib.dump(vectorizer, "model/vectorizer.pkl")
print("✅ Vectorizer berhasil disimpan sebagai 'model/vectorizer.pkl'.")

# --- Fungsi untuk melatih dan menyimpan model ---
def train_and_save_model(df_sub, label_col, model_filename):
    print(f"\nMelatih model untuk '{label_col}'...")
    df_sub = df_sub.dropna(subset=[label_col])
    X = vectorizer.transform(df_sub['gabungan_interaksi'])
    y = df_sub[label_col]
    
    if df_sub.empty:
        print(f"⚠️ Data kosong untuk target '{label_col}', model tidak dilatih.")
        return

    model = MultinomialNB()
    model.fit(X, y)
    joblib.dump(model, f"model/{model_filename}")
    print(f"✅ Model '{label_col}' berhasil disimpan sebagai '{model_filename}'.")

# --- Melatih Masing-masing Model ---
train_and_save_model(df, 'status', 'model_status.pkl')
train_and_save_model(df, 'Jenis_Promo', 'model_promo.pkl')
train_and_save_model(df, 'Mode', 'model_mode.pkl')

# --- Selesai ---
print("\n--- Proses Selesai ---")
print("Semua model (status, Jenis_Promo, mode) dan vectorizer telah berhasil dibuat.")
