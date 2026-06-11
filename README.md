# ScenTab - Parfum Inventory & Price History

Aplikasi Inventory Parfum mewah dengan pelacakan fluktuasi harga menggunakan **Streamlit**, **Prisma ORM (Python)**, dan **PostgreSQL (Aiven Cloud)**.

---

## 📂 Struktur Folder Proyek

Proyek ini telah diinisialisasi dengan struktur folder berikut:

```text
flowerinventory/
├── .env                  # Menyimpan kredensial database (DATABASE_URL)
├── requirements.txt      # Berisi daftar library Python yang dibutuhkan
├── README.md             # File dokumentasi ini (petunjuk setup)
├── app.py                # File utama aplikasi web Streamlit (dengan fallback dummy data)
├── prisma/
│   └── schema.prisma     # Definisi model tabel database (Parfum & Riwayat Harga)
└── src/
    ├── __init__.py       # Mendefinisikan direktori src sebagai package
    └── database.py       # Helper untuk menginisialisasi & cache Prisma Client
```

---

## 🚀 Langkah-Langkah Setup & Migrasi Database

Ikuti panduan berikut untuk menjalankan aplikasi dan menghubungkannya dengan database PostgreSQL di Aiven Cloud.

### Langkah 1: Persiapan Virtual Environment & Install Dependensi
Buka terminal (PowerShell di Windows) di folder root `flowerinventory/` dan jalankan perintah berikut:

```powershell
# 1. Buat virtual environment python
python -m venv venv

# 2. Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip dan install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Langkah 2: Konfigurasi Database (Aiven Cloud)
1. Buka [Aiven Console](https://console.aiven.io/) dan buat database PostgreSQL gratis atau berbayar.
2. Dapatkan **Connection URI** database Anda. Formatnya menyerupai:
   `postgres://avnadmin:password@host:port/defaultdb?sslmode=require`
3. Buat file bernama `.env` di root folder proyek (`flowerinventory/.env`) dan isi dengan URL koneksi tersebut:

```env
DATABASE_URL="postgres://avnadmin:password@host:port/defaultdb?sslmode=require"
```

---

### Langkah 3: Inisialisasi & Migrasi Database dengan Prisma
Jalankan dua perintah berikut di terminal Anda untuk menyiapkan skema database:

```powershell
# 1. Generate client module Python untuk Prisma
prisma generate

# 2. Push schema.prisma ke PostgreSQL Aiven Cloud (membuat tabel baru secara otomatis)
prisma db push
```

> [!TIP]
> Perintah `prisma db push` sangat cocok digunakan untuk pengembangan cepat. Perintah ini akan langsung mensinkronisasikan schema Prisma ke PostgreSQL Cloud tanpa perlu membuat file riwayat migrasi lokal.

---

### Langkah 4: Jalankan Aplikasi Streamlit
Setelah database termigrasi dan Prisma Client tergenerasi, jalankan Streamlit:

```powershell
streamlit run app.py
```

Buka browser Anda di alamat default `http://localhost:8501`. 
- Jika koneksi berhasil, status di sidebar akan berwarna hijau: **Prisma Connected**.
- Jika Anda belum menghubungkan database, aplikasi akan tetap berjalan dalam mode demo dengan **Dummy Data** yang interaktif (bisa tambah data & update harga di memori sementara).
