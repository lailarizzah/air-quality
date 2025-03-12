import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Pastikan dataset telah difilter dengan benar
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

st.write("Kolom yang tersedia dalam dataset:", data.columns.tolist())

# Pastikan nama kolom tidak case-sensitive
data.columns = data.columns.str.lower()

if "year" not in data.columns:
    st.error("Kolom 'year' tidak ditemukan dalam dataset!")
    st.stop()

if "year" not in data.columns:
    st.error("Kolom 'year' tidak ditemukan dalam dataset!")
    st.stop()
# Load data
data = load_data()

# Sidebar untuk filter tahun dan bulan
st.sidebar.header("Filter Data")
year_filter = st.sidebar.selectbox("Pilih Tahun", data["year"].unique())
month_filter = st.sidebar.selectbox("Pilih Bulan", data["month"].unique())

data_filtered = data[(data["year"] == year_filter) & (data["month"] == month_filter)]

# Judul Dashboard
st.title("Dashboard Kualitas Udara - Kota Aotizhongxin")

# Menampilkan dataset
st.subheader("Data PM₂.₅")
st.write(data_filtered.head())

# Visualisasi PM2.5 berdasarkan weekday vs weekend
data_filtered["weekday"] = pd.to_datetime(data_filtered[["year", "month", "day"]]).dt.weekday

data_filtered["weekend"] = data_filtered["weekday"].apply(lambda x: "Weekend" if x >= 5 else "Weekday")

st.subheader("Perbandingan PM₂.₅ Weekday vs Weekend")
fig, ax = plt.subplots()
sns.boxplot(x="weekend", y="PM2.5", data=data_filtered, ax=ax)
st.pyplot(fig)

# Korelasi faktor yang mempengaruhi PM2.5
st.subheader("Korelasi Faktor terhadap PM₂.₅")
correlation = data_filtered.corr()["PM2.5"].sort_values(ascending=False)
st.write(correlation)
