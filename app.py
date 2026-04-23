"""
=============================================================
  HỆ THỐNG AI AGENT HỖ TRỢ LUẬT SƯ
  Module 1: Nghiên cứu hồ sơ & Soạn thảo văn bản
=============================================================
Cài đặt (chạy 1 lần trong Command Prompt):
  pip install streamlit anthropic python-docx pypdf2 pillow

Chạy app:
  streamlit run app.py
=============================================================
"""

import streamlit as st
import anthropic
import json
import base64
import io
import os
import re
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import PyPDF2

# ─────────────────────────────────────────────
#  CẤU HÌNH TÀI KHOẢN (thêm luật sư mới ở đây)
# ─────────────────────────────────────────────
TAI_KHOAN = {
    "ls.hoang": {
        "mat_khau": "Hoang@2026",
        "ho_ten":   "Luật sư Nguyễn Minh Hoàng",
        "chuc_vu":  "Luật sư thành viên",
        "vai_tro":  "luat_su",
    },
    "ls.thang": {
        "mat_khau": "Thang@2026",
        "ho_ten":   "Luật sư Trịnh Chiến Thắng",
        "chuc_vu":  "Luật sư thành viên",
        "vai_tro":  "luat_su",
    },
    "ls.lan": {
        "mat_khau": "Lan@2026",
        "ho_ten":   "Luật sư Nguyễn Thị Thanh Lan",
        "chuc_vu":  "Luật sư thành viên",
        "vai_tro":  "luat_su",
    },
    "ls.phuong": {
        "mat_khau": "Phuong@2026",
        "ho_ten":   "Luật sư Lê Thuý Phượng",
        "chuc_vu":  "Luật sư thành viên",
        "vai_tro":  "luat_su",
    },
    "ls.nga": {
        "mat_khau": "Nga@2026",
        "ho_ten":   "Luật sư Phạm Thị Nga",
        "chuc_vu":  "Luật sư thành viên",
        "vai_tro":  "luat_su",
    },
    "ls.dong": {
        "mat_khau": "Dong@2026",
        "ho_ten":   "Luật sư Lê Viễn Đông",
        "chuc_vu":  "Luật sư thành viên",
        "vai_tro":  "luat_su",
    },
    "admin": {
        "mat_khau": "Admin@MTL2026",
        "ho_ten":   "Quản trị viên",
        "chuc_vu":  "Quản lý hệ thống",
        "vai_tro":  "quan_tri",
    },
}

TEN_CONG_TY = "CÔNG TY LUẬT TNHH MINH TÚ"
DIA_CHI_CT  = "Trụ sở: 4/9 Đường số 3 Cư Xá Đô Thành, Phường Bàn Cờ, TP. Hồ Chí Minh"
DIA_CHI_DN  = "CN Đà Nẵng: 81 Xô Viết Nghệ Tĩnh, Phường Cẩm Lệ, TP. Đà Nẵng"
SBT_CT      = "Hotline: 19000031 | Website: luatminhtu.vn | Email: info.luatminhtu@gmail.com"

# ─────────────────────────────────────────────
#  KHỞI TẠO TRANG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MTL Legal Agent Premium",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Màu thương hiệu MTL ──
MTL_NAVY  = "#1E4D82"   # xanh navy (ô M, L)
MTL_GOLD  = "#A8874A"   # vàng đồng (ô T, đường kẻ)
MTL_NAVY2 = "#163960"   # navy đậm hơn cho gradient
MTL_GOLD2 = "#C9A96E"   # vàng sáng hơn cho hover

