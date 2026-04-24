"""
=============================================================
  MTL LEGAL AGENT PREMIUM
  Công ty Luật TNHH Minh Tú
=============================================================
Cài đặt (chạy 1 lần):
  pip install streamlit anthropic python-docx PyPDF2 pillow

Chạy app:
  streamlit run app.py
=============================================================
"""

import streamlit as st
import anthropic
import base64
import io
import os
import re
import json
from datetime import datetime

# OAuth + Gmail API
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import urllib.parse
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import PyPDF2

# =============================================================
#  API KEY — cấu hình trong Railway Variables
#  Tên biến trong Railway: ANTHROPIC_API_KEY
# =============================================================
API_KEY_FALLBACK = ""
# =============================================================

# ─────────────────────────────────────────────
#  THÔNG TIN CÔNG TY
# ─────────────────────────────────────────────
TEN_CONG_TY = "CÔNG TY LUẬT TNHH MINH TÚ"
DIA_CHI_CT  = "Trụ sở: 4/9 Đường số 3 Cư Xá Đô Thành, Phường Bàn Cờ, TP. Hồ Chí Minh"
DIA_CHI_DN  = "CN Đà Nẵng: 81 Xô Viết Nghệ Tĩnh, Phường Cẩm Lệ, TP. Đà Nẵng"
SBT_CT      = "Hotline: 19000031 | Website: luatminhtu.vn | Email: info.luatminhtu@gmail.com"

# ─────────────────────────────────────────────
#  TÀI KHOẢN LUẬT SƯ
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

# ─────────────────────────────────────────────
#  MÀU THƯƠNG HIỆU MTL
# ─────────────────────────────────────────────
MTL_NAVY  = "#1E4D82"
MTL_GOLD  = "#A8874A"
MTL_NAVY2 = "#163960"
MTL_GOLD2 = "#C9A96E"

# ─────────────────────────────────────────────
#  CẤU HÌNH TRANG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MTL Legal Agent Premium",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
#MainMenu, footer, header {{ visibility: hidden; }}

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
section[data-testid="stSidebar"] hr {{ border-color: {MTL_GOLD}44 !important; }}
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: 1px solid {MTL_GOLD} !important;
    color: {MTL_GOLD} !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {MTL_GOLD} !important;
    color: white !important;
}}
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] {{
    background: rgba(255,255,255,0.05) !important;
    border: 2px dashed {MTL_GOLD}99 !important;
    border-radius: 10px !important;
}}
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] * {{
    color: {MTL_GOLD2} !important;
}}
section[data-testid="stSidebar"] .stFileUploader button {{
    background: {MTL_GOLD} !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}}
