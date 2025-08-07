import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np

# Konfigurasi halaman
st.set_page_config(page_title="Simulasi CS ICONNET", page_icon="📞", layout="wide")

# === Cek dan Buat Folder ===
os.makedirs("model", exist_ok=True)
os.makedirs("dataset", exist_ok=True)

# === Placeholder Model jika gagal load ===
class FakeModel:
    def predict(self, data):
        return ["(model tidak ditemukan)"]

class FakeVectorizer:
    def transform(self, data):
        return np.zeros((len(data), 1))

# === Load Model dan Data ===
@st.cache_resource
def load_models():
    try:
        vectorizer = joblib.load("model/vectorizer.pkl")
    except:
        vectorizer = FakeVectorizer()
        st.warning("vectorizer.pkl tidak ditemukan.")

    try:
        model_status = joblib.load("model/model_status.pkl")
    except:
        model_status = FakeModel()
        st.warning("model_status.pkl tidak ditemukan.")

    try:
        model_promo = joblib.load("model/model_promo.pkl")
    except:
        model_promo = FakeModel()
        st.warning("model_promo.pkl tidak ditemukan.")

    try:
        model_mode = joblib.load("model/model_mode.pkl")
    except:
        model_mode = FakeModel()
        st.warning("model_mode.pkl tidak ditemukan.")

    return vectorizer, model_status, model_promo, model_mode

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")

        # Rename jika kolom masih format .0, .1, .2, dst
        if 'Pertanyaan_CS.0' in df.columns and 'Pertanyaan_CS_1' not in df.columns:
            # Deteksi semua kolom pertanyaan dan jawaban secara dinamis
            pertanyaan_cols = [col for col in df.columns if col.startswith('Pertanyaan_CS.')]
            jawaban_cols = [col for col in df.columns if col.startswith('Jawaban_Pelanggan.')]
            
            # Rename pertanyaan columns
            for col in pertanyaan_cols:
                if '.' in col:
                    index = col.split('.')[-1]
                    if index.isdigit():
                        new_name = f"Pertanyaan_CS_{int(index)+1}"
                        df = df.rename(columns={col: new_name})
            
            # Rename jawaban columns  
            for col in jawaban_cols:
                if '.' in col:
                    index = col.split('.')[-1]
                    if index.isdigit():
                        new_name = f"Jawaban_Pelanggan_{int(index)+1}"
                        df = df.rename(columns={col: new_name})

        return df
    except Exception as e:
        st.error(f"❌ Gagal memuat dataset: {e}")
        return pd.DataFrame()

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

# === Load ===
vectorizer, model_status, model_promo, model_mode = load_models()
df = load_data()

# === Inisialisasi Session State ===
if "mode" not in st.session_state:
    st.session_state.mode = None
if "step" not in st.session_state:
    st.session_state.step = 1
if "pertanyaan_list" not in st.session_state:
    st.session_state.pertanyaan_list = []
if "jawaban_list" not in st.session_state:
    st.session_state.jawaban_list = []
if "dynamic_cols" not in st.session_state:
    st.session_state.dynamic_cols = None

st.title("📞 Simulasi Percakapan CS ICONNET")
st.markdown("Simulasi dinamis berdasarkan jawaban pelanggan, dengan prediksi status, promo, dan mode.")
st.divider()