st.markdown(f"""
<style>
/* ── Ẩn header/footer mặc định của Streamlit ── */
#MainMenu, footer, header {{ visibility: hidden; }}

/* ── Sidebar Premium ── */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {MTL_NAVY2} 0%, {MTL_NAVY} 60%, #122d50 100%);
    border-right: 2px solid {MTL_GOLD};
}}
section[data-testid="stSidebar"] * {{ color: #e8eef5 !important; }}
section[data-testid="stSidebar"] input {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid {MTL_GOLD} !important;
    color: white !important;
    border-radius: 6px !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: {MTL_GOLD}44 !important;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: 1px solid {MTL_GOLD} !important;
    color: {MTL_GOLD} !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.2s;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {MTL_GOLD} !important;
    color: white !important;
}}

/* ── Header chính ── */
.mtl-header {{
    background: linear-gradient(135deg, {MTL_NAVY2} 0%, {MTL_NAVY} 70%, #1a5592 100%);
    border-bottom: 3px solid {MTL_GOLD};
    padding: 0;
    border-radius: 12px;
    margin-bottom: 24px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(30,77,130,0.25);
}}
.mtl-header-inner {{
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 18px 28px;
}}
.mtl-logo-block {{
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
}}
.mtl-box {{
    width: 40px; height: 40px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 700; color: white;
    font-family: Georgia, serif;
    letter-spacing: -1px;
}}
.mtl-box-navy {{ background: {MTL_NAVY2}; border: 1.5px solid rgba(255,255,255,0.3); }}
.mtl-box-gold  {{ background: {MTL_GOLD};  border: 1.5px solid rgba(255,255,255,0.3); }}
.mtl-divider {{
    width: 2px; height: 52px;
    background: linear-gradient(to bottom, transparent, {MTL_GOLD}, transparent);
    margin: 0 12px;
}}
.mtl-title-block h1 {{
    margin: 0; color: white;
    font-size: 1.25rem; font-weight: 700; letter-spacing: 0.5px;
}}
.mtl-title-block .mtl-sub {{
    margin: 3px 0 0; color: {MTL_GOLD2};
    font-size: 0.82rem; letter-spacing: 0.3px;
}}
.mtl-user-badge {{
    margin-left: auto;
    background: rgba(255,255,255,0.08);
    border: 1px solid {MTL_GOLD}66;
    border-radius: 8px;
    padding: 8px 16px;
    text-align: right;
}}
.mtl-user-badge .name {{ color: white; font-weight: 600; font-size: 0.9rem; }}
.mtl-user-badge .role {{ color: {MTL_GOLD2}; font-size: 0.78rem; }}
.mtl-user-badge .date {{ color: rgba(255,255,255,0.5); font-size: 0.72rem; margin-top: 2px; }}

/* ── Trang đăng nhập ── */
.login-card {{
    background: white;
    border-radius: 16px;
    padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(30,77,130,0.15);
    border-top: 4px solid {MTL_GOLD};
    max-width: 420px;
    margin: 0 auto;
}}
.login-logo {{
    display: flex; align-items: center; justify-content: center; gap: 4px;
    margin-bottom: 6px;
}}
.login-title {{ text-align: center; color: {MTL_NAVY}; font-size: 1.3rem; font-weight: 700; margin: 0 0 4px; }}
.login-sub   {{ text-align: center; color: {MTL_GOLD}; font-size: 0.82rem; letter-spacing: 1px; margin: 0 0 24px; text-transform: uppercase; font-weight: 600; }}

/* ── Kết quả phân tích ── */
.result-box {{
    background: linear-gradient(135deg, #f0f5ff 0%, #fafbff 100%);
    border-left: 4px solid {MTL_NAVY};
    border-top: 1px solid #e0e8f5;
    border-right: 1px solid #e0e8f5;
    border-bottom: 1px solid #e0e8f5;
    padding: 20px 24px;
    border-radius: 0 10px 10px 0;
    margin-top: 16px;
    line-height: 1.75;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 2px solid {MTL_GOLD}44;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
}}
.stTabs [aria-selected="true"] {{
    background: {MTL_NAVY} !important;
    color: white !important;
    border-bottom: 2px solid {MTL_GOLD} !important;
}}

/* ── Buttons ── */
.stButton > button {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {MTL_NAVY} 0%, {MTL_NAVY2} 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(30,77,130,0.3) !important;
}}
.stButton > button[kind="primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(30,77,130,0.4) !important;
}}

/* ── Upload box ── */
.stFileUploader > div {{
    border: 2px dashed {MTL_GOLD}88 !important;
    border-radius: 10px !important;
    background: rgba(168,135,74,0.04) !important;
}}

/* Fix chữ trắng trong sidebar uploader */
section[data-testid="stSidebar"] .stFileUploader {{
    background: transparent !important;
}}
section[data-testid="stSidebar"] .stFileUploader > div {{
    background: rgba(255,255,255,0.06) !important;
    border: 2px dashed {MTL_GOLD}99 !important;
    border-radius: 10px !important;
}}
section[data-testid="stSidebar"] .stFileUploader label,
section[data-testid="stSidebar"] .stFileUploader span,
section[data-testid="stSidebar"] .stFileUploader p,
section[data-testid="stSidebar"] .stFileUploader small,
section[data-testid="stSidebar"] .stFileUploader div {{
    color: #e8eef5 !important;
}}
section[data-testid="stSidebar"] .stFileUploader button {{
    background: {MTL_GOLD} !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}}
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] {{
    background: rgba(255,255,255,0.05) !important;
    border: 2px dashed {MTL_GOLD}99 !important;
    border-radius: 10px !important;
}}
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] * {{
    color: #C9A96E !important;
}}

/* ── Download button ── */
.stDownloadButton > button {{
    background: linear-gradient(135deg, {MTL_GOLD} 0%, #8a6d38 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(168,135,74,0.35) !important;
}}
.stDownloadButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(168,135,74,0.5) !important;
}}

/* ── Gold divider ── */
.gold-divider {{
    height: 2px;
    background: linear-gradient(to right, transparent, {MTL_GOLD}, transparent);
    margin: 20px 0;
    border: none;
}}

/* ── Section heading ── */
.section-heading {{
    color: {MTL_NAVY};
    font-size: 1.05rem;
    font-weight: 700;
    border-left: 4px solid {MTL_GOLD};
    padding-left: 12px;
    margin: 16px 0 12px;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  QUẢN LÝ ĐĂNG NHẬP
# ─────────────────────────────────────────────
if "dang_nhap" not in st.session_state:
    st.session_state.dang_nhap = False
    st.session_state.nguoi_dung = None

def dang_nhap(ten_tk, mat_khau):
    if ten_tk in TAI_KHOAN and TAI_KHOAN[ten_tk]["mat_khau"] == mat_khau:
        st.session_state.dang_nhap = True
        st.session_state.nguoi_dung = {**TAI_KHOAN[ten_tk], "ten_tk": ten_tk}
        return True
    return False

def dang_xuat():
    st.session_state.dang_nhap = False
    st.session_state.nguoi_dung = None
    st.rerun()

# ─────────────────────────────────────────────
#  TRANG ĐĂNG NHẬP
# ─────────────────────────────────────────────
if not st.session_state.dang_nhap:
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
<div class="login-card">
  <div class="login-logo">
    <div class="mtl-box mtl-box-navy" style="width:42px;height:42px;font-size:1.2rem;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;font-weight:700;color:white;background:#163960;border:1.5px solid rgba(255,255,255,0.3);">M</div>
    <div class="mtl-box mtl-box-gold"  style="width:42px;height:42px;font-size:1.2rem;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;font-weight:700;color:white;background:#A8874A;border:1.5px solid rgba(255,255,255,0.3);">T</div>
    <div class="mtl-box mtl-box-navy" style="width:42px;height:42px;font-size:1.2rem;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;font-weight:700;color:white;background:#163960;border:1.5px solid rgba(255,255,255,0.3);">L</div>
  </div>
  <div style="height:3px;background:linear-gradient(to right,#163960,#A8874A,#163960);border-radius:2px;margin:10px 40px 12px;"></div>
  <p class="login-title">LUẬT MINH TÚ</p>
  <p class="login-sub">⚖ Legal Agent Premium</p>
</div>
""", unsafe_allow_html=True)

        with st.form("dang_nhap_form"):
            ten_tk   = st.text_input("Tên đăng nhập", placeholder="Ví dụ: ls.nguyen")
            mat_khau = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
            nut_dn   = st.form_submit_button("🔐  Đăng nhập", use_container_width=True)

        if nut_dn:
            if dang_nhap(ten_tk.strip(), mat_khau):
                st.success("✅ Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu.")

        st.markdown("<p style='text-align:center;color:#bbb;font-size:0.75rem;margin-top:16px;'>© 2025 Công ty Luật TNHH Minh Tú — Bảo mật & Bảo mật</p>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  HÀM TRÍCH XUẤT NỘI DUNG FILE
# ─────────────────────────────────────────────
def doc_pdf(file_bytes):
    """Đọc nội dung file PDF"""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        noi_dung = []
        for i, trang in enumerate(reader.pages):
            txt = trang.extract_text()
            if txt:
                noi_dung.append(f"[Trang {i+1}]\n{txt}")
        return "\n\n".join(noi_dung) if noi_dung else "⚠️ Không đọc được nội dung PDF (có thể là ảnh scan)."
    except Exception as e:
        return f"Lỗi đọc PDF: {str(e)}"

def doc_docx(file_bytes):
    """Đọc nội dung file Word"""
    try:
        doc = Document(io.BytesIO(file_bytes))
        noi_dung = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(noi_dung)
    except Exception as e:
        return f"Lỗi đọc DOCX: {str(e)}"

def anh_sang_base64(file_bytes, loai_file):
    """Chuyển ảnh sang base64 để gửi Claude"""
    return base64.standard_b64encode(file_bytes).decode("utf-8")

# ─────────────────────────────────────────────
#  HÀM GỌI CLAUDE API
# ─────────────────────────────────────────────
def goi_claude(api_key, messages, system_prompt):
    """Gọi Claude API và trả về kết quả"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return "❌ API Key không hợp lệ. Vui lòng kiểm tra lại."
    except Exception as e:
        return f"❌ Lỗi kết nối: {str(e)}"

def phan_tich_ho_so(api_key, noi_dung_files, yeu_cau_them=""):
    """AI phân tích hồ sơ pháp lý"""
    system = f"""Bạn là chuyên gia pháp lý Việt Nam tại {TEN_CONG_TY}, chuyên về pháp luật đất đai, 
xây dựng, đầu tư và dân sự. Hãy phân tích hồ sơ và trả lời bằng tiếng Việt, 
ngôn ngữ chuyên nghiệp, súc tích, có cấu trúc rõ ràng.

Khi phân tích, hãy đưa ra:
1. TÓM TẮT VỤ VIỆC (3-5 câu)
2. CÁC BÊN LIÊN QUAN
3. VẤN ĐỀ PHÁP LÝ CỐT LÕI
4. CĂN CỨ PHÁP LÝ ÁP DỤNG (Luật, Nghị định, Thông tư)
5. ĐÁNH GIÁ RỦI RO & CƠ HỘI
6. HƯỚNG XỬ LÝ ĐỀ XUẤT
7. CÁC TÀI LIỆU CẦN BỔ SUNG (nếu có)"""

    messages = []
    for item in noi_dung_files:
        if item["loai"] == "anh":
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": item["media_type"],
                            "data": item["du_lieu"],
                        }
                    },
                    {"type": "text", "text": f"File: {item['ten']} — Đây là tài liệu trong hồ sơ vụ việc."}
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": f"File: {item['ten']}\n\nNội dung:\n{item['du_lieu']}"
            })

    cau_hoi = f"Hãy phân tích toàn bộ hồ sơ trên."
    if yeu_cau_them:
        cau_hoi += f"\n\nYêu cầu thêm: {yeu_cau_them}"
    messages.append({"role": "user", "content": cau_hoi})

    return goi_claude(api_key, messages, system)

def soan_don_tu(api_key, loai_don, noi_dung_vu_viec, thong_tin_bo_sung=""):
    """AI soạn đơn từ pháp lý"""
    system = f"""Bạn là luật sư chuyên nghiệp tại {TEN_CONG_TY}. Hãy soạn thảo {loai_don} 
theo đúng mẫu pháp lý Việt Nam, bao gồm:
- Quốc hiệu, tiêu ngữ
- Tiêu đề văn bản
- Kính gửi
- Phần trình bày (có căn cứ pháp lý cụ thể)  
- Phần kính đề nghị / yêu cầu
- Phần cam kết / ký tên

Dùng ngôn ngữ pháp lý chuẩn, trang trọng. Để [TRỐNG] ở những chỗ cần điền thêm thông tin."""

    messages = [
        {"role": "user", "content": f"Thông tin vụ việc:\n{noi_dung_vu_viec}"},
        {"role": "user", "content": f"Hãy soạn: {loai_don}.\n{thong_tin_bo_sung}"}
    ]
    return goi_claude(api_key, messages, system)

def hoi_tu_do(api_key, lich_su_chat, cau_hoi, noi_dung_files=None):
    """Hỏi đáp tự do về vụ việc"""
    system = f"""Bạn là chuyên gia pháp lý tại {TEN_CONG_TY}. Trả lời các câu hỏi về pháp luật 
Việt Nam một cách chuyên nghiệp, có dẫn chiếu luật cụ thể khi cần. Ngôn ngữ: tiếng Việt."""

    messages = list(lich_su_chat)

    if noi_dung_files:
        for item in noi_dung_files:
            if item["loai"] != "anh":
                messages.insert(0, {
                    "role": "user",
                    "content": f"[Hồ sơ đã tải lên - {item['ten']}]:\n{item['du_lieu'][:2000]}..."
                })

    messages.append({"role": "user", "content": cau_hoi})
    return goi_claude(api_key, messages, system)

# ─────────────────────────────────────────────
#  HÀM TẠO FILE WORD
# ─────────────────────────────────────────────
def tao_file_word(tieu_de, noi_dung, ten_ls, chuc_vu, ngay_thang=None):
    """Tạo file Word theo định dạng chuẩn công ty"""
    doc = Document()

    # Thiết lập trang A4
    section = doc.sections[0]
    section.page_width  = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.0)

    # ── TIÊU ĐỀ CÔNG TY ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(TEN_CONG_TY)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1a, 0x3a, 0x5c)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"{DIA_CHI_CT}\n{DIA_CHI_DN}\n{SBT_CT}")
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)

    # Đường kẻ phân cách
    duong_ke = doc.add_paragraph()
    duong_ke.alignment = WD_ALIGN_PARAGRAPH.CENTER
    duong_ke.add_run("─" * 60)
    duong_ke.runs[0].font.color.rgb = RGBColor(0x1a, 0x3a, 0x5c)

    doc.add_paragraph()

    # ── TIÊU ĐỀ VĂN BẢN ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(tieu_de.upper())
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.font.bold = True

    # Ngày tháng
    if not ngay_thang:
        ngay_thang = datetime.now().strftime("Ngày %d tháng %m năm %Y")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"({ngay_thang})")
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.italic = True

    doc.add_paragraph()

    # ── NỘI DUNG CHÍNH ──
    # Xử lý nội dung: tách dòng và định dạng
    dong_chu = noi_dung.split("\n")
    for dong in dong_chu:
        dong = dong.strip()
        if not dong:
            doc.add_paragraph()
            continue

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Phát hiện tiêu đề (toàn chữ hoa hoặc bắt đầu bằng số thứ tự)
        la_tieu_de = (
            dong.isupper() or
            re.match(r"^\d+[\.\)]\s+[A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ]", dong) or
            dong.startswith("**")
        )

        dong_sach = dong.replace("**", "").replace("###", "").replace("##", "").replace("# ", "")

        run = p.add_run(dong_sach)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

        if la_tieu_de:
            run.font.bold = True
        else:
            p.paragraph_format.first_line_indent = Cm(1.0)

    doc.add_paragraph()
    doc.add_paragraph()

    # ── CHỮ KÝ ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(f"TP. Hồ Chí Minh, {datetime.now().strftime('%d/%m/%Y')}\n")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(f"{chuc_vu}\n\n\n\n{ten_ls}")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.bold = True

    # Xuất ra bytes
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ─────────────────────────────────────────────
#  GIAO DIỆN CHÍNH
# ─────────────────────────────────────────────
nd = st.session_state.nguoi_dung

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(f"""
<div style="text-align:center; padding: 16px 0 8px;">
  <div style="display:flex;align-items:center;justify-content:center;gap:3px;margin-bottom:8px;">
    <div style="width:34px;height:34px;border-radius:6px;background:#163960;border:1.5px solid rgba(255,255,255,0.25);display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;font-weight:700;color:white;font-size:1rem;">M</div>
    <div style="width:34px;height:34px;border-radius:6px;background:#A8874A;border:1.5px solid rgba(255,255,255,0.25);display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;font-weight:700;color:white;font-size:1rem;">T</div>
    <div style="width:34px;height:34px;border-radius:6px;background:#163960;border:1.5px solid rgba(255,255,255,0.25);display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;font-weight:700;color:white;font-size:1rem;">L</div>
  </div>
  <div style="font-size:0.72rem;letter-spacing:1.5px;color:#C9A96E;text-transform:uppercase;font-weight:600;">Legal Agent Premium</div>
</div>
<div style="height:1px;background:linear-gradient(to right,transparent,#A8874A,transparent);margin:4px 0 16px;"></div>
<div style="background:rgba(255,255,255,0.06);border:1px solid rgba(168,135,74,0.3);border-radius:10px;padding:12px 14px;margin-bottom:4px;">
  <div style="font-size:0.78rem;color:#A8874A;margin-bottom:2px;text-transform:uppercase;letter-spacing:0.5px;">Người dùng</div>
  <div style="font-weight:700;font-size:0.95rem;">{nd['ho_ten']}</div>
  <div style="font-size:0.78rem;opacity:0.7;">{nd['chuc_vu']}</div>
</div>
""", unsafe_allow_html=True)

    # API Key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "") or st.text_input(
        "🔑 Anthropic API Key (nếu chưa cấu hình)",
        type="password",
        placeholder="sk-ant-...",
        help="Lấy tại: console.anthropic.com"
    )

    st.markdown("<div style='height:1px;background:rgba(168,135,74,0.25);margin:12px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.8rem;color:#C9A96E;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>📂 Tải hồ sơ lên</div>", unsafe_allow_html=True)

    files_upload = st.file_uploader(
        "Chọn file (PDF, Word, ảnh)",
        type=["pdf", "docx", "png", "jpg", "jpeg", "tiff", "bmp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # Xử lý files đã tải
    if "noi_dung_files" not in st.session_state:
        st.session_state.noi_dung_files = []

    if files_upload:
        st.session_state.noi_dung_files = []
        for f in files_upload:
            bytes_data = f.read()
            ten = f.name
            loai_file = ten.rsplit(".", 1)[-1].lower()

            if loai_file == "pdf":
                noi_dung = doc_pdf(bytes_data)
                st.session_state.noi_dung_files.append({
                    "ten": ten, "loai": "pdf", "du_lieu": noi_dung
                })
            elif loai_file == "docx":
                noi_dung = doc_docx(bytes_data)
                st.session_state.noi_dung_files.append({
                    "ten": ten, "loai": "docx", "du_lieu": noi_dung
                })
            elif loai_file in ["png", "jpg", "jpeg", "tiff", "bmp"]:
                b64 = anh_sang_base64(bytes_data, loai_file)
                media_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                             "png": "image/png", "tiff": "image/tiff", "bmp": "image/bmp"}
                st.session_state.noi_dung_files.append({
                    "ten": ten, "loai": "anh",
                    "du_lieu": b64,
                    "media_type": media_map.get(loai_file, "image/jpeg"),
                })

        if st.session_state.noi_dung_files:
            st.success(f"✅ Đã tải {len(st.session_state.noi_dung_files)} file")
            for item in st.session_state.noi_dung_files:
                icon = "🖼️" if item["loai"] == "anh" else "📄"
                st.markdown(f"<div style='font-size:0.82rem;padding:3px 0;'>{icon} {item['ten']}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:rgba(168,135,74,0.25);margin:12px 0;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Đăng xuất", use_container_width=True):
        dang_xuat()

# ── HEADER ──
st.markdown(f"""
<div class="mtl-header">
  <div class="mtl-header-inner">
    <div class="mtl-logo-block">
      <div class="mtl-box mtl-box-navy">M</div>
      <div class="mtl-box mtl-box-gold">T</div>
      <div class="mtl-box mtl-box-navy">L</div>
    </div>
    <div class="mtl-divider"></div>
    <div class="mtl-title-block">
      <h1>LUẬT MINH TÚ</h1>
      <p class="mtl-sub">⚖ Legal Agent Premium &nbsp;·&nbsp; Hệ thống hỗ trợ pháp lý thông minh</p>
    </div>
    <div class="mtl-user-badge">
      <div class="name">{nd['ho_ten']}</div>
      <div class="role">{nd['chuc_vu']}</div>
      <div class="date">{datetime.now().strftime('%d/%m/%Y  %H:%M')}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS CHỨC NĂNG ──
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Phân tích hồ sơ",
    "📝 Soạn thảo văn bản",
    "💬 Hỏi đáp pháp lý",
    "📋 Hướng dẫn sử dụng",
])

