# -*- coding: utf-8 -*-
"""DASHBOARD GIÁM SÁT TỔN THẤT ĐIỆN NĂNG - ĐIỆN LỰC CHƯ PĂH

Giao diện Streamlit thu nhỏ gọn, loại bỏ thẻ "Nhận Đầu Nguồn", tối ưu khoảng
trống đỉnh trang, hiển thị sắc nét tiêu đề KPI và tự động tính toán số liệu.
"""

import logging
from pathlib import Path
import warnings
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Tắt các cảnh báo không cần thiết và ẩn log ngắt kết nối WebSocket asyncio trên Windows
warnings.filterwarnings("ignore")
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# 1. CẤU HÌNH TRANG & CẤU TRÚC GIAO DIỆN
st.set_page_config(
    page_title="HỆ THỐNG GIÁM SÁT TTĐN - ĐIỆN LỰC CHƯ PĂH",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. TÙY CHỈNH GIAO DIỆN CSS MODERN EVN COMPACT (SẮC NÉT & TỐI ƯU HIỂN THỊ)
st.markdown(
    """
<style>
    /* Xóa/Giảm khoảng trống lề trên cùng của trang chính */
    div[data-testid="stBlockContainer"], .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Xóa/Giảm khoảng trống lề trên cùng của Sidebar */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem !important;
    }

    /* Thu nhỏ/ẩn thanh Header mặc định của Streamlit */
    header[data-testid="stHeader"] {
        height: 1rem !important;
        background: transparent !important;
    }

    /* Header chính Banner EVN - Thu nhỏ chiều cao */
    .main-header {
        background: linear-gradient(135deg, #004e92 0%, #000428 100%);
        padding: 12px 18px !important;
        border-radius: 8px;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 12px !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: #ffffff !important;
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }
    .main-header p {
        color: #e2e8f0 !important;
        font-size: 0.88rem !important;
        margin: 3px 0 0 0 !important;
    }
    
    /* Ép khung thẻ KPI nhỏ gọn (nền trắng nét rõ cả Dark/Light mode) */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border-left: 4px solid #004E92 !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    
    /* Tiêu đề thẻ KPI (Label) - Ép màu xanh EVN đậm, nét chữ rõ ràng trên mọi trình duyệt */
    div[data-testid="stMetricLabel"], 
    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricLabel"] p,
    label[data-testid="stMetricLabel"] {
        color: #004E92 !important;
        font-size: 0.95rem !important;
        font-weight: 800 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #004E92 !important;
    }
    
    /* Giá trị số thẻ KPI (Value) - Đen đậm chuẩn nét */
    div[data-testid="stMetricValue"], 
    div[data-testid="stMetricValue"] *,
    div[data-testid="stMetricValue"] div {
        color: #0F172A !important;
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    
    /* Tiêu đề phân khu */
    .section-title {
        color: #004E92;
        font-weight: 700;
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 4px;
    }

    /* Thu nhỏ chiều rộng & padding của Sidebar (Bộ Lọc) */
    section[data-testid="stSidebar"] {
        width: 240px !important;
    }
    section[data-testid="stSidebar"] > div {
        padding: 1.2rem 0.8rem !important;
    }
    /* Thu nhỏ tiêu đề và chữ trong Sidebar */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        font-size: 1.05rem !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        font-size: 0.82rem !important;
    }
    /* Thu nhỏ chiều cao & padding ô Selectbox trong Sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        font-size: 0.85rem !important;
    }
    section[data-testid="stSidebar"] div[role="button"] {
        padding-top: 4px !important;
        padding-bottom: 4px !important;
        min-height: 34px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Banner Header
st.markdown(
    """
<div class="main-header">
    <h1>⚡ HỆ THỐNG GIÁM SÁT TỔN THẤT ĐIỆN NĂNG TỰ ĐỘNG</h1>
    <p>CÔNG TY ĐIỆN LỰC GIA LAI — ĐIỆN LỰC CHƯ PĂH</p>
</div>
""",
    unsafe_allow_html=True,
)

# 3. QUẢN LÝ THƯ MỤC DỮ LIỆU
BASE_DIR = Path(__file__).parent.absolute() / "DATA_OUTPUT"

available_dates = []
if BASE_DIR.exists():
    for year_dir in BASE_DIR.iterdir():
        if year_dir.is_dir():
            for month_dir in year_dir.iterdir():
                if month_dir.is_dir():
                    for day_dir in month_dir.iterdir():
                        if day_dir.is_dir():
                            available_dates.append(
                                f"{year_dir.name}-{month_dir.name}-{day_dir.name}"
                            )

available_dates.sort(reverse=True)

if not available_dates:
    st.error(
        "⚠️ Chưa tìm thấy dữ liệu trong thư mục `DATA_OUTPUT/`. Vui lòng chạy"
        " file Python tính toán trước!"
    )
    st.stop()

# Sidebar Bộ Lọc
st.sidebar.title("🔍 Bộ Lọc Dữ Liệu")
selected_date = st.sidebar.selectbox("📅 Chọn Ngày Báo Cáo:", available_dates)
y, m, d = selected_date.split("-")
path_ngay = BASE_DIR / y / m / d

# Đường dẫn file dữ liệu
file_b4 = path_ngay / f"Bieu4_TongHop_TT_{selected_date}.xlsx"
file_tba = path_ngay / f"ChiTiet_DauTram_TBA_{selected_date}.xlsx"
file_am = path_ngay / f"DanhSach_CanhBao_DoiCongTo_Am_{selected_date}.xlsx"
file_xt = path_ngay / f"BaoCao_XuatTuyen_TrungThe_{selected_date}.xlsx"

# 4. KHU VỰC THẺ KPI TỔNG HỢP (GỒM 3 THẺ: TRUNG ÁP, HẠ ÁP, TOÀN ĐƠN VỊ)
if file_b4.exists():
    df_b4 = pd.read_excel(file_b4, skiprows=3)
    r = df_b4.iloc[0]

    a_nhan_dn = float(r.iloc[2]) if pd.notnull(r.iloc[2]) else 0.0
    a_nhan_kh = float(r.iloc[3]) if pd.notnull(r.iloc[3]) else 0.0
    a_giao_ngay = float(r.iloc[4]) if pd.notnull(r.iloc[4]) else 0.0
    tt_ta_kwh = float(r.iloc[5]) if pd.notnull(r.iloc[5]) else 0.0
    tt_ta_pct = float(r.iloc[6]) if pd.notnull(r.iloc[6]) else 0.0
    tt_ha_kwh = float(r.iloc[7]) if pd.notnull(r.iloc[7]) else 0.0
    tt_ha_pct = float(r.iloc[8]) if pd.notnull(r.iloc[8]) else 0.0

    if pd.notnull(r.iloc[9]):
        tt_tong_kwh = float(r.iloc[9])
    else:
        tt_tong_kwh = tt_ta_kwh + tt_ha_kwh

    tong_nhan = a_nhan_dn + a_nhan_kh - a_giao_ngay
    if pd.notnull(r.iloc[10]):
        tt_tong_pct = float(r.iloc[10])
    else:
        tt_tong_pct = (
            (tt_tong_kwh * 100 / tong_nhan) if tong_nhan > 0 else 0.0
        )

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "🔷 TTĐN Trung Áp",
        f"{tt_ta_kwh:,.0f} kWh",
        f"{tt_ta_pct:.2f}%",
        delta_color="inverse",
    )
    kpi2.metric(
        "🔶 TTĐN Hạ Áp",
        f"{tt_ha_kwh:,.0f} kWh",
        f"{tt_ha_pct:.2f}%",
        delta_color="inverse",
    )
    kpi3.metric(
        "🌐 TTĐN Toàn Đơn Vị",
        f"{tt_tong_kwh:,.0f} kWh",
        f"{tt_tong_pct:.2f}%",
        delta_color="inverse",
    )

# 5. CÁC TAB BÁO CÁO PHÂN TÍCH CHUYÊN SÂU
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Phân Tích Tổng Quan",
    "🏢 Chi Tiết Trạm TBA",
    "🔌 Xuất Tuyến Trung Thế",
    "⚠️ Cảnh Báo Anomaly",
])

with tab1:
    c_left, c_right = st.columns([5, 5])

    with c_left:
        st.markdown(
            "<div class='section-title'>📌 Tỷ Trọng Sản Lượng Tổn Thất"
            " (TA/HA)</div>",
            unsafe_allow_html=True,
        )
        if file_b4.exists():
            df_donut = pd.DataFrame({
                "Cấp Điện Áp": ["Trung Áp (TA)", "Hạ Áp (HA)"],
                "Sản Lượng Tổn Thất (kWh)": [tt_ta_kwh, tt_ha_kwh],
            })
            fig_donut = px.pie(
                df_donut,
                names="Cấp Điện Áp",
                values="Sản Lượng Tổn Thất (kWh)",
                hole=0.55,
                color="Cấp Điện Áp",
                color_discrete_map={
                    "Trung Áp (TA)": "#005A9C",
                    "Hạ Áp (HA)": "#E63946",
                },
            )
            fig_donut.update_traces(
                textposition="inside", textinfo="percent+label+value"
            )
            fig_donut.update_layout(margin=dict(t=15, b=15, l=15, r=15), height=290)
            st.plotly_chart(fig_donut, width="stretch")

    with c_right:
        st.markdown(
            "<div class='section-title'>🎯 Gauge Tỷ Lệ Tổn Thất Toàn Đơn Vị</div>",
            unsafe_allow_html=True,
        )
        val_gauge = tt_tong_pct if file_b4.exists() else 2.36
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=val_gauge,
                number={"suffix": "%", "font": {"size": 36}},
                gauge={
                    "axis": {"range": [0, 8]},
                    "bar": {"color": "#005A9C"},
                    "steps": [
                        {"range": [0, 2.5], "color": "#d4edda"},
                        {"range": [2.5, 4.5], "color": "#fff3cd"},
                        {"range": [4.5, 8], "color": "#f8d7da"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.8,
                        "value": 4.5,
                    },
                },
            )
        )
        fig_gauge.update_layout(margin=dict(t=25, b=10, l=20, r=20), height=290)
        st.plotly_chart(fig_gauge, width="stretch")

    if file_tba.exists():
        df_tba = pd.read_excel(file_tba)
        col_tt = [c for c in df_tba.columns if "%" in c or "Tỷ lệ" in c]
        col_sl = [c for c in df_tba.columns if "Sản lượng" in c or "kWh" in c]

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(
                "<div class='section-title'>📈 Tương Quan: Sản Lượng vs Tỷ Lệ Tổn"
                " Thất TBA</div>",
                unsafe_allow_html=True,
            )
            if col_tt and col_sl:
                fig_scat = px.scatter(
                    df_tba,
                    x=col_sl[0],
                    y=col_tt[0],
                    color=col_tt[0],
                    hover_name="Tên trạm/điểm đo",
                    color_continuous_scale="Reds",
                    labels={col_sl[0]: "Sản Lượng (kWh)", col_tt[0]: "Tỷ Lệ TT (%)"},
                )
                fig_scat.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_scat, width="stretch")

        with sc2:
            st.markdown(
                "<div class='section-title'>📊 Phân Bổ Tỷ Lệ Tổn Thất Các Trạm"
                " TBA</div>",
                unsafe_allow_html=True,
            )
            if col_tt:
                fig_hist = px.histogram(
                    df_tba,
                    x=col_tt[0],
                    nbins=25,
                    color_discrete_sequence=["#005A9C"],
                    labels={col_tt[0]: "Tỷ Lệ Tổn Thất (%)", "count": "Số Trạm"},
                )
                fig_hist.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_hist, width="stretch")

with tab2:
    if file_tba.exists():
        df_tba = pd.read_excel(file_tba)
        col_tt = [c for c in df_tba.columns if "%" in c or "Tỷ lệ" in c]

        st.markdown(
            "<div class='section-title'>🔴 Top 15 Trạm TBA Có Tỷ Lệ Tổn Thất Cao"
            " Nhất (>5%)</div>",
            unsafe_allow_html=True,
        )
        if col_tt:
            df_high = df_tba.sort_values(by=col_tt[0], ascending=False).head(15)
            fig_bar = px.bar(
                df_high,
                x="Mã trạm",
                y=col_tt[0],
                hover_data=["Tên trạm/điểm đo"],
                color=col_tt[0],
                color_continuous_scale="Reds",
                text_auto=".2f",
                labels={col_tt[0]: "Tỷ lệ TT (%)"},
            )
            fig_bar.update_layout(height=340)
            st.plotly_chart(fig_bar, width="stretch")

        st.markdown(
            "<div class='section-title'>📋 Danh Sách Tất Cả Trạm TBA Chi"
            " Tiết</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(df_tba, width="stretch", height=320)

with tab3:
    if file_xt.exists():
        df_xt = pd.read_excel(file_xt, skiprows=8)

        # Tự động tính toán lại Tỷ lệ tổn thất (%) nếu ô Excel chứa công thức trả về NaN
        col_nhan = pd.to_numeric(df_xt.iloc[:, 3], errors="coerce").fillna(0)
        col_giao = pd.to_numeric(df_xt.iloc[:, 4], errors="coerce").fillna(0)
        col_tp8 = pd.to_numeric(df_xt.iloc[:, 7], errors="coerce").fillna(0)
        col_tp9 = pd.to_numeric(df_xt.iloc[:, 8], errors="coerce").fillna(0)
        col_tp10 = pd.to_numeric(df_xt.iloc[:, 9], errors="coerce").fillna(0)
        col_tp11 = pd.to_numeric(df_xt.iloc[:, 10], errors="coerce").fillna(0)

        col_tp_tong = col_tp8 + col_tp9 + col_tp10 + col_tp11
        tt_kwh = col_nhan - col_giao - col_tp_tong
        tt_pct_calc = (tt_kwh * 100 / col_nhan).where(col_nhan > 0, 0)

        val_col12 = pd.to_numeric(df_xt.iloc[:, 12], errors="coerce")
        if val_col12.isnull().all():
            df_xt["Tỷ Lệ Tổn Thất (%)"] = tt_pct_calc
        else:
            df_xt["Tỷ Lệ Tổn Thất (%)"] = val_col12.fillna(tt_pct_calc)

        df_xt_clean = df_xt.dropna(subset=[df_xt.columns[1]]).copy()
        df_xt_clean = df_xt_clean[
            ~df_xt_clean[df_xt_clean.columns[1]].astype(str).str.contains("TỔNG")
        ]

        st.markdown(
            "<div class='section-title'>⚡ Tổn Thất Điện Năng Theo Xuất Tuyến"
            " Trung Thế</div>",
            unsafe_allow_html=True,
        )
        fig_xt = px.bar(
            df_xt_clean,
            x=df_xt_clean.columns[1],
            y="Tỷ Lệ Tổn Thất (%)",
            color="Tỷ Lệ Tổn Thất (%)",
            color_continuous_scale="Tealgrn",
            text_auto=".2f",
            labels={
                df_xt_clean.columns[1]: "Lộ Đường Dây",
                "Tỷ Lệ Tổn Thất (%)": "Tỷ Lệ Tổn Thất (%)",
            },
        )
        fig_xt.update_layout(height=380, xaxis_tickangle=-35)
        st.plotly_chart(fig_xt, width="stretch")

with tab4:
    st.markdown(
        "<div class='section-title'>⚠️ Danh Sách Công Tơ Cảnh Báo Sản Lượng"
        " Âm</div>",
        unsafe_allow_html=True,
    )
    if file_am.exists():
        df_am = pd.read_excel(file_am)
        if not df_am.empty:
            st.dataframe(df_am, width="stretch")
        else:
            st.success("🎉 Không ghi nhận trường hợp công tơ bị âm sản lượng.")