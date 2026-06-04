# ShopeeFood — Evidence Pack

## 1. Nhóm và track

**Tên nhóm:** B6
**Track:** Food delivery / ordering
**Product/app đã chọn:** ShopeeFood
**Build slice đang nghĩ:** Giúp sinh viên/người đi làm chọn bữa trưa phù hợp trong dưới 1 phút bằng gợi ý 3 lựa chọn dựa trên ngân sách, khẩu vị, thời gian giao và voucher.

## 2. Self-use evidence

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Tìm bữa trưa dưới 60k, không cay, giao nhanh | (chụp màn hình quá trình lướt nhiều quán, so giá, voucher và phí ship) | Happy / Failure | Người dùng phải lướt nhiều; thông tin về giá, ship, voucher phân tán |
| So sánh nhiều quán cùng món với giá khác nhau | (chụp màn hình danh sách món/quán tương tự) | Happy / Low-confidence | Việc lựa chọn bị chậm do cần so sánh nhiều tiêu chí |
| Không chắc chắn nếu món có phù hợp khẩu vị/giới hạn ăn | (ghi chú từ quá trình thử) | Failure / Correction | Thông tin món chưa rõ, user cần cảnh báo hoặc xác nhận thêm |

## 3. User / review / social evidence

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| “Mình mở ShopeeFood nhưng nhiều lựa chọn quá, cuối cùng lướt 10 phút vẫn chưa biết ăn gì.” | Phỏng vấn nhanh 3 người dùng | Sinh viên / người đi làm | Quá nhiều lựa chọn, mất quá nhiều thời gian để quyết định |
| “Nhiều khi chọn quán vì voucher nhưng cộng phí ship vào lại không rẻ.” | Phỏng vấn nhanh | Sinh viên / người đi làm | So sánh voucher + phí ship gây nhầm lẫn |
| “Mình muốn tìm món phù hợp ngân sách nhưng phải tự so từng quán.” | Phỏng vấn nhanh | Sinh viên / người đi làm | Tốn công so sánh thủ công, không có gợi ý rõ ràng |

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| Now / GrabFood | Gợi ý quán, hiển thị voucher & phí ship rõ ràng | Hiển thị tổng chi phí sau voucher/ship ngay | Có thể áp dụng giao diện gợi ý đơn giản |
| Beamin / GoFood | Cung cấp bộ lọc nhanh và đề xuất món phổ biến, có section “gợi ý hôm nay” | Dùng các bộ lọc thông minh và xếp hạng để giúp user chọn nhanh | Có thể áp dụng phần filter + đề xuất top 3 |

## 5. Evidence -> Insight

Evidence nổi bật nhất:
- Người dùng ShopeeFood phải lướt nhiều, so sánh giá/voucher/ship/rating để tìm bữa trưa phù hợp.
- Người dùng dễ bị lạc khi chỉ có nhiều lựa chọn mà không có gợi ý quyết định nhanh.

Insight:
- User không chỉ cần đặt đồ ăn, mà cần hỗ trợ chọn món ngay khi mở app.
- Họ cần một quyết định nhanh dựa trên ngân sách, khẩu vị, thời gian và điều kiện giao hàng.

Opportunity:
- AI có thể giúp bằng cách augment việc lựa chọn: lọc, xếp hạng và giải thích 3 lựa chọn phù hợp thay vì để user tự so sánh tất cả.

## 6. Evidence đổi SPEC như thế nào?

- [ ] Đổi user chính.
- [ ] Đổi pain statement.
- [x] Đổi build slice.
- [x] Đổi Auto/Aug decision.
- [ ] Đổi 4 paths.
- [ ] Đổi failure mode.
- [ ] Đổi owner/test plan.

Trước evidence, nhóm có thể định tập trung vào tính năng đặt đơn nhanh.
Sau evidence, nhóm đổi thành tập trung vào việc giúp user quyết định món nhanh hơn bằng gợi ý AI.
Lý do: evidence cho thấy vấn đề không phải đặt món, mà là quyết định trong một biển lựa chọn.
