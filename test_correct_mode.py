import pandas as pd

print("🧪 TEST DENGAN NILAI MODE YANG BENAR")
print("=" * 45)

df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")

print("Mode values di dataset:", df['Mode'].unique())

# Test filter dengan kapitalisasi yang benar
for mode in ['Winback', 'Retention', 'Telecollection']:
    filtered = df[df['Mode'] == mode]
    print(f"Mode '{mode}': {len(filtered)} baris")
    
    if len(filtered) > 0:
        # Cek apakah ada pertanyaan
        if 'Pertanyaan_CS.0' in filtered.columns:
            questions = filtered['Pertanyaan_CS.0'].dropna().unique()
            print(f"  -> Pertanyaan unik: {len(questions)}")
            if len(questions) > 0:
                print(f"  -> Sample: {questions[0][:50]}...")
        
print("\n✅ SOLUSI: Gunakan 'Winback', 'Retention', 'Telecollection' (kapital awal)")
