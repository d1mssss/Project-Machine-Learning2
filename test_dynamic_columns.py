import pandas as pd

def get_dynamic_columns(df):
    """Mendeteksi kolom pertanyaan dan jawaban secara dinamis"""
    pertanyaan_cols = []
    jawaban_cols = []
    
    # Cari semua kolom pertanyaan
    for col in df.columns:
        if 'Pertanyaan_CS' in col:
            # Extract number from column name
            parts = col.split('_')
            if len(parts) >= 3 and parts[-1].isdigit():
                pertanyaan_cols.append((int(parts[-1]), col))
    
    # Cari semua kolom jawaban
    for col in df.columns:
        if 'Jawaban_Pelanggan' in col:
            # Extract number from column name
            parts = col.split('_')
            if len(parts) >= 3 and parts[-1].isdigit():
                jawaban_cols.append((int(parts[-1]), col))
    
    # Sort berdasarkan nomor
    pertanyaan_cols.sort(key=lambda x: x[0])
    jawaban_cols.sort(key=lambda x: x[0])
    
    return pertanyaan_cols, jawaban_cols

# Load dataset
try:
    df = pd.read_excel('dataset/dataset_filled_status_promo.xlsx')
    print("✅ Dataset berhasil dimuat")
    print(f"Shape: {df.shape}")
    
    print("\n=== Kolom Original ===")
    all_cols = df.columns.tolist()
    question_related = [col for col in all_cols if 'Pertanyaan' in col]
    answer_related = [col for col in all_cols if 'Jawaban' in col]
    
    print("Kolom yang mengandung 'Pertanyaan':")
    for col in question_related:
        print(f"  - {col}")
    
    print("\nKolom yang mengandung 'Jawaban':")
    for col in answer_related:
        print(f"  - {col}")
    
    # Test rename logic
    print("\n=== Test Rename Logic ===")
    df_test = df.copy()
    
    # Rename jika kolom masih format .0, .1, .2, dst
    if 'Pertanyaan_CS.0' in df_test.columns and 'Pertanyaan_CS_1' not in df_test.columns:
        print("Melakukan rename kolom...")
        # Deteksi semua kolom pertanyaan dan jawaban secara dinamis
        pertanyaan_cols_orig = [col for col in df_test.columns if col.startswith('Pertanyaan_CS.')]
        jawaban_cols_orig = [col for col in df_test.columns if col.startswith('Jawaban_Pelanggan.')]
        
        print(f"Ditemukan {len(pertanyaan_cols_orig)} kolom pertanyaan original")
        print(f"Ditemukan {len(jawaban_cols_orig)} kolom jawaban original")
        
        # Rename pertanyaan columns
        for col in pertanyaan_cols_orig:
            if '.' in col:
                index = col.split('.')[-1]
                if index.isdigit():
                    new_name = f"Pertanyaan_CS_{int(index)+1}"
                    df_test = df_test.rename(columns={col: new_name})
                    print(f"  Rename: {col} -> {new_name}")
        
        # Rename jawaban columns  
        for col in jawaban_cols_orig:
            if '.' in col:
                index = col.split('.')[-1]
                if index.isdigit():
                    new_name = f"Jawaban_Pelanggan_{int(index)+1}"
                    df_test = df_test.rename(columns={col: new_name})
                    print(f"  Rename: {col} -> {new_name}")
    
    # Test dynamic detection
    print("\n=== Test Dynamic Detection ===")
    pertanyaan_cols, jawaban_cols = get_dynamic_columns(df_test)
    
    print(f"Kolom Pertanyaan yang terdeteksi ({len(pertanyaan_cols)}):")
    for idx, col_name in pertanyaan_cols:
        non_empty = df_test[col_name].dropna().shape[0]
        print(f"  {idx}. {col_name} (data: {non_empty} baris)")
    
    print(f"\nKolom Jawaban yang terdeteksi ({len(jawaban_cols)}):")
    for idx, col_name in jawaban_cols:
        non_empty = df_test[col_name].dropna().shape[0]
        print(f"  {idx}. {col_name} (data: {non_empty} baris)")
    
    print(f"\n=== Summary ===")
    print(f"Total kolom pertanyaan: {len(pertanyaan_cols)}")
    print(f"Total kolom jawaban: {len(jawaban_cols)}")
    print(f"Max step yang bisa dilakukan: {min(len(pertanyaan_cols), len(jawaban_cols))}")
    
except Exception as e:
    print(f"❌ Error: {e}")
