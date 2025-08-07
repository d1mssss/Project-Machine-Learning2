# app.py

import streamlit as st
import joblib
import os
import json
import numpy as np

# Konfigurasi halaman
st.set_page_config(page_title="Simulasi CS ICONNET", page_icon="📞", layout="wide")

# === Placeholder jika model/file gagal dimuat ===
class FakePredictor:
    def predict(self, data):
        return ["(model tidak ditemukan)"]

class FakeVectorizer:
    def transform(self, data):
        return np.zeros((len(data), 1))

# === Fungsi untuk memuat semua aset (model & flow) ===
@st.cache_resource
def load_assets():
    """Memuat vectorizer, model prediksi, dan alur percakapan."""
    assets = {}
    # Load Vectorizer
    try:
        assets['vectorizer'] = joblib.load("model/vectorizer.pkl")
    except Exception:
        assets['vectorizer'] = FakeVectorizer()
        st.warning("model/vectorizer.pkl tidak ditemukan.")
    
    # Load Models
    model_files = ['model_status.pkl', 'model_promo.pkl', 'model_mode.pkl']
    for mf in model_files:
        key = mf.split('.')[0] # e.g., 'model_status'
        try:
            assets[key] = joblib.load(f"model/{mf}")
        except Exception:
            assets[key] = FakePredictor()
            st.warning(f"model/{mf} tidak ditemukan.")

    # Load Conversation Flow
    try:
        with open("model/conversation_flow.json", 'r', encoding='utf-8') as f:
            assets['flow'] = json.load(f)
    except Exception:
        assets['flow'] = {}
        st.error("❌ Gagal memuat alur percakapan 'conversation_flow.json'. Jalankan train.py terlebih dahulu.")
        st.stop()
        
    return assets

# === Inisialisasi Aplikasi ===
assets = load_assets()
st.title("📞 Simulasi Percakapan CS ICONNET")
st.markdown("Simulasi ini sepenuhnya dijalankan berdasarkan model alur percakapan dan model prediksi.")

# Inisialisasi session state
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.history = [] # Menyimpan {'q': ..., 'a': ...}
    st.session_state.current_node = {}
    st.session_state.selected_mode = None

# === Fungsi untuk mereset simulasi ===
def reset_simulation():
    """Mengembalikan session state ke awal."""
    st.session_state.step = 0
    st.session_state.history = []
    st.session_state.current_node = assets['flow'].get(st.session_state.selected_mode, {})
    st.rerun()

# === Tampilan Utama ===
# Pemilihan Mode (Hanya jika belum dimulai)
if st.session_state.step == 0:
    st.session_state.selected_mode = st.selectbox(
        "1️⃣ Pilih Mode Simulasi", 
        [""] + list(assets['flow'].keys())
    )
    if st.session_state.selected_mode:
        if st.button("Mulai Simulasi"):
            st.session_state.step = 1
            st.session_state.current_node = assets['flow'].get(st.session_state.selected_mode, {})
            st.rerun()
else:
    st.info(f"🎯 Mode: **{st.session_state.selected_mode}** | Langkah: **{st.session_state.step}**")
    
    # Tampilkan riwayat percakapan
    if st.session_state.history:
        with st.expander("📖 Riwayat Percakapan"):
            for i, item in enumerate(st.session_state.history):
                st.markdown(f"**Q{i+1}:** `{item['q']}`")
                st.markdown(f"**A{i+1}:** `{item['a']}`")
                st.divider()

    # Logika Alur Percakapan
    current_node = st.session_state.current_node
    
    # Cek apakah masih ada pertanyaan di node saat ini
    if isinstance(current_node, dict) and current_node:
        # Ambil pertanyaan pertama dari node saat ini
        pertanyaan_saat_ini = list(current_node.keys())[0]
        
        st.subheader(f"📞 Pertanyaan {st.session_state.step}:")
        st.info(pertanyaan_saat_ini)
        
        # Opsi jawaban adalah keys dari level selanjutnya
        opsi_jawaban = list(current_node[pertanyaan_saat_ini].keys())
        
        jawaban_terpilih = st.radio(
            "Pilih Jawaban Pelanggan:",
            opsi_jawaban,
            key=f"answer_{st.session_state.step}"
        )

        if st.button("Jawab & Lanjutkan", key=f"submit_{st.session_state.step}"):
            # Simpan ke riwayat
            st.session_state.history.append({'q': pertanyaan_saat_ini, 'a': jawaban_terpilih})
            # Update node ke level selanjutnya
            st.session_state.current_node = current_node[pertanyaan_saat_ini][jawaban_terpilih]
            st.session_state.step += 1
            st.rerun()
    else:
        # Akhir dari percakapan
        st.success("✅ Simulasi Selesai!")
        st.subheader("📊 Hasil Prediksi Berdasarkan Keseluruhan Percakapan:")
        
        # Gabungkan seluruh histori untuk prediksi
        full_conversation_text = " ".join([f"{item['q']} {item['a']}" for item in st.session_state.history])
        
        # Vectorize teks
        vectorized_text = assets['vectorizer'].transform([full_conversation_text])
        
        # Lakukan prediksi
        pred_status = assets['model_status'].predict(vectorized_text)[0]
        pred_promo = assets['model_promo'].predict(vectorized_text)[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Prediksi Status Akhir", pred_status)
        with col2:
            st.metric("Prediksi Jenis Promo", pred_promo)
            
    # Tombol Reset selalu tersedia setelah simulasi dimulai
    st.markdown("---")
    if st.button("🔁 Reset Simulasi"):
        reset_simulation()