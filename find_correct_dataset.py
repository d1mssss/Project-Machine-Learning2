import pandas as pd
import os

print("🔍 MENCARI DATASET YANG SESUAI UNTUK APP.PY")
print("="*50)

# List semua file dataset
dataset_files = [
    "dataset/dataset_filled_status_promo.xlsx",
    "dataset/simulasi_data_kompleks_300.xlsx", 
    "dataset/dataset_gabungan_600_baris.xlsx",
    "dataset/dataset_beragam_kondisi_final.xlsx",
    "dataset/simulasi_data_final_400.xlsx",
    "dataset/simulasi_data_200_final_rapi.xlsx"
]

for file_path in dataset_files:
    if os.path.exists(file_path):
        try:
            print(f"\n📁 {file_path}")
            df = pd.read_excel(file_path)
            print(f"   Shape: {df.shape}")
            
            # Cek kolom Mode
            has_mode = 'Mode' in df.columns
            print(f"   Mode column: {'✅' if has_mode else '❌'}")
            
            if has_mode:
                mode_values = df['Mode'].unique()
                print(f"   Mode values: {mode_values}")
                
                # Cek untuk setiap mode
                for mode in ['winback', 'retention', 'telecollection']:
                    count = len(df[df['Mode'] == mode])
                    print(f"     {mode}: {count} rows")
            
            # Cek kolom pertanyaan
            question_cols = [col for col in df.columns if 'pertanyaan' in col.lower() or 'cs' in col.lower()]
            print(f"   Question columns: {question_cols}")
            
            # Cek kolom jawaban
            answer_cols = [col for col in df.columns if 'jawaban' in col.lower() or 'pelanggan' in col.lower()]
            print(f"   Answer columns: {answer_cols}")
            
            if has_mode and question_cols and answer_cols:
                print("   🎯 COCOK UNTUK APP!")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"\n📁 {file_path} - File tidak ditemukan")

print("\n" + "="*50)
print("REKOMENDASI:")
print("1. Gunakan dataset yang memiliki kolom 'Mode'")
print("2. Pastikan ada kolom pertanyaan dan jawaban")
print("3. Update app.py untuk menggunakan dataset yang tepat")
