# ShopeeFood — Evidence + Thin SPEC

## 1. Track, product/app và user

**Track:** Food delivery / ordering
**Product/app thật:** ShopeeFood
**User cụ thể:** Sinh viên/người đi làm cần đặt bữa trưa nhanh, dưới 60.000đ, không cay và giao trong 30 phút.
**Nhóm có phải user thật không? Nếu không, khác ở đâu?**
Nhóm đã tự dùng ShopeeFood để lấy evidence và phỏng vấn ít nhất 3 người dùng thật (sinh viên/người đi làm).

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Self-use: tìm bữa trưa dưới 60k, không cay, giao nhanh | Nhóm tự dùng ShopeeFood, chụp màn hình quá trình | Người dùng phải lướt nhiều, so sánh giá, phí ship, voucher, rating và time giao | Build slice cần tập trung vào hỗ trợ quyết định món nhanh thay vì tìm toàn bộ app |
| Interview 3-5 người dùng | Phỏng vấn nhanh bạn bè/sinh viên/người đi làm | “Mình mở ShopeeFood nhưng nhiều lựa chọn quá, cuối cùng lướt 10 phút vẫn chưa biết ăn gì.” | Pain statement phải nêu rõ quyết định bị chậm do quá nhiều lựa chọn và điều kiện khác nhau |
| Observation task | Quan sát người dùng tìm “bữa trưa dưới 60k, không cay, giao nhanh” | Họ phải cân nhắc voucher/ship/giá, vẫn chưa tự tin với lựa chọn cuối cùng | AI cần gợi ý 3 lựa chọn phù hợp, user không cần tự so sánh toàn bộ dữ liệu |

## 3. Pain statement

```text
User là sinh viên/người đi làm đang tìm bữa trưa trên ShopeeFood,
vì có quá nhiều lựa chọn, voucher, phí ship và thời gian giao khác nhau,
dẫn tới họ phải lướt quá lâu, so sánh thủ công và vẫn chưa chắc chọn món nào.
Bằng chứng chính là: “Mình mở ShopeeFood nhưng nhiều lựa chọn quá, cuối cùng lướt 10 phút vẫn chưa biết ăn gì.”
```

## 4. Opportunity statement

Bằng chứng cho thấy vấn đề không chỉ là “muốn đặt đồ ăn”, mà là người dùng cần ra quyết định nhanh trong một biển lựa chọn.

**Opportunity:** “Làm thế nào để giúp người dùng ShopeeFood chọn được món phù hợp trong dưới 1 phút thay vì phải tự lướt, so sánh và cân nhắc quá nhiều lựa chọn?”

## 5. Build slice

```text
Cho sinh viên muốn đặt bữa trưa dưới 60k, không cay, giao nhanh,
prototype sẽ dùng AI để chọn ra 3 món/quán phù hợp nhất dựa trên ngân sách, khẩu vị, thời gian giao và voucher,
tạo ra gợi ý rõ ràng với lý do chọn,
và xử lý failure mode bằng cách hỏi lại hoặc cảnh báo khi thông tin chưa đủ.
```

## 6. Auto/Aug decision

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:**
AI cần hỗ trợ quyết định, nên chỉ gợi ý món phù hợp. Người dùng vẫn giữ quyền chọn cuối cùng vì họ cần xem voucher, khẩu vị và ràng buộc cá nhân.

**Human role:**
User là decider cuối cùng; AI hỗ trợ bằng gợi ý, giải thích và cảnh báo.

## 7. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | User nhập yêu cầu rõ: “Tôi muốn ăn trưa dưới 60k, không cay, giao nhanh.” AI đề xuất 3 lựa chọn phù hợp và giải thích lý do. |
| Low-confidence | User nhập mơ hồ: “Ăn gì cũng được.” AI hỏi lại: “Bạn muốn ăn no, ăn nhẹ, healthy hay rẻ nhất?” để làm rõ yêu cầu. |
| Failure | AI gợi ý món cay dù user nói không ăn cay, hoặc món vượt ngân sách. |
| Correction | User chọn “Không ăn cay” hoặc “Quá ngân sách”, AI cập nhật lại danh sách phù hợp hơn. |

## 8. Failure mode nguy hiểm nhất

```text
Nếu user cho biết không ăn cay / ăn chay / dị ứng / ngân sách chặt chẽ,
AI có thể gợi ý món không phù hợp với ràng buộc quan trọng,
hậu quả là user đặt sai món hoặc không tin tưởng giải pháp.
Prototype sẽ xử lý bằng cách ưu tiên các điều kiện bắt buộc, hỏi lại khi thông tin chưa rõ, và cảnh báo nếu nguyên liệu chưa đủ rõ.
Owner kiểm thử path này là Bạn D.
```

## 9. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| Bạn A | Research / evidence | Screenshot self-use, phỏng vấn 3-5 người dùng, observation notes |
| Bạn B | SPEC | Pain statement, opportunity, build slice, four paths, failure mode |
| Bạn C | Prototype | Mockup UI/flow nhập nhu cầu + gợi ý + correction screen |
| Bạn D | Test / failure path | Test data: quán, giá, phí ship, voucher, rating, thời gian giao; kiểm thử happy/low-confidence/failure/correction |
| Bạn E | Demo script / repo | README, kịch bản demo, slide summary |

## 10. Pain point ngắn gọn

**Pain point:**
Người dùng ShopeeFood mất thời gian chọn món vì có quá nhiều quán, món, voucher và phí ship khác nhau. Họ phải tự so sánh thủ công để tìm món phù hợp với ngân sách, khẩu vị và thời gian giao.
