# Định Dạng Dữ Liệu CSV

Tài liệu này mô tả định dạng của các file CSV được sử dụng trong dự án.

## charging_stations.csv

File này chứa danh sách các trạm sạc xe điện.

### Định dạng:
```
name,address,lat,lng,type
```

### Các cột:
- **name**: Tên trạm sạc (string)
- **address**: Địa chỉ của trạm sạc (string)
- **lat**: Vĩ độ (latitude) của trạm sạc (float)
- **lng**: Kinh độ (longitude) của trạm sạc (float)
- **type**: Loại trạm sạc (ví dụ: "VinFast DC 30kW", "VinFast AC 11kW")

### Ví dụ:
```csv
name,address,lat,lng,type
Vincom Plaza Hòa Bình,Đường Cù Chính Lan P. Đồng Tiến TP. Hòa Bình,20.825869749770696,105.35107579543782,VinFast DC 30kW
Serena Resort Kim Bôi,Xóm Khai Đồi Xã Sào Báy H. Kim Bôi,20.598787151034674,105.58918731670616,VinFast AC 11kW
```

### Lưu ý:
- File phải có header ở dòng đầu tiên
- Tọa độ phải là số thực (float) hợp lệ
- Không được để trống các cột lat, lng

## BOT.csv

File này chứa danh sách các trạm thu phí BOT.

### Định dạng:
```
Tên,Địa chỉ / Lý trình / Hành trình,"Vĩ độ, Kinh độ",Mức thu (Xe điện/Nhóm 1)
```

### Các cột:
- **Tên**: Tên trạm BOT (string)
- **Địa chỉ / Lý trình / Hành trình**: Thông tin địa chỉ hoặc lý trình của trạm BOT (string)
- **Vĩ độ, Kinh độ**: Tọa độ của trạm BOT, định dạng "lat,lng" (string chứa 2 số float phân tách bởi dấu phẩy)
- **Mức thu (Xe điện/Nhóm 1)**: Mức phí thu của trạm BOT cho xe điện (string, ví dụ: "15.000 VNĐ")

### Ví dụ:
```csv
Tên,Địa chỉ / Lý trình / Hành trình,"Vĩ độ, Kinh độ",Mức thu (Xe điện/Nhóm 1)
Trạm Pháp Vân - Cầu Giẽ,"Km188 - Km212, Thanh Trì, Hà Nội","20.9431,105.8494",15.000 VNĐ
Trạm Nam Cầu Giẽ,"Km213, Duy Tiên, Hà Nam","20.6276,105.9325",35.000 VNĐ
```

### Lưu ý:
- File phải có header ở dòng đầu tiên
- Cột "Vĩ độ, Kinh độ" phải chứa 2 số float phân tách bởi dấu phẩy
- Cột "Mức thu" có thể chứa văn bản mô tả phí (ví dụ: "15.000 VNĐ")

## Cách thêm dữ liệu mới

### Thêm trạm sạc mới:
1. Mở file `charging_stations.csv` bằng text editor hoặc Excel
2. Thêm dòng mới với format: `tên,địa chỉ,vĩ độ,kinh độ,loại trạm`
3. Lưu file và chạy lại chương trình

### Thêm trạm BOT mới:
1. Mở file `BOT.csv` bằng text editor hoặc Excel
2. Thêm dòng mới với format: `tên,"địa chỉ","vĩ độ,kinh độ",mức thu`
3. Chú ý: Cột tọa độ phải có dấu ngoặc kép bao quanh
4. Lưu file và chạy lại chương trình

## Công cụ tìm tọa độ

Để tìm tọa độ (lat, lng) của một địa điểm:
- Sử dụng Google Maps: Click phải vào địa điểm → chọn tọa độ để copy
- Sử dụng OpenStreetMap: Click vào địa điểm → xem thông tin tọa độ bên phải
- Format: Vĩ độ (lat) trước, Kinh độ (lng) sau, phân tách bởi dấu phẩy

## Giới hạn

- Thuật toán tìm đường sử dụng khoảng cách Haversine (đường chim bay)
- Khoảng cách thực tế trên đường sẽ được ước tính bằng cách nhân với hệ số ROAD_FACTOR (1.25)
- Dữ liệu trạm sạc và BOT cần được cập nhật thường xuyên để đảm bảo tính chính xác
