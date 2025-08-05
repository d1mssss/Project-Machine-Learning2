import streamlit as st
import joblib
import os
import pandas as pd

# 1. Load semua model (dengan cache biar efisien)
@st.cache_resource
def load_models():
    models = {}
    for i in range(1, 6):
        path = f"model/model_pertanyaan_{i}.pkl"
        if os.path.exists(path):
            models[i] = joblib.load(path)
    return models

models = load_models()

# 2. Konfigurasi UI
st.set_page_config(page_title="Chat Prediksi Pertanyaan CS", layout="centered")
st.title("💬 Prediksi Bertahap Pertanyaan CS")


# 3. Inisialisasi sesi
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "step" not in st.session_state:
    st.session_state.step = 1

# 4. Fungsi prediksi berdasarkan step
def generate_pertanyaan(chat_history, jawaban_baru, step):
    # Gabungkan semua history menjadi 1 input konteks
    all_input = " ".join([item["text"] for item in chat_history if item["role"] == "pelanggan"])
    context = f"bisa dihubungi {all_input} {jawaban_baru} bersedia bayar"
    
    model = models.get(step)
    if model:
        pred = model.predict([context])[0]
        return pred
    else:
        return "Terima kasih atas jawabannya."

# 5. Tampilkan riwayat percakapan
for chat in st.session_state.chat_history:
    if chat["role"] == "cs":
        st.markdown(f"**👩‍💼 CS:** {chat['text']}")
    else:
        st.markdown(f"**🧑 Pelanggan:** {chat['text']}")

# 6. Input user
jawaban = st.text_input("✍️ Masukkan jawaban pelanggan")

# 7. Tombol kirim
if st.button("Kirim Jawaban"):
    if jawaban.strip() == "":
        st.warning("Jawaban tidak boleh kosong.")
    else:
        st.session_state.chat_history.append({"role": "pelanggan", "text": jawaban})

        if st.session_state.step <= 5:
            next_pertanyaan = generate_pertanyaan(st.session_state.chat_history, jawaban, st.session_state.step)
            st.session_state.chat_history.append({"role": "cs", "text": next_pertanyaan})
            st.session_state.step += 1
        else:
            st.session_state.chat_history.append({"role": "cs", "text": "Terima kasih atas jawabannya."})

        st.rerun()


#tombol input
def simpan_ke_excel(chat_history, filename="dataset/riwayat_chat.xlsx"):
    # Buat DataFrame dari chat
    data = []
    for i in range(0, len(chat_history), 2):  # anggap selalu 1 jawaban pelanggan -> 1 respon CS
        pelanggan = chat_history[i]["text"] if chat_history[i]["role"] == "pelanggan" else ""
        cs = chat_history[i+1]["text"] if i+1 < len(chat_history) and chat_history[i+1]["role"] == "cs" else ""
        data.append({"Jawaban Pelanggan": pelanggan, "Pertanyaan CS": cs})

    df = pd.DataFrame(data)

    # Jika file sudah ada → append
    if os.path.exists(filename):
        df_lama = pd.read_excel(filename)
        df_baru = pd.concat([df_lama, df], ignore_index=True)
    else:
        df_baru = df

    df_baru.to_excel(filename, index=False)
    return filename

if st.button("💾 Simpan ke Excel"):
    file_excel = simpan_ke_excel(st.session_state.chat_history)
    st.success(f"Riwayat percakapan berhasil disimpan ke file: `{file_excel}`")


# 8. Tombol reset
if st.button("🔁 Reset Percakapan"):
    st.session_state.chat_history = []
    st.session_state.step = 1
    st.success("Percakapan telah direset.")
    st.rerun()

# 9. Info
st.markdown("---")
st.caption("🤖 Sistem prediksi pertanyaan ini menggunakan beberapa model machine learning terpisah berdasarkan langkah pertanyaan.")


