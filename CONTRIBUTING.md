# Hướng dẫn Đóng góp

Cảm ơn bạn đã quan tâm đến việc đóng góp cho dự án Lập kế hoạch lộ trình xe ô tô điện!

## Quy trình đóng góp

1. **Fork repository**
   - Tạo một bản fork của repository này trên GitHub

2. **Clone repository về máy local**
   ```bash
   git clone https://github.com/your-username/EVNhom12.git
   cd EVNhom12
   ```

3. **Cài đặt dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Tạo branch mới cho tính năng của bạn**
   ```bash
   git checkout -b feature/ten-tinh-nang
   ```

5. **Thực hiện thay đổi**
   - Viết code rõ ràng, có comment
   - Tuân thủ coding style của dự án
   - Thêm tests cho các tính năng mới

6. **Chạy tests**
   ```bash
   python test_file.py -v
   ```

7. **Commit changes**
   ```bash
   git add .
   git commit -m "Mô tả ngắn gọn về thay đổi"
   ```

8. **Push lên GitHub**
   ```bash
   git push origin feature/ten-tinh-nang
   ```

9. **Tạo Pull Request**
   - Mở Pull Request từ branch của bạn vào branch main của repository gốc
   - Mô tả chi tiết các thay đổi và lý do

## Coding Standards

### Python Style Guide
- Tuân thủ PEP 8 (Python style guide)
- Sử dụng 4 spaces cho indentation
- Tên biến, hàm: snake_case
- Tên class: PascalCase
- Tối đa 100 ký tự mỗi dòng

### Comments và Documentation
- Viết docstring cho tất cả các hàm và class
- Comment giải thích logic phức tạp
- Sử dụng tiếng Việt hoặc tiếng Anh nhất quán

### Tests
- Viết unit tests cho mọi tính năng mới
- Đảm bảo tất cả tests pass trước khi submit PR
- Coverage mục tiêu: > 70%

## Các loại đóng góp được chào đón

### Bug Fixes
- Sửa lỗi trong code
- Cải thiện xử lý lỗi
- Fix typos trong documentation

### Tính năng mới
- Thêm thuật toán tìm đường mới
- Tích hợp API bản đồ thực tế
- Cải thiện UI/UX
- Thêm hỗ trợ ngôn ngữ

### Documentation
- Cải thiện README
- Thêm ví dụ sử dụng
- Viết tutorials
- Dịch sang ngôn ngữ khác

### Testing
- Thêm test cases
- Cải thiện test coverage
- Performance testing

### Refactoring
- Tối ưu code
- Loại bỏ code trùng lặp
- Cải thiện architecture

## Quy tắc khi đóng góp

1. **Tôn trọng**: Tôn trọng tất cả contributors và maintainers
2. **Code chất lượng**: Đảm bảo code của bạn hoạt động đúng và có tests
3. **Documentation**: Cập nhật documentation nếu cần
4. **No breaking changes**: Tránh thay đổi làm hỏng code hiện tại
5. **Incremental changes**: Chia nhỏ thay đổi thành các PR nhỏ, dễ review

## Báo cáo lỗi (Bug Reports)

Khi báo cáo lỗi, vui lòng bao gồm:

1. **Mô tả lỗi**: Mô tả ngắn gọn về lỗi
2. **Các bước tái hiện**:
   - Bước 1: ...
   - Bước 2: ...
   - Bước 3: ...
3. **Kết quả mong đợi**: Điều gì nên xảy ra
4. **Kết quả thực tế**: Điều gì đã xảy ra
5. **Môi trường**:
   - OS: (ví dụ: Windows 10, Ubuntu 20.04)
   - Python version: (ví dụ: 3.9.7)
   - Package versions: (từ `pip list`)
6. **Screenshots**: Nếu có
7. **Logs**: Error messages hoặc stack traces

## Đề xuất tính năng (Feature Requests)

Khi đề xuất tính năng mới:

1. **Tóm tắt**: Mô tả ngắn gọn tính năng
2. **Lý do**: Tại sao tính năng này hữu ích?
3. **Đề xuất giải pháp**: Cách implement tính năng
4. **Alternatives**: Các giải pháp khác đã xem xét
5. **Additional context**: Screenshots, mockups, links liên quan

## Liên hệ

Nếu có câu hỏi về việc đóng góp, vui lòng:
- Mở issue trên GitHub
- Liên hệ với maintainers qua GitHub

## License

Bằng cách đóng góp vào dự án này, bạn đồng ý rằng đóng góp của bạn sẽ được license dưới cùng license với dự án.

---

Cảm ơn bạn đã đọc hướng dẫn này! 🚗⚡
