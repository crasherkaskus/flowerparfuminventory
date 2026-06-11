import streamlit as st

@st.cache_resource
def get_db_client():
    """
    Mengembalikan instance Prisma Client yang di-cache.
    Menggunakan try-except untuk menangani kondisi sebelum 'prisma generate' dijalankan.
    """
    try:
        from prisma import Prisma
        db = Prisma()
        return db
    except ImportError:
        return None
