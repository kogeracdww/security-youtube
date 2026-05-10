#!/usr/bin/env python3
"""
03_video.py - YouTube Shorts 動画合成（セキュリティ版）
Pillowでフレーム生成 → FFmpegで動画化
"""
import json, os, sys, subprocess, shutil, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SAFE_TOP = 285
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FS_HOOK, FS_PHRASE, FS_TITLE, FS_LOGO = 96, 38, 58, 34
CAMERA_SAFE = 120   # カメラホール下端の余白
PAD_X = 80          # 左右余白px（フック用）
WHITE = (255, 255, 255, 255)
WHITE_DIM = (255, 255, 255, 180)
SHADOW = (0, 0, 0, 160)


def get_bgm_samples(bgm_path: str) -> int:
    """BGMの実際のサンプル数を取得してaloopのsizeに使う"""
    try:
        r = subprocess.run([
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'stream=nb_samples,sample_rate,duration',
            '-select_streams', 'a:0', '-of', 'json', bgm_path
        ], capture_output=True, text=True)
        data = json.loads(r.stdout)
        s = data.get('streams', [{}])[0]
        if s.get('nb_samples') and s['nb_samples'] != 'N/A':
            return int(s['nb_samples'])
        dur = float(s.get('duration', 30))
        sr  = int(s.get('sample_rate', 44100))
        return int(dur * sr)
    except Exception:
        return 1323000  # 30秒@44100Hzのフォールバック


def clean(s: str) -> str:
    if not s: return ""
    s = s.replace("\\n", " ").replace("\n", " ")
    for ch in ["—","–","\u2014","\u2013"]: s = s.replace(ch, "-")
    while "  " in s: s = s.replace("  ", " ")
    return s.strip()


def draw_centered(draw, text, y, font, color=WHITE, max_w=W-120):
    text = clean(text)
    if not text: return
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2]-bbox[0] > max_w and line:
            lines.append(line); line = w
        else:
            line = test
    if line: lines.append(line)
    lh = int(draw.textbbox((0,0),"A",font=font)[3] * 1.5)
    cy = y
    for l in lines:
        bbox = draw.textbbox((0,0), l, font=font)
        x = (W - (bbox[2]-bbox[0])) // 2
        draw.text((x+2, cy+2), l, font=font, fill=SHADOW)
        draw.text((x, cy), l, font=font, fill=color)
        cy += lh


def make_frame(bg_img, texts):
    if bg_img:
        frame = bg_img.copy().convert("RGBA")
    else:
        frame = Image.new("RGBA", (W,H), (20,20,35,255))
    draw = ImageDraw.Draw(frame)
    for text, y, fs, dim in texts:
        try: font = ImageFont.truetype(FONT_PATH, fs)
        except: font = ImageFont.load_default()
        color = WHITE_DIM if dim else WHITE
        # フックは左右余白PAD_Xを確保
        max_w = W - PAD_X * 2 if fs >= FS_HOOK else W - 120
        draw_centered(draw, text, y, font, color=color, max_w=max_w)
    return frame.convert("RGB")


def render_frames(bg_path, hook, phrases, no, dur=20.0):
    import re
    bg = None
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        r = max(W/img.width, H/img.height)
        nw, nh = int(img.width*r), int(img.height*r)
        img = img.resize((nw,nh), Image.LANCZOS)
        bg = img.crop(((nw-W)//2, (nh-H)//2, (nw-W)//2+W, (nh-H)//2+H))

    # レイアウト（カメラホール考慮）
    # カメラホール下端 + フォントサイズ以上の余白
    hook_y   = CAMERA_SAFE + FS_HOOK      # 約216px〜
    phrase_y = hook_y + FS_HOOK * 3       # フックの下
    title_y  = CAMERA_SAFE + FS_TITLE
    logo_y   = title_y + FS_TITLE + 20

    def get_texts(t):
        if t < 15:
            # 最初から全部表示（フック + key_phrases[0-2]）
            texts = [(hook, hook_y, FS_HOOK, False)]
            for i, p in enumerate(phrases[:3]):
                texts.append((p, phrase_y + i * int(FS_PHRASE * 2.2), FS_PHRASE, False))
            return texts
        elif t < 19:
            # タイトルカード
            p4 = phrases[3] if len(phrases) > 3 else ""
            p4 = re.sub(r"^No\.\d+\s*[\-—–]\s*", "", p4)
            return [(p4, title_y, FS_TITLE, False),
                    ("Digital Security", logo_y, FS_LOGO, True)]
        else:
            # ループ：フックのみ
            return [(hook, hook_y, FS_HOOK, False)]

    tmpdir = tempfile.mkdtemp()
    fps, total = 30, int(dur*30)
    for fn in range(total):
        make_frame(bg, get_texts(fn/fps)).save(f"{tmpdir}/f{fn:06d}.png")
    return tmpdir


def main():
    no     = os.environ.get("SECURITY_NO", "0")
    hook   = os.environ.get("SECURITY_HOOK", "")
    bgm    = os.environ.get("SECURITY_BGM", "bgm_calm.mp3")
    illus  = os.environ.get("SECURITY_ILLUSTRATION", "")
    pjson  = os.environ.get("SECURITY_KEY_PHRASES", "[]")
    audio  = os.environ.get("AUDIO_PATH", "")
    dur    = 20.0

    phrases = json.loads(pjson)
    bgm_p   = f"assets/bgm/{bgm}"
    ill_p   = f"assets/illustrations/{illus}"
    has_bgm = os.path.exists(bgm_p)
    has_img = os.path.exists(ill_p)

    print(f"🔒 No.{no} セキュリティ動画合成開始")
    print(f"   BGM: {bgm_p} ({'OK' if has_bgm else 'なし'})")
    print(f"   Illustration: {ill_p} ({'OK' if has_img else 'なし'})")

    tmpdir = render_frames(ill_p if has_img else None, hook, phrases, no, dur)

    os.makedirs("output", exist_ok=True)
    out = f"output/video_{no.zfill(3)}.mp4"

    cmd = ["ffmpeg", "-y", "-framerate", "30",
           "-i", f"{tmpdir}/f%06d.png",
           "-i", audio]
    if has_bgm:
        cmd += ["-i", bgm_p]

    if has_bgm:
        bgm_samples = get_bgm_samples(bgm_p)
        af = ("[1:a]apad=whole_dur=20[narr_pad]"  # ナレーション短くても20秒まで延長
              ";[2:a]volume=0.28[bgm_v]"
              f";[bgm_v]aloop=loop=-1:size={bgm_samples}[bgm_l]"
              ";[narr_pad][bgm_l]amix=inputs=2:duration=first[aout]")
        cmd += ["-filter_complex", af, "-map", "0:v", "-map", "[aout]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]

    cmd += ["-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-b:v", "8M", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]

    r = subprocess.run(cmd, capture_output=True, text=True)
    shutil.rmtree(tmpdir, ignore_errors=True)

    if r.returncode != 0:
        print("❌ FFmpeg エラー:", r.stderr[-2000:], file=sys.stderr)
        sys.exit(1)

    print(f"✅ 完成: {out}")
    env_file = os.environ.get("GITHUB_ENV", "")
    if env_file:
        open(env_file, "a").write(f"VIDEO_PATH={out}\n")
    else:
        print(f"VIDEO_PATH={out}")

if __name__ == "__main__":
    main()
