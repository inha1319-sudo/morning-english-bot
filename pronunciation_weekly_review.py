import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
FEEDBACK_FILE = SCRIPT_DIR / "발음피드백.md"
PRONUNCIATION_INSTRUCTION_FILE = SCRIPT_DIR / "ChatGPT단어시험지시문.md"

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

def read_feedback_file():
    """Read feedback markdown file"""
    if not FEEDBACK_FILE.exists():
        return None

    with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def extract_this_week_feedback(content):
    """Extract feedback from this week (last 7 days)"""
    if not content:
        return None

    # Get today's date and last 7 days
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    # Parse feedback entries by date
    # Pattern: "## YYYY-MM-DD"
    date_pattern = r'## (\d{4}-\d{2}-\d{2})'
    dates = re.findall(date_pattern, content)

    # Filter dates within this week
    this_week_dates = []
    for date_str in dates:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if week_ago <= date <= today:
                this_week_dates.append(date_str)
        except:
            pass

    if not this_week_dates:
        return None

    # Extract content for this week
    this_week_content = ""
    for date_str in this_week_dates:
        # Find the section for this date
        pattern = f'## {date_str}.*?(?=## |$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            this_week_content += match.group(0)

    return this_week_content if this_week_content else None

def analyze_feedback(content):
    """Analyze weekly feedback and extract patterns"""
    if not content:
        return None

    analysis = {
        "total_expressions": 0,
        "expressions_list": [],
        "weakest_expressions": [],
        "common_issues": {},
        "days_practiced": set()
    }

    # Extract all feedback entries
    expr_pattern = r'### 표현 \d+: (.+?)\n'
    expressions = re.findall(expr_pattern, content)
    analysis["total_expressions"] = len(expressions)
    analysis["expressions_list"] = expressions[:10]  # 최대 10개

    # Extract dates practiced
    date_pattern = r'## (\d{4}-\d{2}-\d{2})'
    dates = re.findall(date_pattern, content)
    analysis["days_practiced"] = set(dates)

    # Extract weakest expressions
    weakest_pattern = r'\*\*특히 아쉬웠던 표현\*\*: (.+?)(?=\n|$)'
    weakest_matches = re.findall(weakest_pattern, content)
    for match in weakest_matches:
        if match.strip():
            analysis["weakest_expressions"].append(match.strip())

    # Extract common issues
    issue_pattern = r'\*\*공통 문제점\*\*: (.+?)(?=\n|$)'
    issue_matches = re.findall(issue_pattern, content)
    for match in issue_matches:
        issue = match.strip()
        if issue:
            analysis["common_issues"][issue] = analysis["common_issues"].get(issue, 0) + 1

    return analysis

def create_review_message(analysis):
    """Create weekly review message"""
    if not analysis or analysis["total_expressions"] == 0:
        return "이번주 발음 연습 기록이 없어요. 내일부터 시작해봐!"

    lines = []
    lines.append("<b>📊 이번주 발음 연습 통계</b>")
    lines.append("")

    # Stats
    lines.append(f"총 연습 표현: {analysis['total_expressions']}개")
    lines.append(f"연습한 날: {len(analysis['days_practiced'])}일")
    lines.append("")

    # Weakest expressions
    if analysis["weakest_expressions"]:
        lines.append("<b>⚠️ 특히 아쉬웠던 표현 (다시 연습하기)</b>")
        for expr in analysis["weakest_expressions"][:5]:
            lines.append(f"• {expr}")
        lines.append("")

    # Common issues
    if analysis["common_issues"]:
        lines.append("<b>🔧 공통 문제점 (주의하세요)</b>")
        sorted_issues = sorted(analysis["common_issues"].items(), key=lambda x: x[1], reverse=True)
        for issue, count in sorted_issues[:3]:
            lines.append(f"• {issue} (나타난 횟수: {count}회)")
        lines.append("")

    lines.append("<b>📚 이제 단어 시험을 봐볼까요?</b>")
    lines.append("다음 메시지의 ChatGPT 지시문을 복사해서")
    lines.append("새 대화에 붙여넣고 start를 보내세요!")

    return "\n".join(lines)

def create_word_test_instruction(expressions):
    """Create word test instruction for ChatGPT"""
    if not expressions:
        return None

    # Format expressions for template
    expr_text = ""
    for i, expr in enumerate(expressions, 1):
        expr_text += f"{i}. {expr}\n"

    instruction = f"""이번주 배운 영어 표현들의 뜻을 테스트합니다.

[표현 목록 (총 {len(expressions)}개)]
{expr_text}

[단어 시험 규칙]
1. 한국어로만 진행.
2. 위 표현들을 하나씩 영어로 말해주기. (예: "Break the bank")
3. 사용자가 그 표현의 뜻을 한국어로 답하기.
4. 사용자가 답하면 맞는지 평가.
5. 틀렸으면 정답을 알려주고 같은 표현으로 다시 한번 출제하기.
6. 맞으면 "맞아! 다음."이라고만 하고 다음 표현으로 넘어가기.
7. 모든 표현을 다 테스트하면 "다 끝났어. wrap up해봐"라고 하기.
8. 별표, 우물정자, 번호, 제목 쓰지 마. 자연스러운 한국어 문장만.

아직 시작 전. "준비 완료."라고만 하고 멈춰."""

    return instruction

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

    # Read feedback file
    content = read_feedback_file()

    # Extract this week's feedback
    this_week = extract_this_week_feedback(content)

    if not this_week:
        message = "이번주 발음 연습 기록이 없어요. 매일 아침 발음 봇 메시지를 받고 연습해보세요!"
        send_telegram_message(token, chat_id, message)
        print("No feedback this week")
        return

    # Analyze feedback
    analysis = analyze_feedback(this_week)

    # Create and send review message
    review_message = create_review_message(analysis)
    send_telegram_message(token, chat_id, review_message)

    # Create and send word test instruction
    if analysis["expressions_list"]:
        word_test = create_word_test_instruction(analysis["expressions_list"])
        if word_test:
            # Send as code block
            escaped = word_test.replace("<", "&lt;").replace(">", "&gt;")
            instruction_message = f"<pre><code>{escaped}</code></pre>"
            send_telegram_message(token, chat_id, instruction_message)

    print(f"Sent weekly review for {analysis['total_expressions']} expressions with word test")

if __name__ == "__main__":
    main()