.mtl-header {{
    background: linear-gradient(135deg, {MTL_NAVY2} 0%, {MTL_NAVY} 70%, #1a5592 100%);
    border-bottom: 3px solid {MTL_GOLD};
    border-radius: 12px;
    margin-bottom: 24px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(30,77,130,0.25);
}}
.mtl-header-inner {{
    display: flex; align-items: center; gap: 20px; padding: 18px 28px;
}}
.mtl-box {{
    width: 40px; height: 40px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 700; color: white; font-family: Georgia, serif;
}}
.mtl-box-navy {{ background: {MTL_NAVY2}; border: 1.5px solid rgba(255,255,255,0.3); }}
.mtl-box-gold  {{ background: {MTL_GOLD};  border: 1.5px solid rgba(255,255,255,0.3); }}
.mtl-divider {{
    width: 2px; height: 52px;
    background: linear-gradient(to bottom, transparent, {MTL_GOLD}, transparent);
    margin: 0 12px;
}}
.mtl-title-block h1 {{ margin: 0; color: white; font-size: 1.25rem; font-weight: 700; }}
.mtl-title-block .mtl-sub {{ margin: 3px 0 0; color: {MTL_GOLD2}; font-size: 0.82rem; }}
.mtl-user-badge {{
    margin-left: auto;
    background: rgba(255,255,255,0.08);
    border: 1px solid {MTL_GOLD}66;
    border-radius: 8px; padding: 8px 16px; text-align: right;
}}
.mtl-user-badge .name {{ color: white; font-weight: 600; font-size: 0.9rem; }}
.mtl-user-badge .role {{ color: {MTL_GOLD2}; font-size: 0.78rem; }}
.mtl-user-badge .date {{ color: rgba(255,255,255,0.5); font-size: 0.72rem; margin-top: 2px; }}
.login-card {{
    background: white; border-radius: 16px; padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(30,77,130,0.15);
    border-top: 4px solid {MTL_GOLD}; max-width: 420px; margin: 0 auto;
}}
.login-title {{ text-align: center; color: {MTL_NAVY}; font-size: 1.3rem; font-weight: 700; margin: 8px 0 4px; }}
.login-sub {{ text-align: center; color: {MTL_GOLD}; font-size: 0.82rem; letter-spacing: 1px; margin: 0 0 24px; text-transform: uppercase; font-weight: 600; }}
.result-box {{
    background: linear-gradient(135deg, #f0f5ff 0%, #fafbff 100%);
    border-left: 4px solid {MTL_NAVY};
    border-top: 1px solid #e0e8f5; border-right: 1px solid #e0e8f5; border-bottom: 1px solid #e0e8f5;
    padding: 20px 24px; border-radius: 0 10px 10px 0; margin-top: 16px; line-height: 1.75;
}}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 2px solid {MTL_GOLD}44; }}
.stTabs [data-baseweb="tab"] {{ border-radius: 8px 8px 0 0 !important; font-weight: 600 !important; padding: 8px 18px !important; }}
.stTabs [aria-selected="true"] {{ background: {MTL_NAVY} !important; color: white !important; border-bottom: 2px solid {MTL_GOLD} !important; }}
.stButton > button {{ border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s !important; }}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {MTL_NAVY} 0%, {MTL_NAVY2} 100%) !important;
    border: none !important; color: white !important;
    box-shadow: 0 2px 8px rgba(30,77,130,0.3) !important;
}}
.stDownloadButton > button {{
    background: linear-gradient(135deg, {MTL_GOLD} 0%, #8a6d38 100%) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  XÁC ĐỊNH API KEY
# ─────────────────────────────────────────────
def lay_api_key():
    # Đọc thẳng từ env var Railway
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    # Fallback: key dự phòng điền tay
    if API_KEY_FALLBACK and len(API_KEY_FALLBACK) > 20:
        return API_KEY_FALLBACK
    return ""

API_KEY = lay_api_key()

# ─────────────────────────────────────────────
#  ĐĂNG NHẬP
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

if not st.session_state.dang_nhap:
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
<div class="login-card">
  <div style="display:flex;align-items:center;justify-content:center;gap:4px;margin-bottom:8px;">
    <div class="mtl-box mtl-box-navy" style="width:42px;height:42px;">M</div>
    <div class="mtl-box mtl-box-gold"  style="width:42px;height:42px;">T</div>
    <div class="mtl-box mtl-box-navy" style="width:42px;height:42px;">L</div>
  </div>
  <div style="height:3px;background:linear-gradient(to right,#163960,#A8874A,#163960);border-radius:2px;margin:10px 40px 12px;"></div>
  <p class="login-title">LUẬT MINH TÚ</p>
  <p class="login-sub">⚖ Legal Agent Premium</p>
</div>
""", unsafe_allow_html=True)

        with st.form("form_dn"):
            ten_tk   = st.text_input("Tên đăng nhập", placeholder="Ví dụ: ls.hoang")
            mat_khau = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
            nut      = st.form_submit_button("🔐  Đăng nhập", use_container_width=True)

        if nut:
            if dang_nhap(ten_tk.strip(), mat_khau):
                st.success("✅ Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu.")

        st.markdown("<p style='text-align:center;color:#bbb;font-size:0.75rem;margin-top:16px;'>© 2026 Công ty Luật TNHH Minh Tú</p>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  HÀM ĐỌC FILE
# ─────────────────────────────────────────────
def doc_pdf(file_bytes):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        noi_dung = []
        for i, trang in enumerate(reader.pages):
            txt = trang.extract_text()
            if txt:
                noi_dung.append(f"[Trang {i+1}]\n{txt}")
        return "\n\n".join(noi_dung) if noi_dung else "⚠️ Không đọc được nội dung PDF."
    except Exception as e:
        return f"Lỗi đọc PDF: {e}"

def doc_docx(file_bytes):
    try:
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"Lỗi đọc DOCX: {e}"

# ─────────────────────────────────────────────
#  HÀM GỌI CLAUDE
# ─────────────────────────────────────────────
def goi_claude(messages, system_prompt):
    try:
        client = anthropic.Anthropic(api_key=API_KEY)
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return "❌ API Key không hợp lệ. Kiểm tra lại dòng ANTHROPIC_API_KEY ở đầu file app.py."
    except Exception as e:
        return f"❌ Lỗi: {e}"

def phan_tich_ho_so(noi_dung_files, yeu_cau=""):
    system = f"""Bạn là chuyên gia pháp lý Việt Nam tại {TEN_CONG_TY}.
Phân tích hồ sơ bằng tiếng Việt, chuyên nghiệp, có cấu trúc rõ ràng gồm:
1. TÓM TẮT VỤ VIỆC  2. CÁC BÊN LIÊN QUAN  3. VẤN ĐỀ PHÁP LÝ CỐT LÕI
4. CĂN CỨ PHÁP LÝ  5. ĐÁNH GIÁ RỦI RO & CƠ HỘI  6. HƯỚNG XỬ LÝ ĐỀ XUẤT  7. TÀI LIỆU CẦN BỔ SUNG"""
    messages = []
    for item in noi_dung_files:
        if item["loai"] == "anh":
            messages.append({"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": item["media_type"], "data": item["du_lieu"]}},
                {"type": "text", "text": f"File: {item['ten']}"},
            ]})
        else:
            messages.append({"role": "user", "content": f"File: {item['ten']}\n\n{item['du_lieu']}"})
    cau_hoi = "Hãy phân tích toàn bộ hồ sơ."
    if yeu_cau:
        cau_hoi += f"\n\nYêu cầu thêm: {yeu_cau}"
    messages.append({"role": "user", "content": cau_hoi})
    return goi_claude(messages, system)

def soan_don_tu(loai_don, noi_dung, them=""):
    system = f"""Bạn là luật sư chuyên nghiệp tại {TEN_CONG_TY}.
Soạn {loai_don} theo mẫu pháp lý Việt Nam: quốc hiệu, tiêu ngữ, tiêu đề, kính gửi,
nội dung (có căn cứ pháp lý), kính đề nghị, cam kết. Để [TRỐNG] nơi cần điền thêm."""
    messages = [
        {"role": "user", "content": f"Thông tin vụ việc:\n{noi_dung}"},
        {"role": "user", "content": f"Soạn: {loai_don}.\n{them}"},
    ]
    return goi_claude(messages, system)

def hoi_dap(lich_su, cau_hoi, files=None):
    system = f"Bạn là chuyên gia pháp lý tại {TEN_CONG_TY}. Trả lời chuyên nghiệp, dẫn chiếu luật cụ thể khi cần."
    messages = list(lich_su)
    if files:
        for item in files:
            if item["loai"] != "anh":
                messages.insert(0, {"role": "user", "content": f"[Hồ sơ - {item['ten']}]:\n{item['du_lieu'][:2000]}"})
    messages.append({"role": "user", "content": cau_hoi})
    return goi_claude(messages, system)

# ─────────────────────────────────────────────
#  TẠO FILE WORD — ĐỊNH DẠNG MTL PREMIUM
# ─────────────────────────────────────────────
# Màu MTL chuẩn (lấy từ file mẫu công ty)
C_NAVY      = RGBColor(0x1B, 0x4A, 0x7A)   # Navy chính
C_NAVY_DARK = RGBColor(0x16, 0x3D, 0x66)   # Navy đậm
C_GOLD      = RGBColor(0xB8, 0x97, 0x3A)   # Vàng đồng
C_GOLD2     = RGBColor(0xCD, 0xB0, 0x60)   # Vàng sáng
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
C_DARK      = RGBColor(0x1E, 0x29, 0x3B)   # Chữ chính
C_MUTED     = RGBColor(0x64, 0x74, 0x8B)   # Chữ phụ

def _set_cell_bg(cell, hex_color):
    """Tô màu nền ô bảng"""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def _set_cell_border(cell, top=None, bottom=None, left=None, right=None):
    """Đặt viền ô"""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        if val:
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'), val.get('val', 'single'))
            el.set(qn('w:sz'), str(val.get('sz', 4)))
            el.set(qn('w:color'), val.get('color', 'auto'))
            tcBorders.append(el)
    tcPr.append(tcBorders)

def _run(para, text, size, bold=False, italic=False, color=None):
    run = para.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    return run

def tao_file_word(tieu_de, noi_dung, ten_ls, chuc_vu):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.shared import Inches

    doc = Document()

    # ── Thiết lập trang A4 ──
    sec = doc.sections[0]
    sec.page_width    = Cm(21)
    sec.page_height   = Cm(29.7)
    sec.top_margin    = Cm(1.2)
    sec.bottom_margin = Cm(1.2)
    sec.left_margin   = Cm(1.2)
    sec.right_margin  = Cm(1.2)

    # Xóa spacing mặc định
    style = doc.styles['Normal']
    style.font.name = "Times New Roman"
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after  = Pt(0)

    # ── HEADER: Logo + Tiêu đề tài liệu ──
    tbl_header = doc.add_table(rows=1, cols=2)
    tbl_header.style = 'Table Grid'
    tbl_header.autofit = False
    tbl_header.columns[0].width = Cm(7)
    tbl_header.columns[1].width = Cm(11.8)

    # Ô trái: logo
    cell_logo = tbl_header.cell(0, 0)
    _set_cell_bg(cell_logo, "1B4A7A")
    p_logo = cell_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Nhúng logo nếu có file
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")
    if os.path.exists(logo_path):
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Cm(5.5))
    else:
        _run(p_logo, "MINHTU LAW CO., LTD", 12, bold=True, color=C_WHITE)

    # Ô phải: loại tài liệu
    cell_title = tbl_header.cell(0, 1)
    _set_cell_bg(cell_title, "FFFFFF")
    cell_title.width = Cm(11.8)
    p_type = cell_title.paragraphs[0]
    p_type.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_type.paragraph_format.space_before = Pt(12)
    _run(p_type, tieu_de.upper(), 11, bold=True, color=C_NAVY)
    p_sub = cell_title.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _run(p_sub, f"Ngày {datetime.now().strftime('%d/%m/%Y')}", 8.5, color=C_MUTED)
    p_sub2 = cell_title.add_paragraph()
    p_sub2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _run(p_sub2, f"Người soạn: {ten_ls}  ·  {chuc_vu}", 8, italic=True, color=C_MUTED)

    doc.add_paragraph()

    # ── BANNER: RIÊNG TƯ & BẢO MẬT ──
    tbl_banner = doc.add_table(rows=1, cols=1)
    tbl_banner.style = 'Table Grid'
    tbl_banner.columns[0].width = Cm(18.6)
    cell_banner = tbl_banner.cell(0, 0)
    _set_cell_bg(cell_banner, "1B4A7A")
    p_banner = cell_banner.paragraphs[0]
    p_banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_banner.paragraph_format.space_before = Pt(4)
    p_banner.paragraph_format.space_after  = Pt(4)
    _run(p_banner, "✦   THÔNG TIN BẢO MẬT  ·  CONFIDENTIAL   ✦", 7.5, bold=True, color=C_WHITE)

    doc.add_paragraph()

    # ── NỘI DUNG CHÍNH ──
    dong_list = [d for d in noi_dung.split("\n")]
    i = 0
    while i < len(dong_list):
        dong = dong_list[i].strip()
        dong_sach = dong.replace("**", "").replace("###", "").replace("##", "").replace("# ", "").strip()

        if not dong_sach:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue

        # Phát hiện tiêu đề section (toàn hoa, bắt đầu số, hoặc **text**)
        la_section = bool(
            (dong.isupper() and len(dong) > 3) or
            re.match(r"^\d+[\.\)]\s+[A-ZÁÀẢÃẠ]", dong) or
            (dong.startswith("**") and dong.endswith("**"))
        )

        if la_section:
            # Section header: navy nền, chữ trắng
            tbl_sec = doc.add_table(rows=1, cols=1)
            tbl_sec.style = 'Table Grid'
            tbl_sec.columns[0].width = Cm(18.6)
            cell_sec = tbl_sec.cell(0, 0)
            _set_cell_bg(cell_sec, "1B4A7A")
            p_sec = cell_sec.paragraphs[0]
            p_sec.paragraph_format.space_before = Pt(5)
            p_sec.paragraph_format.space_after  = Pt(5)
            p_sec.paragraph_format.left_indent  = Cm(0.3)
            _run(p_sec, dong_sach, 9.5, bold=True, color=C_WHITE)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        else:
            # Đoạn nội dung thường
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after      = Pt(4)
            p.paragraph_format.left_indent      = Cm(0.5)
            p.paragraph_format.first_line_indent = Cm(0)

            # Sub-heading nhỏ (bắt đầu bằng •, -, số)
            la_bullet = bool(re.match(r"^[•\-\*]\s", dong_sach) or re.match(r"^\d+\.\s", dong_sach))

            if la_bullet:
                p.paragraph_format.left_indent = Cm(1.0)
                _run(p, dong_sach, 9.5, color=C_DARK)
            else:
                _run(p, dong_sach, 9.5, color=C_DARK)

        i += 1

    # ── CHỮ KÝ ──
    doc.add_paragraph()
    tbl_sign = doc.add_table(rows=1, cols=2)
    tbl_sign.style = 'Table Grid'
    tbl_sign.columns[0].width = Cm(9.3)
    tbl_sign.columns[1].width = Cm(9.3)

    cell_l = tbl_sign.cell(0, 0)
    cell_r = tbl_sign.cell(0, 1)
    _set_cell_bg(cell_l, "F8FAFC")
    _set_cell_bg(cell_r, "F8FAFC")

    p_l = cell_l.paragraphs[0]
    p_l.paragraph_format.space_before = Pt(8)
    p_l.paragraph_format.space_after  = Pt(8)
    p_l.paragraph_format.left_indent  = Cm(0.5)
    _run(p_l, "Kính trân trọng,\n", 9.5, color=C_MUTED)
    p_l2 = cell_l.add_paragraph()
    p_l2.paragraph_format.left_indent = Cm(0.5)
    _run(p_l2, f"\n\n{ten_ls}", 10, bold=True, color=C_NAVY)
    p_l3 = cell_l.add_paragraph()
    p_l3.paragraph_format.left_indent = Cm(0.5)
    _run(p_l3, chuc_vu, 8.5, color=C_MUTED)
    p_l4 = cell_l.add_paragraph()
    p_l4.paragraph_format.left_indent = Cm(0.5)
    p_l4.paragraph_format.space_after = Pt(8)
    _run(p_l4, TEN_CONG_TY, 8.5, italic=True, color=C_GOLD)

    p_r = cell_r.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.paragraph_format.space_before = Pt(8)
    p_r.paragraph_format.right_indent = Cm(0.5)
    _run(p_r, "Hiệu lực văn bản\n", 8, bold=True, color=C_GOLD)
    p_r2 = cell_r.add_paragraph()
    p_r2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r2.paragraph_format.right_indent = Cm(0.5)
    _run(p_r2, f"TP. Hồ Chí Minh, {datetime.now().strftime('%d/%m/%Y')}", 9.5, bold=True, color=C_NAVY)
    p_r3 = cell_r.add_paragraph()
    p_r3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r3.paragraph_format.right_indent = Cm(0.5)
    p_r3.paragraph_format.space_after  = Pt(8)
    _run(p_r3, "Tài liệu soạn bởi MTL Legal Agent Premium", 7.5, italic=True, color=C_MUTED)

    # ── FOOTER: Gold bar ──
    doc.add_paragraph()
    tbl_footer = doc.add_table(rows=1, cols=1)
    tbl_footer.style = 'Table Grid'
    tbl_footer.columns[0].width = Cm(18.6)
    cell_f = tbl_footer.cell(0, 0)
    _set_cell_bg(cell_f, "B8973A")
    p_f = cell_f.paragraphs[0]
    p_f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f.paragraph_format.space_before = Pt(3)
    p_f.paragraph_format.space_after  = Pt(3)
    _run(p_f, f"© 2026 MINHTU LAW CO., LTD  |  OUR EXPERIENCE IS YOUR SUCCESS  |  {SBT_CT}", 6.5, bold=True, color=C_WHITE)

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
<div style="text-align:center;padding:16px 0 8px;">
  <div style="display:flex;align-items:center;justify-content:center;gap:3px;margin-bottom:8px;">
    <div class="mtl-box mtl-box-navy" style="width:34px;height:34px;font-size:1rem;">M</div>
    <div class="mtl-box mtl-box-gold"  style="width:34px;height:34px;font-size:1rem;">T</div>
    <div class="mtl-box mtl-box-navy" style="width:34px;height:34px;font-size:1rem;">L</div>
  </div>
  <div style="font-size:0.72rem;letter-spacing:1.5px;color:{MTL_GOLD2};text-transform:uppercase;font-weight:600;">Legal Agent Premium</div>
</div>
<div style="height:1px;background:linear-gradient(to right,transparent,{MTL_GOLD},transparent);margin:4px 0 16px;"></div>
<div style="background:rgba(255,255,255,0.06);border:1px solid rgba(168,135,74,0.3);border-radius:10px;padding:12px 14px;margin-bottom:12px;">
  <div style="font-size:0.72rem;color:{MTL_GOLD};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:3px;">Người dùng</div>
  <div style="font-weight:700;font-size:0.95rem;">{nd['ho_ten']}</div>
  <div style="font-size:0.78rem;opacity:0.7;">{nd['chuc_vu']}</div>
</div>
""", unsafe_allow_html=True)

    if API_KEY:
        st.markdown("""
<div style="background:rgba(100,180,100,0.15);border:1px solid #4a9a4a;border-radius:8px;
padding:8px 12px;font-size:0.78rem;color:#90ee90;margin-bottom:12px;">
✅ API Key đã được cấu hình
</div>""", unsafe_allow_html=True)
        # Debug: hiện 8 ký tự đầu để xác nhận đúng key
        st.markdown(f"<div style='font-size:0.7rem;color:#888;margin-bottom:8px;'>Key: {API_KEY[:12]}...{API_KEY[-4:]}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:rgba(220,80,80,0.15);border:1px solid #c04040;border-radius:8px;
padding:8px 12px;font-size:0.78rem;color:#ff9090;margin-bottom:12px;">
⚠️ Chưa có API Key!<br>Mở file app.py → tìm dòng ANTHROPIC_API_KEY → dán key vào
</div>""", unsafe_allow_html=True)

    st.markdown(f"<div style='height:1px;background:rgba(168,135,74,0.25);margin:4px 0 12px;'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.8rem;color:{MTL_GOLD2};font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>📂 Tải hồ sơ lên</div>", unsafe_allow_html=True)

    files_upload = st.file_uploader(
        "Chọn file",
        type=["pdf", "docx", "png", "jpg", "jpeg", "tiff", "bmp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if "noi_dung_files" not in st.session_state:
        st.session_state.noi_dung_files = []

    if files_upload:
        st.session_state.noi_dung_files = []
        for f in files_upload:
            data = f.read()
            ext  = f.name.rsplit(".", 1)[-1].lower()
            if ext == "pdf":
                st.session_state.noi_dung_files.append({"ten": f.name, "loai": "pdf", "du_lieu": doc_pdf(data)})
            elif ext == "docx":
                st.session_state.noi_dung_files.append({"ten": f.name, "loai": "docx", "du_lieu": doc_docx(data)})
            elif ext in ["png", "jpg", "jpeg", "tiff", "bmp"]:
                media = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "tiff": "image/tiff", "bmp": "image/bmp"}
                st.session_state.noi_dung_files.append({
                    "ten": f.name, "loai": "anh",
                    "du_lieu": base64.standard_b64encode(data).decode(),
                    "media_type": media.get(ext, "image/jpeg"),
                })
        if st.session_state.noi_dung_files:
            st.success(f"✅ Đã tải {len(st.session_state.noi_dung_files)} file")
            for item in st.session_state.noi_dung_files:
                icon = "🖼️" if item["loai"] == "anh" else "📄"
                st.markdown(f"<div style='font-size:0.8rem;padding:2px 0;'>{icon} {item['ten']}</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='height:1px;background:rgba(168,135,74,0.25);margin:12px 0;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Đăng xuất", use_container_width=True):
        dang_xuat()

    # ── GMAIL OAuth ──────────────────────────────
    st.markdown(f"<div style='height:1px;background:rgba(168,135,74,0.25);margin:12px 0;'></div>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.8rem;color:{MTL_GOLD2};font-weight:600;"
        f"text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>📧 Gmail</div>",
        unsafe_allow_html=True,
    )

    # Khoá session theo từng luật sư để tách biệt hoàn toàn
    _cred_key = f"gcred_{nd['ten_tk']}"

    def _get_creds():
        """Lấy credentials đã lưu của luật sư này."""
        return st.session_state.get(_cred_key)

    def _is_connected():
        c = _get_creds()
        if not c:
            return False
        # Tự refresh token nếu hết hạn
        if c.expired and c.refresh_token:
            try:
                c.refresh(Request())
                st.session_state[_cred_key] = c
            except Exception:
                return False
        return c.valid

    # Đọc cấu hình OAuth từ Railway env vars
    _CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
    _CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    _APP_URL       = os.environ.get("APP_URL", "http://localhost:8501")
    _SCOPES        = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ]

    _oauth_ready = bool(_CLIENT_ID and _CLIENT_SECRET)

    if not _oauth_ready:
        st.markdown(
            "<div style='background:rgba(220,80,80,0.15);border:1px solid #c04040;"
            "border-radius:8px;padding:8px 10px;font-size:0.75rem;color:#ff9090;'>"
            "⚠️ Chưa cấu hình OAuth<br>Thêm GOOGLE_CLIENT_ID và<br>"
            "GOOGLE_CLIENT_SECRET vào Railway</div>",
            unsafe_allow_html=True,
        )
    elif _is_connected():
        c = _get_creds()
        # Lấy email từ userinfo
        _email_disp = st.session_state.get(f"gemail_{nd['ten_tk']}", "Gmail đã kết nối")
        st.markdown(
            f"<div style='background:rgba(100,180,100,0.15);border:1px solid #4a9a4a;"
            f"border-radius:8px;padding:8px 10px;font-size:0.78rem;color:#90ee90;'>"
            f"✅ {_email_disp}</div>",
            unsafe_allow_html=True,
        )
        if st.button("↩ Ngắt kết nối Gmail", use_container_width=True,
                     key=f"gdisconn_{nd['ten_tk']}"):
            st.session_state.pop(_cred_key, None)
            st.rerun()
    else:
        _qp    = st.query_params
        _code  = _qp.get("code", "")
        _state = _qp.get("state", "")
        _clean_url = _APP_URL.rstrip("/")

        if _code and _state == nd["ten_tk"]:
            # Dùng requests gọi thẳng Google Token API — không qua Flow
            import requests as _http
            _done_key = f"oauth_done_{_code[:28]}"

            if st.session_state.get(_cred_key) and st.session_state[_cred_key].valid:
                # Đã có credentials hợp lệ → chỉ xoá params
                st.query_params.clear()
                st.rerun()
            elif not st.session_state.get(_done_key):
                st.session_state[_done_key] = True
                with st.spinner("Đang xác thực với Google..."):
                    _tok = _http.post(
                        "https://oauth2.googleapis.com/token",
                        data={
                            "code":          _code,
                            "client_id":     _CLIENT_ID,
                            "client_secret": _CLIENT_SECRET,
                            "redirect_uri":  _clean_url,
                            "grant_type":    "authorization_code",
                        },
                        timeout=15,
                    ).json()

                if "error" in _tok:
                    st.session_state.pop(_done_key, None)
                    st.error(f"Google từ chối: {_tok.get('error_description', _tok['error'])}")
                else:
                    # Tạo Credentials thủ công từ token nhận được
                    _creds = Credentials(
                        token=_tok["access_token"],
                        refresh_token=_tok.get("refresh_token"),
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=_CLIENT_ID,
                        client_secret=_CLIENT_SECRET,
                        scopes=_SCOPES,
                    )
                    st.session_state[_cred_key] = _creds
                    # Lấy địa chỉ email
                    try:
                        _info = _http.get(
                            "https://www.googleapis.com/oauth2/v2/userinfo",
                            headers={"Authorization": f"Bearer {_tok['access_token']}"},
                            timeout=10,
                        ).json()
                        st.session_state[f"gemail_{nd['ten_tk']}"] = _info.get("email", "")
                    except Exception:
                        pass
                    st.query_params.clear()
                    st.rerun()
        else:
            # Tạo URL đăng nhập Google thủ công — không qua Flow
            _scope_str = urllib.parse.quote(" ".join(_SCOPES))
            _state_str = urllib.parse.quote(nd["ten_tk"])
            _redir_str = urllib.parse.quote(_clean_url)
            _auth_url  = (
                "https://accounts.google.com/o/oauth2/v2/auth"
                f"?client_id={_CLIENT_ID}"
                f"&redirect_uri={_redir_str}"
                f"&response_type=code"
                f"&scope={_scope_str}"
                f"&access_type=offline"
                f"&prompt=consent"
                f"&state={_state_str}"
            )
            st.markdown(
                f'<a href="{_auth_url}" target="_self">'
                f'<button style="width:100%;background:#4285F4;color:white;border:none;'
                f'border-radius:8px;padding:9px;font-size:0.85rem;font-weight:600;'
                f'cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;">'
                f'<svg width="18" height="18" viewBox="0 0 48 48">'
                f'<path fill="#fff" d="M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z"/>'
                f'</svg>Đăng nhập với Google</button></a>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div style='font-size:0.71rem;color:#aaa;margin-top:5px;text-align:center;'>"
                "Dùng mật khẩu Gmail thông thường</div>",
                unsafe_allow_html=True,
            )

# ── HEADER ──
st.markdown(f"""
<div class="mtl-header">
  <div class="mtl-header-inner">
    <div style="display:flex;align-items:center;gap:4px;flex-shrink:0;">
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

# ── TABS ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Phân tích hồ sơ",
    "📝 Soạn thảo văn bản",
    "💬 Hỏi đáp pháp lý",
    "📋 Hướng dẫn sử dụng",
    "📧 Email Intelligence",
])

# ══════════════════════════════════════════════
#  TAB 1 — PHÂN TÍCH HỒ SƠ
# ══════════════════════════════════════════════
with tab1:
    st.subheader("🔍 Phân tích hồ sơ vụ việc")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        yeu_cau = st.text_area(
            "Yêu cầu phân tích cụ thể (tùy chọn)",
            placeholder="Ví dụ: Tập trung vào thời hiệu khởi kiện, quyền đòi bồi thường...",
            height=80,
        )
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        nut_pt = st.button("🚀 Phân tích ngay", use_container_width=True, type="primary")

    if nut_pt:
        if not API_KEY:
            st.error("❌ Chưa có API Key. Mở file app.py, tìm dòng ANTHROPIC_API_KEY và điền key vào.")
        elif not st.session_state.noi_dung_files:
            st.warning("⚠️ Vui lòng tải ít nhất 1 file hồ sơ ở thanh bên trái.")
        else:
            with st.spinner("🤖 AI đang nghiên cứu hồ sơ..."):
                ket_qua = phan_tich_ho_so(st.session_state.noi_dung_files, yeu_cau)
                st.session_state.ket_qua_phan_tich = ket_qua

    if "ket_qua_phan_tich" in st.session_state and st.session_state.ket_qua_phan_tich:
        st.markdown("---")
        st.markdown("#### 📊 Kết quả phân tích")
        st.markdown(
            f'<div class="result-box">{st.session_state.ket_qua_phan_tich.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        word_bytes = tao_file_word(
            "BÁO CÁO PHÂN TÍCH HỒ SƠ VỤ VIỆC",
            st.session_state.ket_qua_phan_tich,
            nd["ho_ten"], nd["chuc_vu"],
        )
        st.download_button(
            "⬇️ Tải xuống file Word", data=word_bytes,
            file_name=f"PhanTich_{datetime.now().strftime('%d%m%Y_%H%M')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

# ══════════════════════════════════════════════
#  TAB 2 — SOẠN THẢO
# ══════════════════════════════════════════════
with tab2:
    st.subheader("📝 Soạn thảo văn bản pháp lý")

    LOAI_DON = [
        "Đơn khởi kiện", "Đơn yêu cầu thi hành án", "Đơn đề nghị hòa giải",
        "Đơn tố cáo", "Đơn xin cấp bản sao hồ sơ",
        "Đơn xin gia hạn nộp tiền tạm ứng án phí",
        "Hợp đồng dịch vụ pháp lý", "Thông báo pháp lý (Legal Notice)",
        "Biên bản cuộc họp", "Phiếu yêu cầu tư vấn", "Văn bản khác (tự nhập)",
    ]

    col1, col2 = st.columns(2)
    with col1:
        loai_don = st.selectbox("Loại văn bản", LOAI_DON)
    with col2:
        if loai_don == "Văn bản khác (tự nhập)":
            loai_don = st.text_input("Nhập loại văn bản", placeholder="Ví dụ: Đơn phản đối...")

    noi_dung_vv = st.text_area(
        "Mô tả vụ việc / thông tin cần đưa vào",
        placeholder="Nguyên đơn: ...\nBị đơn: ...\nNội dung tranh chấp: ...\nYêu cầu: ...",
        height=140,
    )

    if "ket_qua_phan_tich" in st.session_state and st.session_state.ket_qua_phan_tich:
        if st.checkbox("📂 Lấy thông tin từ hồ sơ đã phân tích"):
            noi_dung_vv = st.session_state.ket_qua_phan_tich[:1500]

    them = st.text_input("Yêu cầu thêm", placeholder="Ví dụ: Nhấn mạnh điều 166 BLDS...")

    if st.button("✍️ Soạn văn bản", type="primary"):
        if not API_KEY:
            st.error("❌ Chưa có API Key. Mở file app.py, tìm dòng ANTHROPIC_API_KEY và điền key vào.")
        elif not noi_dung_vv.strip():
            st.warning("⚠️ Vui lòng nhập thông tin vụ việc.")
        else:
            with st.spinner("🤖 AI đang soạn thảo..."):
                van_ban = soan_don_tu(loai_don, noi_dung_vv, them)
                st.session_state.van_ban_soan = van_ban
                st.session_state.loai_van_ban = loai_don

    if "van_ban_soan" in st.session_state and st.session_state.van_ban_soan:
        st.markdown("---")
        vb_edit = st.text_area("✏️ Chỉnh sửa nếu cần", value=st.session_state.van_ban_soan, height=400)
        ten_file = st.session_state.loai_van_ban.replace(" ", "_")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            word_bytes = tao_file_word(st.session_state.loai_van_ban, vb_edit, nd["ho_ten"], nd["chuc_vu"])
            st.download_button(
                "⬇️ Tải xuống file Word", data=word_bytes,
                file_name=f"{ten_file}_{datetime.now().strftime('%d%m%Y')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with col_d2:
            st.download_button(
                "📋 Tải xuống file TXT", data=vb_edit.encode("utf-8"),
                file_name=f"{ten_file}_{datetime.now().strftime('%d%m%Y')}.txt",
                mime="text/plain", use_container_width=True,
            )

# ══════════════════════════════════════════════
#  TAB 3 — HỎI ĐÁP
# ══════════════════════════════════════════════
with tab3:
    st.subheader("💬 Hỏi đáp pháp lý")

    if "lich_su_chat" not in st.session_state:
        st.session_state.lich_su_chat = []

    for tin in st.session_state.lich_su_chat:
        with st.chat_message("user" if tin["role"] == "user" else "assistant",
                             avatar="👤" if tin["role"] == "user" else "⚖️"):
            st.write(tin["content"])

    cau_hoi = st.chat_input("Hỏi về pháp luật, vụ việc, hoặc nội dung hồ sơ đã tải lên...")

    if cau_hoi:
        if not API_KEY:
            st.error("❌ Chưa có API Key. Mở file app.py, tìm dòng ANTHROPIC_API_KEY và điền key vào.")
        else:
            st.session_state.lich_su_chat.append({"role": "user", "content": cau_hoi})
            with st.chat_message("user", avatar="👤"):
                st.write(cau_hoi)
            with st.chat_message("assistant", avatar="⚖️"):
                with st.spinner("Đang tra cứu..."):
                    tra_loi = hoi_dap(st.session_state.lich_su_chat[:-1], cau_hoi, st.session_state.noi_dung_files)
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
### 🔑 Cấu hình API Key (chỉ làm 1 lần)

Mở file `app.py` → tìm dòng số **21**:
```
ANTHROPIC_API_KEY = "sk-ant-"
```
Thay `sk-ant-` bằng key thật của bạn. Lấy key tại: **console.anthropic.com**

---

### 🚀 Sử dụng hàng ngày

**Bước 1:** Tải hồ sơ vụ việc ở thanh bên trái (PDF, Word, ảnh chụp, chữ viết tay).

**Bước 2:** Chọn chức năng:
- **Phân tích hồ sơ** — AI đọc toàn bộ hồ sơ, phân tích pháp lý, xuất báo cáo Word.
- **Soạn thảo văn bản** — Chọn loại đơn, AI soạn đúng mẫu pháp lý, tải về Word.
- **Hỏi đáp pháp lý** — Chat trực tiếp về luật và hồ sơ đã tải lên.

---

### 👥 Danh sách tài khoản

| Tài khoản | Mật khẩu | Họ tên |
|-----------|----------|--------|
""" + "\n".join([f"| `{tk}` | `{info['mat_khau']}` | {info['ho_ten']} |" for tk, info in TAI_KHOAN.items()]) + f"""

---
### 🏢 {TEN_CONG_TY}
{DIA_CHI_CT}  
{DIA_CHI_DN}  
{SBT_CT}
""")

# ══════════════════════════════════════════════
#  TAB 5 — EMAIL INTELLIGENCE
# ══════════════════════════════════════════════

# ── Gmail API helpers ──────────────────────────────────────────
def _gmail_service():
    """Trả về Gmail service của luật sư đang đăng nhập."""
    creds = st.session_state.get(f"gcred_{nd['ten_tk']}")
    if not creds or not creds.valid:
        return None
    return build("gmail", "v1", credentials=creds)


def tai_email_gmail_api(so_luong: int = 12) -> list:
    """Tải email từ Gmail qua API."""
    svc = _gmail_service()
    if not svc:
        return []
    try:
        resp = svc.users().messages().list(
            userId="me", maxResults=so_luong, labelIds=["INBOX"]
        ).execute()
        msgs = resp.get("messages", [])
        results = []
        for m in msgs:
            full = svc.users().messages().get(
                userId="me", id=m["id"], format="full"
            ).execute()
            headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
            subject = headers.get("Subject", "(Không có tiêu đề)")
            from_   = headers.get("From", "")
            date_   = headers.get("Date", "")[:22]

            # Parse sender
            _m = re.match(r'"?(.+?)"?\s*<(.+?)>', from_)
            from_name  = _m.group(1).strip() if _m else from_
            from_email = _m.group(2).strip() if _m else from_

            # Lấy text body
            body = _extract_body(full["payload"])

            unread = "UNREAD" in full.get("labelIds", [])
            results.append({
                "id":        m["id"],
                "fromName":  from_name,
                "fromEmail": from_email,
                "subject":   subject,
                "date":      date_,
                "body":      body[:4000],
                "unread":    unread,
            })
        return results
    except Exception as e:
        st.error(f"Gmail API lỗi: {e}")
        return []


def _extract_body(payload: dict) -> str:
    """Lấy nội dung text/plain từ payload email."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result
    return ""


def gui_email_gmail_api(to: str, subject: str, body: str) -> bool:
    """Gửi email reply qua Gmail API."""
    svc = _gmail_service()
    if not svc:
        return False
    try:
        import email as email_lib
        from email.mime.text import MIMEText
        msg = MIMEText(body, "plain", "utf-8")
        sender = st.session_state.get(f"gemail_{nd['ten_tk']}", "me")
        msg["From"]    = sender
        msg["To"]      = to
        msg["Subject"] = f"Re: {subject}"
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        svc.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        return True
    except Exception as e:
        st.error(f"Gửi email lỗi: {e}")
        return False


# ── AI helpers — tái sử dụng goi_claude() ──────────────────────
def phan_tich_email_phap_ly(email: dict) -> dict:
    system = f"Bạn là trợ lý pháp lý tại {TEN_CONG_TY}. Trả về JSON thuần, không markdown."
    prompt = f"""Phân tích email và trả về đúng JSON:
{{
  "urgency": "high|medium|low", "urgency_score": 0-100,
  "urgency_reason": "lý do", "category": "loại vụ việc",
  "summary": "tóm tắt 1-2 câu",
  "legal_issues": ["vấn đề 1","vấn đề 2"],
  "relevant_laws": ["Luật 1","Luật 2"],
  "parties": [{{"role":"vai trò","name":"tên"}}],
  "action_items": ["việc 1","việc 2"],
  "deadline": "thời hạn hoặc null",
  "risk_level": "Cao|Trung bình|Thấp"
}}
Tiêu đề: {email.get('subject','')}
Từ: {email.get('fromName','')} <{email.get('fromEmail','')}>
Nội dung:\n{email.get('body','')[:3000]}"""
    text = goi_claude([{"role":"user","content":prompt}], system)
    try:
        return json.loads(text.replace("```json","").replace("```","").strip())
    except Exception:
        return {}


def soan_phan_hoi(email: dict, analysis: dict, tone: str) -> str:
    tone_map = {
        "formal":   "trang trọng, văn phong luật sư chuyên nghiệp",
        "friendly": "thân thiện, gần gũi nhưng vẫn chuyên nghiệp",
        "firm":     "kiên quyết, rõ ràng, thể hiện quyền hạn",
        "urgent":   "khẩn cấp, nhấn mạnh cần hành động ngay",
    }
    ctx = ""
    if analysis:
        ctx = (f"\nPhân tích: {analysis.get('summary','')}\n"
               f"Hành động: {'; '.join(analysis.get('action_items',[]))}")
    system = f"Bạn là luật sư tại {TEN_CONG_TY}."
    prompt = (f"Soạn email phản hồi tiếng Việt, giọng {tone_map.get(tone,'trang trọng')}. "
              f"Bắt đầu 'Kính gửi...', KHÔNG viết subject, xác nhận nhận email, "
              f"nêu hướng xử lý, đề xuất bước tiếp theo. "
              f"Ký tên: {nd['ho_ten']} — {TEN_CONG_TY}{ctx}\n\n"
              f"Tiêu đề: {email.get('subject','')}\n"
              f"Từ: {email.get('fromName','')}\n"
              f"Nội dung:\n{email.get('body','')[:2000]}")
    return goi_claude([{"role":"user","content":prompt}], system)


def gan_tag(email: dict) -> list:
    text = f"{email.get('subject','')} {email.get('body','')}".lower()
    rules = {
        "🔴 Khẩn":       ["khẩn","gấp","ngay","vi phạm","khởi kiện"],
        "🟡 Hợp đồng":   ["hợp đồng","ký kết","điều khoản","soát xét"],
        "🟣 Tranh chấp": ["tranh chấp","kiện","tòa án","bồi thường"],
        "🟢 Tư vấn":     ["tư vấn","hỏi","thành lập","startup"],
    }
    tags = [t for t, kws in rules.items() if any(k in text for k in kws)]
    return tags if tags else ["🔵 Thông thường"]


EMAIL_MAU = [
    {"id":"m1","unread":True,"fromName":"Nguyễn Văn Minh","fromEmail":"nvminh@vietcorp.vn",
     "date":"09:42","subject":"Tranh chấp hợp đồng mua bán căn hộ — cần tư vấn khẩn",
     "body":"Kính gửi Luật sư,\n\nTôi đã ký hợp đồng mua căn hộ tại dự án Green Valley ngày 15/03/2024, giá trị 3,2 tỷ đồng. Chủ đầu tư vi phạm:\n1. Trễ bàn giao 8 tháng\n2. Từ chối trả phạt điều 9 (0.05%/ngày)\n3. Đơn phương thay đổi thiết kế\n\nCần tư vấn khẩn.\n\nTrân trọng,\nNguyễn Văn Minh"},
    {"id":"m2","unread":True,"fromName":"Trần Thị Hà","fromEmail":"ttha@mfg.com.vn",
     "date":"Hôm qua","subject":"Soát xét hợp đồng phân phối độc quyền 5M USD",
     "body":"Luật sư kính mến,\n\nChuẩn bị ký hợp đồng phân phối với Korea Tech Co., Ltd., giá trị 5M USD/năm. Cần soát xét Điều 6, 12, 15 và Phụ lục A.\nHạn ký: 30/04/2025.\n\nTrân trọng,\nTrần Thị Hà"},
    {"id":"m3","unread":False,"fromName":"Phạm Quốc Bảo","fromEmail":"pqbao@startup.io",
     "date":"20/04","subject":"Tư vấn thành lập startup FinTech P2P Lending",
     "body":"Kính gửi Văn phòng Luật Minh Tú,\n\nCần tư vấn thành lập startup FinTech (P2P Lending):\n1. Hình thức pháp nhân\n2. Cấu trúc vốn Seed từ Singapore\n3. NĐ 52/2021\n\nNgân sách: 50-80tr.\n\nTrân trọng, Phạm Quốc Bảo"},
]


# ══════════════════════════════════════════════
#  RENDER TAB 5
# ══════════════════════════════════════════════
with tab5:
    for _k, _v in {
        "ei_emails":[], "ei_selected":None,
        "ei_analysis":None, "ei_draft":"",
        "ei_tone":"formal", "ei_sent":[],
    }.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # Kiểm tra kết nối
    _connected = bool(
        st.session_state.get(f"gcred_{nd['ten_tk']}") and
        st.session_state.get(f"gcred_{nd['ten_tk']}").valid
    )
    _gmail_addr = st.session_state.get(f"gemail_{nd['ten_tk']}", "")

    # Banner
    _status = (f"<span style='color:#90ee90;'>✅ {_gmail_addr}</span>"
               if _connected else
               "<span style='color:#ffa07a;'>⚠️ Chưa kết nối — nhấn nút Google ở thanh bên</span>")
    st.markdown(f"""
<div style="background:linear-gradient(135deg,{MTL_NAVY2} 0%,{MTL_NAVY} 100%);
border-radius:10px;padding:14px 20px;margin-bottom:18px;
border-left:4px solid {MTL_GOLD};display:flex;align-items:center;justify-content:space-between;">
  <div>
    <span style="color:white;font-size:1.05rem;font-weight:700;">📧 Email Intelligence</span>
    <span style="color:{MTL_GOLD2};font-size:0.8rem;margin-left:12px;">
      Gmail API · Phân tích pháp lý AI · Soạn thảo tự động
    </span>
  </div>
  <div>{_status}</div>
</div>""", unsafe_allow_html=True)

    col_inbox, col_email, col_ai = st.columns([1.2, 2, 1.8])

    # ── CỘT 1: HỘP THƯ ──────────────────────
    with col_inbox:
        st.markdown(f"<div style='font-weight:700;color:{MTL_NAVY};margin-bottom:8px;'>📬 Hộp thư</div>",
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("↻ Tải email", use_container_width=True, key="ei_load"):
                if not _connected:
                    st.warning("Đăng nhập Google ở thanh bên trước")
                else:
                    with st.spinner("Đang tải..."):
                        emails = tai_email_gmail_api(so_luong=12)
                    if emails:
                        st.session_state.ei_emails = emails
                        st.rerun()
                    else:
                        st.error("Không tải được email")
        with c2:
            if st.button("📋 Demo", use_container_width=True, key="ei_demo"):
                st.session_state.ei_emails = EMAIL_MAU
                st.rerun()

        emails = st.session_state.ei_emails
        if not emails:
            st.markdown("<div style='color:#aaa;font-size:0.82rem;text-align:center;"
                        "padding:24px 0;'>Đăng nhập Gmail → Tải email<br>hoặc nhấn Demo</div>",
                        unsafe_allow_html=True)
        else:
            chua_doc = sum(1 for e in emails if e.get("unread"))
            st.caption(f"{chua_doc} chưa đọc · {len(emails)} tổng")
            for em in emails:
                _sel = st.session_state.ei_selected
                is_sel = bool(_sel and _sel.get("id") == em["id"])
                tags   = gan_tag(em)
                label  = ("🔵 " if em.get("unread") else "") + em["fromName"]
                subj   = em["subject"][:36] + ("…" if len(em["subject"]) > 36 else "")
                if st.button(f"{label}\n{' '.join(tags[:1])}  {subj}",
                             key=f"ei_em_{em['id']}", use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    st.session_state.ei_selected = em
                    st.session_state.ei_analysis  = None
                    st.session_state.ei_draft     = ""
                    st.rerun()

    # ── CỘT 2: NỘI DUNG EMAIL ───────────────
    with col_email:
        em = st.session_state.ei_selected
        if em is None:
            st.markdown("<div style='color:#aaa;text-align:center;padding:80px 0;'>"
                        "👈 Chọn email để xem</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='font-size:1rem;font-weight:700;color:{MTL_NAVY};"
                f"border-bottom:2px solid {MTL_GOLD}44;padding-bottom:8px;margin-bottom:10px;'>"
                f"{em['subject']}</div>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.markdown(f"**Từ:** {em['fromName']}  \n`{em['fromEmail']}`")
            m2.markdown(f"**Lúc:** {em.get('date','')}")
            tags_html = " &nbsp;".join(
                f"<span style='background:{MTL_NAVY}11;border:1px solid {MTL_NAVY}33;"
                f"border-radius:4px;padding:2px 8px;font-size:0.75rem;'>{t}</span>"
                for t in gan_tag(em))
            st.markdown(tags_html, unsafe_allow_html=True)
            st.divider()
            body_safe = em["body"].replace("<","&lt;").replace(">","&gt;")
            st.markdown(
                f"<div style='background:#f8f9fc;border:1px solid #e0e8f5;"
                f"border-left:3px solid {MTL_NAVY};border-radius:0 8px 8px 0;"
                f"padding:16px 18px;font-size:0.87rem;line-height:1.85;"
                f"white-space:pre-wrap;max-height:360px;overflow-y:auto;'>"
                f"{body_safe}</div>", unsafe_allow_html=True)
            st.divider()
            qa, qb, qc = st.columns(3)
            with qa:
                if st.button("🔍 Phân tích AI", use_container_width=True, key="ei_analyze"):
                    with st.spinner("Claude đang phân tích..."):
                        st.session_state.ei_analysis = phan_tich_email_phap_ly(em)
                    st.rerun()
            with qb:
                if st.button("✦ Soạn thảo", use_container_width=True, key="ei_draft_btn"):
                    with st.spinner("Claude đang soạn..."):
                        st.session_state.ei_draft = soan_phan_hoi(
                            em, st.session_state.ei_analysis, st.session_state.ei_tone)
                    st.rerun()
            with qc:
                if st.button("📄 Tạo văn bản", use_container_width=True, key="ei_docbtn"):
                    a = st.session_state.ei_analysis
                    if a:
                        nd_vb = (f"Vụ việc: {em['subject']}\nKhách hàng: {em['fromName']}\n\n"
                                 f"Tóm tắt: {a.get('summary','')}\n\n"
                                 f"Vấn đề pháp lý:\n" + "\n".join(f"- {i}" for i in a.get("legal_issues",[])) +
                                 f"\n\nHành động:\n" + "\n".join(f"{i+1}. {x}" for i,x in enumerate(a.get("action_items",[]))))
                        vb = soan_don_tu("Thư tư vấn pháp lý", nd_vb)
                        st.session_state.van_ban_soan  = vb
                        st.session_state.loai_van_ban = "Thư tư vấn pháp lý"
                        st.success("✅ Đã tạo — xem tab Soạn thảo văn bản")
                    else:
                        st.warning("Phân tích AI trước")

    # ── CỘT 3: AI PANEL ─────────────────────
    with col_ai:
        if st.session_state.ei_selected is None:
            st.info("Chọn email để bắt đầu")
        else:
            em = st.session_state.ei_selected
            ai1, ai2, ai3 = st.tabs(["🔍 Phân tích", "✍ Soạn thảo", "📤 Đã gửi"])

            with ai1:
                a = st.session_state.ei_analysis
                if a is None:
                    st.markdown("<div style='color:#aaa;text-align:center;padding:24px 0;'>"
                                "Nhấn 🔍 Phân tích AI</div>", unsafe_allow_html=True)
                elif a == {}:
                    st.error("Phân tích thất bại — kiểm tra API Key")
                else:
                    score = a.get("urgency_score", 0)
                    level = a.get("urgency","low")
                    bar_c = {"high":"#e53e3e","medium":"#d69e2e","low":"#38a169"}.get(level,"#718096")
                    urg_l = {"high":"🔴 Khẩn cấp","medium":"🟡 Trung bình","low":"🟢 Thấp"}.get(level,"")
                    st.markdown(
                        f"<div style='display:flex;justify-content:space-between;margin-bottom:4px;'>"
                        f"<b style='font-size:0.85rem;'>{urg_l}</b>"
                        f"<span style='color:#718096;font-size:0.8rem;'>{score}/100</span></div>"
                        f"<div style='background:#e2e8f0;border-radius:4px;height:6px;'>"
                        f"<div style='background:{bar_c};width:{score}%;height:6px;border-radius:4px;'></div></div>",
                        unsafe_allow_html=True)
                    st.caption(a.get("urgency_reason",""))
                    if a.get("deadline"):
                        st.warning(f"⏱ {a['deadline']}")
                    st.markdown(
                        f"<div style='background:{MTL_NAVY}08;border-left:3px solid {MTL_GOLD};"
                        f"border-radius:0 6px 6px 0;padding:10px 12px;margin:10px 0;'>"
                        f"<b style='font-size:0.85rem;color:{MTL_NAVY};'>{a.get('category','')}</b><br>"
                        f"<span style='font-size:0.82rem;color:#4a5568;'>{a.get('summary','')}</span></div>",
                        unsafe_allow_html=True)
                    if a.get("legal_issues"):
                        with st.expander("⚖ Vấn đề pháp lý", expanded=True):
                            for iss in a["legal_issues"]: st.markdown(f"- {iss}")
                    if a.get("relevant_laws"):
                        with st.expander("📋 Căn cứ pháp lý"):
                            for law in a["relevant_laws"]: st.markdown(f"`{law}`")
                    if a.get("action_items"):
                        with st.expander("✅ Hành động", expanded=True):
                            for i, act in enumerate(a["action_items"],1): st.markdown(f"{i}. {act}")
                    risk = a.get("risk_level","")
                    risk_ic = {"Cao":"🔴","Trung bình":"🟡","Thấp":"🟢"}.get(risk,"")
                    st.divider()
                    st.caption(f"Rủi ro: {risk_ic} {risk}")
                    bao_cao = (
                        f"VỤ VIỆC: {em['subject']}\nKHÁCH HÀNG: {em['fromName']}\n\n"
                        f"TÓM TẮT:\n{a.get('summary','')}\n\n"
                        f"VẤN ĐỀ PHÁP LÝ:\n" + "\n".join(f"- {i}" for i in a.get("legal_issues",[])) +
                        f"\n\nCĂN CỨ PHÁP LÝ:\n" + "\n".join(f"- {l}" for l in a.get("relevant_laws",[])) +
                        f"\n\nHÀNH ĐỘNG CẦN LÀM:\n" + "\n".join(f"{i+1}. {x}" for i,x in enumerate(a.get("action_items",[]))))
                    wb = tao_file_word("BÁO CÁO PHÂN TÍCH EMAIL", bao_cao, nd["ho_ten"], nd["chuc_vu"])
                    st.download_button("⬇️ Xuất báo cáo Word", data=wb,
                        file_name=f"PhanTichEmail_{datetime.now().strftime('%d%m%Y_%H%M')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True)

            with ai2:
                tone_vi = {"formal":"Trang trọng","friendly":"Thân thiện",
                           "firm":"Kiên quyết","urgent":"Khẩn cấp"}
                tone_sel = st.radio("Giọng văn", options=list(tone_vi.keys()),
                                    format_func=lambda x: tone_vi[x],
                                    horizontal=True, key="ei_tone_r")
                st.session_state.ei_tone = tone_sel
                if st.button("✦ Tạo nháp AI", use_container_width=True, key="ei_gen"):
                    with st.spinner("Claude đang soạn..."):
                        st.session_state.ei_draft = soan_phan_hoi(
                            em, st.session_state.ei_analysis, tone_sel)
                    st.rerun()
                reply_to = st.text_input("Gửi đến", value=em.get("fromEmail",""), key="ei_to")
                draft = st.text_area("Nội dung phản hồi", value=st.session_state.ei_draft,
                                     height=240, key="ei_ta",
                                     placeholder="Nhấn '✦ Tạo nháp AI' hoặc tự soạn...")
                st.session_state.ei_draft = draft
                sa, sb = st.columns(2)
                with sa:
                    if draft.strip():
                        wb2 = tao_file_word(f"Phản hồi: {em['subject']}", draft, nd["ho_ten"], nd["chuc_vu"])
                        st.download_button("⬇️ Tải Word", data=wb2,
                            file_name=f"PhanHoi_{datetime.now().strftime('%d%m%Y_%H%M')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True)
                with sb:
                    if st.button("📤 Gửi Gmail", type="primary",
                                 use_container_width=True, key="ei_send"):
                        if not draft.strip():
                            st.warning("Nhập nội dung trước")
                        elif not _connected:
                            st.error("Đăng nhập Google ở thanh bên trước")
                        else:
                            with st.spinner("Đang gửi..."):
                                ok = gui_email_gmail_api(reply_to, em["subject"], draft)
                            if ok:
                                st.session_state.ei_sent.append({
                                    "to": reply_to, "subject": em["subject"],
                                    "body": draft, "time": datetime.now().strftime("%H:%M %d/%m"),
                                })
                                st.success("✅ Email đã gửi!")
                                st.session_state.ei_draft = ""
                                st.rerun()

            with ai3:
                sent = st.session_state.ei_sent
                if not sent:
                    st.info("Chưa có email nào được gửi")
                else:
                    for item in reversed(sent):
                        with st.expander(f"✅ {item['time']} → {item['to']}"):
                            st.markdown(f"**{item['subject']}**")
                            st.text(item["body"][:300] + ("…" if len(item["body"])>300 else ""))
