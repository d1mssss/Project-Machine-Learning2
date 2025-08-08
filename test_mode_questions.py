import pandas as pd

# Load dataset
df = pd.read_excel('dataset/dataset_filled_status_promo.xlsx')

# Rename jika kolom masih .0
if 'Pertanyaan_CS.0' in df.columns and 'Pertanyaan_CS' not in df.columns:
    for i in range(5):
        if f"Pertanyaan_CS.{i}" in df.columns:
            df = df.rename(columns={f"Pertanyaan_CS.{i}": f"Pertanyaan_CS_{i+1}"})
        if f"Jawaban_Pelanggan.{i}" in df.columns:
            df = df.rename(columns={f"Jawaban_Pelanggan.{i}": f"Jawaban_Pelanggan_{i+1}"})

print("=== Cek Pertanyaan per Mode ===")
modes = df['Mode'].unique()

for mode in modes:
    print(f"\n--- Mode: {mode} ---")
    filtered_df = df[df['Mode'] == mode]
    print(f"Jumlah baris untuk mode {mode}: {len(filtered_df)}")
    
    # Cek pertanyaan pertama untuk mode ini
    pertanyaan_col = "Pertanyaan_CS_1"
    if pertanyaan_col in filtered_df.columns:
        pertanyaan_unik = filtered_df[pertanyaan_col].dropna().unique().tolist()
        print(f"Pertanyaan unik untuk {mode}:")
        for i, q in enumerate(pertanyaan_unik[:3], 1):  # Tampilkan 3 pertanyaan pertama
            print(f"  {i}. {q}")
        if len(pertanyaan_unik) > 3:
            print(f"  ... dan {len(pertanyaan_unik) - 3} pertanyaan lainnya")
    else:
        print(f"Kolom {pertanyaan_col} tidak ditemukan")

print("\n=== Cek apakah pertanyaan berbeda per mode ===")
# Bandingkan pertanyaan pertama antar mode
all_first_questions = {}
for mode in modes:
    filtered_df = df[df['Mode'] == mode]
    pertanyaan_col = "Pertanyaan_CS_1"
    if pertanyaan_col in filtered_df.columns:
        pertanyaan_unik = filtered_df[pertanyaan_col].dropna().unique().tolist()
        all_first_questions[mode] = set(pertanyaan_unik)

# Cek overlap
if len(all_first_questions) > 1:
    modes_list = list(all_first_questions.keys())
    for i in range(len(modes_list)):
        for j in range(i+1, len(modes_list)):
            mode1, mode2 = modes_list[i], modes_list[j]
            overlap = all_first_questions[mode1] & all_first_questions[mode2]
            print(f"Overlap pertanyaan antara {mode1} dan {mode2}: {len(overlap)} pertanyaan")
            if overlap:
                print(f"  Contoh overlap: {list(overlap)[:2]}")
