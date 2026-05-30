import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN UI/UX GABUNGAN
st.set_page_config(
    page_title="IDX Dual-Engine Stock Intelligence",
    page_icon="🧠",
    layout="wide"
)

# Custom Styling Premium UI
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 25px; border-left: 6px solid #1e3a8a; }
    .catalyst-card { background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 5px solid #d97706; margin-bottom: 10px; }
    .metric-box { background-color: #f1f5f9; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    h2 { color: #1e3a8a; font-weight: 700; margin-bottom: 15px; }
    h3 { color: #0f172a; font-weight: 600; }
    h4 { color: #475569; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 IDX Dual-Engine Stock Intelligence")
st.caption("Kombinasi Kalkulator Finansial: Model Graham (Asset-Value) & Model Buffett (Growth-Conservative)")
st.write("---")

# 2. INPUT KODE SAHAM UTAMA
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_input = st.text_input("✍️ Masukkan Kode Saham IDX (Contoh: BBRI, ADRO, AMRT):", value="BBRI").strip().upper()

if ticker_input:
    ticker_sym = f"{ticker_input}.JK"
    
    with st.spinner(f"Sinkronisasi data multi-kalkulator untuk {ticker_input}..."):
        try:
            ticker = yf.Ticker(ticker_sym)
            info = ticker.info
            
            if 'longName' not in info:
                st.error(f"❌ Kode saham '{ticker_input}' tidak valid di IDX.")
                st.stop()
                
            # --- FETCHING DATA MENTAH AKURAT (SAMA UNTUK KEDUA MODEL) ---
            current_price = info.get('currentPrice', info.get('regularMarketPrice', np.nan))
            company_name = info.get('longName', 'N/A')
            market_cap = info.get('marketCap', 0) / 1e9
            eps = info.get('trailingEps', np.nan)
            roe = info.get('returnOnEquity', np.nan)
            rev_growth = info.get('revenueGrowth', np.nan)
            
            # Patch Perbaikan Data Ekuitas & BVPS Manual agar 100% Akurat
            total_equity = info.get('totalAssets', 0) - info.get('totalLiabilities', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            
            if shares_outstanding > 0 and total_equity > 0:
                bvps = total_equity / shares_outstanding
                pbv = current_price / bvps
            else:
                bvps = info.get('bookValue', np.nan)
                pbv = info.get('priceToBook', np.nan)
            
            # HEADER RINGKASAN EMITEN
            st.subheader(f"📊 {ticker_input} - {company_name}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga Terakhir", f"Rp {current_price:,}" if not pd.isna(current_price) else "N/A")
            c2.metric("Market Capitalization", f"Rp {market_cap:,.2f} Miliar")
            c3.metric("Sektor Industri", info.get('sector', 'N/A'))
            
            # ==========================================
            # 3. MEMBUAT SISTEM TAB (UX SEPERTI WEBSITE PROFESIONAL)
            # ==========================================
            st.write("")
            tab1, tab2, tab3 = st.tabs([
                "🏛️ Model 1: Graham Style (Asset Value)", 
                "🦅 Model 2: Buffett Style (Growth Conservative)",
                "⚡ Radar Akumulasi & Katalis"
            ])
            
            # ------------------------------------------
            # TAB 1: GRAHAM STYLE
            # ------------------------------------------
            with tab1:
                st.markdown("<div class='report-card' style='border-left-color: #10b981;'>", unsafe_allow_html=True)
                st.write("### 🎯 Nilai Intrinsik Berdasarkan Graham Number")
                st.caption("Fokus: Menilai aset bersih riil saat ini dan kapasitas laba aktual tanpa menebak masa depan.")
                
                if not pd.isna(eps) and not pd.isna(bvps) and eps > 0 and bvps > 0:
                    fair_price_graham = np.sqrt(22.5 * eps * bvps)
                    mos_graham = ((fair_price_graham - current_price) / fair_price_graham) * 100
                else:
                    fair_price_graham = eps * 10 if (not pd.isna(eps) and eps > 0) else np.nan
                    mos_graham = ((fair_price_graham - current_price) / fair_price_graham) * 100 if not pd.isna(fair_price_graham) else np.nan
                
                g1, g2, g3 = st.columns(3)
                g1.markdown(f"<div class='metric-box'>Harga Saat Ini<br><span style='color:#0f172a; font-size:20px;'>Rp {current_price:,}</span></div>", unsafe_allow_html=True)
                g2.markdown(f"<div class='metric-box'>Harga Wajar Murni (Graham)<br><span style='color:#10b981; font-size:20px;'>Rp {round(fair_price_graham):,}</span></div>", unsafe_allow_html=True)
                
                if not pd.isna(mos_graham):
                    mos_color = "#10b981" if mos_graham > 20 else ("#d97706" if mos_graham >= 0 else "#dc2626")
                    g3.markdown(f"<div class='metric-box'>Diskon Pasar (MoS)<br><span style='color:{mos_color}; font-size:20px;'>{round(mos_graham, 2)} %</span></div>", unsafe_allow_html=True)
                    
                    st.markdown("<h4>📌 Penilaian Graham Style:</h4>", unsafe_allow_html=True)
                    if mos_graham > 25:
                        st.success(f"🟢 **SANGAT DISKON:** Harga aset nyata jauh di atas harga pasar. Bagus untuk investasi jangka panjang dengan proteksi penurunan yang kuat.")
                    elif mos_graham >= 0:
                        st.info("🟡 **FAIR VALUE:** Harga saham mencerminkan kapasitas nilai buku saat ini secara wajar.")
                    else:
                        st.error("🔴 **OVERVALUED:** Harga pasar saat ini sudah terlalu premium dibanding valuasi nilai buku aset bersihnya.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            # ------------------------------------------
            # TAB 2: BUFFETT STYLE
            # ------------------------------------------
            with tab2:
                st.markdown("<div class='report-card' style='border-left-color: #2563eb;'>", unsafe_allow_html=True)
                st.write("### 🦅 Harga Maksimal Layak Beli (Buffett Conservative)")
                st.caption("Fokus: Memotong langsung harga wajar masa depan dengan batas pengaman (MoS 20%) untuk mengunci profit maksimum.")
                
                # Formula simulasi Buffett Style (Menerapkan diskon pengaman ketat dari nilai Graham dasar atau kelayakan PE)
                if not pd.isna(fair_price_graham):
                    # Mengunci langsung batas beli aman dengan diskon 20% dari target jangka panjang
                    buffett_buy_limit = fair_price_graham * 0.80
                    is_worth_buy = current_price < buffett_buy_limit
                    potensi_diskon_buffett = ((buffett_buy_limit - current_price) / buffett_buy_limit) * 100
                else:
                    buffett_buy_limit = np.nan
                    is_worth_buy = False
                
                b1, b2, b3 = st.columns(3)
                b1.markdown(f"<div class='metric-box'>Harga Saat Ini<br><span style='color:#0f172a; font-size:20px;'>Rp {current_price:,}</span></div>", unsafe_allow_html=True)
                b2.markdown(f"<div class='metric-box'>Batas Maksimal Beli Aman<br><span style='color:#2563eb; font-size:20px;'>Rp {round(buffett_buy_limit):,}</span></div>", unsafe_allow_html=True)
                
                if is_worth_buy:
                    b3.markdown(f"<div class='metric-box'>Status Sinyal Beli<br><span style='color:#16a34a; font-size:20px;'>🟢 UNDERVALUE</span></div>", unsafe_allow_html=True)
                    st.success(f"🟢 **LAYAK EKSEKUSI:** Harga pasar saat ini berada di bawah batas maksimal beli psikologis Anda. Tersedia ekstra diskon sebesar **{round(potensi_diskon_buffett, 1)}%** dari batas aman Buffett.")
                else:
                    b3.markdown(f"<div class='metric-box'>Status Sinyal Beli<br><span style='color:#dc2626; font-size:20px;'>🔴 KEMAHALAN</span></div>", unsafe_allow_html=True)
                    st.error("🔴 **TUNGGU DULU (Wait):** Harga saat ini sudah melampaui batas aman beli konservatif. Disarankan tunggu koreksi kembali mendekati area batas bawah.")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Parameter Kesehatan Bisnis Standar Buffett (>15% ROE)
                st.write("#### 🏥 Cek Kesehatan Finansial Perusahaan:")
                h1, h2 = st.columns(2)
                if not pd.isna(roe) and roe > 0.15:
                    h1.success(f"✅ **ROE SANGAT SEHAT ({round(roe*100, 2)}%):** Memenuhi standar emas Warren Buffett (>15%). Perusahaan sangat efisien menghasilkan laba bersih.")
                else:
                    h1.warning(f"⚠️ **ROE MODERAT ({round(roe*100, 2)}%):** Efisiensi modal berada di bawah standar emas 15%.")
                    
                if not pd.isna(rev_growth) and rev_growth > 0.10:
                    h2.success(f"✅ **PERTUMBUHAN KUAT ({round(rev_growth*100, 2)}%):** Bisnis memiliki keunggulan kompetitif ekonomi (*Moat*) sehingga omset terus membesar.")
                else:
                    h2.info(f"ℹ️ **PERTUMBUHAN STABIL ({round(rev_growth*100, 2)}%):** Pertumbuhan berjalan konstan namun cenderung melambat.")

            # ------------------------------------------
            # TAB 3: RADAR AKUMULASI & KATALIS
            # ------------------------------------------
            with tab3:
                st.write("### ⚡ Deteksi Arus Kas Pasar & Berita Penggerak")
                df_hist = ticker.history(period="6mo")
                
                if len(df_hist) >= 50:
                    df_hist['Avg_Vol_20'] = df_hist['Volume'].rolling(window=20).mean()
                    df_hist['MA50'] = df_hist['Close'].rolling(window=50).mean()
                    
                    latest_row = df_hist.iloc[-1]
                    vol_ratio = latest_row['Volume'] / latest_row['Avg_Vol_20'] if latest_row['Avg_Vol_20'] > 0 else 0
                    ma50_val = latest_row['MA50']
                    
                    r1, r2 = st.columns(2)
                    r1.metric("Volume Ratio Hari Ini (Proxy Bandar)", f"{round(vol_ratio, 2)} x lipat")
                    r2.metric("Arah Tren Harga Jangka Menengah", "BULLISH 📈" if current_price > ma50_val else "BEARISH 📉")
                    
                    if current_price < ma50_val and vol_ratio >= 1.5:
                        st.warning("⚠️ **AKUMULASI DI HARGA BAWAH (Buy on Weakness):** Tren harga grafik menurun, tetapi terjadi lonjakan transaksi sangat besar. Pola ini valid sebagai indikator bahwa institusi besar/asing sedang menyerap barang di harga murah secara masif.")
                    elif current_price > ma50_val and vol_ratio >= 1.5:
                        st.success("🎯 **STRONG ENTRY POINT:** Harga bergerak naik naik dikonfirmasi dengan dorongan volume akumulasi yang kuat. Waktu terbaik untuk ikut masuk pasar.")
                    else:
                        st.info("📊 **FASING WATCHLIST:** Transaksi harian berjalan normal. Anda bisa fokus melakukan akumulasi secara berkala (cicil dingin).")
                
                # Live News Scraper Katalis
                st.write("---")
                st.write("#### 📰 Berita Pasar & Info Aksi Korporasi Terkini:")
                news_list = ticker.news
                if news_list:
                    for news in news_list[:3]:
                        title = news.get('title', 'N/A')
                        publisher = news.get('publisher', 'N/A')
                        link = news.get('link', '#')
                        is_catalyst = any(k in title.lower() for k in ['rups', 'dividen', 'dividend', 'rights issue', 'laba', 'profit'])
                        
                        if is_catalyst:
                            st.markdown(f"<div class='catalyst-card'><strong>🚨 KATALIS UTAMA: <a href='{link}' target='_blank'>{title}</a></strong><br><small>Sumber: {publisher}</small></div>", unsafe_allow_html=True)
                        else:
                            st.write(f"🔹 **[{publisher}]** [{title}]({link})")
                else:
                    st.info("Tidak ada berita aksi korporat material terbaru yang terdeteksi.")

        except Exception as e:
            st.error(f"Gagal memproses data multi-dimensi: {str(e)}")
