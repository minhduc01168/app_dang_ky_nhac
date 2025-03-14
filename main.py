from flask import Flask, render_template, request, redirect, url_for, session
import re
import requests
import json
import redis

app = Flask(__name__)
app.secret_key = "nhatteo2403"

admin_password = "@nhat24032002"

# Kết nối Upstash Redis
REDIS_URL = "rediss://default:AWdXAAIjcDE2YTU2MDYyZGUyOWY0NjQ2YjE4MWQ1OTRiOWQ0ZDYwZnAxMA@related-wildcat-26455.upstash.io:6379"
r = redis.from_url(REDIS_URL, decode_responses=True)

# Hàm load danh sách nhạc từ Redis
def load_songs():
    playlist_json = r.get("music_playlist")
    return json.loads(playlist_json) if playlist_json else []

# Hàm lưu danh sách nhạc vào Redis
def save_songs(data):
    r.set("music_playlist", json.dumps(data, ensure_ascii=False))

# Kiểm tra link YouTube
def is_youtube_url(url):
    return "youtube.com/watch" in url or "youtu.be/" in url

# Lấy thông tin video từ YouTube
def get_youtube_info(url):
    if not is_youtube_url(url):
        return None, None

    video_id = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)", url)
    if video_id:
        video_id = video_id.group(1)

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

# Trang chính
@app.route('/', methods=['GET', 'POST'])
def index():
    danh_sach_nhac = load_songs()
    error_message = None

    if request.method == 'POST':
        link_nhac = request.form['link_nhac']
        if link_nhac:
            if not is_youtube_url(link_nhac):
                error_message = "Vui lòng chỉ nhập link YouTube"
            else:
                title, thumbnail = get_youtube_info(link_nhac)
                if title and thumbnail:
                    if not any(song["link"] == link_nhac for song in danh_sach_nhac):
                        danh_sach_nhac.append({"link": link_nhac, "title": title, "thumbnail": thumbnail})
                        save_songs(danh_sach_nhac)
                else:
                    error_message = "Không thể xử lý link YouTube này"

    return render_template('index.html', danh_sach_nhac=danh_sach_nhac, is_admin=session.get('is_admin', False), error_message=error_message)

# Xóa nhạc
@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if session.get('is_admin'):
        danh_sach_nhac = load_songs()
        if 0 <= index < len(danh_sach_nhac):
            del danh_sach_nhac[index]
            save_songs(danh_sach_nhac)
    return redirect(url_for('index'))

# Đăng nhập admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == admin_password:
            session['is_admin'] = True
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
    app.run(debug=True)
