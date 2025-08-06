import streamlit as st
import joblib
import pandas as pd

# Load model
model_status = joblib.load('model/model_status.pkl')
model_promo = joblib.load('model/model_promo.pkl')

# Load dataset
df = pd.read_excel("dataset/dataset_gabungan_600_baris.xlsx")

# Ambil kolom pertanyaan dan jawaban
pertanyaan_cols = [col for col in df.columns if col.startswith("Pertanyaan_CS")]
jawaban_cols = [col for col in df.columns if col.startswith("Jawaban_Pelanggan")]

# Kata kunci yang menghentikan simulasi
STOP_KEYWORDS = ["rejected", "nomor tidak aktif", "nomor salah", "tidak bisa dihubungi"]

# Konfigurasi tampilan
st.set_page_config(page_title="Simulasi CS ICONNET", page_icon="🤖")
st.title("🤖 Simulasi Dinamis ICONNET")

# Inisialisasi session state
if "jawaban_user" not in st.session_state:
    st.session_state.jawaban_user = []
if "current_level" not in st.session_state:
    st.session_state.current_level = 0
if "trigger_next" not in st.session_state:
    st.session_state.trigger_next = False
if "status_stopped" not in st.session_state:
    st.session_state.status_stopped = False
if "selected_pertanyaan" not in st.session_state:
    st.session_state.selected_pertanyaan = []

# Menentukan 4 pertanyaan teratas berdasarkan kemunculan
all_pertanyaan = pd.concat([df[col].dropna() for col in pertanyaan_cols], ignore_index=True)
most_common_questions = all_pertanyaan.value_counts().nlargest(4).index.tolist()

# Pilih 1 dari 4 pertanyaan untuk memulai simulasi
if not st.session_state.selected_pertanyaan:
    st.markdown("### Pilih Pertanyaan Awal")
    for i, q in enumerate(most_common_questions):
        if st.button(q, key=f"start_{i}"):
            st.session_state.selected_pertanyaan = [q]
            st.session_state.jawaban_user = []
            st.session_state.current_level = 0
            st.session_state.trigger_next = False
            st.session_state.status_stopped = False
            st.rerun()
else:
    # Filter baris berdasarkan pertanyaan yang dipilih
    filtered_df = df.copy()
    filtered_df = filtered_df[
        filtered_df[pertanyaan_cols[0]] == st.session_state.selected_pertanyaan[0]
    ]

    # Tambahkan filter berdasarkan jawaban sebelumnya
    for i, jawaban in enumerate(st.session_state.jawaban_user):
        if i < len(jawaban_cols):
            filtered_df = filtered_df[filtered_df[jawaban_cols[i]] == jawaban]

    # Jalankan pertanyaan berikutnya
    level = st.session_state.current_level
    if (
        level < len(pertanyaan_cols)
        and not filtered_df.empty
        and pd.notna(filtered_df.iloc[0][pertanyaan_cols[level]])
    ):
        pertanyaan = filtered_df.iloc[0][pertanyaan_cols[level]]
        current_jawaban_col = jawaban_cols[level] if level < len(jawaban_cols) else None

        if current_jawaban_col and current_jawaban_col in filtered_df.columns:
            jawaban_options = filtered_df[current_jawaban_col].dropna().unique().tolist()
        else:
            jawaban_options = []

        if jawaban_options:
            jawaban = st.selectbox(f"{level+1}. {pertanyaan}", jawaban_options, key=f"jawaban_{level}")
            if st.button("Lanjut", key=f"btn_{level}"):
                st.session_state.jawaban_user.append(jawaban)

                if any(stop in jawaban.lower() for stop in STOP_KEYWORDS):
                    st.session_state.status_stopped = True
                    st.session_state.current_level = len(pertanyaan_cols)
                else:
                    st.session_state.current_level += 1
                    st.session_state.trigger_next = True
        else:
            jawaban = st.text_input(f"{level+1}. {pertanyaan} (jawaban manual)", key=f"manual_jawaban_{level}")
            if st.button("Lanjut", key=f"btn_manual_{level}") and jawaban.strip():
                st.session_state.jawaban_user.append(jawaban.strip())

                if any(stop in jawaban.lower() for stop in STOP_KEYWORDS):
                    st.session_state.status_stopped = True
                    st.session_state.current_level = len(pertanyaan_cols)
                else:
                    st.session_state.current_level += 1
                    st.session_state.trigger_next = True

    # Rerun jika perlu
    if st.session_state.trigger_next:
        st.session_state.trigger_next = False
        st.rerun()

    # Jika selesai atau tidak ada data cocok, atau pertanyaan kosong
    if (
        st.session_state.current_level >= len(pertanyaan_cols)
        or filtered_df.empty
        or (level < len(pertanyaan_cols) and not pd.notna(filtered_df.iloc[0][pertanyaan_cols[level]]))
    ):
        fitur_user = ' '.join(st.session_state.jawaban_user).strip()

        st.markdown("---")
        if not fitur_user:
            st.warning("⚠️ Tidak ada data jawaban yang bisa diproses.")
        elif st.session_state.status_stopped:
            st.error("❌ Simulasi dihentikan karena pelanggan tidak dapat dihubungi atau nomor tidak valid.")
            st.write("**Status:** Tidak diproses")
            st.write("**Jenis Promo:** Tidak tersedia")
        else:
            st.write("Jawaban pengguna:", st.session_state.jawaban_user)
            st.write("Fitur untuk prediksi:", fitur_user)

            status_pred = model_status.predict([fitur_user])[0]
            promo_pred = model_promo.predict([fitur_user])[0]

            st.success("✅ **Hasil Prediksi**")
            st.write(f"**Status Pelanggan:** {status_pred}")
            st.write(f"**Jenis Promo:** {promo_pred}")

        if st.button("🔁 Ulangi Simulasi"):
            st.session_state.jawaban_user = []
            st.session_state.current_level = 0
            st.session_state.trigger_next = False
            st.session_state.status_stopped = False
            st.session_state.selected_pertanyaan = []
            st.rerun()
