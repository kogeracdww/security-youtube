#!/usr/bin/env python3
"""02_audio.py - Google Cloud TTSでナレーション生成"""
import json, os, sys, base64, urllib.request

GCP_API_KEY = os.environ.get("GCP_API_KEY", "")
TTS_ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"

def synthesize(text: str, output_path: str):
    if not GCP_API_KEY:
        raise ValueError("GCP_API_KEY が設定されていません")
    body = json.dumps({
        "input": {"text": text},
        "voice": {
            "languageCode": "en-US",
            "name": "en-US-Standard-D",
            "ssmlGender": "MALE"
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 0.95,
            "pitch": -1.0
        }
    }).encode()
    url = f"{TTS_ENDPOINT}?key={GCP_API_KEY}"
    req = urllib.request.Request(url, data=body,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        audio_data = base64.b64decode(result["audioContent"])
    with open(output_path, "wb") as f:
        f.write(audio_data)
    print(f"✅ 音声生成完了: {output_path}")

def main():
    no = os.environ.get("SECURITY_NO", "0")
    script = os.environ.get("SECURITY_SCRIPT", "")
    if not script:
        print("❌ SECURITY_SCRIPT が未設定", file=sys.stderr)
        sys.exit(1)
    os.makedirs("output", exist_ok=True)
    output_path = f"output/audio_{no.zfill(3)}.mp3"
    synthesize(script, output_path)
    env_file = os.environ.get("GITHUB_ENV", "")
    if env_file:
        with open(env_file, "a") as f:
            f.write(f"AUDIO_PATH={output_path}\n")
    else:
        print(f"AUDIO_PATH={output_path}")

if __name__ == "__main__":
    main()
