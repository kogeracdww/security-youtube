#!/usr/bin/env python3
"""01_select.py - 当日投稿すべきセキュリティコンテンツを選択"""
import json, os, sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

def main():
    today = datetime.now(JST).date()

    with open("data/security.json", encoding="utf-8") as f:
        items = json.load(f)
    with open("data/posted.json", encoding="utf-8") as f:
        posted_data = json.load(f)

    posted_nos = set(str(x) for x in posted_data.get("posted", []))

    # 当日スケジュールかつ未投稿
    targets = []
    for c in items:
        if str(c["no"]) in posted_nos:
            continue
        sched = datetime.fromisoformat(c["schedule"]).astimezone(JST)
        if sched.date() == today:
            targets.append(c)

    # フォールバック：未投稿の最古
    if not targets:
        remaining = [c for c in sorted(items, key=lambda x: x["no"])
                     if str(c["no"]) not in posted_nos]
        if not remaining:
            print("✅ 全35本投稿完了", file=sys.stderr)
            sys.exit(0)
        targets = [remaining[0]]

    target = targets[0]
    print(f"✅ Selected: No.{target['no']} {target['hook'][:40]}")

    hook_escaped = target.get("hook", "").replace("\n", "\\n")
    phrases_json = json.dumps(target.get("key_phrases", []), ensure_ascii=False)

    output = (
        f"SECURITY_NO={target['no']}\n"
        f"SECURITY_ID={target['id']}\n"
        f"SECURITY_HOOK={hook_escaped}\n"
        f"SECURITY_BGM={target.get('bgm','bgm_calm.mp3')}\n"
        f"SECURITY_ILLUSTRATION={target.get('illustration','img_calm.png')}\n"
        f"SECURITY_KEY_PHRASES={phrases_json}\n"
        f"SECURITY_SCRIPT={target.get('script','')}\n"
        f"SECURITY_CATEGORY={target.get('category','')}\n"
    )

    env_file = os.environ.get("GITHUB_ENV", "")
    if env_file:
        with open(env_file, "a") as f:
            f.write(output)
    else:
        print(output)

if __name__ == "__main__":
    main()
