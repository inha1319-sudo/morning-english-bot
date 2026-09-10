import os
import json
import requests
from datetime import datetime
from pathlib import Path
import re

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
READ_HISTORY_FILE = SCRIPT_DIR / "읽음기록.json"
ERROR_LOG_FILE = SCRIPT_DIR / "실수장부.md"

# 주간 실수 추적 데이터
WEAK_POINTS = {
    "시제": "시간이 어떻게 흘렀는지 헷갈릴 때",
    "수일치": "주어의 수를 잘못 맞춰서",
    "동사형태": "동사를 잘못된 형태로 사용할 때",
    "관사": "a/an/the를 놓치거나 잘못 쓸 때",
    "단복수": "명사의 복수형을 빠뜨릴 때",
    "전치사": "전치사 선택이 헷갈릴 때",
    "어순": "단어 순서가 잘못될 때",
    "자동사타동사": "동사의 성질을 모를 때",
    "단어선택": "좀 더 자연스러운 표현이 있을 때",
    "발음": "발음이 헷갈릴 때",
}

# 대안 표현 데이터 (실수 유형별)
ALTERNATIVE_EXPRESSIONS = {
    "시제": [
        "시간 순서를 명확히 하면 어떨까?",
        "지금/과거/미래를 다시 생각해보면?",
        "좀 더 명확한 시간 표현은?",
    ],
    "수일치": [
        "주어를 다시 보면?",
        "singular/plural을 한 번 더 체크하면?",
    ],
    "동사형태": [
        "동사의 기본형부터 생각해보면?",
        "어떤 형태의 동사가 맞을까?",
    ],
    "관사": [
        "첫 등장인가, 아니면 이미 언급된 건가?",
        "일반적인 건지, 특정한 건지?",
    ],
    "단어선택": [
        "더 자연스러운 표현이 있을까?",
        "네이티브처럼 쓰려면?",
    ],
}

