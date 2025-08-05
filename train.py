import pandas as pd
import joblib
import re
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.utils import shuffle

# 1. Load Dataset
file_path = "dataset/simulasi_data_final_rapi.xlsx"
df = pd.read_excel(file_path)
print(f"Dataset dimuat: {df.shape[0]} baris")

# 2. Buat kolom context bertahap
df['context'] = df['Status_Dihubungi'].astype(str) + " " + df['Jawaban_Pelanggan'].astype(str) + " " + df['Minat_Lanjut'].astype(str)
for i in range(1, 6):
    prev = 'context' if i == 1 else f'context{i-1}'
    df[f'context{i}'] = df[prev] + " " + df[f'Pertanyaan_CS.{i}'].fillna('')

# 3. Stopwords dan fungsi pembersih teks
factory = StopWordRemoverFactory()
stopwords_id = set(factory.get_stop_words())
extra_stopwords = {'nya', 'kok', 'sih', 'deh', 'dong', 'mah'}
stopwords_id.update(extra_stopwords)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stopwords_id]
    return ' '.join(tokens)

# 4. Folder model
model_dir = "model"
os.makedirs(model_dir, exist_ok=True)

# 5. Loop untuk latih model CS.1 - CS.5
for i in range(1, 6):
    input_col = f"context{i}"
    target_col = f"Pertanyaan_CS.{i}"

    data = df[[input_col, target_col]].rename(columns={input_col: "input", target_col: "target"})
    data.dropna(inplace=True)

    # Optional: Tambahkan pembersihan kosong setelah clean_text
    data['input'] = data['input'].apply(clean_text)
    data = data[~data['input'].isna() & ~data['target'].isna()]

    if len(data) == 0:
        print(f"❌ Data kosong untuk model {i}. Melewati.")
        continue

    print(f"✅ Melatih model {i} dengan {len(data)} data")

    X_train, X_test, y_train, y_test = train_test_split(data['input'], data['target'], test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print(classification_report(y_test, y_pred))

    model_path = os.path.join(model_dir, f"model_pertanyaan_{i}.pkl")
    joblib.dump(pipeline, model_path)
    print(f"💾 Model {i} disimpan di: {model_path}")

