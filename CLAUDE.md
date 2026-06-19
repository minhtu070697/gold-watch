# Gold Watch — routine báo cáo giá vàng (chạy 7h sáng giờ VN)

Mỗi lần chạy: tổng hợp diễn biến giá vàng **hôm trước** và **GỬI EMAIL** cho người
dùng (`tusvo.dev@gmail.com`). Trình bày ngắn gọn, số liệu cụ thể, không dài dòng.

## CÁCH GỬI EMAIL (quan trọng — đọc trước khi gửi)

- **KHÔNG** dùng connector Gmail để gửi: nó chỉ tạo *nháp*, không gửi đi.
- **KHÔNG** dùng SMTP: sandbox chặn cổng 25/465/587.
- **DÙNG** `scripts/send_report.py` — gửi qua HTTPS email API (Resend/SendGrid).

  Quy trình 3 bước (luôn gửi kèm bản HTML cho đẹp):

  ```bash
  # 1) Viết báo cáo text vào report.txt (theo CẤU TRÚC BÁO CÁO bên dưới).
  # 2) Dựng HTML đẹp từ report.txt:
  python3 scripts/build_html.py report.txt > report.html
  # 3) Gửi cả text + HTML:
  python3 scripts/send_report.py --subject "<tiêu đề>" \
      --body-file report.txt --html-file report.html
  ```

  `scripts/build_html.py` tự định dạng: banner tiêu đề, **in đậm tên từng mục**
  (có vạch vàng bên trái), gạch đầu dòng, và ô nhấn mạnh cho dòng kết luận (bắt
  đầu bằng `→`). Vì vậy report.txt nên giữ đúng quy ước: tiêu đề lớn nằm trên một
  dòng `====`, mỗi mục bắt đầu bằng `1)`, `2)`…, gạch đầu dòng dùng `•` (và `-`
  cho ý phụ), dòng kết luận của mục bắt đầu bằng `→`.

  Script cần biến môi trường `RESEND_API_KEY` (hoặc `SENDGRID_API_KEY`) đã được
  cấu hình trong routine. **Người gửi (`MAIL_FROM`) phải là địa chỉ đã verify**
  trên SendGrid — hiện là `tusvo.dev@gmail.com` (đúng chính tả, có chữ "s"); nếu
  sai sẽ bị HTTP 403 "verified Sender Identity". Nếu in ra `HTTP 2xx -> SENT` là
  thành công; nếu báo thiếu key hoặc lỗi, dừng và báo lại người dùng (đừng âm
  thầm bỏ qua). Lưu ý: gửi *từ* địa chỉ `@gmail.com` qua SendGrid hay bị Gmail
  cho vào Spam — nếu không thấy mail, kiểm tra Spam/Promotions.

## CẤU TRÚC BÁO CÁO (6 mục)

1. **VÀNG THẾ GIỚI (XAU/USD)** — search giá hôm qua: đáy thấp nhất (kèm giờ nếu
   có), đỉnh cao nhất (kèm giờ), giá đóng phiên. So 3 mốc: sàn **$4.022** / vùng
   test **$4.080–4.124** / cò súng (đỉnh gần nhất — hỏi người dùng số cụ thể nếu chưa rõ).
2. **VÀNG VIỆT NAM** — nhẫn trơn 9999 và vàng miếng SJC hôm qua (mua/bán), tính
   spread (bán − mua), so mốc **2–3 triệu**.
3. **TRẠNG THÁI XU HƯỚNG** — hôm qua tạo đáy mới thấp hơn hay đã ngừng? Nếu đi
   ngang thì mấy ngày liên tiếp?
4. **CHECKLIST 4 BƯỚC** — đang ở bước nào (1: ngừng tạo đáy / 2: đi ngang /
   3: đáy cao hơn / 4: bứt phá). Đủ 4/5 chưa?
5. **TIN NÓNG** — 2–3 tin ảnh hưởng vàng nhất 24h (Fed, USD, lợi suất TPCP Mỹ,
   Trung Đông, lạm phát).
6. **ĐỊNH HƯỚNG** — hôm nay tiếp tục chờ hay vùng hành động đã mở?

## BỐI CẢNH NGƯỜI DÙNG (giữ nguyên trong mọi báo cáo)

Mua vàng **vật chất 1 lượng**, ôm tới **2027**. **KHÔNG bắt dao rơi.** Chỉ mua khi
**checklist xác nhận (≥4/5) + spread VN co lại**.
