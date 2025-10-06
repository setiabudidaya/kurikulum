import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

# Nama file Excel yang akan langsung dibaca
FILE_EXCEL = "data_kurikulum.xlsx"

# Mengatur judul halaman dan layout
st.set_page_config(page_title="Status kurikulum Program Studi", layout="wide")

# --- Bagian Header dan Logo ---
col1, col2 = st.columns([1, 4])

with col1:
    # Ganti URL ini dengan URL logo universitas Anda
    st.image("https://upload.wikimedia.org/wikipedia/id/thumb/b/bc/Logo_Universitas_Sriwijaya.svg/1008px-Logo_Universitas_Sriwijaya.svg.png?20240818010951", width=150)

with col2:
    st.title("Sistem Informasi Pemantauan Kurikulum")
    st.write("Aplikasi ini digunakan untuk memantau status kurikulum program studi di lingkungan Universitas Sriwijaya")
    st.markdown("---")

# --- Bagian Pembacaan File Excel ---
try:
    # Langsung membaca data dari file Excel
    df = pd.read_excel(FILE_EXCEL)

    # Mengubah kolom 'Tanggal SK' menjadi format datetime
    df['Tanggal SK'] = pd.to_datetime(df['Tanggal SK'], errors='coerce')

    # Menghitung sisa hari
    today = pd.to_datetime(date.today()) # Convert today to datetime for calculation
    df['Lama Tahun'] = (today - df['Tanggal SK']).dt.days / 365.25 # Calculate in years

    # --- Tambahan: Ringkasan Tabel Lama Pemberlakuan ---
    st.header("Ringkasan Status Lama Pemberlakuan")

    # Mengelompokkan data berdasarkan Lama Tahun
    next_0_years_count = len(df[(df['Lama Tahun'] >= 0) & (df['Lama Tahun'] <= 2)])
    next_2_years_count = len(df[(df['Lama Tahun'] > 2) & (df['Lama Tahun'] <= 5)])
    next_5_years_count = len(df[(df['Lama Tahun'] > 5) & (df['Lama Tahun'] <= 7)])
    next_7_years_count = len(df[df['Lama Tahun'] > 7])
    summary_data = {
        'Rentang Waktu': ['0-2 Tahun', '2-5 Tahun', '5-7 Tahun', 'Lebih dari 7 Tahun'],
        'Jumlah Prodi': [next_0_years_count, next_2_years_count, next_5_years_count, next_7_years_count]
    }


    summary_df = pd.DataFrame(summary_data)

    st.dataframe(summary_df, hide_index=True)
    st.markdown("---")

    # Fungsi untuk styling baris
    def row_color(row):
        # Apply styling based on the numerical value before formatting
        # Access the original numerical 'Lama Tahun' from the main df
        original_years_left = df.loc[row.name, 'Lama Tahun']
        if pd.notna(original_years_left):
            if original_years_left > 7:
                return ['background-color: #ffcccc'] * len(row)  # Merah muda
            elif original_years_left > 5:
                return ['background-color: #ffffcc'] * len(row)  # Kuning muda
            else:
                return [''] * len(row)
        else:
            return [''] * len(row)

    # --- Tata Letak with Kolom ---
    st.header("Ringkasan dan Detail Kurikulum")

    # Kolom for grafik and tabel
    col_chart, col_table = st.columns([1, 2])

    with col_chart:
        st.subheader("Ringkasan Status")
        # Grafik batang for status kurikulum
        # Binning 'Lama Tahun' for the bar chart
        bins = [0, 2, 5, 7, float('inf')]
        labels = ['0-2 Tahun', '2-5 Tahun', '5-7 Tahun', 'Lebih dari 7 Tahun']
        df['Lama Tahun Binned'] = pd.cut(df['Lama Tahun'], bins=bins, labels=labels, right=True)

        studi_by_kurikulum = df['Lama Tahun Binned'].value_counts().reset_index()
        studi_by_kurikulum.columns = ['Lama Tahun', 'Jumlah Program Studi']
        # Sort by 'Lama Tahun' alphabetically
        studi_by_kurikulum = studi_by_kurikulum.sort_values('Lama Tahun')
        fig_kurikulum = px.bar(studi_by_kurikulum, x='Lama Tahun', y='Jumlah Program Studi', title='Jumlah Prodi per Lama Pemberlakuan dalam Tahun',
                               labels={'Lama Tahun':'Lama Pemberlakuan'})                             
        
        st.plotly_chart(fig_kurikulum, use_container_width=True)


    with col_table:
        st.subheader("Data Kurikulum")
        # Create DataFrame baru for displayed, only columns which are guaranteed to exist
        df_display = df[['Nama Program Studi','SK Kurikulum', 'Tanggal SK', 'Lama Tahun']].copy()

        # Format 'Lama Tahun' to one decimal place as string to remove trailing zeros
        df_display['Lama Tahun'] = df_display['Lama Tahun'].apply(lambda x: f'{x:.1f}' if pd.notna(x) else x)

        # Search Feature
        search_query = st.text_input("Cari Program Studi:", "")

        if search_query:
            filtered_df = df_display[df_display['Nama Program Studi'].str.contains(search_query, case=False, na=False)]
            # Apply styling to the filtered dataframe as well
            st.dataframe(filtered_df.style.apply(row_color, axis=1), use_container_width=True)
        else:
            st.dataframe(df_display.style.apply(row_color, axis=1), use_container_width=True)


except FileNotFoundError:
    st.error(f"File '{FILE_EXCEL}' tidak ditemukan di folder yang sama. Pastikan file Excel Anda ada di sana.")
except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca file: {e}. Pastikan file Excel Anda memiliki kolom: 'Nama Program Studi', 'SK Kurikulum', 'Tanggal SK'")


