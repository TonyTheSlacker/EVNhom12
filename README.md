# Dự án Lập Kế Hoạch Lộ Trình Xe Ô Tô Điện

Ứng dụng Python mô phỏng, tối ưu lộ trình di chuyển cho xe ô tô điện, hỗ trợ tìm đường qua các trạm sạc, tránh trạm BOT, xuất PDF, và hiển thị bản đồ tương tác.

## Tính năng chính

- Nhập địa chỉ hoặc tọa độ cho điểm bắt đầu/kết thúc, tự động đồng bộ.
- Tìm lộ trình tối ưu bằng thuật toán A* hoặc UCS, dựa trên dữ liệu trạm sạc thực tế.
- Tính toán quãng đường, thời gian lái xe, thời gian sạc, chi phí sạc, phí BOT.
- Tránh trạm thu phí BOT nếu người dùng chọn.
- Hiển thị chi tiết lộ trình, các trạm sạc, trạng thái pin, hoạt động xe.
- Xuất kết quả lộ trình ra file PDF.
- Hiển thị bản đồ lộ trình bằng Folium (HTML).
- Giao diện Tkinter hỗ trợ Dark Mode, trực quan, dễ sử dụng.

## Lưu ý (Note)

- Đây là project sinh viên, chưa tối ưu cho thực tế, chỉ mang tính mô phỏng và học thuật.
- Đường đi tính toán là đường chim bay (Haversine), chưa phải đường bộ thực tế, chưa tích hợp bản đồ giao thông thật.
- Dữ liệu trạm sạc/BOT là mẫu, không đầy đủ hoặc cập nhật liên tục.
- Chưa tối ưu về tốc độ thuật toán, hiệu năng, và giao diện người dùng chuyên nghiệp.
- Một số tính năng nâng cao (tìm đường tránh kẹt xe, tối ưu chi phí thực tế, bản đồ tương tác nâng cao,...) chưa có.
- Các thuật toán chỉ dựa trên dữ liệu tĩnh, không có API bản đồ hoặc dữ liệu động.
- Chỉ hỗ trợ các mẫu xe điện có sẵn trong danh sách, chưa cho phép thêm xe mới từ giao diện.

## Cấu trúc dự án

- `main.py`: Giao diện người dùng, xử lý nhập liệu, hiển thị kết quả.
- `file.py`: Thuật toán tìm đường, logic tối ưu lộ trình.
- `models.py`: Định nghĩa lớp xe điện, danh sách xe mẫu.
- `pdf_utils.py`: Xuất lộ trình ra file PDF, xử lý dữ liệu BOT.
- `utils.py`: Hàm tiện ích, tính toán phụ trợ.
- `export_pdf.py`: (Tùy chọn) hỗ trợ xuất PDF.
- `test_file.py`: Kiểm thử đơn vị cho các hàm chính.
- `requirements.txt`: Thư viện cần thiết.
- `charging_stations.csv`: Dữ liệu trạm sạc (tên, địa chỉ, tọa độ).
- `BOT.csv`: Dữ liệu trạm thu phí BOT (tên, địa chỉ, tọa độ, phí).
- `routes/`: Thư mục chứa các file PDF lộ trình đã xuất.
- `route_map_temp.html`: File bản đồ lộ trình tạm thời.

## Hướng dẫn sử dụng

1. Cài đặt các thư viện cần thiết:
   ```
   pip install pandas numpy matplotlib geopy folium fpdf
   ```
2. Chuẩn bị dữ liệu:
   - Đảm bảo có file `charging_stations.csv` và `BOT.csv` trong thư mục dự án.
3. Chạy chương trình:
   ```
   python main.py
   ```
4. Sử dụng giao diện để nhập thông tin, chọn xe, thuật toán, và xuất kết quả.

## Kiểm thử

- Chạy kiểm thử đơn vị:
  ```
  python test_file.py
  ```

## Tác giả & Đóng góp

- **Châu Hoàn Thiện – 49.01.103.077**
  - Xây dựng thuật toán UCS, nhập tọa độ/địa chỉ, xuất PDF lộ trình, xử lý dữ liệu BOT.csv và charging_stations.csv, các chức năng phụ trợ, darkmode.
- **Châu Vĩ Khôn – 45.01.104.116**
  - Thiết kế giao diện Tkinter, tạo UI, sửa lỗi thuật toán UCS, bổ sung xuất bản đồ HTML (Folium), tối ưu trải nghiệm người dùng, fix các lỗi còn lại.
- **Diệp Quang Huy – 49.01.104.050**
  - Xây dựng thuật toán A* ban đầu, cung cấp nền tảng cho phần tìm đường tối ưu.
- **Liêu Lâm Tài – 48.01.104.116**
  - Viết kiểm thử đơn vị (`test_file.py`), kiểm tra dữ liệu đầu vào, hỗ trợ tạo hàm tiện ích.
- **Lê Việt Hoàng Thảo – 47.01.104.196**
  - Viết hàm xuất danh sách trạm sạc ra PDF (`export_pdf.py`), hỗ trợ kiểm tra dữ liệu, đóng góp ý tưởng giao diện.
