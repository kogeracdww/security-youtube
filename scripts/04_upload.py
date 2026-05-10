#!/usr/bin/env python3
"""04_upload.py - YouTube Data API v3 アップロード（セキュリティ版）"""
import json, os, sys, urllib.request, urllib.parse

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

def get_access_token() -> str:
    data = urllib.parse.urlencode({
        "client_id":     os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
        "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
        "grant_type":    "refresh_token"
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data,
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]

def build_metadata(no: str, hook: str, script: str, category: str) -> dict:
    hashtags = "#cybersecurity #shorts #digitalsecurity #privacy #scam #infosec #datasecurity #onlinesafety"

    # カテゴリ別絵文字
    emoji_map = {
        "スマホ・2026年":  "📱",
        "AI・2026年":      "🤖",
        "社会・2026年":    "🌐",
        "写真・位置情報":  "📍",
        "QRコード":        "📷",
        "デジタル全般":    "🔒",
        "政府・大学レポ":  "📋",
    }
    emoji = emoji_map.get(category, "🔐")

    description = (
        f"{emoji} Digital Security\n\n"
        f"⚠️ {hook}\n\n"
        f"{script}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ Stay safe in the digital world.\n"
        "Knowledge is your best protection.\n\n"
        "📲 Protect yourself with these apps:\n\n"
        "📍 GPS Wipe: Photo Privacy\n"
        "https://play.google.com/store/apps/details?id=com.blocktracking.gpswipe\n\n"
        "📷 No Location Camera - GPS Off\n"
        "https://play.google.com/store/apps/details?id=io.kogera.noloccam\n\n"
        "🔍 QR Reader: Safe Scan SSL Check\n"
        "https://play.google.com/store/apps/details?id=com.kogera.qrtrapinsight\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{hashtags}"
    )
    return {
        "snippet": {
            "title": f"{hook[:70]} 🔒 #shorts",
            "description": description,
            "tags": ["cybersecurity","digital security","privacy","scam","phishing",
                     "QR code","GPS","AI security","shorts"],
            "categoryId": "28",  # Science & Technology
            "defaultLanguage": "en"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids": False
        }
    }

def upload_video(video_path: str, metadata: dict, token: str) -> str:
    meta_bytes = json.dumps(metadata).encode()
    boundary = b"---SecurityYTBoundary"
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    body = (b"--"+boundary+b"\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
            +meta_bytes+b"\r\n--"+boundary+b"\r\nContent-Type: video/mp4\r\n\r\n"
            +video_bytes+b"\r\n--"+boundary+b"--")
    url = f"{UPLOAD_URL}?uploadType=multipart&part=snippet,status"
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/related; boundary={boundary.decode()}",
        "Content-Length": str(len(body))
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["id"]

def update_posted(no: str):
    path = "data/posted.json"
    try:
        with open(path) as f: data = json.load(f)
    except: data = {"posted": []}
    if no not in data["posted"]:
        data["posted"].append(no)
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    no       = os.environ.get("SECURITY_NO", "0")
    hook     = os.environ.get("SECURITY_HOOK", "")
    script   = os.environ.get("SECURITY_SCRIPT", "")
    category = os.environ.get("SECURITY_CATEGORY", "")
    video    = os.environ.get("VIDEO_PATH", "")

    if not video or not os.path.exists(video):
        print(f"❌ 動画ファイルなし: {video}", file=sys.stderr)
        sys.exit(1)

    print(f"📤 アップロード開始: No.{no}")
    token = get_access_token()
    meta  = build_metadata(no, hook, script, category)
    vid_id = upload_video(video, meta, token)
    print(f"✅ アップロード完了: https://youtube.com/shorts/{vid_id}")
    update_posted(no)
    print(f"✅ posted.json 更新: No.{no}")

if __name__ == "__main__":
    main()
