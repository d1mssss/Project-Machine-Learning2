import pandas as pd

# Baca dataset Customer ID
df = pd.read_excel('dataset/datasets_Customer_ID.xlsx')

print("=== INFORMASI DATASET CUSTOMER ID ===")
print(f"Total Customer ID: {len(df)}")
print(f"Kolom: {df.columns.tolist()}")
print(f"Tipe data: {df.dtypes.tolist()}")

print("\n=== SAMPLE CUSTOMER ID ===")
sample_ids = df.head(10)['Customer_ID'].tolist()
for i, customer_id in enumerate(sample_ids, 1):
    print(f"{i:2d}. {customer_id}")

print(f"\n=== STATISTIK ===")
print(f"Customer ID unik: {df['Customer_ID'].nunique()}")
print(f"Ada duplikat: {'Ya' if df['Customer_ID'].duplicated().any() else 'Tidak'}")
