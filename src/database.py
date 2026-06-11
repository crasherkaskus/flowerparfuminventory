import streamlit as st
import subprocess
import sys

def generate_client():
    try:
        # Menjalankan 'prisma generate' menggunakan interpreter Python yang aktif
        # agar berjalan sukses di lingkungan Streamlit Community Cloud.
        subprocess.run([sys.executable, "-m", "prisma", "generate"], check=True)
        return True
    except Exception as e:
        st.warning(f"Otomatisasi 'prisma generate' gagal: {e}. Anda mungkin perlu menjalankannya secara manual di terminal.")
        return False

@st.cache_resource
def get_db_client():
    """
    Mengembalikan instance Prisma Client yang di-cache.
    Mendeteksi jika client belum digenerasi, lalu menjalankannya secara otomatis.
    Sangat berguna untuk proses deployment di Streamlit Community Cloud.
    """
    try:
        from src.generated.prisma import Prisma
        db = Prisma()
        return db
    except (ImportError, RuntimeError) as e:
        # Cek jika error disebabkan karena client belum digenerasi
        err_msg = str(e)
        if "hasn't been generated yet" in err_msg or isinstance(e, ImportError):
            with st.spinner("Menggenerasi database client Prisma untuk pertama kali... Mohon tunggu..."):
                if generate_client():
                    try:
                        from src.generated.prisma import Prisma
                        db = Prisma()
                        return db
                    except Exception as ex:
                        st.error(f"Gagal memuat Prisma setelah generasi otomatis: {ex}")
                        return None
        else:
            st.error(f"Error tidak dikenal saat inisialisasi Prisma: {e}")
        return None
