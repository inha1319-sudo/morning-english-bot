import os
import json
import random
from datetime import datetime
import requests
from pathlib import Path

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
HISTORY_FILE = SCRIPT_DIR / "history.json"
CHATGPT_INSTRUCTION_FILE = SCRIPT_DIR / "ChatGPT지시문.md"
REVIEW_LIST_FILE = SCRIPT_DIR / "복습목록.md"

# 목표 표현 데이터 (표현, 한국어 뜻)
EXPRESSIONS_DATA = [
    ("Those little splurges add up, too.", "그렇게 조금씩 한 사치들이 결국 쌓이는 거지."),
    ("It's a vicious cycle.", "그건 악순환이야."),
    ("Saving feels like a chore.", "저축하는 게 귀찮은 일처럼 느껴지긴 하지."),
    ("I get what you're saying.", "네 말 알겠어."),
    ("That's the whole point.", "그게 핵심이야."),
    ("It goes both ways.", "양쪽 다 그런 거야."),
    ("I hear what you're saying.", "내가 너 말 들었고."),
    ("At the end of the day.", "결국."),
    ("It depends on how you look at it.", "어떻게 보느냐에 따라 다르지."),
    ("That's a fair point.", "그건 타당한 주장이야."),
    ("Let's agree to disagree.", "의견은 다르지만 존중하자."),
    ("I'm not sure I follow.", "뭔 말인지 좀 잘 모르겠는데."),
    ("That's debatable.", "그건 논쟁의 여지가 있어."),
    ("I see it differently.", "나는 다르게 봐."),
    ("It's not black and white.", "까맣게 하얗게 하는 건 아니야."),
    ("There's a reason for that.", "그럴 만한 이유가 있지."),
    ("I totally get where you're coming from.", "네가 왜 그렇게 생각하는지 알겠어."),
    ("That being said.", "하지만."),
    ("Ideally, yes, but realistically...", "이상적으로는 맞지만 현실적으로는..."),
    ("You make a good point.", "그건 좋은 포인트네."),
    ("I never thought of it that way.", "그런 각도로는 생각해 본 적이 없는데."),
    ("That's easier said than done.", "말은 쉬워도 하기는 힘들지."),
    ("It's complicated.", "복잡해."),
    ("I'm torn on this.", "이건 정하기 힘들어."),
    ("That's a double-edged sword.", "양날의 검이네."),
    ("There's no one-size-fits-all solution.", "만능 해결책은 없어."),
    ("It's not that simple.", "단순하지 않아."),
    ("I beg to differ.", "난 다르게 생각해."),
    ("You have a point.", "일리가 있어."),
    ("I can see both sides.", "둘 다 이해가 돼."),
]

