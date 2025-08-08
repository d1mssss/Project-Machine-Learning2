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

def get_relevant_answers(df, mode, step, pertanyaan_terpilih=None, jawaban_sebelumnya=None):
    """Mendapatkan 4 jawaban yang paling relevan untuk pertanyaan dan konteks saat ini"""
    
    # Get dynamic columns
    pertanyaan_cols, jawaban_cols = get_dynamic_columns(df)
    
    # Filter berdasarkan mode
    filtered_data = df[df['Mode'] == mode].copy()
    
    # Jika ada jawaban sebelumnya, filter lebih lanjut
    if step > 1 and jawaban_sebelumnya:
        prev_jawaban_col = None
        for j_idx, j_col in jawaban_cols:
            if j_idx == step - 1:
                prev_jawaban_col = j_col
                break
        
        if prev_jawaban_col and prev_jawaban_col in filtered_data.columns:
            filtered_data = filtered_data[filtered_data[prev_jawaban_col] == jawaban_sebelumnya]
    
    # Dapatkan kolom jawaban untuk step ini
    current_jawaban_col = None
    for j_idx, j_col in jawaban_cols:
        if j_idx == step:
            current_jawaban_col = j_col
            break
    
    if current_jawaban_col and current_jawaban_col in filtered_data.columns:
        # Ambil jawaban yang tersedia untuk konteks ini
        jawaban_tersedia = filtered_data[current_jawaban_col].dropna().value_counts()
        
        # Ambil 4 jawaban paling umum (atau semua jika kurang dari 4)
        top_answers = jawaban_tersedia.head(4).index.tolist()
        
        return top_answers, jawaban_tersedia
    
    return [], pd.Series()

# Load dan test dataset
try:
    df = pd.read_excel('dataset/dataset_filled_status_promo.xlsx')
    
    # Rename jika kolom masih format .0, .1, .2, dst
    if 'Pertanyaan_CS.0' in df.columns and 'Pertanyaan_CS_1' not in df.columns:
        # Deteksi semua kolom pertanyaan dan jawaban secara dinamis
        pertanyaan_cols_orig = [col for col in df.columns if col.startswith('Pertanyaan_CS.')]
        jawaban_cols_orig = [col for col in df.columns if col.startswith('Jawaban_Pelanggan.')]
        
        # Rename pertanyaan columns
        for col in pertanyaan_cols_orig:
            if '.' in col:
                index = col.split('.')[-1]
                if index.isdigit():
                    new_name = f"Pertanyaan_CS_{int(index)+1}"
                    df = df.rename(columns={col: new_name})
        
        # Rename jawaban columns  
        for col in jawaban_cols_orig:
            if '.' in col:
                index = col.split('.')[-1]
                if index.isdigit():
                    new_name = f"Jawaban_Pelanggan_{int(index)+1}"
                    df = df.rename(columns={col: new_name})
    
    print("✅ Dataset berhasil dimuat dan diproses")
    print(f"Shape: {df.shape}")
    
    # Test untuk setiap mode
    modes = df['Mode'].unique()
    print(f"\n=== Test Jawaban Relevan untuk {len(modes)} Mode ===")
    
    for mode in modes:
        print(f"\n--- Mode: {mode} ---")
        mode_data = df[df['Mode'] == mode]
        print(f"Data tersedia: {len(mode_data)} baris")
        
        # Test step 1
        print(f"\nStep 1 untuk mode {mode}:")
        answers_step1, counts_step1 = get_relevant_answers(df, mode, 1)
        print(f"  Jawaban tersedia: {len(answers_step1)}")
        for i, ans in enumerate(answers_step1, 1):
            count = counts_step1[ans] if ans in counts_step1 else 0
            print(f"    {i}. {ans} ({count} kali)")
        
        # Test step 2 dengan jawaban pertama dari step 1
        if answers_step1:
            jawaban_pertama = answers_step1[0]
            print(f"\nStep 2 untuk mode {mode} dengan jawaban sebelumnya '{jawaban_pertama}':")
            answers_step2, counts_step2 = get_relevant_answers(df, mode, 2, None, jawaban_pertama)
            print(f"  Jawaban tersedia: {len(answers_step2)}")
            for i, ans in enumerate(answers_step2, 1):
                count = counts_step2[ans] if ans in counts_step2 else 0
                print(f"    {i}. {ans} ({count} kali)")
    
    print(f"\n=== Summary ===")
    pertanyaan_cols, jawaban_cols = get_dynamic_columns(df)
    print(f"Total kolom pertanyaan: {len(pertanyaan_cols)}")
    print(f"Total kolom jawaban: {len(jawaban_cols)}")
    print(f"Mode tersedia: {', '.join(modes)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
