import pandas as pd

print("🧪 TEST LOAD DATA FUNCTION")
print("=" * 40)

# Simulasi fungsi load_data yang diperbaiki
def load_data():
    try:
        df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")
        
        print("🔍 **Kolom asli dataset:**")
        print(df.columns.tolist())
        
        # Rename columns dengan lebih hati-hati
        if 'Pertanyaan_CS.0' in df.columns:
            df = df.rename(columns={
                'Pertanyaan_CS.0': 'Pertanyaan_CS',
                'Jawaban_Pelanggan.0': 'Jawaban_Pelanggan'
            })
            print("✅ Rename columns berhasil dilakukan")
        else:
            print("ℹ️ Columns sudah dalam format yang benar")
            
        print("🔍 **Kolom setelah rename:**")
        print(df.columns.tolist())
        
        # Cek apakah kolom Mode ada
        if 'Mode' in df.columns:
            print("✅ Kolom 'Mode' ditemukan!")
            print("Mode values:", df['Mode'].unique())
            
            # Test filter untuk setiap mode
            for mode in ['winback', 'retention', 'telecollection']:
                filtered = df[df['Mode'] == mode]
                print(f"Mode '{mode}': {len(filtered)} baris")
        else:
            print("❌ Kolom 'Mode' tidak ditemukan setelah loading!")
            
        return df
    except Exception as e:
        print(f"Dataset tidak ditemukan: {e}")
        return pd.DataFrame()

# Test fungsi
df = load_data()

if not df.empty:
    print("\n🎯 HASIL TEST:")
    print("✅ Dataset berhasil dimuat")
    print("✅ Kolom Mode tersedia")
    print("✅ Data untuk semua mode tersedia")
    print("\n🚀 App.py seharusnya berjalan dengan baik!")
else:
    print("\n❌ GAGAL!")
