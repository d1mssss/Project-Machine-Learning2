import streamlit as st
import joblib
import os
import json
import numpy as np
import pandas as pd
import io
import sys
import re

# Konfigurasi halaman
st.set_page_config(page_title="Simulasi CS ICONNET", page_icon="📞", layout="wide")

# === Konfigurasi Path ===
MODEL_DIR = "model"
NEW_INTERACTIONS_FILE = "new_interactions.csv"

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
    """Memuat vectorizer, model prediksi, alur percakapan, dan daftar Customer ID."""
    assets = {}
    
    # Load Customer ID list
    try:
        assets['customer_ids'] = joblib.load(os.path.join(MODEL_DIR, "customer_ids.pkl"))
        st.success(f"✅ Berhasil memuat {len(assets['customer_ids'])} Customer ID.")
    except Exception:
        assets['customer_ids'] = set()
        st.error(f"❌ Gagal memuat daftar Customer ID. Jalankan train.py terlebih dahulu.")
    
    # Load Vectorizer
    try:
        assets['vectorizer'] = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))
    except Exception:
        assets['vectorizer'] = FakeVectorizer()
        st.warning(f"{os.path.join(MODEL_DIR, 'vectorizer.pkl')} tidak ditemukan.")
    
    # Load Models
    model_files = ['model_status.pkl', 'model_promo.pkl', 'model_mode.pkl']
    for mf in model_files:
        key = mf.split('.')[0]
        try:
            assets[key] = joblib.load(os.path.join(MODEL_DIR, mf))
        except Exception:
            assets[key] = FakePredictor()
            st.warning(f"{os.path.join(MODEL_DIR, mf)} tidak ditemukan.")

    # Load Conversation Flow
    try:
        with open(os.path.join(MODEL_DIR, "conversation_flow.json"), 'r', encoding='utf-8') as f:
            assets['flow'] = json.load(f)
    except Exception:
        assets['flow'] = {}
        st.error(f"❌ Gagal memuat alur percakapan '{os.path.join(MODEL_DIR, 'conversation_flow.json')}'. Jalankan train.py terlebih dahulu.")
        st.stop()
        
    return assets

# === Fungsi untuk menyimpan interaksi baru ===
def save_new_interaction(history, predictions, mode, customer_id):
    """Menyimpan alur percakapan baru ke file CSV."""
    try:
        # Ubah riwayat menjadi format baris tunggal seperti Excel asli
        new_row = {
            'Customer_ID': customer_id,
            'Mode': mode
        }
        for i, item in enumerate(history):
            new_row[f'Pertanyaan_CS.{i}'] = item['q']
            new_row[f'Jawaban_Pelanggan.{i}'] = item['a']
        
        # Tambahkan prediksi sebagai label
        new_row['Status'] = predictions['status']  # Sesuaikan dengan nama kolom di dataset
        new_row['Jenis_Promo'] = predictions['promo']
        new_row['Estimasi_Pembayaran'] = predictions['estimasi_pembayaran']
        
        new_df = pd.DataFrame([new_row])
        
        # Tambahkan ke file CSV, buat header jika file belum ada
        if not os.path.exists(NEW_INTERACTIONS_FILE):
            new_df.to_csv(NEW_INTERACTIONS_FILE, index=False, mode='w', header=True)
        else:
            new_df.to_csv(NEW_INTERACTIONS_FILE, index=False, mode='a', header=False)
            
        st.toast(f"💡 Interaksi baru disimpan di '{NEW_INTERACTIONS_FILE}'!", icon="💡")
    except Exception as e:
        st.error(f"Gagal menyimpan interaksi baru: {e}")

# === Fungsi untuk konversi ke Excel (untuk download) ===
@st.cache_data
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil_Simulasi')
    processed_data = output.getvalue()
    return processed_data

