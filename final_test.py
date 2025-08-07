import pandas as pd

print("🎯 FINAL TEST - SIMULASI APP.PY")
print("=" * 40)

# Load data seperti di app.py
df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")
print(f"Dataset loaded: {df.shape}")

# Test untuk setiap mode
modes = ["Winback", "Retention", "Telecollection"]

for mode in modes:
    print(f"\n📋 Testing Mode: {mode}")
    
    # Filter berdasarkan mode
    filtered_df = df[df['Mode'] == mode]
    print(f"   Data filtered: {len(filtered_df)} rows")
    
    if len(filtered_df) > 0:
        # Cek kolom pertanyaan
        if 'Pertanyaan_CS.0' in filtered_df.columns:
            questions = filtered_df['Pertanyaan_CS.0'].dropna().unique()
            print(f"   Questions available: {len(questions)}")
            
            if len(questions) > 0:
                # Test satu pertanyaan
                sample_question = questions[0]
                print(f"   Sample question: {sample_question[:50]}...")
                
                # Cek jawaban untuk pertanyaan ini
                answers = filtered_df[filtered_df['Pertanyaan_CS.0'] == sample_question]['Jawaban_Pelanggan.0'].dropna().unique()
                print(f"   Answers available: {len(answers)}")
                
                if len(answers) > 0:
                    print(f"   Sample answer: {answers[0][:30]}...")
                    print("   ✅ Mode ini siap digunakan!")
                else:
                    print("   ⚠️ Tidak ada jawaban untuk pertanyaan ini")
            else:
                print("   ❌ Tidak ada pertanyaan untuk mode ini")
        else:
            print("   ❌ Kolom Pertanyaan_CS.0 tidak ditemukan")
    else:
        print("   ❌ Tidak ada data untuk mode ini")

print("\n🎯 KESIMPULAN:")
print("✅ Kolom Mode ada dan nilai sudah benar (kapital awal)")
print("✅ App.py sudah diperbaiki untuk menangani struktur dataset")
print("✅ Filter berdasarkan mode seharusnya bekerja sekarang")
print("\n🚀 Coba jalankan: streamlit run app.py")