# ══════════════════════════════════════════════
#  TAB 1 — PHÂN TÍCH HỒ SƠ
# ══════════════════════════════════════════════
with tab1:
    st.subheader("🔍 Phân tích hồ sơ vụ việc")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        yeu_cau_them = st.text_area(
            "Yêu cầu phân tích cụ thể (tùy chọn)",
            placeholder="Ví dụ: Tập trung vào quyền đòi bồi thường, thời hiệu khởi kiện...",
            height=80,
        )

    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        nut_phan_tich = st.button("🚀 Phân tích ngay", use_container_width=True, type="primary")

    if nut_phan_tich:
        if not api_key:
            st.warning("⚠️ Vui lòng nhập API Key ở thanh bên trái.")
        elif not st.session_state.noi_dung_files:
            st.warning("⚠️ Vui lòng tải ít nhất 1 file hồ sơ.")
        else:
            with st.spinner("🤖 AI đang nghiên cứu hồ sơ..."):
                ket_qua = phan_tich_ho_so(api_key, st.session_state.noi_dung_files, yeu_cau_them)
                st.session_state.ket_qua_phan_tich = ket_qua

    if "ket_qua_phan_tich" in st.session_state and st.session_state.ket_qua_phan_tich:
        st.markdown("---")
        st.markdown("#### 📊 Kết quả phân tích")
        st.markdown(
            f'<div class="result-box">{st.session_state.ket_qua_phan_tich.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True
        )

        # Nút tải xuống Word
        st.markdown("<br>", unsafe_allow_html=True)
        word_bytes = tao_file_word(
            tieu_de="BÁO CÁO PHÂN TÍCH HỒ SƠ VỤ VIỆC",
            noi_dung=st.session_state.ket_qua_phan_tich,
            ten_ls=nd["ho_ten"],
            chuc_vu=nd["chuc_vu"],
        )
        st.download_button(
            label="⬇️ Tải xuống file Word",
            data=word_bytes,
            file_name=f"PhanTichHoSo_{datetime.now().strftime('%d%m%Y_%H%M')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
        )

