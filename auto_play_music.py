import json
import webbrowser
import time
import yt_dlp
import os
import redis

# Kết nối Upstash Redis
REDIS_URL = "redis://:AWdXAAIjcDE2YTU2MDYyZGUyOWY0NjQ2YjE4MWQ1OTRiOWQ0ZDYwZnAxMA@related-wildcat-26455.upstash.io:6379"
r = redis.from_url(REDIS_URL, decode_responses=True)

# Đọc danh sách nhạc từ Redis
def load_playlist():
    playlist_json = r.get("music_playlist")
    return json.loads(playlist_json) if playlist_json else []

# Cập nhật danh sách nhạc
def update_playlist(new_data):
    r.set("music_playlist", json.dumps(new_data, ensure_ascii=False))

# Lấy thời lượng video YouTube
def get_video_duration(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get('duration', 0)

# Chạy nhạc từ danh sách
def play_music():
    while True:
        playlist = load_playlist()

        if not playlist:
            print("🎶 Không còn bài hát nào, thoát chương trình!")
            break

        song = playlist[0]
        link = song["link"]
        title = song.get("title", "Video không có tiêu đề")

        print(f"🎵 Đang mở: {title} ({link})")
        webbrowser.open(link)

        duration = get_video_duration(link) - 5
        print(f"⏳ Đợi {duration} giây để chuyển bài tiếp theo...")
        time.sleep(duration)

        # Xóa bài hát đã phát
        playlist.pop(0)
        update_playlist(playlist)

        print(f"✅ Đã xóa: {title} khỏi danh sách!\n")

# Chạy chương trình
play_music()
