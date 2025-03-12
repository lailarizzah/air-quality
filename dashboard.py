import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# URL dataset
DATA_URL = "https://raw.githubusercontent.com/lailarizzah/air-quality/refs/heads/main/PRSA_Data_Aotizhongxin.csv"

# Fungsi untuk memuat data
def load_data():
    df = pd.read_csv(DATA_URL)
    return df

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
