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

# Menampilkan dataset
st.subheader("Data PM₂.₅")
st.dataframe(data_filtered)  # Bisa discroll dan difilter langsung

# Visualisasi Boxplot 
st.subheader("Distribusi PM₂.₅: Weekday vs Weekend")

# Pastikan data numerik
data_filtered = data_filtered.apply(pd.to_numeric, errors="coerce")

# Buat boxplot
fig, ax = plt.subplots(figsize=(6, 4))
sns.boxplot(x="weekend", y="PM2.5", data=data_filtered, ax=ax)
ax.set_xticklabels(["Weekday", "Weekend"])
ax.set_ylabel("Kadar PM₂.₅")

# Tampilkan boxplot di Streamlit
st.pyplot(fig)

# **Interpretasi otomatis**
weekday_data = data_filtered[data_filtered["weekend"] == 0]["PM2.5"]
weekend_data = data_filtered[data_filtered["weekend"] == 1]["PM2.5"]

# Hitung statistik utama
median_weekday = weekday_data.median()
median_weekend = weekend_data.median()
iqr_weekday = weekday_data.quantile(0.75) - weekday_data.quantile(0.25)
iqr_weekend = weekend_data.quantile(0.75) - weekend_data.quantile(0.25)

# **Buat interpretasi otomatis**
interpretation = []
if median_weekday > median_weekend:
    interpretation.append(f"Median PM₂.₅ pada **hari kerja** lebih tinggi ({median_weekday:.1f}) dibandingkan dengan **akhir pekan** ({median_weekend:.1f}). Ini menunjukkan bahwa aktivitas di hari kerja mungkin berkontribusi terhadap peningkatan polusi udara.")
else:
    interpretation.append(f"Median PM₂.₅ pada **akhir pekan** lebih tinggi ({median_weekend:.1f}) dibandingkan dengan **hari kerja** ({median_weekday:.1f}). Hal ini bisa terjadi karena faktor seperti peningkatan aktivitas kendaraan di akhir pekan.")

if iqr_weekday > iqr_weekend:
    interpretation.append(f"Variasi kadar PM₂.₅ lebih besar pada **hari kerja** (IQR = {iqr_weekday:.1f}) dibandingkan dengan **akhir pekan** (IQR = {iqr_weekend:.1f}). Ini menunjukkan bahwa fluktuasi polusi lebih besar di hari kerja.")
else:
    interpretation.append(f"Variasi kadar PM₂.₅ lebih besar pada **akhir pekan** (IQR = {iqr_weekend:.1f}) dibandingkan dengan **hari kerja** (IQR = {iqr_weekday:.1f}).")

# Tampilkan interpretasi di Streamlit
st.markdown("### Interpretasi Boxplot")
for text in interpretation:
    st.write("- " + text)

# Korelasi PM 2.5 dengan Faktor Cuaca 
st.subheader("Korelasi PM₂.₅ dengan Faktor Cuaca")

# Bersihkan format angka dengan benar
data_filtered = data_filtered.apply(pd.to_numeric, errors="coerce")

# Pilih hanya kolom faktor cuaca
weather_factors = ["PM2.5", "TEMP", "PRES", "WSPM", "RAIN"]
data_weather = data_filtered[weather_factors]

# Hitung korelasi hanya untuk faktor cuaca
correlation = data_weather.corr()["PM2.5"].drop("PM2.5").sort_values(ascending=False)

# Tampilkan tabel korelasi
st.dataframe(correlation)

# Interpretasi otomatis berdasarkan korelasi
interpretation = []
for factor, value in correlation.items():
    if value > 0.5:
        interpretation.append(f"PM₂.₅ memiliki korelasi positif yang kuat dengan **{factor}** (r = {value:.2f}). Ini berarti peningkatan {factor} cenderung meningkatkan PM₂.₅.")
    elif value > 0.2:
        interpretation.append(f"PM₂.₅ memiliki korelasi positif sedang dengan **{factor}** (r = {value:.2f}). Ada kecenderungan hubungan positif, tetapi tidak terlalu kuat.")
    elif value < -0.2:
        interpretation.append(f"PM₂.₅ memiliki korelasi negatif dengan **{factor}** (r = {value:.2f}). Ini menunjukkan bahwa peningkatan {factor} dapat mengurangi kadar PM₂.₅.")
    else:
        interpretation.append(f"PM₂.₅ memiliki korelasi lemah dengan **{factor}** (r = {value:.2f}). Hubungannya tidak terlalu signifikan.")

# Tampilkan interpretasi di Streamlit
st.markdown("### Interpretasi Korelasi")
for text in interpretation:
    st.write("- " + text)

# Visualisasi korelasi dengan heatmap
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(data_weather.corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)

# Tampilkan heatmap di Streamlit
st.pyplot(fig)