# === Fungsi untuk ekstraksi tanggal real-time ===
def extract_date_from_conversation(history):
    """Ekstrak tanggal langsung dari percakapan user saat prediksi - prioritas pertanyaan pembayaran."""
    
    # Pattern untuk mendeteksi tanggal dalam berbagai format (urutan penting!)
    date_patterns = [
        # Format dengan kata kunci tanggal
        r'tanggal\s+(\d{1,2}\s+[a-zA-Z]+)',         # "tanggal 14 september"
        r'tgl\s+(\d{1,2}\s+[a-zA-Z]+)',             # "tgl 14 september"  
        r'pada\s+(\d{1,2}\s+[a-zA-Z]+)',            # "pada 14 september"
        r'tanggal\s+(\d{1,2}/\d{1,2})',             # "tanggal 14/9"
        r'tanggal\s+(\d{1,2}-\d{1,2})',             # "tanggal 14-9"
        
        # Format dengan kata kunci waktu pembayaran
        r'(?:bisa|akan|mau|ingin|rencana)\s+(?:bayar|setor|transfer|lunas)\s+(?:tanggal\s+)?(\d{1,2}\s+[a-zA-Z]+)',  # "bisa bayar 15 september"
        r'(?:bisa|akan|mau|ingin|rencana)\s+(?:bayar|setor|transfer|lunas)\s+(?:tanggal\s+)?(\d{1,2}/\d{1,2})',      # "bisa bayar 15/9"
        r'(?:bayar|setor|transfer|lunas)\s+(?:tanggal\s+)?(\d{1,2}\s+[a-zA-Z]+)',                                   # "bayar 15 september"
        r'(?:bayar|setor|transfer|lunas)\s+(?:tanggal\s+)?(\d{1,2}/\d{1,2})',                                       # "bayar 15/9"
        
        # Format dengan kata kunci gaji/uang masuk
        r'(?:gaji|uang|dana|duit)\s+(?:masuk|turun|cair)\s+(?:tanggal\s+)?(\d{1,2}\s+[a-zA-Z]+)',                  # "gaji masuk 25 september"
        r'(?:gaji|uang|dana|duit)\s+(?:masuk|turun|cair)\s+(?:tanggal\s+)?(\d{1,2}/\d{1,2})',                      # "gaji masuk 25/9"
        
        # Format standalone tanggal
        r'(\d{1,2}/\d{1,2})(?:\s|$|[^\d])',         # "14/9" standalone
        r'(\d{1,2}-\d{1,2})(?:\s|$|[^\d])',         # "14-9" standalone
        r'(\d{1,2}\s+[a-zA-Z]+)',                   # "14 september" (terakhir karena paling umum)
    ]
    
    # Keywords untuk pertanyaan pembayaran (lebih lengkap)
    payment_keywords = [
        'kapan', 'bayar', 'pembayaran', 'lunas', 'setor', 'transfer', 
        'cicil', 'angsur', 'tempo', 'deadline', 'jatuh tempo', 'pelunasan',
        'gaji', 'uang', 'dana', 'duit', 'masuk', 'turun', 'cair',
        'bisa', 'akan', 'mau', 'ingin', 'rencana', 'siap'
    ]
    
    # PRIORITAS 1: Cari jawaban untuk pertanyaan pembayaran
    for item in reversed(history):  # Mulai dari yang terbaru
        pertanyaan = str(item['q']).lower()
        jawaban = str(item['a']).strip().lower()
        
        # Cek apakah pertanyaan berkaitan dengan pembayaran
        is_payment_question = any(keyword in pertanyaan for keyword in payment_keywords)
        
        if is_payment_question and jawaban:
            # Cek juga apakah jawaban mengandung kata-kata pembayaran (double check)
            payment_in_answer = any(keyword in jawaban for keyword in ['bayar', 'setor', 'transfer', 'lunas', 'gaji', 'uang'])
            
            for pattern in date_patterns:
                matches = re.findall(pattern, item['a'], re.IGNORECASE)  # Gunakan jawaban asli untuk preserve case
                if matches:
                    extracted_date = matches[0].strip()
                    # Jika ada indikasi pembayaran di jawaban, berikan prioritas tinggi
                    if payment_in_answer:
                        return f"Tanggal {extracted_date}"
                    else:
                        return f"Tanggal {extracted_date}"
    
    # PRIORITAS 2: Cari jawaban yang mengandung kata-kata pembayaran meskipun pertanyaannya tidak
    for item in reversed(history):
        jawaban = str(item['a']).strip()
        jawaban_lower = jawaban.lower()
        
        # Cek apakah jawaban mengandung kata-kata terkait pembayaran
        payment_context = any(keyword in jawaban_lower for keyword in [
            'bayar', 'setor', 'transfer', 'lunas', 'gaji', 'uang', 'dana', 'duit',
            'masuk', 'turun', 'cair', 'bisa', 'akan', 'mau', 'siap'
        ])
        
        if payment_context and jawaban:
            for pattern in date_patterns:
                matches = re.findall(pattern, jawaban, re.IGNORECASE)
                if matches:
                    extracted_date = matches[0].strip()
                    return f"Tanggal {extracted_date}"
    
    # PRIORITAS 3: Cari di semua jawaban sebagai fallback
    for item in reversed(history):  # Mulai dari jawaban terakhir
        jawaban = str(item['a']).strip()
        if jawaban:
            for pattern in date_patterns:
                matches = re.findall(pattern, jawaban, re.IGNORECASE)
                if matches:
                    # Kembalikan tanggal pertama yang ditemukan dari jawaban terbaru
                    extracted_date = matches[0].strip()
                    return f"Tanggal {extracted_date}"
    
    return None

