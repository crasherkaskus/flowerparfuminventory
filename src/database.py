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

def patch_prisma_builder():
    """
    Melakukan monkey patch pada fungsi internal _is_prisma_model_type milik Prisma.
    Ini bertujuan untuk mengatasi masalah reload modul parsial oleh Streamlit yang menyebabkan
    mismatch kelas induk (_PrismaModel) sehingga memicu error 'Expected type to have a __prisma_model__'.
    """
    try:
        from src.generated.prisma import _builder
        orig_is_prisma = _builder._is_prisma_model_type
        
        def patched_is_prisma(type_):
            if orig_is_prisma(type_):
                return True
            # Fallback jika issubclass standar gagal karena class type mismatch saat reload modul
            return any(base.__name__ == '_PrismaModel' for base in getattr(type_, '__mro__', []))
        
        _builder._is_prisma_model_type = patched_is_prisma
    except Exception:
        # Abaikan jika modul builder belum digenerasi
        pass

def clean_prisma_sys_modules():
    """
    Membersihkan cache modul generated prisma dari sys.modules.
    Memaksa Python melakukan impor baru yang konsisten untuk semua komponen client Prisma.
    """
    to_delete = [k for k in sys.modules.keys() if 'src.generated.prisma' in k]
    for key in to_delete:
        sys.modules.pop(key, None)

@st.cache_resource
def get_db_client():
    """
    Mengembalikan instance Prisma Client yang di-cache.
    Mendeteksi jika client belum digenerasi, lalu menjalankannya secara otomatis.
    Sangat berguna untuk proses deployment di Streamlit Community Cloud.
    """
    # Bersihkan cache modul generated prisma sebelum mengimpor client
    clean_prisma_sys_modules()
    
    try:
        from src.generated.prisma import Prisma
        # Terapkan monkey patch ke builder
        patch_prisma_builder()
        db = Prisma()
        return db
    except (ImportError, RuntimeError) as e:
        # Cek jika error disebabkan karena client belum digenerasi
        err_msg = str(e)
        if "hasn't been generated yet" in err_msg or isinstance(e, ImportError):
            with st.spinner("Menggenerasi database client Prisma untuk pertama kali... Mohon tunggu..."):
                if generate_client():
                    try:
                        clean_prisma_sys_modules()
                        from src.generated.prisma import Prisma
                        patch_prisma_builder()
                        db = Prisma()
                        return db
                    except Exception as ex:
                        st.error(f"Gagal memuat Prisma setelah generasi otomatis: {ex}")
                        return None
        else:
            st.error(f"Error tidak dikenal saat inisialisasi Prisma: {e}")
        return None
