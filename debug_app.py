import streamlit as st
import pandas as pd

# Debug version of app.py to identify the issue

st.title("🔍 DEBUG - Simulasi CS ICONNET")
st.markdown("Mari kita cek apa yang terjadi dengan dataset...")

# Load dataset
try:
    df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")
    if 'Pertanyaan_CS.0' in df.columns:
        df = df.rename(columns={
            'Pertanyaan_CS.0': 'Pertanyaan_CS',
            'Jawaban_Pelanggan.0': 'Jawaban_Pelanggan'
        })
    
    st.success(f"✅ Dataset berhasil dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")
    
    # Show columns
    st.subheader("📋 Kolom yang tersedia:")
    st.write(df.columns.tolist())
    
    # Check Mode column
    st.subheader("🔍 Cek Kolom 'Mode':")
    if 'Mode' in df.columns:
        st.success("✅ Kolom 'Mode' ditemukan!")
        mode_values = df['Mode'].dropna().unique()
        st.write("Nilai unik dalam kolom Mode:")
        st.write(mode_values)
        
        # Show value counts
        st.write("Distribusi data per mode:")
        st.write(df['Mode'].value_counts())
        
        # Test filtering
        st.subheader("🧪 Test Filter per Mode:")
        for mode in mode_values:
            filtered = df[df['Mode'] == mode]
            st.write(f"Mode '{mode}': {len(filtered)} baris")
            if len(filtered) > 0 and 'Pertanyaan_CS' in filtered.columns:
                unique_questions = filtered['Pertanyaan_CS'].dropna().nunique()
                st.write(f"  → Pertanyaan unik: {unique_questions}")
            else:
                st.error(f"  → Tidak ada data atau kolom 'Pertanyaan_CS' tidak ada")
    else:
        st.error("❌ Kolom 'Mode' TIDAK ditemukan!")
        # Look for similar columns
        mode_like = [col for col in df.columns if 'mode' in col.lower()]
        if mode_like:
            st.write(f"Kolom yang mirip 'mode': {mode_like}")
    
    # Check Pertanyaan_CS column
    st.subheader("🔍 Cek Kolom 'Pertanyaan_CS':")
    if 'Pertanyaan_CS' in df.columns:
        st.success("✅ Kolom 'Pertanyaan_CS' ditemukan!")
        total_questions = df['Pertanyaan_CS'].dropna().nunique()
        st.write(f"Total pertanyaan unik: {total_questions}")
        
        # Show sample questions
        sample_q = df['Pertanyaan_CS'].dropna().unique()[:5]
        st.write("Sample pertanyaan:")
        for i, q in enumerate(sample_q, 1):
            st.write(f"{i}. {q}")
    else:
        st.error("❌ Kolom 'Pertanyaan_CS' TIDAK ditemukan!")
        cs_like = [col for col in df.columns if 'pertanyaan' in col.lower() or 'cs' in col.lower()]
        if cs_like:
            st.write(f"Kolom yang mirip: {cs_like}")
    
    # Show sample data
    st.subheader("📊 Sample Data (5 baris pertama):")
    st.dataframe(df.head())
    
except Exception as e:
    st.error(f"❌ Error loading dataset: {e}")
    st.write("Pastikan file 'dataset/dataset_filled_status_promo.xlsx' ada dan bisa dibaca.")