# === Fungsi untuk mendapatkan status auto training ===
def get_auto_training_status():
    """Mendapatkan status smart auto training"""
    try:
        from datetime import datetime, timedelta
        
        status = {
            "new_interactions": 0,
            "last_training": None,
            "next_training": None,
            "auto_trainer_running": False,
            "data_changed": False,
            "needs_training": False
        }
        
        # Cek jumlah interaksi baru
        if os.path.exists(NEW_INTERACTIONS_FILE):
            new_df = pd.read_csv(NEW_INTERACTIONS_FILE)
            status["new_interactions"] = len(new_df)
        
        # Cek training terakhir
        if os.path.exists("last_auto_train.txt"):
            with open("last_auto_train.txt", 'r') as f:
                last_train = datetime.fromisoformat(f.read().strip())
                status["last_training"] = last_train
                status["next_training"] = last_train + timedelta(hours=24)
        
        # Cek apakah auto trainer sedang berjalan
        if os.path.exists("auto_train_log.txt"):
            status["auto_trainer_running"] = True
        
        # Cek apakah data berubah (menggunakan hash)
        try:
            # Hitung hash data saat ini
            df = pd.read_excel("dataset/dataset_filled_status_promo.xlsx")
            import hashlib
            current_hash = hashlib.md5(df.to_string().encode()).hexdigest()
            
            # Bandingkan dengan hash terakhir
            if os.path.exists("data_hash.txt"):
                with open("data_hash.txt", 'r') as f:
                    last_hash = f.read().strip()
                status["data_changed"] = (current_hash != last_hash)
            else:
                status["data_changed"] = True  # Belum pernah training
                
        except Exception:
            pass
        
        # Tentukan apakah perlu training
        MIN_NEW_INTERACTIONS = 3
        status["needs_training"] = (
            status["new_interactions"] >= MIN_NEW_INTERACTIONS or 
            status["data_changed"]
        )
            
        return status
    except Exception:
        return None

# === Inisialisasi Aplikasi ===
assets = load_assets()
st.title("📞 Simulasi CS ICONNET (v2)")
st.markdown("Sekarang dengan input manual untuk melatih ulang model di masa depan.")