# 주제 데이터 (OPIC 준비용: 일상 + 의견)
TOPICS_DATA = [
    # === 의견 주제 (기존) ===
    {
        "topic": "원격 근무 vs 사무실 근무",
        "situation": "당신은 새로운 팀 리더인 Alex와 회사의 업무 방식에 대해 얘기하고 있습니다. 요즘 원격 근무와 사무실 근무 중 어느 쪽이 더 나을지 고민 중입니다.",
        "first_dialogue": "Do you think working from home is better than being in an office?"
    },
    {
        "topic": "소셜 미디어의 영향",
        "situation": "당신은 Jordan이라는 친구와 카페에서 만났습니다. 요즘 젊은 세대의 소셜 미디어 사용에 대해 논의 중입니다.",
        "first_dialogue": "How do you feel about how much time people spend on social media?"
    },
    {
        "topic": "전공 선택의 중요성",
        "situation": "당신은 대학 상담사인 Morgan과 진로 상담을 하고 있습니다. 학생들이 돈이 되는 직업을 택해야 하는지, 흥미 있는 분야를 택해야 하는지 의견이 나뉩니다.",
        "first_dialogue": "Should students choose a major based on earning potential or passion?"
    },
    {
        "topic": "육아와 경력",
        "situation": "당신은 동료인 Sam과 퇴근 후 대화 중입니다. 육아 책임과 경력 추구 사이에서의 균형에 대해 얘기하고 있습니다.",
        "first_dialogue": "Is it possible to balance raising kids with having an ambitious career?"
    },
    {
        "topic": "도시 vs 시골 생활",
        "situation": "당신은 이사를 고민 중인 친구 Casey와 통화 중입니다. 도시의 편의성과 시골의 평온함 중 어느 것이 더 중요한지 논의하고 있습니다.",
        "first_dialogue": "Do you think living in a big city is worth the cost and hassle?"
    },
    {
        "topic": "기술이 삶을 나아지게 했는가",
        "situation": "당신은 조부모 세대인 Taylor와 저녁 식사를 하고 있습니다. 요즘 기술이 정말 우리 삶을 더 나아지게 했는지에 대해 토론하고 있습니다.",
        "first_dialogue": "Has technology really made our lives better or just more complicated?"
    },
    {
        "topic": "여행: 계획 vs 즉흥",
        "situation": "당신은 여행 친구인 Riley와 다음 휴가 계획을 짜고 있습니다. 세세하게 계획을 짜야 하는지 아니면 즉흥적으로 가야 하는지 의견이 다릅니다.",
        "first_dialogue": "Do you prefer planning every detail of a trip or just winging it?"
    },
    {
        "topic": "학교 체벌",
        "situation": "당신은 학부모인 Jamie와 자녀 교육 방식에 대해 얘기 중입니다. 학교에서의 엄격한 훈육이 필요한지, 아니면 너무 가혹한지 의견을 나누고 있습니다.",
        "first_dialogue": "Do you think schools are too strict or not strict enough with discipline?"
    },
    {
        "topic": "가격 vs 품질",
        "situation": "당신은 쇼핑몰에서 친구 Alex를 만났습니다. 비싼 명품과 저렴한 대량 생산 제품 중 어느 것이 더 가치 있는지 의견이 나뉩니다.",
        "first_dialogue": "Do you think expensive brands are worth the price, or is it just marketing?"
    },
    {
        "topic": "개인 정보 보호 vs 보안",
        "situation": "당신은 보안 전문가인 Morgan과 카페에서 개인정보 유출 뉴스에 대해 이야기 중입니다. 프라이버시를 얼마나 포기해야 안전할 수 있는지 토론하고 있습니다.",
        "first_dialogue": "How much privacy should we be willing to give up for better security?"
    },

    # === 일상 주제 (OPIC 맞춤형) ===
    {
        "topic": "좋아하는 영화",
        "situation": "당신은 친구 Blake와 영화 관람 후 카페에 앉아 있습니다. 최근에 본 영화와 선호하는 장르에 대해 얘기하고 있습니다.",
        "first_dialogue": "What was the last movie you watched? Did you like it?"
    },
    {
        "topic": "주말 계획",
        "situation": "당신은 동료 Cameron과 금요일 오후에 대화하고 있습니다. 다가오는 주말을 어떻게 보낼지 계획을 나누고 있습니다.",
        "first_dialogue": "What do you usually do on weekends?"
    },
    {
        "topic": "공원 방문",
        "situation": "당신은 친구 Dakota와 공원 산책을 하고 있습니다. 공원을 좋아하는 이유와 자주 가는 활동에 대해 얘기하고 있습니다.",
        "first_dialogue": "How often do you come to the park? What do you like about it?"
    },
    {
        "topic": "해변 휴가",
        "situation": "당신은 친구 Drew와 해변 여행 후 이야기하고 있습니다. 해변에서 무엇을 하는 걸 가장 좋아하는지 대화 중입니다.",
        "first_dialogue": "Do you enjoy going to the beach? What's your favorite thing to do there?"
    },
    {
        "topic": "요리와 음식",
        "situation": "당신은 친구 Finley와 집에서 함께 요리하고 있습니다. 즐겨 하는 요리와 요리하는 이유에 대해 얘기하고 있습니다.",
        "first_dialogue": "Do you like cooking? What's your favorite dish to make?"
    },
    {
        "topic": "운동과 건강",
        "situation": "당신은 피트니스 센터에서 친구 Harley를 만났습니다. 운동 습관과 건강 유지 방법에 대해 대화 중입니다.",
        "first_dialogue": "What kind of exercise do you do regularly? How do you stay healthy?"
    },
    {
        "topic": "조깅과 러닝",
        "situation": "당신은 조깅 모임에서 새로운 친구 Haven을 만났습니다. 조깅을 시작한 이유와 자주 달리는 장소에 대해 얘기하고 있습니다.",
        "first_dialogue": "How long have you been jogging? Do you run alone or with friends?"
    },
    {
        "topic": "국내 여행 계획",
        "situation": "당신은 여행사 직원인 Jazz와 국내 여행 패키지를 살펴보고 있습니다. 자주 가는 여행지와 여행 스타일에 대해 대화 중입니다.",
        "first_dialogue": "Where do you usually travel within Korea? What do you like to do on trips?"
    },
    {
        "topic": "최근 여행 경험",
        "situation": "당신은 친구 Keenan과 최근 다녀온 여행에 대해 이야기하고 있습니다. 가장 인상적인 경험과 추천할 만한 장소에 대해 나누고 있습니다.",
        "first_dialogue": "Tell me about your last trip. Where did you go and what did you do?"
    },
    {
        "topic": "집에서의 휴가",
        "situation": "당신은 친구 Logan과 휴가 계획에 대해 얘기하고 있습니다. 바쁜 일정 속에서 집에서 쉬는 것의 가치에 대해 대화 중입니다.",
        "first_dialogue": "How do you prefer to spend your vacation? At home or traveling?"
    },
    {
        "topic": "가족과의 시간",
        "situation": "당신은 친구 Morgan과 주말에 가족과 함께 보내는 시간에 대해 얘기하고 있습니다. 함께 즐겨 하는 활동과 가족 관계에 대해 대화 중입니다.",
        "first_dialogue": "What do you like to do with your family in your free time?"
    },
    {
        "topic": "음악 감상",
        "situation": "당신은 친구 Parker와 카페에서 좋아하는 음악에 대해 얘기하고 있습니다. 선호하는 장르와 최근 즐겨 듣는 아티스트에 대해 대화 중입니다.",
        "first_dialogue": "What kind of music do you enjoy listening to?"
    },
    {
        "topic": "취미 활동",
        "situation": "당신은 커뮤니티 센터에서 친구 Quinn과 만났습니다. 각자의 취미 활동과 시간을 내서 하는 이유에 대해 얘기하고 있습니다.",
        "first_dialogue": "What hobbies do you have? How often do you get to do them?"
    },
    {
        "topic": "건강한 생활 습관",
        "situation": "당신은 의사인 Ryan과 건강한 생활 방식에 대해 상담하고 있습니다. 식습관과 운동, 수면 등 일상 건강 관리에 대해 대화 중입니다.",
        "first_dialogue": "What do you do to maintain a healthy lifestyle?"
    },
    {
        "topic": "요리 실력",
        "situation": "당신은 친구 Sidney와 요리에 대해 얘기하고 있습니다. 요리 경험과 가장 잘하는 음식, 배우고 싶은 요리에 대해 대화 중입니다.",
        "first_dialogue": "How good are you at cooking? What's the hardest dish you've tried to make?"
    },
    {
        "topic": "계절별 활동",
        "situation": "당신은 친구 Tyler와 각 계절마다 즐기는 활동에 대해 얘기하고 있습니다. 봄, 여름, 가을, 겨울 각각에 선호하는 활동에 대해 대화 중입니다.",
        "first_dialogue": "What's your favorite season? What do you like to do during that time?"
    },
    {
        "topic": "일과 생활의 균형",
        "situation": "당신은 친구 Vega와 일과 여가시간의 균형에 대해 얘기하고 있습니다. 일을 마친 후 개인 시간을 어떻게 활용하는지 대화 중입니다.",
        "first_dialogue": "How do you balance work and your personal life?"
    },
    {
        "topic": "외식 vs 집에서 요리",
        "situation": "당신은 배우자 또는 친구 Wren과 저녁 계획을 세우고 있습니다. 외식이 좋은지, 집에서 요리하는 게 좋은지에 대해 의견을 나누고 있습니다.",
        "first_dialogue": "Do you prefer eating out at restaurants or cooking at home?"
    },
]

