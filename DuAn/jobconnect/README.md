# JobConnect — HTML / CSS / JavaScript

## Chạy
Mở thư mục bằng VS Code, chạy index.html với Live Server. Hoặc chạy:

    python -m http.server 5500

Truy cập http://localhost:5500. Không cần npm hay thư viện ngoài.

## File
- index.html: khung giao diện, tìm kiếm, các trang ứng viên, modal.
- style.css: giao diện responsive Desktop / Tablet / Mobile.
- app.js: dữ liệu mẫu và logic tương tác.

## Phạm vi Task 8–15
8. HTML/CSS/JS thuần theo yêu cầu; không phải React/Next/Tailwind. Có responsive.
9. Mô phỏng vai trò Candidate/Recruiter; không có lựa chọn đăng ký Admin. Không có xác thực hoặc RBAC backend thật. Email nhập vào chỉ chọn hồ sơ demo, không xác minh danh tính; mọi dữ liệu local đều có thể sửa bằng DevTools.
10. Danh sách, tìm kiếm theo tên/vị trí/công ty/kỹ năng, địa điểm, hình thức, lương tối thiểu, sắp xếp. Số ms là thời gian lọc dữ liệu trong trình duyệt, KHÔNG phải đo API và không chứng minh SLA 500 ms.
11. Lưu/bỏ lưu, không thêm trùng cùng ID tin trong mỗi tài khoản demo.
12. CV được lưu dưới dạng Blob trong IndexedDB theo email demo. Kiểm tra đuôi .pdf, MIME application/pdf, dung lượng <= 5*1024*1024 byte, chữ ký %PDF-. Kiểm tra này không thay thế xác thực/parsing và quét file ở máy chủ. Xóa dữ liệu trình duyệt sẽ mất CV.
13. Rút đơn chỉ khi submitted, reviewing hoặc interviewed; accepted/rejected/withdrawn là trạng thái kết thúc trong demo. Rút đơn không cho phép nộp lại. Nếu đặc tả backend định nghĩa kết thúc khác, cần thống nhất lại danh sách trạng thái được rút.
14. Hiển thị và lọc đủ submitted/reviewing/interviewed/accepted/rejected/withdrawn. Đơn thực tế tạo trong demo chỉ chuyển submitted → withdrawn; các trạng thái khác phải do backend/nhà tuyển dụng cập nhật. Không có nút ứng viên tự đổi trạng thái.
15. Form chọn CV, thư giới thiệu, kiểm tra tin đang mở và chống ứng tuyển trùng. Giữ lịch sử cả đơn withdrawn để chặn nộp lại.

## Hướng dẫn dùng thử
1. Đăng nhập bằng tên, email mẫu và vai trò Ứng viên (không dùng dữ liệu nhạy cảm).
2. Hồ sơ & CV → chọn một PDF hợp lệ.
3. Tìm việc → xem chi tiết → ứng tuyển → chọn CV → gửi.
4. Đơn ứng tuyển → xem trạng thái hoặc rút đơn.
5. Nhấn trái tim để lưu và bỏ lưu công việc.
6. Đăng xuất và chọn email khác để dùng một hồ sơ demo khác.

## Khi nối backend (bắt buộc để dùng thật)
- Máy chủ xác minh phiên/token và lấy user_id/role từ danh tính đã xác thực. Không tin role/user_id gửi từ trình duyệt.
- Middleware: API ứng viên chỉ nhận Candidate; API tuyển dụng chỉ nhận Recruiter, API quản trị chỉ Admin. Trả 401 khi chưa xác thực, 403 khi sai vai trò; kiểm tra quyền sở hữu tài nguyên.
- Đăng ký công khai chỉ cho Candidate/Recruiter; từ chối giá trị Admin. Không gán hàng loạt role từ request. Admin phải được cấp qua luồng quản trị được bảo vệ.
- UNIQUE(candidate_id,job_id) cho saved_jobs và applications; xử lý xung đột ở DB, không chỉ kiểm tra trước khi INSERT.
- Nộp đơn: giao dịch kiểm tra tin còn mở, CV thuộc ứng viên; tạo submitted. Rút đơn bằng UPDATE có điều kiện trạng thái và chủ sở hữu trong cùng thao tác nguyên tử.
- CV: giới hạn request/file 5 MB tại server, kiểm tra MIME/chữ ký và parse PDF, quét nội dung, lưu riêng tư với tên ngẫu nhiên; chỉ chủ sở hữu và nhà tuyển dụng được phép xem theo chính sách. Lưu bản CV gắn với đơn nếu muốn lịch sử còn tải được khi CV gốc bị xóa.
- Lọc/tìm kiếm trên server, phân trang, index phù hợp và đo p95 API dưới tải thực để đánh giá mục tiêu <500 ms.
- Dùng HTTPS, validation đầu vào, truy vấn tham số hóa; bảo vệ CSRF khi dùng cookie, giới hạn tần suất API đăng nhập/upload.

## API gợi ý
GET /api/jobs?q=&location=&type=&salaryMin=&sort=&page=
GET /api/jobs/:id
GET /api/me/saved-jobs
PUT /api/me/saved-jobs/:jobId
DELETE /api/me/saved-jobs/:jobId
GET /api/me/cvs
POST /api/me/cvs (multipart/form-data)
DELETE /api/me/cvs/:cvId
GET /api/me/applications?status=
POST /api/jobs/:jobId/applications { cvId, coverLetter }
PATCH /api/me/applications/:id/withdraw

Thay nguồn dữ liệu localStorage/IndexedDB bằng fetch tới các API đã xác thực. Không triển khai bản demo này làm hệ thống thật khi chưa có backend.

## Kiểm tra đã thực hiện
- node --check app.js: đạt.
- Kiểm tra đường dẫn file liên kết và cấu trúc đóng gói.
- Chưa chạy kiểm thử giao diện tự động hoặc đo API; gói không kèm backend.
