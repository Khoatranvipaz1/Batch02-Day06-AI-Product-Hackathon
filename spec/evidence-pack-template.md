# Evidence Pack — ShopeeFood AI Group Meal Finder

Nộp kèm `thin-spec.md` cuối Day 05.

---

## 1. Nhóm và track

**Tên nhóm:** `[Điền tên nhóm]`

**Track:** Food Delivery / Local Commerce

**Product/app đã chọn:** ShopeeFood

**Build slice đang nghĩ:**  
AI hỗ trợ tìm quán/món phù hợp nhiều điều kiện cùng lúc khi user đặt đồ ăn cho nhóm.

**Ví dụ task chính:**  
User muốn tìm: **cơm gà cho 5 người, budget 50k/người, gần đây, rating trên 4 sao, có tặng nước hoặc ưu đãi nước uống.**

---

## 2. Self-use evidence

Nhóm tự dùng app/workflow và ghi lại điểm gãy.

| Observation | Screenshot/link cần lưu | Path liên quan | Điều học được |
|---|---|---|---|
| ShopeeFood hiện cho user tìm theo **quán** hoặc **món ăn**, ví dụ gõ “cơm gà”. |  | As-is / Happy search cơ bản | Search hiện tại tốt cho nhu cầu đơn giản: tìm một món hoặc một quán. |
| Khi user có nhiều điều kiện như “5 người, cơm gà, 50k/người, gần đây, trên 4 sao, có tặng nước”, user phải tự kiểm tra từng kết quả. | Low-confidence / Manual comparison | App chưa có nơi để nhập yêu cầu tự nhiên nhiều điều kiện cùng lúc. |
| User phải mở từng quán để xem menu, giá từng phần, combo, số lượng phù hợp cho 5 người. |  Manual filtering | User phải tự tính tổng tiền và giá/người. |
| User phải tự kiểm tra rating, khoảng cách, phí ship, voucher, ưu đãi và đồ tặng kèm. | Failure / Risk | Thông tin cần quyết định nằm rải rác ở nhiều màn hình. |
| Nếu không có quán nào thỏa tất cả điều kiện, app không giúp user biết nên nới điều kiện nào trước, ví dụ tăng budget hay bỏ điều kiện tặng nước. | Failure path | Thiếu recovery path cho multi-constraint search. |

**Kết luận self-use:**  
ShopeeFood có search món/quán và các thông tin cần thiết như giá, rating, khoảng cách, promo, voucher. Tuy nhiên, khi user có nhiều điều kiện cùng lúc, app chưa giúp gom các điều kiện này thành một truy vấn tự nhiên và chưa tự shortlist các lựa chọn phù hợp nhất. User phải tự mở nhiều quán, tự kiểm tra từng tiêu chí và tự so sánh.

---

## 3. User / review / social evidence

Nguồn có thể là phỏng vấn nhanh, review app, comment, hoặc observation từ người ngoài nhóm.

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| “Khi đặt đồ ăn cho nhóm, mình thường phải hỏi mọi người ăn gì, rồi tự lọc quán theo giá, rating, khoảng cách và voucher. Mất thời gian nhất là so sánh nhiều quán.” | Kế hoạch phỏng vấn nhanh 1–2 người dùng ShopeeFood trước M1 Day 06 | Người thường đặt đồ ăn cho nhóm bạn / nhóm học | User không chỉ search món, mà cần tối ưu nhiều điều kiện cùng lúc. |
| “Nếu app gợi ý sẵn 2–3 quán phù hợp với budget và số người thì tiện hơn, miễn là mình vẫn được kiểm tra lại giỏ hàng.” | Kế hoạch phỏng vấn nhanh trước M1 Day 06 | Người dùng đặt đồ ăn online | User muốn AI hỗ trợ shortlist, nhưng vẫn muốn giữ quyền xác nhận đơn hàng. |
| “Khuyến mãi và phí ship thay đổi nên mình hay phải vào checkout mới biết tổng tiền thật.” | Kế hoạch phỏng vấn nhanh trước M1 Day 06 | Người dùng nhạy cảm với budget | Failure mode nguy hiểm là AI nói sai giá / sai ưu đãi / chưa tính phí ship. |

