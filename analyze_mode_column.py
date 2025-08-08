import pandas as pd
import numpy as np

print("🔍 ANALISIS DETAIL DATASET - MENCARI KOLOM 'Mode'")
print("=" * 60)

# Load dataset yang digunakan app.py
try:
    df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")
    print(f"✅ Dataset berhasil dimuat: {df.shape}")
    
    # Cek semua kolom
    print(f"\n📋 SEMUA KOLOM ({len(df.columns)} total):")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. '{col}' (tipe: {df[col].dtype})")
    
    # Cek apakah ada kolom yang mirip 'Mode'
    print(f"\n🔍 MENCARI KOLOM YANG MIRIP 'Mode':")
    mode_like_columns = []
    for col in df.columns:
        if 'mode' in col.lower():
            mode_like_columns.append(col)
            print(f"   ✅ Ditemukan: '{col}'")
    
    if not mode_like_columns:
        print("   ❌ Tidak ada kolom yang mengandung kata 'mode'")
        
        # Cek kolom yang mungkin berisi informasi mode
        possible_mode_cols = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['jenis', 'tipe', 'kategori', 'status']):
                possible_mode_cols.append(col)
        
        if possible_mode_cols:
            print(f"   🤔 Kolom yang mungkin berisi info mode:")
            for col in possible_mode_cols:
                unique_vals = df[col].dropna().unique()
                print(f"      '{col}': {unique_vals}")
    
    # Cek apakah ada data yang mengandung 'winback', 'retention', 'telecollection'
    print(f"\n🔍 MENCARI DATA DENGAN NILAI MODE:")
    target_modes = ['winback', 'retention', 'telecollection']
    
    for col in df.columns:
        if df[col].dtype == 'object':  # Hanya cek kolom string
            for mode in target_modes:
                contains_mode = df[col].astype(str).str.contains(mode, case=False, na=False).any()
                if contains_mode:
                    count = df[col].astype(str).str.contains(mode, case=False, na=False).sum()
                    print(f"   ✅ '{mode}' ditemukan di kolom '{col}': {count} baris")
    
    # Tampilkan sample data
    print(f"\n📊 SAMPLE DATA (5 baris pertama):")
    print(df.head())
    
    # Cek apakah rename columns berhasil
    print(f"\n🔄 CEK RENAME COLUMNS:")
    if 'Pertanyaan_CS.0' in df.columns:
        print("   ⚠️ Kolom 'Pertanyaan_CS.0' masih ada - rename mungkin gagal")
    else:
        print("   ✅ Rename columns berhasil atau tidak diperlukan")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("KEMUNGKINAN PENYEBAB:")
print("1. Dataset tidak memiliki kolom 'Mode'")
print("2. Nama kolom berbeda (case sensitive)")
print("3. Kolom Mode ada tapi dengan nama lain")
print("4. Dataset yang dimuat salah")
