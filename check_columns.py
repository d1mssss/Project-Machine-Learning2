import pandas as pd

# Load dataset
df = pd.read_excel('dataset/dataset_filled_status_promo.xlsx')

# Tampilkan semua kolom yang mengandung Pertanyaan atau Jawaban
print("=== Kolom Pertanyaan dan Jawaban ===")
question_cols = [col for col in df.columns if 'Pertanyaan' in col]
answer_cols = [col for col in df.columns if 'Jawaban' in col]

print(f"Kolom Pertanyaan ({len(question_cols)}):")
for col in question_cols:
    print(f"  - {col}")

print(f"\nKolom Jawaban ({len(answer_cols)}):")
for col in answer_cols:
    print(f"  - {col}")

# Cek apakah ada data di kolom ke-4 dan ke-5
print("\n=== Sample Data untuk Kolom 4 dan 5 ===")
if len(question_cols) > 3:
    print(f"Data {question_cols[3]}:")
    print(df[question_cols[3]].dropna().unique()[:5])
    
if len(answer_cols) > 3:
    print(f"\nData {answer_cols[3]}:")
    print(df[answer_cols[3]].dropna().unique()[:5])

if len(question_cols) > 4:
    print(f"\nData {question_cols[4]}:")
    print(df[question_cols[4]].dropna().unique()[:5])
    
if len(answer_cols) > 4:
    print(f"\nData {answer_cols[4]}:")
    print(df[answer_cols[4]].dropna().unique()[:5])

print(f"\n=== Jumlah Total ===")
print(f"Total kolom pertanyaan: {len(question_cols)}")
print(f"Total kolom jawaban: {len(answer_cols)}")