Nếu chưa kịp lấy nguồn ngoài nhóm trước khi nộp Day 05, ghi rõ:

```text
Đây là giả định dựa trên self-use evidence và observation từ workflow đặt đồ ăn. Nhóm sẽ kiểm bằng cách phỏng vấn nhanh 2 người dùng ShopeeFood trước checkpoint M1 Day 06.

Câu hỏi kiểm chứng:
1. Khi đặt đồ ăn cho nhóm, bạn thường phải kiểm tra những điều kiện nào?
2. Bạn có thấy mất thời gian khi phải mở từng quán để so giá, rating, khoảng cách, voucher không?
3. Nếu có AI gợi ý 3 lựa chọn phù hợp với budget/rating/khoảng cách, bạn có dùng không?
4. Bạn muốn AI tự đặt đơn hay chỉ gợi ý để bạn xác nhận?
```

---

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| Filter trong app giao đồ ăn | Cho lọc theo món, quán, khoảng cách, rating, khuyến mãi, nhưng thường là các filter rời rạc. | User cần một cách gộp nhiều điều kiện thành một truy vấn tự nhiên. | Có. Prototype chatbox / AI search panel. |
| Travel / hotel search | User nhập nhiều điều kiện như số người, budget, rating, vị trí; hệ thống shortlist option phù hợp. | Multi-constraint matching nên trả về shortlist + lý do đề xuất. | Có. Mock shortlist 3 quán. |
| Shopping assistant / recommender | AI hỏi lại khi thiếu thông tin hoặc khi không có kết quả thỏa hết điều kiện. | Khi không có perfect match, AI nên nới điều kiện có kiểm soát. | Có. Prototype failure path “nới điều kiện nào?”. |
| Checkout trong e-commerce | Giá cuối cần được kiểm lại ở bước checkout vì phí, voucher, availability có thể thay đổi. | AI không được khẳng định giá tuyệt đối; cần re-check trước đặt hàng. | Có. Mock warning “giá ước tính, kiểm tra ở checkout”. |

---

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
ShopeeFood hiện cho search theo quán hoặc món, nhưng task đặt đồ ăn cho nhóm có nhiều điều kiện cùng lúc: số người, món muốn ăn, budget/người, vị trí gần, rating, khuyến mãi, đồ tặng kèm và phí ship.

Insight:
User không chỉ cần “tìm cơm gà”. Họ cần giải một bài toán matching nhiều điều kiện để chọn được quán/món phù hợp cho cả nhóm. Search hiện tại khiến user phải tự mở nhiều quán, tự so sánh giá/rating/voucher và tự tính tổng tiền.

Opportunity:
AI có thể augment quá trình tìm kiếm bằng cách hiểu yêu cầu tự nhiên, tách thành constraint, lọc/xếp hạng quán/món và trả về shortlist 2–3 lựa chọn phù hợp kèm lý do, giá/người, tổng giá ước tính và điều kiện cần kiểm tra lại.
```

---

## 6. Evidence đổi SPEC như thế nào?

- [x] Đổi user chính.
- [x] Đổi pain statement.
- [x] Đổi build slice.
- [x] Đổi Auto/Aug decision.
- [x] Đổi 4 paths.
- [x] Đổi failure mode.
- [x] Đổi owner/test plan.

Ghi rõ 1-2 thay đổi quan trọng:

```text
Trước evidence, nhóm có thể nói chung là “thêm chatbot cho ShopeeFood”.

Sau evidence, nhóm đổi scope thành một build slice hẹp hơn:
“AI Group Meal Finder cho trường hợp đặt cơm gà cho 5 người với nhiều điều kiện”.

Lý do:
Giá trị chính không nằm ở việc có chatbox, mà nằm ở việc AI hiểu yêu cầu tự nhiên, chuyển thành constraint, shortlist lựa chọn phù hợp và xử lý trường hợp không có kết quả thỏa hết điều kiện.
```

