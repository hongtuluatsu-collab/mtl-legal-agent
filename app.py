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
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import PyPDF2

# =============================================================
#  ★★★  DÁN API KEY VÀO ĐÂY — CHỈ LÀM 1 LẦN  ★★★
#  Lấy key tại: https://console.anthropic.com
# =============================================================
ANTHROPIC_API_KEY = "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"
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
    # Ưu tiên 1: biến môi trường Railway
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    # Ưu tiên 2: key điền trực tiếp ở đầu file
    if ANTHROPIC_API_KEY and len(ANTHROPIC_API_KEY) > 20:
        return ANTHROPIC_API_KEY
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
#  TẠO FILE WORD
# ─────────────────────────────────────────────
def tao_file_word(tieu_de, noi_dung, ten_ls, chuc_vu):
    doc = Document()
    section = doc.sections[0]
    section.page_width    = Cm(21)
    section.page_height   = Cm(29.7)
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.0)

    def them_doan(text, size=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, color=None):
        p = doc.add_paragraph()
        p.alignment = align
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        if color:
            run.font.color.rgb = color
        return p

    them_doan(TEN_CONG_TY, size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(0x1E, 0x4D, 0x82))
    them_doan(DIA_CHI_CT, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    them_doan(DIA_CHI_DN, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    them_doan(SBT_CT, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    them_doan("─" * 60, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()
    them_doan(tieu_de.upper(), size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    them_doan(f"(Ngày {datetime.now().strftime('%d tháng %m năm %Y')})", size=11, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    for dong in noi_dung.split("\n"):
        dong = dong.strip()
        if not dong:
            doc.add_paragraph()
            continue
        dong_sach = dong.replace("**", "").replace("###", "").replace("##", "").replace("# ", "")
        la_tieu_de = dong.isupper() or re.match(r"^\d+[\.\)]\s", dong) or dong.startswith("**")
        p = them_doan(dong_sach, size=12, bold=la_tieu_de, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        if not la_tieu_de:
            p.paragraph_format.first_line_indent = Cm(1.0)

    doc.add_paragraph()
    doc.add_paragraph()
    them_doan(f"TP. Hồ Chí Minh, {datetime.now().strftime('%d/%m/%Y')}", size=12, italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT)
    them_doan(f"{chuc_vu}\n\n\n\n{ten_ls}", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)

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