# 상대 이름
NAMES_DATA = [
    "Alex", "Jordan", "Morgan", "Casey", "Sam", "Riley", "Jamie", "Taylor",
    "Blake", "Cameron", "Dakota", "Drew", "Finley", "Harley", "Haven",
    "Jazz", "Keenan", "Logan", "Morgan", "Parker", "Quinn", "Ryan",
    "Sidney", "Tyler", "Vega", "Wren"
]

def load_env():
    """Load environment variables from .env file if it exists."""
    if not ENV_FILE.exists():
        return

    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if value:  # Only set if value is not empty
                    os.environ[key.strip()] = value.strip()


def get_telegram_credentials():
    """Get Telegram bot token and chat ID from environment or .env."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        load_env()
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in environment or .env")

    return token, chat_id

def load_history():
    """Load history of recent topics"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"topics": []}

def save_history(topic):
    """Save today's topic to history"""
    history = load_history()
    history["topics"].append({
        "topic": topic,
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    # Keep only last 7 topics
    if len(history["topics"]) > 7:
        history["topics"] = history["topics"][-7:]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_unused_topic():
    """Get a topic that hasn't been used recently"""
    history = load_history()
    used_topics = {h["topic"] for h in history["topics"]}
    
    available = [t for t in TOPICS_DATA if t["topic"] not in used_topics]
    if not available:
        available = TOPICS_DATA
    
    return random.choice(available)

def get_three_expressions():
    """Get 3 random expressions"""
    return random.sample(EXPRESSIONS_DATA, 3)

def get_random_name():
    """Get a random name"""
    return random.choice(NAMES_DATA)

def get_weak_point():
    """Get weak point from review list, or default to '시제'"""
    if not REVIEW_LIST_FILE.exists():
        return "시제"
    
    try:
        with open(REVIEW_LIST_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for the line that starts with "실수종류:"
            lines = content.split('\n')
            error_types = ["시제", "수일치", "동사 형태", "관사", "단복수", "가산·불가산", 
                          "전치사", "자동사·타동사", "어순", "콩글리시", "단어 선택", "빠진 말"]
            
            error_count = {err: 0 for err in error_types}
            
            for line in lines:
                for err in error_types:
                    if err in line:
                        error_count[err] += 1
            
            if any(error_count.values()):
                return max(error_count, key=error_count.get)
    except:
        pass
    
    return "시제"

def read_chatgpt_instruction_template():
    """Read ChatGPT instruction template"""
    with open(CHATGPT_INSTRUCTION_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def fill_instruction_template(template, context):
    """Fill the instruction template with context"""
    result = template
    for key, value in context.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result

def escape_html(text):
    """Escape special characters for HTML"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def create_first_message(topic_data, expressions, weak_point):
    """Create the first message"""
    lines = []
    
    # 주제와 상황
    lines.append(f"<b>주제:</b> {escape_html(topic_data['topic'])}")
    lines.append(f"<b>상황:</b> {escape_html(topic_data['situation'])}")
    lines.append("")
    
    # 목표 표현 (가려짐)
    lines.append("<b>목표 표현:</b>")
    for i, (eng, kor) in enumerate(expressions, 1):
        spoiler_eng = f"<tg-spoiler>{escape_html(eng)}</tg-spoiler>"
        lines.append(f"{i}. {escape_html(kor)}")
        lines.append(f"   {spoiler_eng}")
    lines.append("")
    
    # 학습법 안내
    lines.append("<b>학습법:</b>")
    lines.append("1. 다음 메시지 상자 눌러 복사")
    lines.append("2. ChatGPT 새 대화에 붙여 넣고 전송")
    lines.append("3. Ready. 오면 start 보내고 음성 켜기")
    lines.append("4. 끝나면 wrap up 보내기")
    lines.append("5. 나온 교정을 복사해서 이 봇에게 보내기")
    lines.append("")
    
    # 막힐 때 쓸 말
    lines.append("<b>막힐 때:</b>")
    lines.append("• Explain that in Korean?")
    lines.append("• Can you repeat that again?")
    lines.append("• I'm confused.")
    lines.append("")
    
    # 추가 안내
    lines.append("음성 연습 시간이 없으면 오늘은 그냥 채팅으로만 답을 보내세요.")
    
    # 약점 있으면 추가
    if weak_point and weak_point != "시제":
        lines.insert(4, f"<b>다시 보기:</b> {escape_html(weak_point)}")
        lines.insert(5, "")
    
    return "\n".join(lines)

def create_second_message(filled_instruction):
    """Create the second message with instruction"""
    # Escape HTML for code block
    escaped = escape_html(filled_instruction)
    message = f"<pre><code>{escaped}</code></pre>"
    return message

def send_telegram_message(token, chat_id, text, parse_mode="HTML"):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Split if too long (4096 chars for Telegram, but we'll use 4000 to be safe for code blocks)
    chunks = []
    if len(text) > 4000 and "<code>" not in text:
        # Only split if not a code block
        current_chunk = ""
        for line in text.split("\n"):
            if len(current_chunk) + len(line) + 1 > 4000:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += line + "\n"
        if current_chunk:
            chunks.append(current_chunk)
    else:
        chunks = [text]
    
    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": parse_mode
        }
        
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")
        
        # Add delay between messages
        if i < len(chunks) - 1:
            import time
            time.sleep(1)

def main():
    """Main function"""
    # Load environment
    load_env()
    token, chat_id = get_telegram_credentials()
    
    # Select today's topic and data
    topic_data = get_unused_topic()
    expressions = get_three_expressions()
    name = get_random_name()
    weak_point = get_weak_point()
    
    # Save to history
    save_history(topic_data["topic"])
    
    # Create first message
    first_message = create_first_message(topic_data, expressions, weak_point)
    
    # Read instruction template and fill it
    template = read_chatgpt_instruction_template()
    
    context = {
        "내이름": "Taehoon",
        "상대이름": name,
        "서로의관계": "friends having a discussion",
        "상황": topic_data["situation"],
        "주제": topic_data["topic"],
        "레벨": "20",  # You can adjust this
        "오늘의표현": "\n".join([f'"{eng}" (뜻: {kor})' for eng, kor in expressions]),
        "지난주약점": weak_point,
        "날짜": datetime.now().strftime("%Y-%m-%d"),
        "첫대사": topic_data["first_dialogue"]
    }
    
    filled_instruction = fill_instruction_template(template, context)
    second_message = create_second_message(filled_instruction)
    
    # Send messages
    print("Sending first message...")
    send_telegram_message(token, chat_id, first_message, "HTML")
    
    import time
    time.sleep(1)
    
    print("Sending second message...")
    send_telegram_message(token, chat_id, second_message, "HTML")
    
    print("Messages sent successfully!")

if __name__ == "__main__":
    main()
