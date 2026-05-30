import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN UI/UX
st.set_page_config(
    page_title="IDX Institutional Stock Intelligence",
    page_icon="💎",
    layout="wide"
)

# Custom Styling Premium
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 25px; border-left: 6px solid #1e3a8a; }
    .pro-box { background-color: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 5px solid #16a34a; margin-bottom: 10px; font-size: 14px; }
    .con-box { background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 5px solid #dc2626; margin-bottom: 10px; font-size: 14px; }
    .catalyst-card { background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 5px solid #d97706; margin-bottom: 10px; }
    .metric-box { background-color: #f1f5f9; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    h2 { color: #1e3a8a; font-weight: 700; margin-bottom: 15px; }
    h3 { color: #0f172a; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.title("💎 IDX Institutional Stock Intelligence")
st.caption("Sistem Analisis Multi-Sektor: Deteksi Parameter Spesifik Perbankan, Komoditas, Properti, dan Ritel")
st.write("---")

# 2. INPUT KODE SAHAM
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_input = st.text_input("✍️ Masukkan Kode Saham IDX (Contoh: BBRI, BRPT, ADRO, PWON):", value="BBRI").strip().upper()

if ticker_input:
    ticker_sym = f"{ticker_input}.JK"
    
    with st.spinner(f"Menjalankan kecerdasan buatan multi-sektor untuk {ticker_input}..."):
        try:
            ticker = yf.Ticker(ticker_sym)
            info = ticker.info
            
            if 'longName' not in info:
                st.error(f"❌ Kode saham '{ticker_input}' tidak valid di Bursa Efek Indonesia.")
                st.stop()
                
            # --- DATA RETRIEVAL & CLEANING ---
            current_price = info.get('currentPrice', info.get('regularMarketPrice', np.nan))
            company_name = info.get('longName', 'N/A')
            market_cap = info.get('marketCap', 0) / 1e9
            sector = info.get('sector', 'N/A')
            
            eps = info.get('trailingEps', np.nan)
            pe_ratio = info.get('trailingPE', np.nan)
            roe = info.get('returnOnEquity', np.nan)
            rev_growth = info.get('revenueGrowth', np.nan)
            der = info.get('debtToEquity', np.nan)
            
            # Pengaman Dividend Yield (Bebas Bug 1417%)
            raw_div_yield = info.get('dividendYield', 0)
            div_yield = (raw_div_yield / 100) if raw_div_yield and raw_div_yield > 1 else (raw_div_yield if raw_div_yield else 0)
            
            # Perbaikan Penghitungan Nilai Buku Manual
            total_equity = info.get('totalAssets', 0) - info.get('totalLiabilities', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            bvps = total_equity / shares_outstanding if shares_outstanding > 0 and total_equity > 0 else info.get('bookValue', np.nan)
            pbv = current_price / bvps if bvps > 0 else info.get('priceToBook', np.nan)
            
            df_hist = ticker.history(period="6mo")
            
            # TAMPILAN HEADER
            st.subheader(f"📊 {ticker_input} - {company_name}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga Pasar Terakhir", f"Rp {current_price:,}" if not pd.isna(current_price) else "N/A")
            c2.metric("Market Capitalization", f"Rp {market_cap:,.2f} Miliar")
            c3.metric("Sektor Industri", sector)
            st.write("---")
            
            # ==========================================
            # 3. AUTOMATIC SECTOR CLASSIFIER ENGINE
            # ==========================================
            is_banking = sector == 'Financial Services'
            is_mining = sector in ['Basic Materials', 'Energy']
            is_property = sector == 'Real Estate'
            
            if (not pd.isna(roe) and roe > 0.13 and not pd.isna(rev_growth) and rev_growth > 0.05) or (is_banking and market_cap > 50000):
                is_long_term = True
                char_tag, char_color = "🏛️ INVESTASI JANGKA PANJANG (Core Asset)", "#10b981"
            else:
                is_long_term = False
                char_tag, char_color = "⚡ TRADING JANGKA PENDEK (Tactical Momentum)", "#6366f1"
                
            st.markdown(f"""
            <div class='report-card' style='border-left-color: {char_color}; background-color: #fdfdfd;'>
                <h3>🎯 Karakteristik Gaya Investasi</h3>
                <strong style='color: {char_color}; font-size: 16px;'>{char_tag}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["📊 Sistem Analisis & Valuasi Dinamis", "📰 Live Catalyst & Corporate Action"])
            
            with tab1:
                col_left, col_right = st.columns([3, 2])
                
                with col_left:
                    if is_long_term:
                        st.write("### 🏛️ Valuasi Intrinsik Model Graham & Buffett")
                        fair_price = np.sqrt(22.5 * eps * bvps) if (eps and bvps and eps > 0 and bvps > 0) else (eps * 12 if eps and eps > 0 else current_price * 1.15)
                        buffett_buy_limit = fair_price * 0.80
                        mos = ((fair_price - current_price) / fair_price) * 100
                        
                        v1, v2, v3 = st.columns(3)
                        v1.markdown(f"<div class='metric-box'>Harga Wajar Intrinsik<br><span style='color:#16a34a;'>Rp {round(fair_price):,}</span></div>", unsafe_allow_html=True)
                        v2.markdown(f"<div class='metric-box'>Batas Maksimal Beli<br><span style='color:#2563eb;'>Rp {round(buffett_buy_limit):,}</span></div>", unsafe_allow_html=True)
                        v3.markdown(f"<div class='metric-box'>Margin of Safety (MoS)<br><span style='color:#ca8a04;'>{round(mos, 1)} %</span></div>", unsafe_allow_html=True)
                    else:
                        st.write("### ⚡ Batas Manajemen Risiko Trading Kilat")
                        volatility = df_hist['Close'].pct_change().std() if len(df_hist) >= 20 else 0.03
                        risk_factor = max(volatility * 2, 0.05)
                        stop_loss = current_price * (1 - risk_factor)
                        take_profit = current_price * (1 + (risk_factor * 2))
                        
                        t1, t2, t3 = st.columns(3)
                        t1.markdown(f"<div class='metric-box'>Harga Area Entry<br><span>Rp {current_price:,}</span></div>", unsafe_allow_html=True)
                        t2.markdown(f"<div class='metric-box'>Target Profit (TP)<br><span style='color:#16a34a;'>Rp {round(take_profit):,} (+{round(risk_factor*2*100)}%)</span></div>", unsafe_allow_html=True)
                        t3.markdown(f"<div class='metric-box'>Stop Loss (SL)<br><span style='color:#dc2626;'>Rp {round(stop_loss):,} (-{round(risk_factor*100)}%)</span></div>", unsafe_allow_html=True)
                
                with col_right:
                    st.write("### 🏥 Parameter Umum Finansial")
                    f_df = pd.DataFrame({
                        "Metrik Utama": ["PBV Ratio", "PE Ratio", "ROE (%)", "Revenue Growth (%)", "Dividend Yield (%)"],
                        "Nilai": [
                            f"{round(pbv, 2)} x" if not pd.isna(pbv) else "N/A",
                            f"{round(pe_ratio, 2)} x" if not pd.isna(pe_ratio) else "N/A",
                            f"{round(roe*100, 2)} %" if not pd.isna(roe) else "N/A",
                            f"{round(rev_growth*100, 2)} %" if not pd.isna(rev_growth) else "0.0 %",
                            f"{round(div_yield*100, 2)} %" if div_yield > 0 else "0.0 %"
                        ]
                    })
                    st.dataframe(f_df, use_container_width=True, hide_index=True)
                
                st.write("---")
                
                # ==========================================
                # 4. ADVANCED MATRIX ANALYSIS (SECTOR SMART)
                # ==========================================
                st.write("### 🔍 Matriks Intelijen Risiko & Peluang Spesifik Sektor")
                
                pros_list = []
                cons_list = []
                
                # --- LOGIKA KREATIF AMBIL DATA KHUSUS SEKTOR ---
                if is_banking:
                    # Ambil proksi parameter bank: NIM, Efisiensi Biaya (Makin besar ROE biasanya NIM & CASA kuat)
                    pros_list.append(f"**Struktur Likuiditas Perbankan Kuat:** Sebagai emiten finansial besar, efisiensi dana murah (CASA Proxy) sangat optimal tercermin dari kapasitas ROE Bank yang menyentuh {round(roe*100,1)}%.")
                    # Risiko Perbankan: Pencadangan NPL (Non-Performing Loan) jika ekonomi melambat
                    cons_list.append("**Waspadai Sinyal Risiko NPL Silang:** Pada siklus suku bunga ketat, bank wajib mempertebal pencadangan pencatatan restrukturisasi kredit untuk mencegah lonjakan kredit macet.")
                    
                elif is_mining:
                    gross_margin = info.get('grossMargins', 0) * 100
                    if gross_margin > 25:
                        pros_list.append(f"**Gross Profit Margin Tambang Prima ({round(gross_margin,1)}%):** Perusahaan memiliki biaya produksi hulu yang murah, sangat diuntungkan jika harga komoditas global mengalami *Supercycle*.")
                    else:
                        cons_list.append(f"**Margin Produksi Tambang Tipis ({round(gross_margin,1)}%):** Rentan merugi massal jika harga komoditas acuan dunia mendadak anjlok.")
                    cons_list.append("**Risiko Tinggi Beban CapEx:** Sektor tambang sangat sensitif terhadap pengeluaran modal berat untuk peremajaan alat dan eksplorasi lahan baru.")
                    
                elif is_property:
                    # Properti mengandalkan uang muka (Pre-sales) yang dicatat di kewajiban lancar (Unearned Revenue)
                    pros_list.append("**Potensi Pengakuan Pendapatan Pre-Sales:** Perusahaan di sektor real estate diuntungkan jika serah terima proyek berjalan lancar sesuai target kuartalan.")
                    if not pd.isna(der) and der > 120:
                        cons_list.append(f"**Leverage Properti Berisiko Tinggi (DER: {round(der,1)}%):** Beban utang obligasi pembangunan proyek sangat sensitif terhadap fluktuasi suku bunga acuan BI.")
                
                else:
                    # Sektor Konsumer / Ritel / Lainnya
                    operating_margin = info.get('operatingMargins', 0) * 100
                    if operating_margin > 12:
                        pros_list.append(f"**Daya Saing Sektor Ritel Kuat (Operating Margin: {round(operating_margin,1)}%):** Perusahaan mampu melakukan *pricing power* (menaikkan harga jual produk tanpa kehilangan konsumen).")
                    else:
                        cons_list.append(f"**Margin Operasional Konsumer Tertekan ({round(operating_margin,1)}%):** Rentan menderita akibat penurunan daya beli masyarakat atau lonjakan biaya inflasi bahan baku.")

                # --- PARAMETER TEKNIKAL UMUM ---
                if len(df_hist) >= 20:
                    df_hist['Avg_Vol_20'] = df_hist['Volume'].rolling(window=20).mean()
                    df_hist['MA50'] = df_hist['Close'].rolling(window=50).mean()
                    latest_row = df_hist.iloc[-1]
                    vol_ratio = latest_row['Volume'] / latest_row['Avg_Vol_20'] if latest_row['Avg_Vol_20'] > 0 else 1
                    
                    if vol_ratio >= 1.5:
                        pros_list.append(f"**Deteksi Akumulasi Volume Masif ({round(vol_ratio,1)}x):** Volume perdagangan melonjak tajam harian, mengindikasikan masuknya *Big Money* atau Bandar.")
                    if current_price < latest_row['MA50']:
                        cons_list.append("**Tren Grafik Bearish (Di Bawah MA50):** Harga jangka menengah bergerak turun, hindari melakukan pembelian dalam satu porsi besar sekaligus.")
                
                # Render Tampilan Matriks Risiko-Peluang
                col_pro, col_con = st.columns(2)
                with col_pro:
                    st.write("#### 🟢 Faktor Peluang (Rasio Positif):")
                    for pro in pros_list: st.markdown(f"<div class='pro-box'>{pro}</div>", unsafe_allow_html=True)
                with col_con:
                    st.write("#### ⚠️ Faktor Risiko (Rasio Negatif):")
                    for con in cons_list: st.markdown(f"<div class='con-box'>{con}</div>", unsafe_allow_html=True)
                        
            with tab2:
                # LIVE NEWS CATALYST SCRAPER
                st.write("### 📰 Berita Pasar & Info Aksi Korporasi")
                news_list = ticker.news
                if news_list:
                    for news in news_list[:4]:
                        title = news.get('title', 'N/A')
                        publisher = news.get('publisher', 'N/A')
                        link = news.get('link', '#')
                        is_catalyst = any(k in title.lower() for k in ['rups', 'dividen', 'dividend', 'rights issue', 'laba', 'profit', 'tumbuh'])
                        
                        if is_catalyst:
                            st.markdown(f"<div class='catalyst-card'><strong>🚨 KATALIS UTAMA: <a href='{link}' target='_blank'>{title}</a></strong><br><small>Sumber: {publisher}</small></div>", unsafe_allow_html=True)
                        else:
                            st.write(f"🔹 **[{publisher}]** [{title}]({link})")
                else:
                    st.info("Tidak ada berita aksi korporasi terbaru.")

        except Exception as e:
            st.error(f"Sistem gagal mengekstrak data komprehensif emiten: {str(e)}")