# ══════════════════════════════════════════════
#  TAB 2 — SOẠN THẢO VĂN BẢN
# ══════════════════════════════════════════════
with tab2:
    st.subheader("📝 Soạn thảo văn bản pháp lý")

    LOAI_DON = [
        "Đơn khởi kiện",
        "Đơn yêu cầu thi hành án",
        "Đơn đề nghị hòa giải",
        "Đơn tố cáo",
        "Đơn xin cấp bản sao hồ sơ",
        "Đơn xin gia hạn nộp tiền tạm ứng án phí",
        "Hợp đồng dịch vụ pháp lý",
        "Thông báo pháp lý (Legal Notice)",
        "Biên bản cuộc họp",
        "Phiếu yêu cầu tư vấn",
        "Văn bản khác (tự nhập)",
    ]

    col1, col2 = st.columns(2)
    with col1:
        loai_don_chon = st.selectbox("Loại văn bản cần soạn", LOAI_DON)
    with col2:
        if loai_don_chon == "Văn bản khác (tự nhập)":
            loai_don_chon = st.text_input("Nhập loại văn bản", placeholder="Ví dụ: Đơn phản đối...")

    noi_dung_vu_viec = st.text_area(
        "Mô tả vụ việc / thông tin cần đưa vào văn bản",
        placeholder=(
            "Ví dụ: Nguyên đơn là ông Nguyễn Văn A, sinh năm 1975, CCCD: ..., địa chỉ: ...\n"
            "Bị đơn là Công ty TNHH XYZ...\n"
            "Nội dung tranh chấp: tranh chấp hợp đồng mua bán đất ngày...\n"
            "Yêu cầu: bồi thường thiệt hại..."
        ),
        height=140,
    )

    # Lấy nội dung từ hồ sơ đã phân tích (nếu có)
    if "ket_qua_phan_tich" in st.session_state and st.session_state.ket_qua_phan_tich:
        if st.checkbox("📂 Lấy thông tin từ hồ sơ đã phân tích"):
            noi_dung_vu_viec = st.session_state.ket_qua_phan_tich[:1500]

    thong_tin_bs = st.text_input(
        "Yêu cầu thêm",
        placeholder="Ví dụ: Nhấn mạnh vào điều 166 Bộ luật Dân sự, thêm phần yêu cầu tạm đình chỉ..."
    )

    if st.button("✍️ Soạn văn bản", type="primary"):
        if not api_key:
            st.warning("⚠️ Vui lòng nhập API Key.")
        elif not noi_dung_vu_viec.strip():
            st.warning("⚠️ Vui lòng nhập thông tin vụ việc.")
        else:
            with st.spinner("🤖 AI đang soạn thảo..."):
                van_ban = soan_don_tu(api_key, loai_don_chon, noi_dung_vu_viec, thong_tin_bs)
                st.session_state.van_ban_soan = van_ban
                st.session_state.loai_van_ban = loai_don_chon

    if "van_ban_soan" in st.session_state and st.session_state.van_ban_soan:
        st.markdown("---")

        # Cho phép chỉnh sửa trước khi xuất
        van_ban_chinh_sua = st.text_area(
            "✏️ Chỉnh sửa nội dung (nếu cần)",
            value=st.session_state.van_ban_soan,
            height=400,
        )

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            # Xuất Word
            word_bytes = tao_file_word(
                tieu_de=st.session_state.loai_van_ban,
                noi_dung=van_ban_chinh_sua,
                ten_ls=nd["ho_ten"],
                chuc_vu=nd["chuc_vu"],
            )
            ten_file = st.session_state.loai_van_ban.replace(" ", "_")
            st.download_button(
                label="⬇️ Tải xuống file Word",
                data=word_bytes,
                file_name=f"{ten_file}_{datetime.now().strftime('%d%m%Y')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
        with col_dl2:
            # Xuất bản text
            st.download_button(
                label="📋 Tải xuống văn bản (TXT)",
                data=van_ban_chinh_sua.encode("utf-8"),
                file_name=f"{ten_file}_{datetime.now().strftime('%d%m%Y')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

# ══════════════════════════════════════════════
#  TAB 3 — HỎI ĐÁP PHÁP LÝ
# ══════════════════════════════════════════════
with tab3:
    st.subheader("💬 Hỏi đáp pháp lý")

    if "lich_su_chat" not in st.session_state:
        st.session_state.lich_su_chat = []

    # Hiển thị lịch sử chat
    for tin_nhan in st.session_state.lich_su_chat:
        if tin_nhan["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(tin_nhan["content"])
        else:
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(tin_nhan["content"])

    # Ô nhập câu hỏi
    cau_hoi = st.chat_input("Hỏi về pháp luật, vụ việc, hoặc nội dung hồ sơ...")

    if cau_hoi:
        if not api_key:
            st.warning("⚠️ Vui lòng nhập API Key.")
        else:
            st.session_state.lich_su_chat.append({"role": "user", "content": cau_hoi})
            with st.chat_message("user", avatar="👤"):
                st.write(cau_hoi)

            with st.chat_message("assistant", avatar="⚖️"):
                with st.spinner("Đang tra cứu..."):
                    tra_loi = hoi_tu_do(
                        api_key,
                        st.session_state.lich_su_chat[:-1],
                        cau_hoi,
                        st.session_state.noi_dung_files,
                    )
                    st.write(tra_loi)
                    st.session_state.lich_su_chat.append({"role": "assistant", "content": tra_loi})

    if st.session_state.lich_su_chat:
        if st.button("🗑️ Xóa lịch sử chat"):
            st.session_state.lich_su_chat = []
            st.rerun()

# ══════════════════════════════════════════════
#  TAB 4 — HƯỚNG DẪN
# ══════════════════════════════════════════════
with tab4:
    st.subheader("📋 Hướng dẫn sử dụng MTL Legal Agent Premium")
    st.markdown(f"""
### 🚀 Bắt đầu nhanh

**Bước 1:** Nhập **Anthropic API Key** ở thanh bên trái.
> Lấy key miễn phí tại: [console.anthropic.com](https://console.anthropic.com)

**Bước 2:** Tải hồ sơ vụ việc lên (PDF, Word, ảnh chụp tài liệu, ảnh chữ viết tay).

**Bước 3:** Chọn chức năng:
- **Phân tích hồ sơ** — AI đọc toàn bộ hồ sơ, tóm tắt, xác định vấn đề pháp lý, đề xuất hướng xử lý.
- **Soạn thảo văn bản** — Chọn loại đơn và nhập thông tin, AI soạn xong tải về file Word.
- **Hỏi đáp pháp lý** — Chat trực tiếp về luật, vụ việc, hoặc hồ sơ đã tải lên.

---

### 💡 Mẹo sử dụng hiệu quả

- Tải nhiều file cùng lúc để AI phân tích tổng thể
- Ảnh chụp bằng điện thoại vẫn đọc được (kể cả chữ viết tay)
- Sau khi phân tích xong → sang tab Soạn thảo → tích "Lấy thông tin từ hồ sơ" để tự động điền
- Văn bản soạn xong có thể chỉnh sửa trực tiếp trước khi tải về

---

### 👥 Tài khoản hiện tại
| Tài khoản | Họ tên | Chức vụ |
|-----------|--------|---------|
""" + "\n".join([
    f"| `{tk}` | {info['ho_ten']} | {info['chuc_vu']} |"
    for tk, info in TAI_KHOAN.items()
]) + f"""

---
### 📞 Hỗ trợ kỹ thuật
{DIA_CHI_CT}  
{DIA_CHI_DN}  
{SBT_CT}
""")
