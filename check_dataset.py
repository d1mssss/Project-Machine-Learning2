import pandas as pd

# Load dataset
try:
    df = pd.read_excel('dataset/dataset_filled_status_promo.xlsx')
    print("✅ Dataset berhasil dimuat")
    print(f"Shape: {df.shape}")
    print("\n📋 Kolom yang tersedia:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")
    
    print("\n🔍 Cek kolom 'Mode':")
    if 'Mode' in df.columns:
        print("✅ Kolom 'Mode' ditemukan")
        print("Unique values dalam Mode:")
        mode_values = df['Mode'].unique()
        for val in mode_values:
            print(f"  - {val}")
        print(f"\nJumlah data per mode:")
        print(df['Mode'].value_counts())
    else:
        print("❌ Kolom 'Mode' TIDAK ditemukan!")
        print("Mungkin nama kolomnya berbeda:")
        mode_like_cols = [col for col in df.columns if 'mode' in col.lower()]
        print(f"Kolom yang mirip 'mode': {mode_like_cols}")
    
    print("\n🔍 Cek kolom 'Pertanyaan_CS':")
    if 'Pertanyaan_CS' in df.columns:
        print("✅ Kolom 'Pertanyaan_CS' ditemukan")
        print(f"Jumlah pertanyaan unik: {df['Pertanyaan_CS'].nunique()}")
        print("Sample pertanyaan:")
        sample_questions = df['Pertanyaan_CS'].dropna().unique()[:3]
        for q in sample_questions:
            print(f"  - {q}")
    else:
        print("❌ Kolom 'Pertanyaan_CS' TIDAK ditemukan!")
        cs_like_cols = [col for col in df.columns if 'pertanyaan' in col.lower() or 'cs' in col.lower()]
        print(f"Kolom yang mirip: {cs_like_cols}")

except Exception as e:
    print(f"❌ Error: {e}")
