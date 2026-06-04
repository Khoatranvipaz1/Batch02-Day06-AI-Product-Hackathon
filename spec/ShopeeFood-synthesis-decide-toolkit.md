# ToolKit — B6 ShopeeFood Evidence → Build Slice

## 1. Gom evidence thành cụm

- “Không biết chọn món nào phù hợp trong tầm 60k.”
- “Giá món, phí ship, voucher và thời gian giao làm mình phải so sánh thủ công.”
- “Nếu yêu cầu mơ hồ, app không gợi ý rõ, phải hỏi lại hoặc tự suy.”

## 2. Viết insight

```text
User sinh viên/người đi làm không chỉ cần đặt đồ ăn.
Họ thật ra cần trợ giúp quyết định món phù hợp nhanh chóng,
vì evidence cho thấy họ bị chậm do quá nhiều lựa chọn và điều kiện khác nhau (ngân sách, không cay, giao nhanh, voucher, phí ship).
```

## 3. Viết opportunity

```text
Cơ hội là dùng AI để augment hành động chọn món hẹp,
giúp user nhận được 3 gợi ý phù hợp ngay lập tức,
trong khi vẫn kiểm soát failure/risk bằng cách hỏi lại khi yêu cầu mơ hồ và cảnh báo nếu thông tin món chưa rõ.
```

## 4. Chọn build slice

| Câu hỏi | Đạt khi |
|---|---|
| User cụ thể chưa? | Sinh viên/người đi làm cần bữa trưa dưới 60k, không cay, giao nhanh. |
| Task đủ hẹp chưa? | Tìm 3 món/quán phù hợp nhất cho bữa trưa; không build toàn bộ đặt món. |
| AI decision rõ chưa? | AI chọn và giải thích 3 lựa chọn phù hợp, không tự đặt đơn. |
| Failure path rõ chưa? | Có path AI gợi ý món không đúng ràng buộc hoặc user mơ hồ. |
| Có evidence không? | Có self-use, interview và observation. |

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

- Evidence rõ và task đủ hẹp: giữ scope.
- AI cần chỉ gợi ý, không cần tự động đặt: chọn augmentation.
- Nếu user mơ hồ, phải hỏi lại thay vì đoán bừa.
- Những phần không build Day 06: tích hợp thật với ShopeeFood, đặt đơn tự động, danh sách quán toàn bộ thành phố.

## 6. Câu chốt cuối

```text
Dựa trên evidence self-use và phỏng vấn B6,
nhóm sẽ build prototype slice cho user sinh viên/người đi làm,
để giải quyết pain chọn món trưa dưới 60k trong một biển lựa chọn,
bằng cách AI augment việc chọn 3 món phù hợp nhất,
và sẽ test failure path khi user mơ hồ hoặc có ràng buộc ăn kiêng không rõ.
```

## 7. Backlog

Những thứ **không build trong Day 06**:
- Tích hợp đặt đơn thật vào ShopeeFood.
- Hệ thống tính toán voucher/phí ship chính xác 100% với dữ liệu thực.
- Tìm kiếm và so sánh toàn bộ menu tất cả quán quanh khu vực.
