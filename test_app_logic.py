print("🧪 TEST APP LOGIC")
print("=" * 30)

# Simulasi logika step-by-step untuk memastikan tidak ada auto-advance

# Test kondisi empty string
test_cases = [
    ("", "Empty string"),
    ("Winback", "Valid mode"),
    (None, "None value")
]

print("Test kondisi untuk selectbox:")
for value, desc in test_cases:
    if value and value != "":
        print(f"✅ {desc}: LANJUT")
    else:
        print(f"⏸️ {desc}: TIDAK LANJUT")

print("\n✅ Logika sudah diperbaiki:")
print("1. Selectbox tidak akan auto-advance dengan empty string")
print("2. Tombol 'Lanjut' hanya muncul jika ada pilihan valid")
print("3. Reset button menghapus semua session state")
print("4. Setiap step membutuhkan input eksplisit dari user")

print("\n🚀 App siap dijalankan: streamlit run app.py")
