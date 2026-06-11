import streamlit as st
import pandas as pd
import datetime
from decimal import Decimal
import os

# --- PINDAHKAN STREAMLIT SECRETS KE ENVIRONMENT VARIABLE UNTUK PRISMA ---
# Di Streamlit Community Cloud, rahasia disimpan di st.secrets.
# Prisma membutuhkan DATABASE_URL di env variable sistem (os.environ).
if "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]


# Set page layout and config
st.set_page_config(
    page_title="ScenTab - Parfum Inventory & Price History",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF4B4B, #8A2387);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .card {
        background-color: #1E1E24;
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1f1c2c, #928dab);
        color: white;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
    }
    .badge-dummy {
        background-color: #f39c12;
        color: white;
    }
    .badge-db {
        background-color: #2ecc71;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Try loading database client
from src.database import get_db_client
db_client = get_db_client()

# Check if connection parameters are set
db_connected = False
db_error_msg = ""
if db_client is not None:
    if os.getenv("DATABASE_URL"):
        try:
            # Hubungkan ke database PostgreSQL secara langsung (synchronous)
            if not db_client.is_connected():
                db_client.connect()
            db_connected = True
        except Exception as e:
            db_error_msg = str(e)
            db_connected = False
    else:
        db_error_msg = "DATABASE_URL environment variable is not defined."

# --- SESSION STATE FOR DUMMY DATA FALLBACK ---
if 'parfum_data' not in st.session_state:
    st.session_state.parfum_data = [
        {"id": 1, "nama_parfum": "Chanel No. 5", "stok": 12, "supplier": "PT Aroma Wangi", "created_at": datetime.datetime(2026, 6, 1, 10, 0)},
        {"id": 2, "nama_parfum": "Dior Sauvage", "stok": 25, "supplier": "CV Parfum Jaya", "created_at": datetime.datetime(2026, 6, 2, 11, 30)},
        {"id": 3, "nama_parfum": "Creed Aventus", "stok": 8, "supplier": "PT Distribusi Parfum", "created_at": datetime.datetime(2026, 6, 3, 14, 15)},
    ]

if 'riwayat_harga_data' not in st.session_state:
    st.session_state.riwayat_harga_data = [
        {"id": 1, "parfum_id": 1, "harga_beli": Decimal("2450000.00"), "tanggal_update": datetime.datetime(2026, 6, 1, 10, 0)},
        {"id": 2, "parfum_id": 1, "harga_beli": Decimal("2500000.00"), "tanggal_update": datetime.datetime(2026, 6, 8, 9, 0)},
        {"id": 3, "parfum_id": 2, "harga_beli": Decimal("1850000.00"), "tanggal_update": datetime.datetime(2026, 6, 2, 11, 30)},
        {"id": 4, "parfum_id": 2, "harga_beli": Decimal("1900000.00"), "tanggal_update": datetime.datetime(2026, 6, 9, 10, 0)},
        {"id": 5, "parfum_id": 3, "harga_beli": Decimal("4200000.00"), "tanggal_update": datetime.datetime(2026, 6, 3, 14, 15)},
    ]

# Helper functions to simulate database interactions or use Prisma (once fully active)
def get_all_parfum():
    if db_connected and db_client is not None:
        try:
            parfums = db_client.parfum.find_many(order={"id": "desc"})
            data = []
            for p in parfums:
                data.append({
                    "id": p.id,
                    "nama_parfum": p.nama_parfum,
                    "stok": p.stok,
                    "supplier": p.supplier,
                    "created_at": p.created_at
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Gagal memuat data parfum dari database: {e}")
            return pd.DataFrame(st.session_state.parfum_data)
    return pd.DataFrame(st.session_state.parfum_data)

def get_all_riwayat():
    if db_connected and db_client is not None:
        try:
            riwayats = db_client.riwayatharga.find_many(include={"parfum": True}, order={"id": "desc"})
            data = []
            for r in riwayats:
                data.append({
                    "id_riwayat": r.id,
                    "parfum_id": r.parfum_id,
                    "harga_beli": r.harga_beli,
                    "tanggal_update": r.tanggal_update,
                    "nama_parfum": r.parfum.nama_parfum if r.parfum else "Unknown",
                    "supplier": r.parfum.supplier if r.parfum else "Unknown"
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Gagal memuat data riwayat harga dari database: {e}")
            
    df_riwayat = pd.DataFrame(st.session_state.riwayat_harga_data)
    df_parfum = pd.DataFrame(st.session_state.parfum_data)
    
    # Merge for display
    if not df_riwayat.empty and not df_parfum.empty:
        merged = pd.merge(df_riwayat, df_parfum, left_on="parfum_id", right_on="id", suffixes=('_riwayat', '_parfum'))
        return merged
    return df_riwayat

def add_parfum(nama, stok, supplier, harga_awal):
    if db_connected and db_client is not None:
        try:
            # 1. Simpan Parfum
            new_p = db_client.parfum.create(
                data={
                    "nama_parfum": nama,
                    "stok": int(stok),
                    "supplier": supplier
                }
            )
            # 2. Simpan Riwayat Harga awal
            db_client.riwayatharga.create(
                data={
                    "parfum_id": new_p.id,
                    "harga_beli": Decimal(str(harga_awal))
                }
            )
            return True
        except Exception as e:
            st.error(f"Gagal menyimpan parfum ke database: {e}")
            return False
            
    # Fallback dummy data
    new_id = max([p["id"] for p in st.session_state.parfum_data]) + 1 if st.session_state.parfum_data else 1
    now = datetime.datetime.now()
    st.session_state.parfum_data.append({
        "id": new_id,
        "nama_parfum": nama,
        "stok": stok,
        "supplier": supplier,
        "created_at": now
    })
    
    new_riwayat_id = max([r["id"] for r in st.session_state.riwayat_harga_data]) + 1 if st.session_state.riwayat_harga_data else 1
    st.session_state.riwayat_harga_data.append({
        "id": new_riwayat_id,
        "parfum_id": new_id,
        "harga_beli": Decimal(str(harga_awal)),
        "tanggal_update": now
    })
    return True

def update_harga(parfum_id, harga_baru):
    if db_connected and db_client is not None:
        try:
            db_client.riwayatharga.create(
                data={
                    "parfum_id": int(parfum_id),
                    "harga_beli": Decimal(str(harga_baru))
                }
            )
            return True
        except Exception as e:
            st.error(f"Gagal menyimpan harga baru ke database: {e}")
            return False
            
    # Fallback dummy data
    new_riwayat_id = max([r["id"] for r in st.session_state.riwayat_harga_data]) + 1 if st.session_state.riwayat_harga_data else 1
    now = datetime.datetime.now()
    st.session_state.riwayat_harga_data.append({
        "id": new_riwayat_id,
        "parfum_id": int(parfum_id),
        "harga_beli": Decimal(str(harga_baru)),
        "tanggal_update": now
    })
    return True

def delete_parfum(parfum_id):
    if db_connected and db_client is not None:
        try:
            # onDelete: Cascade handles removing related history records automatically
            db_client.parfum.delete(where={"id": int(parfum_id)})
            return True
        except Exception as e:
            st.error(f"Gagal menghapus data dari database: {e}")
            return False
            
    # Fallback dummy data
    st.session_state.riwayat_harga_data = [r for r in st.session_state.riwayat_harga_data if r["parfum_id"] != int(parfum_id)]
    st.session_state.parfum_data = [p for p in st.session_state.parfum_data if p["id"] != int(parfum_id)]
    return True

def check_parfum_exists(nama):
    """
    Memeriksa apakah parfum dengan nama tertentu sudah terdaftar di database/memori.
    Mengabaikan huruf besar/kecil (case-insensitive) dan spasi berlebih.
    """
    nama_clean = str(nama).strip().lower()
    if db_connected and db_client is not None:
        try:
            # Mencari data di PostgreSQL secara case-insensitive
            p = db_client.parfum.find_first(
                where={
                    "nama_parfum": {
                        "equals": nama_clean,
                        "mode": "insensitive"
                    }
                }
            )
            return p
        except Exception:
            # Fallback jika query filter case-insensitive database gagal
            try:
                parfums = db_client.parfum.find_many()
                for p in parfums:
                    if p.nama_parfum.strip().lower() == nama_clean:
                        return p
            except Exception:
                return None
            
    # Fallback dummy data
    matches = [p for p in st.session_state.parfum_data if p["nama_parfum"].strip().lower() == nama_clean]
    return matches[0] if matches else None


# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&q=80&w=200&h=200", width=120)
    st.markdown("## ScenTab Inventory")
    st.markdown("Aplikasi inventory parfum eksklusif dengan riwayat pelacakan harga.")
    
    # Mode Status Indicator
    if db_connected:
        st.markdown(
            '**Status Database:** <span class="status-badge badge-db">Prisma Connected</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '**Status Database:** <span class="status-badge badge-dummy">Dummy Data Mode</span>',
            unsafe_allow_html=True
        )
        
    menu = st.radio(
        "Navigasi Halaman:",
        ["📊 Dashboard & Analisis", "📦 Kelola Parfum", "📈 Riwayat Harga"]
    )

# --- PAGE 1: DASHBOARD ---
if menu == "📊 Dashboard & Analisis":
    st.markdown('<div class="main-title">🧪 ScenTab Inventory Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analisis Stok Parfum dan Riwayat Tren Harga Terkini</div>', unsafe_allow_html=True)
    
    # Load Data
    df_parfum = get_all_parfum()
    df_riwayat = get_all_riwayat()
    
    # Metrics
    total_parfum = len(df_parfum)
    total_stok = df_parfum['stok'].sum() if not df_parfum.empty else 0
    total_value = 0.0
    
    if not df_parfum.empty:
        # Get latest price for each parfum from df_riwayat
        latest_prices = []
        for p_id in df_parfum['id']:
            if not df_riwayat.empty and 'parfum_id' in df_riwayat.columns:
                p_history = df_riwayat[df_riwayat['parfum_id'] == p_id]
                if not p_history.empty:
                    # Sort by tanggal_update and get the last one
                    latest_price = p_history.sort_values('tanggal_update').iloc[-1]['harga_beli']
                    latest_prices.append(float(latest_price))
                else:
                    latest_prices.append(0.0)
            else:
                latest_prices.append(0.0)
        
        # Calculate total value based on latest prices
        stok_list = list(df_parfum['stok'])
        total_value = sum(latest_prices[i] * stok_list[i] for i in range(len(df_parfum)))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Varian Parfum</h4>
            <div class="metric-value">{total_parfum}</div>
            <p>Varian terdaftar</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #2b5876, #4e4376);">
            <h4>Total Stok Tersedia</h4>
            <div class="metric-value">{total_stok}</div>
            <p>Botol parfum</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #11998e, #38ef7d);">
            <h4>Total Estimasi Aset</h4>
            <div class="metric-value">Rp {total_value:,.2f}</div>
            <p>Nilai berdasarkan harga terakhir</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### 📈 Grafik Tren Harga Rata-Rata Produk")
    
    if not df_riwayat.empty:
        chart_df = df_riwayat.copy()
        chart_df['tanggal_update'] = pd.to_datetime(chart_df['tanggal_update'])
        chart_df['harga_beli'] = chart_df['harga_beli'].astype(float)
        
        # Kelompokkan berdasarkan tanggal untuk mendapatkan rata-rata harga produk keseluruhan
        chart_df['Tanggal'] = chart_df['tanggal_update'].dt.date
        avg_trend = chart_df.groupby('Tanggal')['harga_beli'].mean().reset_index()
        avg_trend = avg_trend.rename(columns={'harga_beli': 'Harga Rata-Rata (Rp)'})
        avg_trend = avg_trend.sort_values('Tanggal')
        
        st.line_chart(
            avg_trend,
            x='Tanggal',
            y='Harga Rata-Rata (Rp)',
            width="stretch"
        )
    else:
        st.info("Belum ada data riwayat harga yang cukup untuk ditampilkan.")

# --- PAGE 2: KELOLA PARFUM ---
elif menu == "📦 Kelola Parfum":
    st.markdown('<div class="main-title">📦 Kelola Inventaris Parfum</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Tambah Varian Baru dan Periksa Ketersediaan Stok</div>', unsafe_allow_html=True)
    
    st.subheader("Daftar Parfum Saat Ini")
    df_parfum = get_all_parfum()
    df_riwayat = get_all_riwayat()
    if not df_parfum.empty:
        # Display beautifully
        df_display = df_parfum.copy()
        df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Mendapatkan harga terbaru untuk masing-masing parfum dari df_riwayat
        latest_prices = []
        for p_id in df_display['id']:
            if not df_riwayat.empty and 'parfum_id' in df_riwayat.columns:
                p_history = df_riwayat[df_riwayat['parfum_id'] == p_id]
                if not p_history.empty:
                    latest_price = p_history.sort_values('tanggal_update').iloc[-1]['harga_beli']
                    latest_prices.append(f"Rp {float(latest_price):,.2f}")
                else:
                    latest_prices.append("Rp 0.00")
            else:
                latest_prices.append("Rp 0.00")
        df_display['harga_terbaru'] = latest_prices

        st.dataframe(
            df_display[['id', 'nama_parfum', 'harga_terbaru', 'stok', 'supplier', 'created_at']].rename(columns={
                'id': 'ID',
                'nama_parfum': 'Nama Parfum',
                'harga_terbaru': 'Harga Terkini',
                'stok': 'Stok (Pcs)',
                'supplier': 'Supplier Utama',
                'created_at': 'Tanggal Dibuat'
            }), 
            hide_index=True,
            width="stretch"
        )
    else:
        st.warning("Inventaris kosong! Silakan tambahkan parfum menggunakan form di bawah.")
        
    st.markdown("---")
    
    st.subheader("➕ Tambah Parfum Baru")
    tab_manual, tab_excel, tab_delete = st.tabs(["📝 Form Manual", "📄 Upload File Excel", "🗑️ Hapus Parfum"])
    
    with tab_manual:
        with st.form("tambah_parfum_form"):
            col_input1, col_input2 = st.columns(2)
            with col_input1:
                nama = st.text_input("Nama Parfum", placeholder="Contoh: Bleu de Chanel")
                stok = st.number_input("Stok Awal", min_value=0, value=10, step=1)
            with col_input2:
                supplier = st.text_input("Supplier", placeholder="Contoh: PT Aroma Import")
                harga_awal = st.number_input("Harga Beli Awal (Rp)", min_value=0, value=1500000, step=50000)
            
            submit = st.form_submit_button("Simpan Parfum")
            if submit:
                if nama and supplier:
                    success = add_parfum(nama, stok, supplier, harga_awal)
                    if success:
                        st.success(f"Berhasil menambahkan parfum '{nama}' ke database!")
                        st.rerun()
                    else:
                        st.error(f"Gagal menambahkan parfum '{nama}' ke database. Cek koneksi Anda.")
                else:
                    st.error("Semua field harus diisi!")
                    
    with tab_excel:
        st.write("Anda dapat mengimpor banyak produk sekaligus dengan mengunggah berkas Excel.")
        
        # Sediakan template excel untuk didownload
        import io
        template_df = pd.DataFrame(columns=["Nama Parfum", "Stok", "Supplier", "Harga Beli"])
        # Contoh baris dummy di template
        template_df.loc[0] = ["Chanel Allure", 15, "PT Aroma Wangi", 2100000]
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Template Parfum')
        
        st.download_button(
            label="📥 Download Template Excel",
            data=buffer.getvalue(),
            file_name="template_import_parfum.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        
        # Uploader file
        uploaded_file = st.file_uploader("Unggah File Excel (.xlsx / .xls)", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                # Membaca excel menggunakan pandas & openpyxl
                df_imported = pd.read_excel(uploaded_file)
                
                # Cek kesesuaian kolom wajib
                required_cols = ["Nama Parfum", "Stok", "Supplier", "Harga Beli"]
                if all(col in df_imported.columns for col in required_cols):
                    # Lakukan pengecekan data di preview dan tambahkan kolom Status Tindakan
                    statuses = []
                    for _, row in df_imported.iterrows():
                        if pd.isna(row["Nama Parfum"]):
                            statuses.append("⚠️ Kolom Nama Kosong")
                            continue
                        nama = str(row["Nama Parfum"]).strip()
                        existing_p = check_parfum_exists(nama)
                        if existing_p is not None:
                            statuses.append("📈 Update Harga (Sudah Ada)")
                        else:
                            statuses.append("➕ Parfum Baru")
                    df_imported["Status Tindakan"] = statuses
                    
                    st.success("Format berkas Excel sesuai! Silakan verifikasi tindakan impor data di bawah:")
                    st.dataframe(df_imported, width="stretch", hide_index=True)
                    
                    if st.button("Proses & Simpan Semua Data Excel", key="btn_save_excel"):
                        new_parfum_count = 0
                        updated_price_count = 0
                        fail_count = 0
                        
                        for _, row in df_imported.iterrows():
                            # Validasi data kosong
                            if pd.isna(row["Nama Parfum"]) or pd.isna(row["Supplier"]):
                                continue
                            
                            nama = str(row["Nama Parfum"]).strip()
                            harga_beli = float(row["Harga Beli"]) if not pd.isna(row["Harga Beli"]) else 0.0
                            
                            # Cek status
                            existing_p = check_parfum_exists(nama)
                            if existing_p is not None:
                                # Jika parfum sudah terdaftar, cukup update harga terbarunya saja
                                p_id = existing_p.id if hasattr(existing_p, 'id') else existing_p['id']
                                success = update_harga(p_id, harga_beli)
                                if success:
                                    updated_price_count += 1
                                else:
                                    fail_count += 1
                            else:
                                # Jika parfum belum terdaftar, tambahkan sebagai parfum baru beserta harga awal
                                success = add_parfum(
                                    nama=nama,
                                    stok=int(row["Stok"]) if not pd.isna(row["Stok"]) else 0,
                                    supplier=str(row["Supplier"]),
                                    harga_awal=harga_beli
                                )
                                if success:
                                    new_parfum_count += 1
                                else:
                                    fail_count += 1
                        
                        if fail_count == 0:
                            st.success(f"Berhasil memproses Excel! {new_parfum_count} parfum baru ditambahkan, {updated_price_count} riwayat harga diperbarui.")
                        else:
                            st.warning(f"Selesai dengan beberapa catatan: {new_parfum_count} parfum baru disimpan, {updated_price_count} harga diperbarui, {fail_count} transaksi gagal ke database.")
                        st.rerun()
                else:
                    st.error(f"Format kolom Excel tidak cocok! Pastikan memiliki kolom berikut: {', '.join(required_cols)}")
            except Exception as e:
                st.error(f"Gagal memproses file Excel: {str(e)}")
                
    with tab_delete:
        st.write("Hapus varian parfum secara permanen dari sistem. Tindakan ini juga akan menghapus log seluruh riwayat harga terkait.")
        df_parfum = get_all_parfum()
        if not df_parfum.empty:
            with st.form("hapus_parfum_form"):
                # Menampilkan dropdown list parfum yang ada
                parfum_del_options = {row['nama_parfum']: row['id'] for idx, row in df_parfum.iterrows()}
                selected_del_parfum = st.selectbox("Pilih Parfum yang Ingin Dihapus:", options=list(parfum_del_options.keys()))
                
                # Checkbox konfirmasi keamanan
                confirm_delete = st.checkbox("Saya mengerti bahwa data ini akan dihapus secara permanen dan tidak dapat dikembalikan.")
                
                submit_del = st.form_submit_button("Hapus Barang", type="secondary")
                if submit_del:
                    if confirm_delete:
                        parfum_id = parfum_del_options[selected_del_parfum]
                        success = delete_parfum(parfum_id)
                        if success:
                            st.success(f"Berhasil menghapus '{selected_del_parfum}' dan seluruh riwayat harga terkait dari database!")
                            st.rerun()
                        else:
                            st.error(f"Gagal menghapus '{selected_del_parfum}' dari database.")
                    else:
                        st.error("Anda harus mencentang kotak konfirmasi sebelum melakukan penghapusan data!")
        else:
            st.info("Belum ada data parfum yang tersedia untuk dihapus.")

# --- PAGE 3: RIWAYAT HARGA ---
elif menu == "📈 Riwayat Harga":
    st.markdown('<div class="main-title">📈 Riwayat & Fluktuasi Harga</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Rekam dan Pantau Harga Beli Parfum dari Waktu ke Waktu</div>', unsafe_allow_html=True)
    
    # 1. Grafik Tren Harga Per Parfum (Paling Atas)
    df_parfum = get_all_parfum()
    df_riwayat = get_all_riwayat()
    
    if not df_parfum.empty and not df_riwayat.empty:
        st.subheader("📊 Grafik Tren Harga Per Varian")
        
        # Option list for dropdown
        parfum_chart_options = {row['nama_parfum']: row['id'] for idx, row in df_parfum.iterrows()}
        selected_chart_parfum = st.selectbox(
            "Pilih Parfum untuk Melihat Grafik Fluktuasi:",
            options=list(parfum_chart_options.keys()),
            key="chart_parfum_selector"
        )
        
        # Filter history based on selected perfume
        selected_id = parfum_chart_options[selected_chart_parfum]
        df_filtered = df_riwayat[df_riwayat['parfum_id'] == selected_id].copy()
        
        if not df_filtered.empty:
            df_filtered['tanggal_update'] = pd.to_datetime(df_filtered['tanggal_update'])
            df_filtered['harga_beli'] = df_filtered['harga_beli'].astype(float)
            
            # Sort chronologically for nice line drawing
            df_filtered = df_filtered.sort_values('tanggal_update')
            
            col_chart, col_table = st.columns([3, 2])
            
            with col_chart:
                st.line_chart(
                    df_filtered,
                    x='tanggal_update',
                    y='harga_beli',
                    width="stretch"
                )
                
            with col_table:
                # Format tampilan harga dan tanggal untuk tabel
                df_table = df_filtered.copy()
                df_table['harga_beli'] = df_table['harga_beli'].apply(lambda x: f"Rp {x:,.2f}")
                df_table['tanggal_update'] = df_table['tanggal_update'].dt.strftime('%Y-%m-%d %H:%M')
                
                # Tampilkan tabel log riwayat harga untuk varian terpilih
                st.dataframe(
                    df_table[['tanggal_update', 'harga_beli']].rename(columns={
                        'tanggal_update': 'Tanggal Perubahan',
                        'harga_beli': 'Harga Beli'
                    }),
                    hide_index=True,
                    width="stretch"
                )
        else:
            st.info("Belum ada riwayat update harga untuk parfum ini.")
            
        st.markdown("---")
        
    col_hist, col_update = st.columns([2, 1])
    
    with col_hist:
        st.subheader("Log Update Harga Terkini")
        df_riwayat = get_all_riwayat()
        if not df_riwayat.empty:
            df_display_riwayat = df_riwayat.copy()
            df_display_riwayat['harga_beli'] = df_display_riwayat['harga_beli'].apply(lambda x: f"Rp {float(x):,.2f}")
            df_display_riwayat['tanggal_update'] = pd.to_datetime(df_display_riwayat['tanggal_update']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(
                df_display_riwayat[[
                    'id_riwayat', 'nama_parfum', 'harga_beli', 'tanggal_update', 'supplier'
                ]].rename(columns={
                    'id_riwayat': 'Log ID',
                    'nama_parfum': 'Nama Parfum',
                    'harga_beli': 'Harga Beli',
                    'tanggal_update': 'Tanggal Update',
                    'supplier': 'Supplier'
                }),
                hide_index=True,
                width="stretch"
            )
        else:
            st.warning("Belum ada riwayat harga.")
            
    with col_update:
        st.subheader("Update Harga Baru")
        df_parfum = get_all_parfum()
        if not df_parfum.empty:
            with st.form("update_harga_form"):
                # Option list for dropdown
                parfum_options = {row['nama_parfum']: row['id'] for idx, row in df_parfum.iterrows()}
                selected_parfum = st.selectbox("Pilih Parfum", options=list(parfum_options.keys()))
                harga_baru = st.number_input("Harga Beli Baru (Rp)", min_value=0, value=1000000, step=50000)
                
                submit = st.form_submit_button("Update Harga")
                if submit:
                    parfum_id = parfum_options[selected_parfum]
                    success = update_harga(parfum_id, harga_baru)
                    if success:
                        st.success(f"Berhasil mengupdate harga untuk {selected_parfum}!")
                        st.rerun()
                    else:
                        st.error(f"Gagal mengupdate harga untuk {selected_parfum} di database.")
        else:
            st.error("Silakan tambah parfum terlebih dahulu untuk dapat mengupdate harga.")


