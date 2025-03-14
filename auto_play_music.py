import json
import webbrowser
import time
import yt_dlp
import os

# Đường dẫn file JSON (chuyển sang đường dẫn tương đối)
json_file = os.path.join(os.path.dirname(__file__), "music_list.json")

# Đọc dữ liệu từ file JSON
def load_playlist():
    if not os.path.exists(json_file):
        return []  # Trả về danh sách rỗng nếu file không tồn tại
    with open(json_file, "r", encoding="utf-8") as file:
        return json.load(file)

# Cập nhật danh sách nhạc sau khi xóa bài đã phát
def update_playlist(new_data):
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(new_data, file, indent=4, ensure_ascii=False)

# Lấy thời lượng video YouTube
def get_video_duration(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get('duration', 0)  # Thời lượng video tính bằng giây

# Chạy nhạc từ danh sách
def play_music():
    while True:
        playlist = load_playlist()

        if not playlist:
            print("🎶 Không còn bài hát nào, thoát chương trình!")
            break

        # Lấy bài hát đầu tiên trong danh sách
        song = playlist[0]
        link = song["link"]
        title = song.get("title", "Video không có tiêu đề")

        print(f"🎵 Đang mở: {title} ({link})")
        webbrowser.open(link)  # Mở link trong trình duyệt

        duration = get_video_duration(link) - 5  # Lấy thời lượng video
        print(f"⏳ Đợi {duration} giây để chuyển bài tiếp theo...")
        time.sleep(duration)  # Chờ đúng thời gian video phát xong

        # Xóa bài hát vừa phát khỏi danh sách và cập nhật JSON
        playlist.pop(0)
        update_playlist(playlist)

        print(f"✅ Đã xóa: {title} khỏi danh sách!\n")

# Chạy chương trình
play_music()
