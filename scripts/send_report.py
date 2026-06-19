#!/usr/bin/env python3
"""Chuyển báo cáo vàng dạng text (report.txt) sang email HTML trình bày đẹp.

Dùng:
    python3 scripts/build_html.py report.txt > report.html

Quy ước nhận dạng (theo CẤU TRÚC BÁO CÁO trong CLAUDE.md):
  • Dòng tiêu đề lớn  -> ngay phía trên một dòng "====" (banner đầu email).
  • "1) ...", "2) ..." -> tiêu đề mục (in đậm, có vạch vàng bên trái).
  • Dòng bắt đầu "•"   -> gạch đầu dòng (in đậm phần nhãn trước dấu ":").
  • Dòng bắt đầu "-"   -> gạch đầu dòng phụ (thụt vào).
  • Dòng bắt đầu "→"   -> ô nhấn mạnh (kết luận của mục).
  • Dòng bắt đầu "("   -> ghi chú nhỏ, mờ ở cuối.
"""
import html
import re
import sys

# Bảng màu — vàng/be chuyên nghiệp
ACCENT = "#b8860b"        # dark goldenrod
ACCENT_DK = "#8a6500"
INK = "#1f2430"
MUTED = "#6b7280"
PAGE_BG = "#f4f5f7"
CARD_BG = "#ffffff"
CALLOUT_BG = "#fff8e6"
CALLOUT_INK = "#5a4a00"

SECTION_RE = re.compile(r"^\s*\d+\)\s")
RULE_RE = re.compile(r"^=+$")


def esc(s):
    return html.escape(s, quote=False)


def bold_label(text):
    """In đậm phần nhãn trước dấu ':' đầu tiên cho dễ đọc."""
    text = esc(text)
    if ":" in text:
        label, rest = text.split(":", 1)
        return f"<strong>{label}:</strong>{rest}"
    return text


def build(report_text):
    raw = report_text.replace("\r\n", "\n").split("\n")

    # Tách tiêu đề lớn: dòng ngay trên dòng "===="
    title = "BÁO CÁO GIÁ VÀNG"
    subtitle = ""
    skip = set()
    for i, ln in enumerate(raw):
        if RULE_RE.match(ln.strip()) and i > 0 and raw[i - 1].strip():
            full = raw[i - 1].strip()
            skip.add(i - 1)
            skip.add(i)
            if "—" in full:
                head, _, tail = full.partition("—")
                title = head.strip() or title
                subtitle = tail.strip()
            else:
                title = full
            break

    rows = []
    for i, ln in enumerate(raw):
        if i in skip:
            continue
        stripped = ln.strip()
        if not stripped:
            rows.append('<tr><td style="height:8px;line-height:8px;font-size:8px;">&nbsp;</td></tr>')
            continue

        if SECTION_RE.match(ln):
            rows.append(
                f'<tr><td style="padding:16px 26px 4px;">'
                f'<div style="font-size:15px;font-weight:700;color:{INK};'
                f'border-left:4px solid {ACCENT};padding-left:11px;line-height:1.35;">'
                f"{esc(stripped)}</div></td></tr>"
            )
        elif stripped.startswith("→"):
            body = bold_label(stripped[1:].strip())
            rows.append(
                f'<tr><td style="padding:6px 26px;">'
                f'<div style="background:{CALLOUT_BG};border-left:3px solid {ACCENT};'
                f'border-radius:5px;padding:9px 13px;font-size:13.5px;line-height:1.55;'
                f'color:{CALLOUT_INK};">▶ {body}</div></td></tr>'
            )
        elif stripped.startswith("•"):
            body = bold_label(stripped[1:].strip())
            rows.append(
                f'<tr><td style="padding:3px 26px 3px 30px;font-size:14px;'
                f'line-height:1.55;color:{INK};">'
                f'<span style="color:{ACCENT};">●</span>&nbsp; {body}</td></tr>'
            )
        elif stripped.startswith("-"):
            body = bold_label(stripped[1:].strip())
            rows.append(
                f'<tr><td style="padding:2px 26px 2px 48px;font-size:13.5px;'
                f'line-height:1.5;color:{INK};">– {body}</td></tr>'
            )
        elif stripped.startswith("("):
            rows.append(
                f'<tr><td style="padding:10px 26px 4px;font-size:12px;'
                f'font-style:italic;color:{MUTED};line-height:1.5;">{esc(stripped)}</td></tr>'
            )
        else:
            rows.append(
                f'<tr><td style="padding:3px 26px;font-size:14px;'
                f'line-height:1.55;color:{INK};">{esc(stripped)}</td></tr>'
            )

    body_rows = "\n".join(rows)
    title_h = esc(title)
    subtitle_h = esc(subtitle)
    subtitle_block = (
        f'<div style="font-size:13px;color:#fff3cf;margin-top:5px;">{subtitle_h}</div>'
        if subtitle
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="margin:0;padding:0;background:{PAGE_BG};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAGE_BG};padding:20px 0;">
<tr><td align="center">
<table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:{CARD_BG};border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
<tr><td style="background-color:{ACCENT};background-image:linear-gradient(135deg,{ACCENT},{ACCENT_DK});padding:22px 26px;">
<div style="font-size:20px;font-weight:800;color:#ffffff;letter-spacing:.3px;">🥇 {title_h}</div>
{subtitle_block}
</td></tr>
{body_rows}
<tr><td style="padding:16px 26px 22px;border-top:1px solid #eee;">
<div style="font-size:11.5px;color:{MUTED};line-height:1.5;">Gold Watch · báo cáo tự động mỗi sáng. Bối cảnh: mua vàng vật chất 1 lượng, ôm tới 2027, không bắt dao rơi — chỉ mua khi checklist ≥4/5 + spread VN co lại.</div>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>
"""


def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ("-", "--stdin"):
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    sys.stdout.write(build(text))


if __name__ == "__main__":
    main()
