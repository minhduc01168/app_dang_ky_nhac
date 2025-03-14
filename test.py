import redis

REDIS_URL = "rediss://default:AWdXAAIjcDE2YTU2MDYyZGUyOWY0NjQ2YjE4MWQ1OTRiOWQ0ZDYwZnAxMA@related-wildcat-26455.upstash.io:6379"
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.set("test", "OK")
    print(r.get("test"))  # Nếu in ra "OK" thì kết nối Redis thành công
except Exception as e:
    print(f"Lỗi kết nối Redis: {e}")
