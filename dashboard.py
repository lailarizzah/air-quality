import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

import pandas as pd

# URL dataset
DATA_URL = "https://raw.githubusercontent.com/lailarizzah/air-quality/refs/heads/main/PRSA_Data_Aotizhongxin.csv"

# Fungsi untuk memuat data dengan penanganan error
def load_data():
    try:
        df = pd.read_csv(DATA_URL, sep=";", engine="python", on_bad_lines="skip", encoding="utf-8")
        return df
    except Exception as e:
        print(f"Terjadi error saat membaca dataset: {e}")
        return pd.DataFrame()  # Mengembalikan DataFrame kosong jika terjadi error

# Load data
data = load_data()

# Sidebar untuk filter tahun dan bulan (hanya satu kali)
st.sidebar.header("Filter Data")
year_filter = st.sidebar.selectbox("Pilih Tahun", data["year"].unique(), key="year_select")
month_filter = st.sidebar.selectbox("Pilih Bulan", data["month"].unique(), key="month_select")

# Pastikan dataset telah difilter setelah pemilihan filter
data_filtered = data[(data["year"] == year_filter) & (data["month"] == month_filter)]

# Jika dataset kosong, tampilkan error
if data_filtered.empty:
    st.error("Data tidak ditemukan! Coba pilih tahun dan bulan lain.")
    st.stop()

# Konversi format tanggal dengan benar
data_filtered.loc[:, "weekday"] = pd.to_datetime(data_filtered[["year", "month", "day"]]).dt.weekday
data_filtered.loc[:, "weekend"] = data_filtered["weekday"].apply(lambda x: "Weekend" if x >= 5 else "Weekday")

# Bersihkan format angka (hapus pemisah ribuan)
data = data.replace({",": "", ".": ""}, regex=True)
data = data.apply(pd.to_numeric, errors="coerce")

# Konversi tanggal ke format datetime
data_filtered.loc[:, "weekday"] = pd.to_datetime(data_filtered[["year", "month", "day"]]).dt.weekday
data_filtered.loc[:, "weekend"] = data_filtered["weekday"].apply(lambda x: "Weekend" if x >= 5 else "Weekday")

# Cek apakah data berhasil dimuat
if data.empty:
    print("Gagal memuat dataset. Periksa kembali format file atau URL.")
else:
    print("Dataset berhasil dimuat!")

# Pastikan nama kolom tidak case-sensitive
data.columns = data.columns.str.lower()

if data.empty:
    st.error("Gagal memuat dataset. Periksa kembali URL atau format data.")
    st.stop()

if st.sidebar.checkbox("Tampilkan kolom dataset"):
    st.write("Kolom yang tersedia dalam dataset:", data.columns.tolist())
    
# Pastikan nama kolom tidak case-sensitive
data.columns = data.columns.str.lower()

if "year" not in data.columns:
    st.error("Kolom 'year' tidak ditemukan dalam dataset!")
    st.stop()

if "year" not in data.columns:
    st.error("Kolom 'year' tidak ditemukan dalam dataset!")
    st.stop()

# Judul Dashboard
st.title("Dashboard Kualitas Udara - Kota Aotizhongxin")

# **1. Filter Data Sesuai Pilihan User**
tahun = st.sidebar.selectbox("Pilih Tahun", sorted(data["year"].unique()))
bulan = st.sidebar.selectbox("Pilih Bulan", sorted(data["month"].unique()))

# Filter data berdasarkan input user
data_filtered = data[(data["year"] == tahun) & (data["month"] == bulan)]

# Pastikan semua angka dikonversi ke format numerik agar tidak error
data_filtered = data_filtered.apply(pd.to_numeric, errors="coerce")

# **2. Tampilkan Data yang Difilter**
st.subheader("Data PM₂.₅")
st.dataframe(data_filtered)  # Menampilkan seluruh data, bukan hanya 5 baris

# **3. Korelasi Faktor Cuaca dengan PM2.5**
st.subheader("Korelasi Faktor Cuaca terhadap PM₂.₅")

# Pilih hanya kolom faktor cuaca
weather_factors = ["TEMP", "PRES", "WSPM", "RAIN"]
numeric_columns = [col for col in weather_factors if col in data_filtered.columns]

# Hitung korelasi hanya dengan faktor cuaca
correlation = data_filtered[numeric_columns].corrwith(data_filtered["PM2.5"])
correlation = correlation.sort_values(ascending=False)

# Tampilkan hasil korelasi
st.write(correlation)

# **4. Boxplot PM₂.₅: Weekday vs Weekend**
st.subheader("Distribusi PM₂.₅: Weekday vs Weekend")

# **Pastikan tidak ada NaN atau hanya satu kategori**
if "weekend" not in data_filtered.columns:
    data_filtered["weekend"] = data_filtered["wd"].apply(lambda x: 1 if x in [6, 7] else 0)  # Anggap wd=6,7 sebagai weekend

# **Hapus NaN di weekend dan PM2.5**
data_filtered = data_filtered.dropna(subset=["weekend", "PM2.5"])

# **Cek apakah masih ada lebih dari satu kategori (weekday & weekend)**
if data_filtered["weekend"].nunique() > 1:
    # Plot boxplot
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(x="weekend", y="PM2.5", data=data_filtered, ax=ax)
    ax.set_xticklabels(["Weekday", "Weekend"])
    ax.set_ylabel("Kadar PM₂.₅")

    # Tampilkan plot di Streamlit
    st.pyplot(fig)
else:
    st.warning("Data yang tersedia hanya berisi satu kategori (hanya weekday atau hanya weekend), sehingga boxplot tidak dapat dibuat.")
