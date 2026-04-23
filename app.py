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
    "ls.lan": {
        "mat_khau": "123456",
        "ho_ten":   "Luật sư Nguyễn Thị Thanh Lan",
        "chuc_vu":  "Counsel",
        "vai_tro":  "luat_su",
    },
    "ls.dong": {
        "mat_khau": "123456",
        "ho_ten":   "Luật sư Lê Viễn Đông",
        "chuc_vu":  "Trưởng CN Đà Nẵng",
        "vai_tro":  "luat_su",
    },
    "admin": {
        "mat_khau": "admin2026",
        "ho_ten":   "Quản trị viên",
        "chuc_vu":  "Quản lý hệ thống",
        "vai_tro":  "quan_tri",
    },
}

TEN_CONG_TY = "CÔNG TY LUẬT TNHH MINH TÚ"
DIA_CHI_CT  = "số 4/9 đường số 3, Cư Xá Đô Thành, Phường Bàn Cờ, TP. Hồ Chí Minh","số 81 Xô Viết Nghệ Tĩnh, Phường Cẩm Lệ, TP. Đà Nẵng"
SBT_CT      = "SĐT: 19000031 | Email: info.luatminhtu@gmail.com"

# ─────────────────────────────────────────────
#  KHỞI TẠO TRANG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MTL Legal Agent Premium",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS tùy chỉnh giao diện
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #1a3a5c, #2d6a9f);
        color: white;
        padding: 20px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .header-box h2 { margin: 0; font-size: 1.4rem; }
    .header-box p  { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .result-box {
        background: #f0f7ff;
        border-left: 4px solid #2d6a9f;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin-top: 12px;
    }
    .tag-success {
        background: #d4edda; color: #155724;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.8rem; font-weight: 600;
    }
    .tag-warning {
        background: #fff3cd; color: #856404;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.8rem; font-weight: 600;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    .login-container {
        max-width: 420px;
        margin: 60px auto;
    }
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
        st.markdown("---")
        st.markdown(f"<h2 style='text-align:center; color:#1a3a5c;'>⚖️ MTL Legal Agent Premium</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#555; margin-bottom:24px;'>{TEN_CONG_TY}</p>", unsafe_allow_html=True)

        with st.form("dang_nhap_form"):
            ten_tk   = st.text_input("Tên đăng nhập", placeholder="Ví dụ: ls.nguyen")
            mat_khau = st.text_input("Mật khẩu", type="password")
            nut_dn   = st.form_submit_button("🔐 Đăng nhập", use_container_width=True)

        if nut_dn:
            if dang_nhap(ten_tk.strip(), mat_khau):
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu.")

        st.markdown("---")
        st.markdown("<p style='text-align:center; color:#999; font-size:0.8rem;'>Tài khoản demo: ls.nguyen / 123456</p>", unsafe_allow_html=True)
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
    run = p.add_run(f"{DIA_CHI_CT}\n{SBT_CT}")
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
    run = p.add_run(f"Pleiku, {datetime.now().strftime('%d/%m/%Y')}\n")
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
    st.markdown(f"### ⚖️ MTL Legal Agent Premium")
    st.markdown(f"**{nd['ho_ten']}**")
    st.markdown(f"_{nd['chuc_vu']}_")
    st.markdown("---")

    # API Key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "") or st.text_input(
        "🔑 Anthropic API Key (nếu chưa cấu hình)",
        type="password",
        placeholder="sk-ant-...",
        help="Lấy tại: console.anthropic.com"
    )

    st.markdown("---")
    st.markdown("**📂 Tải hồ sơ lên**")

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
                st.markdown(f"{icon} {item['ten']}")

    st.markdown("---")
    if st.button("🚪 Đăng xuất", use_container_width=True):
        dang_xuat()

# ── HEADER ──
st.markdown(f"""
<div class="header-box">
  <h2>⚖️ MTL LEGAL AGENT PREMIUM</h2>
  <p>Chào {nd['ho_ten']} — {nd['chuc_vu']} &nbsp;|&nbsp; {datetime.now().strftime('%A, %d/%m/%Y')}</p>
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
{SBT_CT}
""")