def load_env():
    """Load environment variables from .env file"""
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
    """Get Telegram bot token and chat ID"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        load_env()
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found")
    
    return token, chat_id

def load_read_history():
    """Load history of read message IDs"""
    if READ_HISTORY_FILE.exists():
        with open(READ_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"message_ids": []}

def save_read_history(message_ids):
    """Save read message IDs"""
    with open(READ_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump({"message_ids": message_ids}, f, ensure_ascii=False, indent=2)

def get_unread_messages(token, chat_id):
    """Get unread messages from Telegram"""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get updates: {response.text}")
    
    data = response.json()
    if not data.get("ok"):
        return []
    
    read_history = load_read_history()
    read_ids = set(read_history["message_ids"])
    
    unread = []
    for update in data.get("result", []):
        if "message" in update:
            msg = update["message"]
            msg_id = msg.get("message_id")
            
            # Only get messages from our chat
            if msg.get("chat", {}).get("id") == int(chat_id) and msg_id not in read_ids:
                unread.append(msg)
                read_ids.add(msg_id)
    
    # Save updated history
    save_read_history(list(read_ids))
    
    return unread

def group_messages_by_time(messages, time_window_minutes=10):
    """Group messages by time (within time_window_minutes)"""
    if not messages:
        return []
    
    # Sort by timestamp
    sorted_msgs = sorted(messages, key=lambda m: m.get("date", 0))
    
    groups = []
    current_group = [sorted_msgs[0]]
    
    for i in range(1, len(sorted_msgs)):
        current_time = sorted_msgs[i].get("date", 0)
        prev_time = sorted_msgs[i-1].get("date", 0)
        
        if current_time - prev_time <= time_window_minutes * 60:
            current_group.append(sorted_msgs[i])
        else:
            groups.append(current_group)
            current_group = [sorted_msgs[i]]
    
    groups.append(current_group)
    return groups

def extract_feedback_data(text):
    """Extract [내 문장 / 고친 문장 / 실수종류] from feedback"""
    # 패턴: "내가 쓴 문장: ... / 고쳐진 문장: ... / 실수종류: ..."
    # 또는 줄바꿈으로 구분된 형식
    # 또는 ChatGPT 형식: "피드백 1: ... -> ... | 종류"
    patterns = [
        # ChatGPT 형식: "피드백 1: 원문 -> 수정문 | 종류"
        r'(?:피드백\s*\d+\s*:\s*)?([^-]+?)\s*->\s*([^|]+?)\s*\|\s*(.+?)(?:\n|$)',
        # 슬래시로 구분
        r'내(?:가\s+)?쓴\s+(?:문장|표현)[:\s]+([^/]+)\s*/\s*고(?:쳐진|친)\s+(?:문장|표현)[:\s]+([^/]+)\s*/\s*(?:실수|오류)(?:의?\s+)?(?:종류|타입)[:\s]+([^/\n]+)',
        r'내\s+:\s*([^/]+)/고쳐진\s+:\s*([^/]+)/실수종류\s+:\s*([^/\n]+)',
        # 줄바꿈으로 구분
        r'내(?:가\s+)?쓴\s+(?:문장|표현)[:\s]+([^\n]+)\n\s*고(?:쳐진|친)\s+(?:문장|표현)[:\s]+([^\n]+)\n\s*(?:실수|오류)(?:의?\s+)?(?:종류|타입)[:\s]+([^\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return {
                "original": match.group(1).strip(),
                "corrected": match.group(2).strip(),
                "error_type": match.group(3).strip()
            }

    return None

def count_weekly_errors(error_type):
    """Count how many times this error type appeared this week"""
    if not ERROR_LOG_FILE.exists():
        return 0
    
    count = 0
    today = datetime.now()
    week_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)
    
    with open(ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) >= 4:
                try:
                    date_str = parts[0].strip()
                    error = parts[3].strip()
                    
                    if error.lower() == error_type.lower():
                        count += 1
                except:
                    pass
    
    return count

def save_to_error_log(original, corrected, error_type):
    """Save to 실수장부.md"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create file if doesn't exist
    if not ERROR_LOG_FILE.exists():
        with open(ERROR_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("# 실수장부\n\n")
            f.write("날짜 | 내가 쓴 문장 | 고친 문장 | 실수의 종류\n")
            f.write("---|---|---|---\n")
    
    # Append new entry
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{today} | {original} | {corrected} | {error_type}\n")

def escape_html(text):
    """Escape HTML special characters"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def create_feedback_message(feedbacks):
    """Create formatted feedback message"""
    lines = []
    lines.append("<b>오늘의 피드백</b>\n")
    
    for i, feedback in enumerate(feedbacks, 1):
        original = feedback.get("original", "").strip()
        corrected = feedback.get("corrected", "").strip()
        error_type = feedback.get("error_type", "").strip()
        
        lines.append(f"<b>{i}. {escape_html(original)}</b>")
        lines.append(f"→ {escape_html(corrected)}")
        lines.append("")
        
        # 자연스러운 대안 표현
        alts = ALTERNATIVE_EXPRESSIONS.get(error_type, ["좀 더 자연스럽게 표현하면?"])
        if alts:
            lines.append(f"💡 {alts[0]}")
        
        lines.append("")
        
        # 주간 실수 횟수
        weekly_count = count_weekly_errors(error_type)
        if weekly_count > 0:
            lines.append(f"이번 주에 '{error_type}' 실수가 {weekly_count}번 나왔어. 패턴을 인식하면 줄일 수 있어!")
        else:
            lines.append(f"'{error_type}' 타입의 실수네. 한 번 더 신경 써보자!")
        
        lines.append("")
        
        # Save to log
        save_to_error_log(original, corrected, error_type)
    
    return "\n".join(lines)

def send_telegram_message(token, chat_id, text, parse_mode="HTML"):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to send message: {response.text}")

def main():
    """Main function"""
    load_env()
    token, chat_id = get_telegram_credentials()
    
    # Get unread messages
    messages = get_unread_messages(token, chat_id)
    
    if not messages:
        # No messages - ask once
        message = "오늘 대화했어? 피드백을 그대로 붙여넣어 줘."
        send_telegram_message(token, chat_id, message)
        print("No messages. Sent reminder.")
        return
    
    # Group by time
    message_groups = group_messages_by_time(messages)
    
    all_feedbacks = []
    
    for group in message_groups:
        combined_text = "\n".join([msg.get("text", "") for msg in group])
        
        # Extract feedback data
        feedback = extract_feedback_data(combined_text)
        if feedback:
            all_feedbacks.append(feedback)
    
    if all_feedbacks:
        # Create and send feedback message
        response = create_feedback_message(all_feedbacks)
        send_telegram_message(token, chat_id, response, "HTML")
        print(f"Sent feedback for {len(all_feedbacks)} corrections.")
    else:
        # Invalid format
        message = "피드백 형식이 맞는지 확인해줄래? [내가 쓴 문장 / 고친 문장 / 실수종류] 이렇게 보내줘."
        send_telegram_message(token, chat_id, message)
        print("Feedback format not recognized.")

if __name__ == "__main__":
    main()
