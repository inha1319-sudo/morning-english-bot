import os
import sys
import json
import requests
import time
from datetime import datetime
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
FEEDBACK_FILE = SCRIPT_DIR / "발음피드백.md"
STATE_FILE = SCRIPT_DIR / "봇_상태.json"

def load_env():
    """환경 변수 로드"""
    if not ENV_FILE.exists():
        return
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if value:
                    os.environ[key.strip()] = value.strip()

def get_telegram_credentials():
    """텔레그램 토큰과 채팅 ID 로드"""
    token = os.getenv('PRONUNCIATION_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        load_env()
        token = os.getenv('PRONUNCIATION_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        raise ValueError("PRONUNCIATION_BOT_TOKEN or TELEGRAM_CHAT_ID not found")
    return token, chat_id

def load_state():
    """봇 상태(마지막 offset) 로드"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('last_update_id', 0)
    return 0

def save_state(update_id):
    """봇 상태 저장"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_update_id': update_id}, f)

def extract_pronunciation_feedback(text):
    """피드백 추출"""
    feedbacks = []

    # 각 표현 블록 찾기: "표현: ... 내 발음: ... 평가: ... 개선점: ..."
    pattern = r'표현:\s*(.+?)\n내 발음:\s*(.+?)\n평가:\s*(.+?)(?:\n개선점:\s*(.+?))?(?=\n표현:|$)'
    matches = re.findall(pattern, text, re.DOTALL)

    for expr, pron, eval_text, improve in matches:
        feedback = {
            "expression": expr.strip(),
            "pronunciation": pron.strip(),
            "evaluation": eval_text.strip(),
            "improvement": improve.strip() if improve else "",
        }
        feedbacks.append(feedback)

    return feedbacks if feedbacks else None

def save_feedback(feedbacks):
    """피드백 파일에 저장"""
    if not feedbacks:
        return

    if not FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
            f.write("# 발음 피드백 기록\n\n")

    today = datetime.now().strftime("%Y-%m-%d")

    with open(FEEDBACK_FILE, 'a', encoding='utf-8') as f:
        f.write(f"## {today}\n\n")

        for i, fb in enumerate(feedbacks, 1):
            f.write(f"### 표현 {i}: {fb['expression']}\n")
            f.write(f"- **내 발음**: {fb['pronunciation']}\n")
            f.write(f"- **평가**: {fb['evaluation']}\n")
            if fb['improvement']:
                f.write(f"- **개선점**: {fb['improvement']}\n")
            f.write("\n")

        f.write("---\n\n")

    print(f"✅ {len(feedbacks)}개 피드백 저장됨 ({today})")

def get_updates(token, offset):
    """텔레그램 업데이트 가져오기"""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {'offset': offset + 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("ok"):
            return data.get("result", [])
    except Exception as e:
        print(f"에러: {e}")

    return []

def send_confirmation(token, chat_id, count):
    """확인 메시지 발송"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    message = f"✅ {count}개 표현 피드백이 저장되었습니다!"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"메시지 발송 실패: {e}")

def main():
    """메인 루프"""
    load_env()
    token, chat_id = get_telegram_credentials()

    last_update_id = load_state()
    processed_messages = set()

    print("🤖 발음 봇 시작! (Ctrl+C로 종료)")
    print(f"📱 채팅 ID: {chat_id}")
    print("⏳ 메시지를 기다리는 중...\n")

    try:
        while True:
            updates = get_updates(token, last_update_id)

            for update in updates:
                update_id = update['update_id']

                # 중복 메시지 방지
                if update_id in processed_messages:
                    last_update_id = update_id
                    save_state(last_update_id)
                    continue

                if 'message' in update:
                    msg = update['message']
                    text = msg.get('text', '')

                    # 피드백 패턴 감지
                    if '표현:' in text and '내 발음:' in text:
                        feedbacks = extract_pronunciation_feedback(text)

                        if feedbacks:
                            save_feedback(feedbacks)
                            send_confirmation(token, chat_id, len(feedbacks))
                            processed_messages.add(update_id)

                last_update_id = update_id
                save_state(last_update_id)

            # 2초 대기 후 다시 확인
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n👋 봇 종료!")
        save_state(last_update_id)

if __name__ == "__main__":
    main()
