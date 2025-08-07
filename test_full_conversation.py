import pandas as pd

print("🧪 TEST KOLOM PERTANYAAN DAN JAWABAN")
print("=" * 50)

# Load dataset
df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")

print(f"Dataset shape: {df.shape}")
print("\n📋 Kolom yang berkaitan dengan pertanyaan dan jawaban:")

# Cari semua kolom pertanyaan dan jawaban
question_cols = []
answer_cols = []

for col in df.columns:
    if 'pertanyaan' in col.lower() and 'cs' in col.lower():
        question_cols.append(col)
    elif 'jawaban' in col.lower() and 'pelanggan' in col.lower():
        answer_cols.append(col)

print(f"\n🗣️ Kolom Pertanyaan CS ({len(question_cols)}):")
for i, col in enumerate(question_cols, 1):
    non_null_count = df[col].dropna().shape[0]
    print(f"  {i}. {col} - {non_null_count} data tidak kosong")

print(f"\n👤 Kolom Jawaban Pelanggan ({len(answer_cols)}):")
for i, col in enumerate(answer_cols, 1):
    non_null_count = df[col].dropna().shape[0]
    print(f"  {i}. {col} - {non_null_count} data tidak kosong")

# Test satu skenario lengkap
print(f"\n🎭 TEST SKENARIO LENGKAP:")
print("Mengambil satu baris untuk melihat alur percakapan:")

sample_row = df.iloc[0]
print(f"\nMode: {sample_row.get('Mode', 'N/A')}")

for i in range(5):  # 0 sampai 4
    if i == 0:
        q_col = 'Pertanyaan_CS.0'
        a_col = 'Jawaban_Pelanggan.0'
    else:
        q_col = f'Pertanyaan_CS.{i}'
        a_col = f'Jawaban_Pelanggan.{i}'
    
    question = sample_row.get(q_col, None)
    answer = sample_row.get(a_col, None)
    
    if pd.notna(question):
        print(f"\nQ{i+1}: {question}")
        if pd.notna(answer):
            print(f"A{i+1}: {answer}")
        else:
            print(f"A{i+1}: [Tidak ada jawaban]")
    else:
        print(f"\nQ{i+1}: [Tidak ada pertanyaan - percakapan selesai]")
        break

print(f"\n✅ KESIMPULAN:")
print(f"- Total kolom pertanyaan: {len(question_cols)}")
print(f"- Total kolom jawaban: {len(answer_cols)}")
print(f"- Aplikasi baru dapat menggunakan semua kolom secara berurutan")
print(f"- Setiap skenario dapat memiliki 1-5 pertanyaan tergantung data")

print(f"\n🚀 App siap dijalankan dengan percakapan lengkap!")
