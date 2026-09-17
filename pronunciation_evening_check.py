import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
FEEDBACK_FILE = SCRIPT_DIR / "발음피드백.md"
READ_HISTORY_FILE = SCRIPT_DIR / "발음읽음기록.json"

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
    token = os.getenv('PRONUNCIATION_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        load_env()
        token = os.getenv('PRONUNCIATION_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        raise ValueError("PRONUNCIATION_BOT_TOKEN or TELEGRAM_CHAT_ID not found")

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

def extract_pronunciation_feedback(text):
    """
    Extract pronunciation feedback from text.
    Format:
    표현: ...
    내 발음: ...
    평가: ...
    개선점: ...

    Also extracts sentence if provided in the same message.
    """
    feedbacks = []
    sentence = None

    # Try to extract sentence if it exists (sentence that user provided)
    # Common patterns: "문장:" or just a longer English sentence
    sentence_match = re.search(r'문장:\s*(.+?)(?=\n표현:|표현:|$)', text, re.DOTALL)
    if sentence_match:
        sentence = sentence_match.group(1).strip()

    # Split by "표현:" to find multiple feedback blocks
    blocks = re.split(r'(^|\n)(표현:)', text)

    for i in range(1, len(blocks), 2):
        if i + 1 < len(blocks):
            block = "표현:" + blocks[i + 1]

            # Extract each field
            expr_match = re.search(r'표현:\s*(.+?)(?=\n내 발음:|$)', block, re.DOTALL)
            pron_match = re.search(r'내 발음:\s*(.+?)(?=\n평가:|$)', block, re.DOTALL)
            eval_match = re.search(r'평가:\s*(.+?)(?=\n개선점:|$)', block, re.DOTALL)
            improve_match = re.search(r'개선점:\s*(.+?)(?=\n|$)', block, re.DOTALL)

            if expr_match and pron_match and eval_match:
                feedback = {
                    "expression": expr_match.group(1).strip(),
                    "pronunciation": pron_match.group(1).strip(),
                    "evaluation": eval_match.group(1).strip(),
                    "improvement": improve_match.group(1).strip() if improve_match else "",
                    "sentence": sentence,
                }
                feedbacks.append(feedback)

    return feedbacks if feedbacks else None

def extract_weekly_summary(text):
    """Extract weekly summary from feedback"""
    summary = {}

    # Extract "특히 아쉬웠던 표현"
    summary_match = re.search(r'=== 주간 복습용 ===\n특히 아쉬웠던 표현:\s*(.+?)(?=\n공통 문제점:|$)', text, re.DOTALL)
    if summary_match:
        summary["weakest_expressions"] = summary_match.group(1).strip()

    # Extract "공통 문제점"
    problem_match = re.search(r'공통 문제점:\s*(.+?)(?=\n|$)', text, re.DOTALL)
    if problem_match:
        summary["common_issues"] = problem_match.group(1).strip()

    return summary if summary else None

def save_feedback(date, feedbacks, weekly_summary):
    """Save feedback to markdown file"""
    # Create file if doesn't exist
    if not FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
            f.write("# 발음 피드백 기록\n\n")

    # Append new feedback
    with open(FEEDBACK_FILE, 'a', encoding='utf-8') as f:
        f.write(f"## {date}\n\n")

        for i, fb in enumerate(feedbacks, 1):
            f.write(f"### 표현 {i}: {fb['expression']}\n")
            if fb.get('sentence'):
                f.write(f"- **문장**: {fb['sentence']}\n")
            f.write(f"- **내 발음**: {fb['pronunciation']}\n")
            f.write(f"- **평가**: {fb['evaluation']}\n")
            if fb['improvement']:
                f.write(f"- **개선점**: {fb['improvement']}\n")
            f.write("\n")

        if weekly_summary:
            f.write(f"**특히 아쉬웠던 표현**: {weekly_summary.get('weakest_expressions', '')}\n\n")
            f.write(f"**공통 문제점**: {weekly_summary.get('common_issues', '')}\n\n")

        f.write("---\n\n")

def send_telegram_message(token, chat_id, text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
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
        # No messages - remind user
        message = "오늘 발음 연습 했어? ChatGPT에서 wrap up해서 피드백 보내줘."
        send_telegram_message(token, chat_id, message)
        print("No messages. Sent reminder.")
        return

    # Process messages
    today = datetime.now().strftime("%Y-%m-%d")
    all_feedbacks = []
    weekly_summary = None

    for msg in messages:
        text = msg.get("text", "")

        feedbacks = extract_pronunciation_feedback(text)
        if feedbacks:
            all_feedbacks.extend(feedbacks)

            # Also extract weekly summary if present
            summary = extract_weekly_summary(text)
            if summary:
                weekly_summary = summary

    if all_feedbacks:
        # Save feedback
        save_feedback(today, all_feedbacks, weekly_summary)

        # Send confirmation
        message = f"✅ {len(all_feedbacks)}개 표현 피드백 기록했어!\n"
        if weekly_summary:
            message += f"특히 아쉬웠던 표현: {weekly_summary.get('weakest_expressions', '')}\n"
            message += f"공통 문제점: {weekly_summary.get('common_issues', '')}"

        send_telegram_message(token, chat_id, message)
        print(f"Saved {len(all_feedbacks)} feedback entries")
    else:
        # Invalid format
        message = "피드백 형식이 맞는지 확인해줄래?\n표현 / 내 발음 / 평가 / 개선점 이렇게 보내줘."
        send_telegram_message(token, chat_id, message)
        print("Feedback format not recognized.")

if __name__ == "__main__":
    main()
