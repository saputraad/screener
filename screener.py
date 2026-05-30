import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN (UI/UX)
st.set_page_config(
    page_title="IDX Multibagger Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk mempercantik UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { color: #1E3A8A; font-family: 'Helvetica Neue', sans-serif; }
    h3 { color: #1E40AF; }
    </style>
""", unsafe_allow_html=True)

# 2. FUNGSI AMBIL DATA MASSAL (DENGAN CACHING AGAR CEPAT)
@st.cache_data(ttl=3600)  # Data disimpan di cache selama 1 jam
def load_all_idx_data():
    """Mengambil daftar seluruh saham IDX dan memproses metriknya"""
    # Mengambil daftar ~900+ saham IDX dari repositori publik tepercaya
    url = "https://raw.githubusercontent.com/hellonoire/indonesian-stock-tickers/main/tickers.csv"
    try:
        df_raw = pd.read_csv(url)
        if 'ticker' in df_raw.columns:
            raw_tickers = df_raw['ticker'].tolist()
        else:
            raw_tickers = df_raw.iloc[:, 0].tolist()
    except Exception as e:
        # Fallback list jika github bermasalah
        raw_tickers = ["BBCA", "BBRI", "BMRI", "BBNI", "ASII", "TLKM", "UNVR", "ADRO", "PTBA", "ITMG"]

    all_data = []
    
    # Progress bar untuk UX saat loading pertama kali
    progress_bar = st.progress(0, text="Mengunduh & menganalisis seluruh data saham IDX...")
    total = len(raw_tickers)
    
    for idx, ticker_code in enumerate(raw_tickers):
        ticker_sym = f"{ticker_code}.JK"
        
        # Update progress bar (dibatasi agar UI tidak berat)
        if idx % 10 == 0 or idx == total - 1:
            progress_bar.progress((idx + 1) / total, text=f"Memproses {ticker_code} ({idx+1}/{total})")
            
        try:
            t = yf.Ticker(ticker_sym)
            info = t.info
            
            # Ambil Data Fundamental
            pbv = info.get('priceToBook', np.nan)
            pe = info.get('trailingPE', np.nan)
            roe = info.get('returnOnEquity', np.nan)
            market_cap = info.get('marketCap', 0)
            price = info.get('currentPrice', info.get('regularMarketPrice', np.nan))
            
            if pd.isna(pbv) or pd.isna(pe) or pd.isna(roe) or market_cap == 0:
                continue
                
            # Ambil Data Historis untuk Analisis Volume & MA (Entry Point)
            df_hist = t.history(period="3mo")
            if len(df_hist) < 20:
                continue
                
            df_hist['MA50'] = df_hist['Close'].rolling(window=50).mean()
            df_hist['Avg_Vol_20'] = df_hist['Volume'].rolling(window=20).mean()
            
            latest = df_hist.iloc[-1]
            ma50_val = latest['MA50'] if not pd.isna(latest['MA50']) else df_hist['Close'].mean()
            
            current_volume = latest['Volume']
            avg_vol = latest['Avg_Vol_20']
            
            # Penentuan Status Entry (Logika Parameter Maksimal)
            is_uptrend = price > ma50_val
            is_volume_spike = current_volume > (avg_vol * 1.5)
            
            if is_uptrend and is_volume_spike:
                status = "🟢 STRONG BUY (Akumulasi)"
            elif is_uptrend:
                status = "🟡 HOLD / WATCHLIST"
            else:
                status = "🔴 AVOID (Downtrend)"
                
            all_data.append({
                "Ticker": ticker_code,
                "Nama Perusahaan": info.get('longName', 'N/A'),
                "Harga (Rp)": price,
                "Market Cap (Miliar Rp)": round(market_cap / 1e9, 2),
                "PBV (x)": round(pbv, 2),
                "PE Ratio (x)": round(pe, 2),
                "ROE (%)": round(roe * 100, 2),
                "Status Entry": status
            })
        except:
            continue
            
    progress_bar.empty()
    return pd.DataFrame(all_data)

# Load data utama
df_idx = load_all_idx_data()

# ==========================================
# 3. INTERFACE UTAMA (UI/UX DASHBOARD)
# ==========================================

st.title("📈 Smart IDX Multibagger Screener")
st.caption("Dashboard Analisis Saham Gabungan Value/Growth Investing & Akumulasi Volume")
st.write("---")

# LAYOUT SIDEBAR: CONTROLLER PARAMETER (UX yang memudahkan pengguna)
st.sidebar.header("🎛️ Parameter Filter Multibagger")
st.sidebar.write("Sesuaikan kriteria pencarian Anda:")

# Slider interaktif untuk memperkuat UX kontrol
max_market_cap = st.sidebar.slider("Maksimal Market Cap (Miliar Rp)", 500, 500000, 15000, step=500)
min_roe = st.sidebar.slider("Minimal ROE (%)", 0, 50, 12, step=1)
max_pbv = st.sidebar.slider("Maksimal PBV (x)", 0.5, 10.0, 2.5, step=0.1)
max_pe = st.sidebar.slider("Maksimal PE Ratio (x)", 5, 50, 15, step=1)

status_filter = st.sidebar.multiselect(
    "Filter Status Entry:",
    ["🟢 STRONG BUY (Akumulasi)", "🟡 HOLD / WATCHLIST", "🔴 AVOID (Downtrend)"],
    default=["🟢 STRONG BUY (Akumulasi)", "🟡 HOLD / WATCHLIST"]
)

# PROSES FILTER BERDASARKAN INPUT USER
df_filtered = df_idx[
    (df_idx["Market Cap (Miliar Rp)"] <= max_market_cap) &
    (df_idx["ROE (%)"] >= min_roe) &
    (df_idx["PBV (x)"] <= max_pbv) &
    (df_idx["PE Ratio (x)"] <= max_pe) &
    (df_idx["Status Entry"].isin(status_filter))
]

# TAMPILAN HIGHLIGHT METRICS (SUMMARY BANNER)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Saham Teranalisis", f"{len(df_idx)} Saham")
with col2:
    st.metric("Saham Lolos Filter", f"{len(df_filtered)} Saham")
with col3:
    strong_buy_count = len(df_filtered[df_filtered["Status Entry"] == "🟢 STRONG BUY (Akumulasi)"])
    st.metric("Sinyal Strong Buy Ditemukan", f"{strong_buy_count} Emiten")

st.write("### 📋 Hasil Screening Saham Pilihan")
st.write("Gunakan tabel interaktif di bawah ini untuk mengurutkan (*sorting*) data berdasarkan metrik terbaik pilihan Anda.")

# MENAMPILKAN TABEL UTAMA DENGAN FILTER YANG INTERAKTIF
if not df_filtered.empty:
    # Mengurutkan otomatis agar Strong Buy berada paling atas
    df_filtered = df_filtered.sort_values(by="Status Entry", ascending=True)
    
    st.dataframe(
        df_filtered, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Kode"),
            "Harga (Rp)": st.column_config.NumberColumn("Harga Terakhir", format="Rp %d"),
            "Market Cap (Miliar Rp)": st.column_config.NumberColumn("Market Cap", format="%d M"),
            "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f %%"),
        }
    )
else:
    st.warning("Tidak ada saham yang memenuhi semua kriteria pengetatan Anda saat ini. Coba longgarkan parameter di sidebar kiri.")

# FOOTER EDUKASI UI
st.write("---")
st.info("""
💡 **Tips Memaksimalkan Profit Multibagger:**
* **Market Cap Kecil-Menengah** (di bawah Rp15 Triliun) cenderung bergerak lebih lincah dan berpotensi naik beratus-ratus persen.
* Prioritaskan saham berkode **🟢 STRONG BUY (Akumulasi)** karena mengindikasikan lonjakan volume transaksi di atas rata-rata—sebuah penanda kuat bahwa institusi besar atau pasar sedang merespons saham murah tersebut.
""")
