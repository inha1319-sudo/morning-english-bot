import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
from collections import Counter

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
ERROR_LOG_FILE = SCRIPT_DIR / "실수장부.md"
REVIEW_LIST_FILE = SCRIPT_DIR / "복습목록.md"

# 주제 데이터 (아침봇에서 가져옴)
TOPICS_DATA = [
    {
        "topic": "원격 근무 vs 사무실 근무",
        "keywords": ["work", "remote", "office"]
    },
    {
        "topic": "소셜 미디어의 영향",
        "keywords": ["social", "media", "technology"]
    },
    {
        "topic": "전공 선택의 중요성",
        "keywords": ["major", "career", "choice"]
    },
    {
        "topic": "육아와 경력",
        "keywords": ["parenting", "career", "balance"]
    },
    {
        "topic": "도시 vs 시골 생활",
        "keywords": ["city", "rural", "life"]
    },
    {
        "topic": "기술이 삶을 나아지게 했는가",
        "keywords": ["technology", "life", "better"]
    },
    {
        "topic": "여행: 계획 vs 즉흥",
        "keywords": ["travel", "plan", "spontaneous"]
    },
    {
        "topic": "학교 체벌",
        "keywords": ["school", "discipline", "punishment"]
    },
    {
        "topic": "가격 vs 품질",
        "keywords": ["price", "quality", "value"]
    },
    {
        "topic": "개인 정보 보호 vs 보안",
        "keywords": ["privacy", "security", "data"]
    },
]

# 실수 유형별 주제 매핑 (더 자연스러운 매칭)
ERROR_TYPE_TOPICS = {
    "시제": [0, 3, 5],  # 시간 개념이 필요한 주제
    "수일치": [1, 8, 9],
    "동사형태": [0, 4, 6],
    "관사": [2, 7, 8],
    "단복수": [1, 3, 5],
    "전치사": [4, 5, 6],
    "어순": [2, 3, 7],
    "자동사타동사": [0, 4, 5],
    "단어선택": [1, 2, 8],
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

def read_error_log():
    """Read 실수장부.md and parse entries"""
    entries = []
    
    if not ERROR_LOG_FILE.exists():
        return entries
    
    with open(ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.startswith('#') or '---' in line or '날짜' in line:
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                try:
                    date_str = parts[0]
                    original = parts[1]
                    corrected = parts[2]
                    error_type = parts[3]
                    
                    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    entries.append({
                        "date": entry_date,
                        "original": original,
                        "corrected": corrected,
                        "error_type": error_type
                    })
                except:
                    pass
    
    return entries

def get_weekly_stats():
    """Get stats for the past 7 days"""
    entries = read_error_log()
    
    # Calculate 7 days ago
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # Filter entries from past 7 days
    weekly_entries = [e for e in entries if week_ago <= e["date"] <= today]
    
    # Count conversations (unique dates)
    conversation_count = len(set(e["date"] for e in weekly_entries))
    
    # Count error types
    error_types = [e["error_type"] for e in weekly_entries]
    error_counts = Counter(error_types)
    top_3_errors = error_counts.most_common(3)
    
    return {
        "conversation_count": conversation_count,
        "top_3_errors": top_3_errors,
        "all_entries": weekly_entries,
        "error_counts": error_counts
    }

def select_next_week_focus(error_counts):
    """Select the most frequent error type for next week"""
    if not error_counts:
        return "시제"  # Default
    
    most_common = error_counts.most_common(1)[0][0]
    return most_common

def select_topics_for_review(focus_error_type):
    """Select 5 topics related to the focus error type"""
    if focus_error_type in ERROR_TYPE_TOPICS:
        topic_indices = ERROR_TYPE_TOPICS[focus_error_type]
    else:
        topic_indices = list(range(len(TOPICS_DATA)))
    
    # Select up to 5 topics
    selected_indices = topic_indices[:5] if len(topic_indices) >= 5 else topic_indices + list(range(len(TOPICS_DATA)))[:5-len(topic_indices)]
    selected_indices = list(set(selected_indices))[:5]
    
    topics = [TOPICS_DATA[i]["topic"] for i in selected_indices]
    return topics[:5]

def escape_html(text):
    """Escape HTML special characters"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def create_summary_message(stats):
    """Create weekly summary message"""
    lines = []
    
    # Title
    lines.append("<b>이번 주 정리</b>\n")
    
    # 1) 대화 횟수
    conv_count = stats["conversation_count"]
    lines.append(f"대화: {conv_count}번\n")
    
    # 2) 상위 3개 실수
    if stats["top_3_errors"]:
        lines.append("자주 틀린 것:")
        for error_type, count in stats["top_3_errors"][:3]:
            lines.append(f"• {error_type} ({count}번)")
        lines.append("")
    
    # 3) 다음 주 주의사항
    focus = select_next_week_focus(stats["error_counts"])
    lines.append(f"다음 주는 '{focus}'에 집중해보자.")
    
    return "\n".join(lines)

def create_review_list(focus_error_type):
    """Create 복습목록.md content"""
    topics = select_topics_for_review(focus_error_type)
    
    lines = []
    lines.append(f"# 복습목록\n")
    lines.append(f"**다음 주 약점:** {focus_error_type}\n")
    lines.append(f"**학습 주제:**\n")
    
    for i, topic in enumerate(topics, 1):
        lines.append(f"{i}. {topic}")
    
    return "\n".join(lines)

def save_review_list(content):
    """Save 복습목록.md (overwrite)"""
    with open(REVIEW_LIST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

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
    
    # Get weekly stats
    stats = get_weekly_stats()
    
    # Create and send summary message
    summary_message = create_summary_message(stats)
    send_telegram_message(token, chat_id, summary_message, "HTML")
    
    # Create and save review list for next week
    focus_error_type = select_next_week_focus(stats["error_counts"])
    review_content = create_review_list(focus_error_type)
    save_review_list(review_content)
    
    print(f"Weekly summary sent. Focus for next week: {focus_error_type}")

if __name__ == "__main__":
    main()