# === Langkah 1: Pilih Mode ===
mode = st.selectbox("1️⃣ Pilih Mode Simulasi", ["", "Winback", "Retention", "Telecollection"])
if mode:
    st.session_state.mode = mode
    filtered_df = df[df['Mode'] == mode]

    if filtered_df.empty:
        st.warning(f"Tidak ada data untuk Mode: {mode}")
        st.stop()

    # === Deteksi kolom secara dinamis ===
    pertanyaan_cols, jawaban_cols = get_dynamic_columns(df)
    st.session_state.dynamic_cols = (pertanyaan_cols, jawaban_cols)
    
    # Fungsi untuk mendapatkan jawaban yang sesuai dengan pertanyaan dan mode
    def get_relevant_answers(df, mode, step, pertanyaan_terpilih=None, jawaban_sebelumnya=None):
        """Mendapatkan 4 jawaban yang paling relevan untuk pertanyaan dan konteks saat ini"""
        
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
            
            return top_answers
        
        return []

    # === Dinamis: Tentukan max_step berdasarkan kolom yang tersedia ===
    max_step = len(pertanyaan_cols)
    
    # === Tampilkan informasi dataset ===
    st.subheader(f"📈 Progress Percakapan: Langkah {st.session_state.step}")
    progress_bar = st.progress(st.session_state.step / max_step if max_step > 0 else 1)
    st.write(f"Langkah {st.session_state.step} dari {max_step} kolom tersedia")
    
    # === Info Mode dan kolom yang ditemukan ===
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🎯 Mode: **{mode}** | Data: **{len(filtered_df)}** skenario")
    with col2:
        st.info(f"📊 Kolom: **{len(pertanyaan_cols)}** Pertanyaan, **{len(jawaban_cols)}** Jawaban")
    
    # Tampilkan detail kolom yang ditemukan
    if st.checkbox("🔍 Tampilkan Detail Kolom"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Kolom Pertanyaan:**")
            for idx, col_name in pertanyaan_cols:
                non_empty = len(df[col_name].dropna())
                st.write(f"  {idx}. `{col_name}` ({non_empty} data)")
        with col2:
            st.write("**Kolom Jawaban:**")
            for idx, col_name in jawaban_cols:
                unique_answers = len(df[col_name].dropna().unique())
                st.write(f"  {idx}. `{col_name}` ({unique_answers} jawaban unik)")
    
    # === Langkah 2: Alur Simulasi Berdasarkan Step ===

    for step in range(1, st.session_state.step + 1):
        # Dapatkan kolom yang sesuai untuk step ini
        if step <= len(pertanyaan_cols):
            step_index = step - 1  # Convert to 0-based index
            _, pertanyaan_col = pertanyaan_cols[step_index]
            
            # Cari kolom jawaban yang sesuai
            jawaban_col = None
            for j_idx, j_col in jawaban_cols:
                if j_idx == step:
                    jawaban_col = j_col
                    break
        else:
            # Jika step melebihi kolom yang tersedia
            st.info(f"💬 Percakapan selesai - tidak ada kolom untuk langkah {step}")
            break

        if step == 1:
            # Pertanyaan pertama berdasarkan Mode yang dipilih
            if pertanyaan_col in filtered_df.columns:
                pertanyaan_unik = filtered_df[pertanyaan_col].dropna().unique().tolist()
                pertanyaan_terpilih = pertanyaan_unik[0] if pertanyaan_unik else None
                
                # Debug info untuk memastikan filter mode bekerja
                if len(pertanyaan_unik) > 1:
                    st.info(f"🔍 Ditemukan {len(pertanyaan_unik)} variasi pertanyaan untuk mode '{mode}'")
            else:
                pertanyaan_terpilih = None
                st.warning(f"Kolom {pertanyaan_col} tidak ditemukan dalam dataset")
        else:
            # Filter berdasarkan mode DAN jawaban sebelumnya
            if len(st.session_state.jawaban_list) >= step - 1:
                jawaban_sebelumnya = st.session_state.jawaban_list[step - 2]
                
                # Dapatkan kolom jawaban sebelumnya
                prev_jawaban_col = None
                for j_idx, j_col in jawaban_cols:
                    if j_idx == step - 1:
                        prev_jawaban_col = j_col
                        break
                
                if prev_jawaban_col:
                    # Filter: Mode + Jawaban sebelumnya
                    filter_df = filtered_df[filtered_df[prev_jawaban_col] == jawaban_sebelumnya]
                    
                    if pertanyaan_col in filter_df.columns:
                        pertanyaan_tersedia = filter_df[pertanyaan_col].dropna().unique()
                        pertanyaan_terpilih = pertanyaan_tersedia[0] if len(pertanyaan_tersedia) > 0 else None
                        
                        # Debug info
                        if len(pertanyaan_tersedia) > 1:
                            st.info(f"🔍 Ditemukan {len(pertanyaan_tersedia)} variasi pertanyaan untuk mode '{mode}' dengan jawaban sebelumnya: '{jawaban_sebelumnya}'")
                        elif len(pertanyaan_tersedia) == 0:
                            st.warning(f"Tidak ada pertanyaan lanjutan untuk mode '{mode}' dengan jawaban: '{jawaban_sebelumnya}'")
                    else:
                        pertanyaan_terpilih = None
                        st.warning(f"Kolom {pertanyaan_col} tidak ditemukan")
                else:
                    pertanyaan_terpilih = None
                    st.warning(f"Kolom jawaban sebelumnya tidak ditemukan untuk step {step-1}")
            else:
                pertanyaan_terpilih = None

        # Jika tidak ada pertanyaan lagi, hentikan percakapan
        if pertanyaan_terpilih is None or pertanyaan_terpilih == "(tidak ditemukan)":
            st.info(f"💬 Percakapan selesai di langkah {step-1}")
            break
            
        # Pastikan list pertanyaan tidak duplikat
        if len(st.session_state.pertanyaan_list) < step:
            st.session_state.pertanyaan_list.append(pertanyaan_terpilih)
        
        # Auto-scroll ke pertanyaan saat ini dengan container yang bersih
        pertanyaan_container = st.container()
        with pertanyaan_container:
            st.subheader(f"📞 Pertanyaan {step} (Mode: {mode}):")
            st.info(pertanyaan_terpilih)
            
            # Auto-scroll JavaScript untuk fokus ke pertanyaan ini
            st.markdown(f"""
            <script>
                setTimeout(function() {{
                    var element = document.querySelector('[data-testid="stContainer"]');
                    if (element) {{
                        element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }}, 100);
            </script>
            """, unsafe_allow_html=True)

        # Dapatkan jawaban yang relevan untuk pertanyaan ini
        if step == 1:
            jawaban_relevan = get_relevant_answers(df, mode, step, pertanyaan_terpilih)
        else:
            jawaban_sebelumnya = st.session_state.jawaban_list[step - 2] if len(st.session_state.jawaban_list) >= step - 1 else None
            jawaban_relevan = get_relevant_answers(df, mode, step, pertanyaan_terpilih, jawaban_sebelumnya)
        
        # Jika tidak ada jawaban relevan, gunakan semua jawaban dari kolom ini
        if not jawaban_relevan:
            current_jawaban_col = None
            for j_idx, j_col in jawaban_cols:
                if j_idx == step:
                    current_jawaban_col = j_col
                    break
            
            if current_jawaban_col and current_jawaban_col in df.columns:
                jawaban_relevan = df[current_jawaban_col].dropna().unique().tolist()[:4]

        col1, col2 = st.columns(2)
        with col1:
            if jawaban_relevan:
                st.write(f"💡 **{len(jawaban_relevan)} Jawaban Tersedia untuk Konteks Ini:**")
                jawaban_dropdown = st.selectbox(
                    f"Pilih Jawaban untuk Pertanyaan {step}", 
                    [""] + jawaban_relevan, 
                    key=f"jawaban_select_{step}",
                    help=f"Jawaban yang relevan untuk mode '{mode}' dan konteks percakapan saat ini"
                )
            else:
                st.warning("Tidak ada jawaban yang tersedia untuk konteks ini")
                jawaban_dropdown = st.selectbox(
                    f"Pilih Jawaban untuk Pertanyaan {step}", 
                    [""], 
                    key=f"jawaban_select_{step}"
                )
        with col2:
            jawaban_manual = st.text_input(f"Atau ketik jawaban manual:", key=f"jawaban_manual_{step}")
            
            # Tampilkan info debug jika ada jawaban relevan
            if jawaban_relevan:
                with st.expander("🔍 Info Jawaban"):
                    st.write(f"**Total jawaban ditemukan:** {len(jawaban_relevan)}")
                    for i, ans in enumerate(jawaban_relevan, 1):
                        # Hitung frekuensi jawaban ini dalam konteks saat ini
                        current_jawaban_col = None
                        for j_idx, j_col in jawaban_cols:
                            if j_idx == step:
                                current_jawaban_col = j_col
                                break
                        
                        if current_jawaban_col:
                            filter_for_count = filtered_df.copy()
                            if step > 1 and len(st.session_state.jawaban_list) >= step - 1:
                                prev_jawaban_col = None
                                for j_idx, j_col in jawaban_cols:
                                    if j_idx == step - 1:
                                        prev_jawaban_col = j_col
                                        break
                                if prev_jawaban_col:
                                    jawaban_sebelumnya = st.session_state.jawaban_list[step - 2]
                                    filter_for_count = filter_for_count[filter_for_count[prev_jawaban_col] == jawaban_sebelumnya]
                            
                            count = len(filter_for_count[filter_for_count[current_jawaban_col] == ans])
                            st.write(f"  {i}. {ans} ({count} skenario)")

        jawaban_final = jawaban_manual.strip() if jawaban_manual else jawaban_dropdown

        if jawaban_final:
            if len(st.session_state.jawaban_list) < step:
                st.session_state.jawaban_list.append(jawaban_final)

    # === Cek apakah ada pertanyaan selanjutnya ===
    next_step = st.session_state.step + 1
    ada_pertanyaan_selanjutnya = False
    
    if next_step <= max_step and len(st.session_state.jawaban_list) >= st.session_state.step:
        # Cari kolom untuk step selanjutnya
        next_pertanyaan_col = None
        next_jawaban_col = None
        
        for p_idx, p_col in pertanyaan_cols:
            if p_idx == next_step:
                next_pertanyaan_col = p_col
                break
                
        for j_idx, j_col in jawaban_cols:
            if j_idx == st.session_state.step:  # Jawaban untuk step saat ini
                next_jawaban_col = j_col
                break
        
        if next_step == 1:
            # Untuk step pertama, cek berdasarkan mode
            if next_pertanyaan_col and next_pertanyaan_col in filtered_df.columns:
                ada_pertanyaan_selanjutnya = len(filtered_df[next_pertanyaan_col].dropna()) > 0
        else:
            # Untuk step selanjutnya, cek berdasarkan mode + jawaban terakhir
            if (next_pertanyaan_col and next_jawaban_col and 
                len(st.session_state.jawaban_list) >= st.session_state.step):
                
                jawaban_terakhir = st.session_state.jawaban_list[-1]
                filter_df = filtered_df[filtered_df[next_jawaban_col] == jawaban_terakhir]
                
                if next_pertanyaan_col in filter_df.columns:
                    pertanyaan_selanjutnya = filter_df[next_pertanyaan_col].dropna().unique()
                    ada_pertanyaan_selanjutnya = len(pertanyaan_selanjutnya) > 0
                    
                    # Debug info
                    if ada_pertanyaan_selanjutnya:
                        st.success(f"✅ Tersedia {len(pertanyaan_selanjutnya)} pertanyaan lanjutan untuk mode '{mode}'")
                    else:
                        st.info(f"ℹ️ Tidak ada pertanyaan lanjutan untuk mode '{mode}' dengan jawaban: '{jawaban_terakhir}'")

    # === Tambahkan Tombol untuk Melanjutkan ===
    if ada_pertanyaan_selanjutnya and len(st.session_state.jawaban_list) >= st.session_state.step:
        if st.button("➡️ Lanjut Pertanyaan Berikutnya"):
            st.session_state.step += 1
            st.rerun()
    elif len(st.session_state.jawaban_list) >= st.session_state.step:
        st.success("✅ Simulasi Selesai. Menampilkan Prediksi...")

        # Gabungkan jawaban jadi satu fitur
        gabung_jawaban = " ".join(st.session_state.jawaban_list)
        fitur_vector = vectorizer.transform([gabung_jawaban])

        pred_status = model_status.predict(fitur_vector)[0]
        pred_promo = model_promo.predict(fitur_vector)[0]
        pred_mode = model_mode.predict(fitur_vector)[0]

        st.subheader("📊 Hasil Prediksi:")
        st.metric("Status", pred_status)
        st.metric("Promo", pred_promo)
        st.metric("Mode", pred_mode)

        # Tampilkan ringkasan percakapan
        st.subheader("📝 Ringkasan Percakapan:")
        for i, (q, a) in enumerate(zip(st.session_state.pertanyaan_list, st.session_state.jawaban_list), 1):
            with st.expander(f"Langkah {i}"):
                st.write(f"**Pertanyaan:** {q}")
                st.write(f"**Jawaban:** {a}")

        if st.button("🔁 Reset Simulasi"):
            for key in ["mode", "step", "pertanyaan_list", "jawaban_list", "dynamic_cols"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
