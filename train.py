# === train.py ===
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline

# Load dataset
file_path = "dataset/dataset_gabungan_600_baris.xlsx"
df = pd.read_excel(file_path)

# Gabungkan semua jawaban menjadi satu kolom
jawaban_cols = [
    'Jawaban_Pelanggan', 'Jawaban_Pelanggan.1',
    'Jawaban_Pelanggan.2', 'Jawaban_Pelanggan.3', 'Jawaban_Pelanggan.4'
]
df['gabungan_jawaban'] = df[jawaban_cols].astype(str).apply(lambda row: ' '.join(row), axis=1)

# Hapus baris kosong pada target
df = df.dropna(subset=['status', 'Jenis_Promo'])

# Siapkan data dan target
X = df['gabungan_jawaban']
y_status = df['status']
y_promo = df['Jenis_Promo']

# Train model untuk status
pipeline_status = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', DecisionTreeClassifier(random_state=42))
])
pipeline_status.fit(X, y_status)

# Train model untuk promo
pipeline_promo = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', DecisionTreeClassifier(random_state=42))
])
pipeline_promo.fit(X, y_promo)

# Simpan model
joblib.dump(pipeline_status, 'model/model_status.pkl')
joblib.dump(pipeline_promo, 'model/model_promo.pkl')

print("Model berhasil disimpan!")