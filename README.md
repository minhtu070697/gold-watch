# Gold Watch — báo cáo giá vàng mỗi sáng 7h

Routine chạy mỗi 7h sáng (giờ VN): tổng hợp diễn biến giá vàng hôm trước
(XAU/USD + vàng VN), checklist 4 bước, tin nóng, định hướng — rồi **gửi email**
về cho người dùng.

## Vì sao cần script này

Connector Gmail trong môi trường này chỉ tạo được **nháp** (không có hành động
gửi), và raw SMTP (cổng 25/465/587) bị **chặn** trong sandbox. Nhưng HTTPS (443)
thì mở, nên ta gửi mail qua **API email over HTTPS** (`scripts/send_report.py`).

## Thiết lập 1 lần (≈3 phút)

1. Tạo tài khoản miễn phí tại **https://resend.com** (free tier: 100 mail/ngày,
   3.000/tháng — thừa cho 1 mail/ngày).
   - Đăng ký bằng chính email **tusvo.dev@gmail.com** để dùng được ngay địa chỉ
     gửi thử `onboarding@resend.dev` (gửi tới email chủ tài khoản). Muốn gửi từ
     địa chỉ riêng thì verify domain sau cũng được.
2. Lấy **API Key** (Resend → API Keys → Create).
3. Vào cấu hình **routine** này trên claude.ai/code → thêm biến môi trường:
   - `RESEND_API_KEY` = khóa vừa tạo
   - (tùy chọn) `MAIL_TO` = `tusvo.dev@gmail.com`
   - (tùy chọn) `MAIL_FROM` = `Gold Watch <onboarding@resend.dev>`
4. (Nếu cần) thêm `api.resend.com` vào **Allowed domains** của routine.

> Muốn dùng SendGrid thay Resend: đặt `SENDGRID_API_KEY` thay cho `RESEND_API_KEY`.
> Script tự nhận provider theo khóa có sẵn.

## Cách gửi

```bash
python3 scripts/send_report.py --subject "Báo cáo vàng ..." --body-file report.txt
# kèm bản HTML:
python3 scripts/send_report.py --subject "..." --body-file report.txt --html-file report.html
```

Mỗi sáng routine sẽ tạo `report.txt` rồi gọi lệnh trên. Script in ra
`HTTP 200 -> SENT` nếu thành công, hoặc lỗi cụ thể nếu thất bại.