# === Sidebar untuk Status Auto Training ===
with st.sidebar:
    st.header("🤖 Smart Auto Training Status")
    
    training_status = get_auto_training_status()
    if training_status:
        # Status auto trainer
        if training_status["auto_trainer_running"]:
            st.success("✅ Smart Auto Trainer: Aktif")
        else:
            st.error("❌ Smart Auto Trainer: Tidak Aktif")
        
        # Data metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Interaksi Baru", training_status["new_interactions"])
        with col2:
            if training_status["data_changed"]:
                st.metric("Dataset", "Changed 📊")
            else:
                st.metric("Dataset", "Unchanged ✅")
        
        # Status kebutuhan training
        if training_status["needs_training"]:
            st.warning("🚨 PERLU TRAINING")
        else:
            st.success("✅ Model Up-to-date")
            
        # Training timestamps
        if training_status["last_training"]:
            st.write(f"**Training Terakhir:**")
            st.write(training_status["last_training"].strftime("%d/%m/%Y %H:%M"))
            
            st.write(f"**Training Berikutnya:**")
            st.write(training_status["next_training"].strftime("%d/%m/%Y %H:%M"))
            
            # Hitung countdown
            from datetime import datetime
            now = datetime.now()
            if training_status["next_training"] > now:
                time_left = training_status["next_training"] - now
                hours_left = int(time_left.total_seconds() // 3600)
                minutes_left = int((time_left.total_seconds() % 3600) // 60)
                st.info(f"⏰ {hours_left}h {minutes_left}m lagi")
            else:
                st.warning("⚠️ Training terlambat")
        else:
            st.info("Belum ada training otomatis")
            
        # Tombol untuk memulai training manual
        if st.button("🚀 Training Manual"):
            with st.spinner("Memproses smart training..."):
                try:
                    import subprocess
                    result = subprocess.run([
                        sys.executable, "train.py"
                    ], capture_output=True, text=True, cwd=os.getcwd())
                    
                    if result.returncode == 0:
                        st.success("✅ Training manual berhasil!")
                        st.rerun()
                    else:
                        st.error(f"❌ Training gagal: {result.stderr}")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.warning("Status tidak tersedia")
    
    # Link untuk menjalankan smart auto trainer
    st.markdown("---")
    st.markdown("**Untuk menjalankan Smart Auto Trainer:**")
    st.code("python smart_auto_trainer.py")
    st.caption("Training otomatis hanya jika ada data baru")
    
    # Log auto training
    if st.checkbox("📋 Tampilkan Log"):
        if os.path.exists("auto_train_log.txt"):
            with open("auto_train_log.txt", 'r', encoding='utf-8') as f:
                logs = f.read()
            st.text_area("Smart Training Log", logs, height=200)
        else:
            st.info("Belum ada log tersedia")

# Inisialisasi session state
if 'step' not in st.session_state:
    st.session_state.step = 0  # 0: Input Customer ID, 1: Pilih Mode, 2+: Percakapan
    st.session_state.customer_id = ""
    st.session_state.history = []
    st.session_state.current_node = {}
    st.session_state.selected_mode = None
    st.session_state.has_manual_input = False
    st.session_state.predictions = {}  # Tambah session state untuk predictions

def reset_simulation():
    """Mengembalikan session state ke awal."""
    st.session_state.step = 0
    st.session_state.customer_id = ""
    st.session_state.history = []
    st.session_state.current_node = {}
    st.session_state.selected_mode = None
    st.session_state.has_manual_input = False
    st.session_state.predictions = {}  # Reset predictions
    st.rerun()

# === Tampilan Utama ===
if st.session_state.step == 0:
    # Step 0: Input dan Validasi Customer ID
    st.subheader("🔐 Input Customer ID")
    st.info("Masukkan Customer ID Anda untuk memulai simulasi")
    
    customer_id_input = st.text_input(
        "Customer ID:",
        value="",
        placeholder="Contoh: 151200113338",
        key="customer_id_input"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Validasi Customer ID", disabled=(not customer_id_input.strip())):
            customer_id = customer_id_input.strip()
            
            if customer_id in assets['customer_ids']:
                st.session_state.customer_id = customer_id
                st.session_state.step = 1
                st.success(f"✅ Customer ID '{customer_id}' valid! Silahkan pilih mode simulasi.")
                st.rerun()
            else:
                st.error(f"❌ Customer ID '{customer_id}' tidak ditemukan dalam database!")
                st.info("💡 Pastikan Customer ID sudah benar.")
    
    with col2:
        if st.button("📋 Contoh Customer ID"):
            if assets['customer_ids']:
                sample_ids = list(assets['customer_ids'])[:5]
                st.info("Contoh Customer ID yang valid:")
                for i, cid in enumerate(sample_ids, 1):
                    st.code(f"{i}. {cid}")
            else:
                st.warning("Tidak ada Customer ID yang dimuat.")

elif st.session_state.step == 1:
    # Step 1: Pilih Mode Simulasi (setelah Customer ID valid)
    st.success(f"🎯 Customer ID: **{st.session_state.customer_id}**")
    
    st.session_state.selected_mode = st.selectbox(
        "1️⃣ Pilih Mode Simulasi", 
        [""] + list(assets['flow'].keys())
    )
    if st.session_state.selected_mode:
        if st.button("Mulai Simulasi"):
            st.session_state.step = 2
            st.session_state.current_node = assets['flow'].get(st.session_state.selected_mode, {})
            st.rerun()
else:
    # Step 2+: Simulasi Percakapan (step >= 2)
    st.success(f"🎯 Customer ID: **{st.session_state.customer_id}** | Mode: **{st.session_state.selected_mode}** | Langkah: **{st.session_state.step - 1}**")
    
    if st.session_state.history:
        with st.expander("📖 Riwayat Percakapan"):
            for i, item in enumerate(st.session_state.history):
                st.markdown(f"**Q{i+1}:** `{item['q']}`")
                st.markdown(f"**A{i+1}:** `{item['a']}`")
                st.divider()

    current_node = st.session_state.current_node
    
    if isinstance(current_node, dict) and current_node:
        pertanyaan_saat_ini = list(current_node.keys())[0]
        
        st.subheader(f"📞 Pertanyaan {st.session_state.step - 1}:")
        st.info(pertanyaan_saat_ini)
        
        opsi_jawaban = list(current_node[pertanyaan_saat_ini].keys())
        
        # --- Input Ganda (Dropdown + Manual) ---
        col1, col2 = st.columns(2)
        with col1:
            jawaban_dropdown = st.selectbox(
                "Pilih dari jawaban yang ada:",
                [""] + opsi_jawaban,
                key=f"select_{st.session_state.step}"
            )
        with col2:
            jawaban_manual = st.text_input(
                "Atau ketik jawaban baru di sini:",
                key=f"manual_{st.session_state.step}"
            )
            
        # Prioritaskan jawaban manual
        jawaban_final = jawaban_manual.strip() if jawaban_manual.strip() else jawaban_dropdown

        if st.button("Jawab & Lanjutkan", key=f"submit_{st.session_state.step}", disabled=(not jawaban_final)):
            if jawaban_manual.strip():
                st.session_state.has_manual_input = True # Tandai bahwa ada input manual

            st.session_state.history.append({'q': pertanyaan_saat_ini, 'a': jawaban_final})
            
            # PERBAIKAN: Percakapan tetap berlanjut walaupun ada input manual
            if jawaban_final in opsi_jawaban:
                # Jika dari dropdown, ambil node selanjutnya sesuai alur
                next_node = current_node[pertanyaan_saat_ini][jawaban_final]
                st.session_state.current_node = next_node
            else:
                # Jika jawaban manual, cari jawaban terdekat untuk melanjutkan alur
                # atau gunakan jawaban pertama sebagai fallback
                if opsi_jawaban:
                    # Gunakan jawaban pertama sebagai fallback untuk melanjutkan alur
                    fallback_jawaban = opsi_jawaban[0]
                    next_node = current_node[pertanyaan_saat_ini][fallback_jawaban]
                    st.session_state.current_node = next_node
                    st.info(f"💡 Jawaban manual disimpan. Melanjutkan alur menggunakan: '{fallback_jawaban}'")
                else:
                    st.session_state.current_node = {} # Akhir percakapan jika tidak ada opsi

            st.session_state.step += 1
            st.rerun()
    else:
        st.success("✅ Simulasi Selesai!")
        st.subheader("📊 Hasil Percakapan dan Prediksi")
        
        # Lakukan prediksi hanya jika belum ada atau perlu update
        if not st.session_state.predictions:
            full_conversation_text = " ".join([f"{item['q']} {item['a']}" for item in st.session_state.history])
            vectorized_text = assets['vectorizer'].transform([full_conversation_text])
            
            pred_status = assets['model_status'].predict(vectorized_text)[0]
            pred_promo = assets['model_promo'].predict(vectorized_text)[0]
            
            # PERBAIKAN: HANYA gunakan ekstraksi real-time, TIDAK pakai model estimasi pembayaran
            extracted_date = extract_date_from_conversation(st.session_state.history)
            
            if extracted_date:
                # Jika ada tanggal yang disebutkan user, gunakan itu
                pred_estimasi_pembayaran = extracted_date
                st.success(f"📅 Tanggal pembayaran diekstrak langsung: **{extracted_date}**")
            else:
                # Jika tidak ada tanggal, beri informasi bahwa tidak ada tanggal yang disebutkan
                pred_estimasi_pembayaran = "Belum disebutkan tanggal pembayaran"
                st.warning("⚠️ Tidak ada tanggal pembayaran yang disebutkan dalam percakapan")
            
            # Simpan ke session state
            st.session_state.predictions = {
                'status': pred_status, 
                'promo': pred_promo, 
                'estimasi_pembayaran': pred_estimasi_pembayaran
            }
        
        # Gunakan predictions dari session state
        predictions = st.session_state.predictions
        
        # Tampilkan hasil prediksi dengan format khusus untuk tanggal
        st.subheader("📊 Hasil Prediksi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", predictions['status'])
        
        with col2:
            st.metric("Jenis Promo", predictions['promo'])
        
        with col3:
            estimasi = predictions['estimasi_pembayaran']
            if "Tanggal" in str(estimasi):
                st.metric("📅 Estimasi Pembayaran", estimasi)
                # Tambahkan highlight untuk tanggal
                st.info(f"🗓️ Pembayaran dijadwalkan: **{estimasi}**")
            elif "Belum disebutkan" in str(estimasi):
                st.metric("⚠️ Estimasi Pembayaran", estimasi)
                st.warning("💡 Silahkan input tanggal pembayaran secara manual di bawah")
            else:
                st.metric("💰 Estimasi Pembayaran", f"Rp {estimasi:,}" if str(estimasi).isdigit() else estimasi)
        
        # === FITUR EDIT MANUAL ESTIMASI PEMBAYARAN ===
        st.subheader("✏️ Edit Manual Estimasi Pembayaran")
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            estimasi_manual = st.text_input(
                "Ubah estimasi pembayaran (opsional):",
                value="",
                placeholder="Contoh: Tanggal 15 September, 500000, dll.",
                key="edit_estimasi"
            )
        
        with col_edit2:
            if st.button("💾 Update Estimasi", key="update_estimasi"):
                if estimasi_manual.strip():
                    # Update session state predictions
                    st.session_state.predictions['estimasi_pembayaran'] = estimasi_manual.strip()
                    st.success(f"✅ Estimasi pembayaran diubah menjadi: **{estimasi_manual.strip()}**")
                    st.rerun()
        
        # Update predictions dari session state (untuk memastikan perubahan manual tersimpan)
        predictions = st.session_state.predictions
        
        # Buat DataFrame dari hasil (menggunakan predictions terbaru)
        result_data = {
            'Customer_ID': st.session_state.customer_id,
            'Mode': st.session_state.selected_mode
        }
        for i, item in enumerate(st.session_state.history):
            result_data[f'Pertanyaan_CS.{i+1}'] = item['q']
            result_data[f'Jawaban_Pelanggan.{i+1}'] = item['a']
        result_data['Status'] = predictions['status']
        result_data['Jenis_Promo'] = predictions['promo']
        result_data['Estimasi_Pembayaran'] = predictions['estimasi_pembayaran']

        result_df = pd.DataFrame([result_data])
        
        # Tampilkan DataFrame lengkap
        st.subheader("📋 Detail Lengkap")
        st.dataframe(result_df)
        
        # Siapkan data Excel untuk diunduh
        excel_data = to_excel(result_df)
        
        st.download_button(
            label="📥 Download Hasil (Excel)",
            data=excel_data,
            file_name=f"hasil_simulasi_{st.session_state.customer_id}_{st.session_state.selected_mode}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Simpan jika ada input manual
        if st.session_state.has_manual_input:
            st.info("Karena Anda memberikan jawaban manual, alur percakapan ini akan disimpan untuk training selanjutnya.")
            save_new_interaction(st.session_state.history, predictions, st.session_state.selected_mode, st.session_state.customer_id)
            
    st.markdown("---")
    if st.button("🔁 Reset Simulasi"):
        reset_simulation()
