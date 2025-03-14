from flask import Flask, render_template, request, redirect, url_for, session
import re
import requests
import json, os

app = Flask(__name__)
app.secret_key = "nhatteo2403"  # Khóa bí mật cho session

admin_password = "@nhat24032002"  # Mật khẩu admin

# Đường dẫn file JSON
# Đường dẫn file JSON (chuyển sang đường dẫn tương đối)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "music_list.json")

# Hàm load danh sách nhạc từ JSON
def load_songs():
    try:
        print(f"Đang cố gắng đọc file từ: {FILE_PATH}")
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Đã đọc dữ liệu: {data}")
            if isinstance(data, list):
                return data
    except FileNotFoundError:
        print("Không tìm thấy file music_list.json")
    except json.JSONDecodeError as e:
        print(f"Lỗi định dạng JSON: {e}")
    return []

# Hàm lưu danh sách nhạc vào JSON
def save_songs(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

danh_sach_nhac = load_songs()  # Tải dữ liệu từ file JSON

# Hàm lấy thông tin video từ YouTube
# def get_youtube_info(url):
#     video_id = re.search(r"v=([\w-]+)", url)
#     if video_id:
#         video_id = video_id.group(1)
#         api_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
#         try:
#             response = requests.get(api_url)
#             if response.status_code == 200:
#                 data = response.json()
#                 title = data.get("title", "Không xác định")
#             else:
#                 title = "Không xác định"
#         except:
#             title = "Không xác định"
#
#         thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
#         return title, thumbnail_url
#     return "Không xác định", ""
# Hàm kiểm tra link YouTube
def is_youtube_url(url):
    # Kiểm tra các định dạng URL YouTube hợp lệ
    if "youtube.com/watch" in url or "youtu.be/" in url:
        return True
    return False


# Hàm lấy thông tin video từ YouTube
def get_youtube_info(url):
    # Kiểm tra xem có phải link YouTube không
    if not is_youtube_url(url):
        return None, None  # Trả về None nếu không phải link YouTube

    # Xử lý URL dạng youtu.be
    if "youtu.be" in url:
        video_id = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
        if video_id:
            video_id = video_id.group(1)
            # Loại bỏ tham số từ URL (nếu có)
            if "?" in video_id:
                video_id = video_id.split("?")[0]
    # Xử lý URL dạng youtube.com
    else:
        video_id = re.search(r"v=([a-zA-Z0-9_-]+)", url)
        if video_id:
            video_id = video_id.group(1)

    if video_id:
        api_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                title = data.get("title", "Không xác định")
            else:
                title = "Không xác định"
        except:
            title = "Không xác định"

        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        return title, thumbnail_url
    return "Không xác định", ""


# Trang chính (hiển thị danh sách nhạc)
@app.route('/', methods=['GET', 'POST'])
def index():
    danh_sach_nhac = load_songs()  # Luôn lấy danh sách từ file JSON
    error_message = None  # Biến chứa thông báo lỗi

    if request.method == 'POST':
        link_nhac = request.form['link_nhac']
        if link_nhac:
            if not is_youtube_url(link_nhac):
                error_message = "Vui lòng chỉ nhập link YouTube (youtube.com hoặc youtu.be)"
            else:
                title, thumbnail = get_youtube_info(link_nhac)
                if title and thumbnail:
                    if not any(song["link"] == link_nhac for song in danh_sach_nhac):  # Tránh trùng lặp
                        danh_sach_nhac.append({"link": link_nhac, "title": title, "thumbnail": thumbnail})
                        save_songs(danh_sach_nhac)  # Lưu danh sách vào JSON
                else:
                    error_message = "Không thể xử lý link YouTube này, vui lòng kiểm tra lại"
        return render_template('index.html', danh_sach_nhac=danh_sach_nhac, is_admin=session.get('is_admin', False),
                               error_message=error_message)

    return render_template('index.html', danh_sach_nhac=danh_sach_nhac, is_admin=session.get('is_admin', False),
                           error_message=None)

# Xóa nhạc (chỉ admin mới xóa được)
@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if session.get('is_admin'):  # Kiểm tra quyền admin trước khi xóa
        danh_sach_nhac = load_songs()  # Lấy danh sách từ JSON
        if 0 <= index < len(danh_sach_nhac):
            del danh_sach_nhac[index]
            save_songs(danh_sach_nhac)  # Lưu lại danh sách sau khi xóa
    return redirect(url_for('index'))

# Đăng nhập admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == admin_password:
            session['is_admin'] = True
            session['username'] = 'admin'  # Lưu session cho admin
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Sai mật khẩu!")
    return render_template('login.html', error=None)

# Đăng xuất admin
@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
