import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN (UI/UX)
st.set_page_config(
    page_title="IDX Ultimate Multibagger Screener",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Premium UI
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #1E3A8A; }
    h1 { color: #1E3A8A; font-weight: 800; font-family: 'Helvetica Neue', sans-serif; }
    h3 { color: #1E40AF; font-weight: 600; }
    .stButton>button { background-color: #1E3A8A; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# 2. SELEKSI DATA EMITEN SECARA MASAL & AKURAT
@st.cache_data(ttl=3600)
def load_all_idx_data():
    """Menarik semua emiten dari repositori publik dan mengunduh metrik dari Yahoo Finance"""
    url = "https://raw.githubusercontent.com/manvisg/indonesian-stock-tickers/main/tickers.csv"
    try:
        df_raw = pd.read_csv(url)
        ticker_col = [col for col in df_raw.columns if 'ticker' in col.lower() or 'symbol' in col.lower()][0]
        raw_tickers = df_raw[ticker_col].dropna().unique().tolist()
    except:
        try:
            backup_url = "https://raw.githubusercontent.com/yandis/indonesia-stock-list/master/data/stock_list.csv"
            df_raw = pd.read_csv(backup_url)
            raw_tickers = df_raw.iloc[:, 0].dropna().unique().tolist()
        except:
            # Fallback jika terjadi kegagalan jaringan internet total
            raw_tickers = ["BBCA", "BBRI", "BMRI", "BBNI", "ASII", "TLKM", "UNVR", "ADRO", "PTBA", "ITMG", "AMRT", "ICBP"]

    all_data = []
    progress_bar = st.progress(0, text="Menghubungkan ke Bursa Efek Indonesia & mengunduh data finansial...")
    total = len(raw_tickers)
    
    for idx, ticker_code in enumerate(raw_tickers):
        ticker_code = str(ticker_code).strip().upper()
        if len(ticker_code) != 4: 
            continue
            
        ticker_sym = f"{ticker_code}.JK"
        
        if idx % 15 == 0 or idx == total - 1:
            progress_bar.progress((idx + 1) / total, text=f"Menganalisis Struktur Fundamental & Volume: {ticker_code} ({idx+1}/{total})")
            
        try:
            t = yf.Ticker(ticker_sym)
            info = t.info
            
            # --- PARAMETER METODE 1 & 2: VALUE & GROWTH INVESTING ---
            pbv = info.get('priceToBook', np.nan)
            pe = info.get('trailingPE', np.nan)
            roe = info.get('returnOnEquity', np.nan)
            der = info.get('debtToEquity', np.nan)  # Rasio Utang
            rev_growth = info.get('revenueGrowth', np.nan)  # Pertumbuhan Pendapatan
            market_cap = info.get('marketCap', 0)
            price = info.get('currentPrice', info.get('regularMarketPrice', np.nan))
            
            if pd.isna(pbv) or pd.isna(pe) or pd.isna(roe) or market_cap == 0:
                continue
                
            # --- PARAMETER METODE 3 & 4: ENTRY POINT & AKUMULASI (BANDARMOLOGI PROXY) ---
            df_hist = t.history(period="6mo")
            if len(df_hist) < 50:
                continue
                
            df_hist['MA50'] = df_hist['Close'].rolling(window=50).mean()
            df_hist['Avg_Vol_20'] = df_hist['Volume'].rolling(window=20).mean()
            
            latest = df_hist.iloc[-1]
            ma50_val = latest['MA50'] if not pd.isna(latest['MA50']) else df_hist['Close'].mean()
            current_volume = latest['Volume']
            avg_vol_20 = latest['Avg_Vol_20']
            
            # Rasio lonjakan volume harian dibanding rata-rata 20 hari
            volume_ratio = current_volume / avg_vol_20 if avg_vol_20 > 0 else 0
            
            all_data.append({
                "Ticker": ticker_code,
                "Nama Perusahaan": info.get('longName', 'N/A'),
                "Harga (Rp)": price,
                "Market Cap (Miliar Rp)": round(market_cap / 1e9, 2),
                "PBV (x)": round(pbv, 2),
                "PE Ratio (x)": round(pe, 2),
                "ROE (%)": round(roe * 100, 2),
                "DER (%)": round(der, 2) if not pd.isna(der) else 0.0,
                "Revenue Growth (%)": round(rev_growth * 100, 2) if not pd.isna(rev_growth) else 0.0,
                "Volume Ratio (x)": round(volume_ratio, 2),
                "Is Uptrend": price > ma50_val
            })
        except:
            continue
            
    progress_bar.empty()
    return pd.DataFrame(all_data)

# Load data utama ke memory cache
df_idx = load_all_idx_data()

# ==========================================
# 3. INTERFACE UTAMA (DASHBOARD KONTROL TOTAL)
# ==========================================

st.title("🚀 IDX Ultimate Multibagger Screener")
st.caption("Sistem Integrasi: Value Investing + Growth Scaling + Proxy Akumulasi Bandarmologi")
st.write("---")

# SIDEBAR DENGAN PARAMETER YANG DI-GABUNGKAN SECARA TOTAL
st.sidebar.header("🎛️ Parameter Pencarian Multibagger")
st.sidebar.write("Sesuaikan batas toleransi parameter finansial:")

# Kelompok 1: Ukuran & Valuasi (Value Investing)
st.sidebar.subheader("1. Kriteria Ukuran & Valuasi")
max_market_cap = st.sidebar.slider("Maksimal Market Cap (Miliar Rp)", 100, 500000, 15000, step=500, help="Saham < 15T jauh lebih mudah multibagger")
max_pbv = st.sidebar.slider("Maksimal PBV (x)", 0.1, 10.0, 2.5, step=0.1)
max_pe = st.sidebar.slider("Maksimal PE Ratio (x)", 1, 50, 15, step=1)

# Kelompok 2: Profitabilitas & Pertumbuhan (Growth Investing)
st.sidebar.subheader("2. Kinerja & Pertumbuhan")
min_roe = st.sidebar.slider("Minimal ROE (%)", -10, 100, 12, step=1)
min_growth = st.sidebar.slider("Minimal Pertumbuhan Pendapatan (%)", -20, 200, 10, step=5, help="Perusahaan harus bertumbuh secara bisnis")
max_der = st.sidebar.slider("Maksimal Rasio Utang / DER (%)", 10, 500, 150, step=10, help="Menghindari perusahaan bangkrut")

# Kelompok 3: Timing Masuk & Aksi Bandar (Technical & Volume Spike)
st.sidebar.subheader("3. Timing Entry & Lonjakan Volume")
min_vol_ratio = st.sidebar.slider("Minimal Lonjakan Volume (x lipat)", 0.5, 5.0, 1.5, step=0.1, help="Mendeteksi akumulasi oleh institusi atau 'Bandar'")
only_uptrend = st.sidebar.checkbox("Hanya Tampilkan Saham Uptrend (Harga > MA50)", value=True)

# PROSES FILTER MASAL MENGGUNAKAN SELURUH INPUT DI ATAS
df_filtered = df_idx[
    (df_idx["Market Cap (Miliar Rp)"] <= max_market_cap) &
    (df_idx["PBV (x)"] <= max_pbv) &
    (df_idx["PE Ratio (x)"] <= max_pe) &
    (df_idx["ROE (%)"] >= min_roe) &
    (df_idx["Revenue Growth (%)"] >= min_growth) &
    (df_idx["DER (%)"] <= max_der) &
    (df_idx["Volume Ratio (x)"] >= min_vol_ratio)
]

if only_uptrend:
    df_filtered = df_filtered[df_filtered["Is Uptrend"] == True]

# DYNAMIC METRICS FOR UX SUMMARY
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Saham di IDX", f"{len(df_idx)} Emiten")
with col2:
    st.metric("Saham Lolos Filter Ketat", f"{len(df_filtered)} Emiten")
with col3:
    super_signal = len(df_filtered[df_filtered["Volume Ratio (x)"] >= 2.0])
    st.metric("Saham Mengalami Akumulasi Masif (>2x Vol)", f"{super_signal} Emiten")

st.write("### 📋 Daftar Saham Lolos Seleksi Parameter Maksimal")
st.write("Klik judul kolom pada tabel untuk mengurutkan saham dari yang paling potensial (misal urutkan berdasarkan Volume Ratio tertinggi untuk melihat aksi akumulasi terbesar hari ini).")

# TAMPILAN OUTPUT DATA UTAMA
if not df_filtered.empty:
    # Urutkan berdasarkan lonjakan volume transaksi tertinggi sebagai default
    df_final = df_filtered.sort_values(by="Volume Ratio (x)", ascending=False)
    
    # Drop kolom bantuan agar tabel bersih
    df_display = df_final.drop(columns=["Is Uptrend"])
    
    st.dataframe(
        df_display, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Kode Saham"),
            "Harga (Rp)": st.column_config.NumberColumn("Harga", format="Rp %d"),
            "Market Cap (Miliar Rp)": st.column_config.NumberColumn("Market Cap", format="%d M"),
            "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f %%"),
            "DER (%)": st.column_config.NumberColumn("DER (Utang)", format="%.2f %%"),
            "Revenue Growth (%)": st.column_config.NumberColumn("Pertumbuhan", format="%.2f %%"),
            "Volume Ratio (x)": st.column_config.NumberColumn("Lonjakan Volume (Bandar)", format="%.2f x"),
        }
    )
else:
    st.warning("⚠️ Kombinasi parameter Anda terlalu ketat sehingga tidak ada emiten yang lolos hari ini. Coba turunkan syarat 'Minimal Pertumbuhan' atau longgarkan 'Maksimal PE Ratio' di menu sebelah kiri.")

st.write("---")
st.info("""
💡 **Panduan Membaca Sinyal Integrasi Multibagger:**
* **Metode Value & Growth:** Saham dengan ROE tinggi, DER rendah, dan Revenue Growth positif menunjukkan bisnis asli perusahaan tersebut sangat sehat dan berkembang pesat.
* **Metode Entry & Volume Ratio (Aksi Pasar):** Jika nilai **Volume Ratio di atas 1.5x**, artinya volume perdagangan hari ini melonjak tajam melampaui kebiasaannya dalam 20 hari terakhir. Ini adalah indikator valid bahwa **ada transaksi berskala besar (akumulasi institusi/bandar)** yang siap mendorong harga saham murah ini terbang naik.
""")
