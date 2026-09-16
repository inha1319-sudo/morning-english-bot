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
# YouTube 쉐도잉 표현들
EXPRESSIONS_DATA = [
    ("To be honest with you", "솔직히 말해서"),
    ("As a matter of fact", "사실은"),
    ("Speaking of which", "말이 나와서 말인데"),
    ("Come to think of it", "생각해 보니"),
    ("What I'm trying to say is", "내 말의 요점은"),
    ("Long story short", "한마디로 줄이자면"),
    ("In a nutshell", "요약하자면"),
    ("On top of that", "게다가"),
    ("Last but not least", "마지막으로 중요한 건"),
    ("Don't get me wrong", "오해하지 마"),
    ("Strictly speaking", "엄격히 말하자면"),
    ("It just crossed my mind", "방금 떠오른 건데"),
    ("For the time being", "당분간은"),
    ("In the meantime", "그 사이에"),
    ("Contrary to expectation", "기대와 달리"),
    ("Interestingly enough", "흥미롭게도"),
    ("Believe it or not", "믿거나 말거나"),
    ("You know what I mean?", "무슨 말인지 알지?"),
    ("Does that make sense?", "이해가 돼?"),
    ("Let's put it this way", "이렇게 말해볼게"),
    ("If I remember correctly", "내 기억이 맞다면"),
    ("Correct me if I'm wrong", "내가 틀렸을 수도 있지만"),
    ("Honestly", "정직하게/솔직히"),
    ("Actually", "사실은"),
    ("Take a stroll", "산책하다"),
    ("Jogging trail", "조깅 코스/산책로"),
    ("Fresh air", "신선한 공기"),
    ("Greenery", "녹지/초록 식물"),
    ("Bench", "벤치"),
    ("Fountain", "분수대"),
    ("Playground", "놀이터"),
    ("Walk my dog", "개를 산책시키다"),
    ("Enjoy the breeze", "산들바람을 즐기다"),
    ("Cherry blossoms", "벚꽃"),
    ("Foliage", "단풍"),
    ("Picnic", "소풍"),
    ("Ride a bike", "자전거를 타다"),
    ("Be on cloud nine", "기분이 날아갈 듯이 매우 좋을 때"),
    ("Over the moon", "세상을 다 가진 것처럼 기쁠 때"),
    ("Make one's day", "하루를 기분 좋게 만들었을 때"),
    ("Feel blue", "우울하거나 기분이 처질 때"),
    ("Be burned out", "완전히 지치거나 방전되었을 때"),
    ("That's a bummer", "아쉽거나 실망스러울 때"),
    ("Let someone down", "누군가를 실망시켰을 때"),
    ("Drive me crazy", "나를 미치게 만들 때"),
    ("Get on my nerves", "신경을 긁거나 거슬릴 때"),
    ("Freak out", "기겁하거나 멘붕이 올 때"),
    ("Blow off some steam", "화나 스트레스를 풀 때"),
    ("Have butterflies in my stomach", "긴장되거나 설렐 때"),
    ("Be scared to death", "무서워 죽을 것 같을 때"),
    ("Chill out", "느긋하게 쉴 때"),
    ("Recharge my battery", "재충전할 때"),
    ("Feel refreshed", "상쾌하고 개운할 때"),
    ("Mixed feelings", "시원섭섭하거나 만감이 교차할 때"),
    ("Torn between A and B", "결정하기 힘들거나 고민될 때"),
    ("Second to none", "최고이거나 둘째가라면 서러울 때"),
    ("Out of this world", "환상적이거나 세상 맛이 아닐 때"),
    ("Breathtaking", "숨 막히게 아름다울 때"),
    ("Mind-blowing", "충격적으로 멋지거나 놀라울 때"),
    ("Mediocre", "그저 그렇거나 2% 부족할 때"),
    ("Tedious", "지루하고 따분할 때"),
    ("Be hooked on", "~에 푹 빠지다/꽂히다"),
    ("Be obsessed with", "~에 미치도록 좋아하다/집착하다"),
    ("Be into", "~에 관심이 있다/푹 빠져 있다"),
    ("Have a thing for", "~를 특별히 좋아하다/취향이다"),
    ("Be a big fan of", "~의 광팬이다"),
    ("Not my cup of tea", "내 취향이 아니다"),
    ("It's not my thing", "내 스타일이 아니다"),
    ("Go-to place", "단골집/자주 가는 곳"),
    ("Regular haunt", "아지트/자주 출몰하는 곳"),
    ("Kill time", "시간 때우기"),
    ("Lose track of time", "시간 가는 줄 모르다"),
    ("Spend quality time", "오붓하고 알찬 시간 보내기"),
    ("Vibe", "분위기/느낌"),
    ("Cozy atmosphere", "아늑한 분위기"),
    ("Hustle and bustle", "도시의 북적거림/활기참"),
    ("Hidden gem", "숨겨진 명소"),
    ("Hot spot", "핫플레이스/인기 있는 곳"),
    ("A must-visit", "꼭 가봐야 할 곳"),
    ("Tourist trap", "바가지 씌우는 관광지"),
    ("Rip-off", "바가지/너무 비싼 것"),
    ("Bang for the buck", "가성비 최고"),
    ("Reasonable price", "합리적인 가격"),
    ("User-friendly", "사용하기 편한"),
    ("State-of-the-art", "최첨단의"),
    ("Game changer", "판도를 바꾸는 것/혁신"),
    ("Be a creature of habit", "늘 하던 대로 하는 사람"),
    ("Morning person", "아침형 인간"),
    ("Night owl", "올빼미족"),
    ("Have a hectic schedule", "눈코 뜰 새 없이 바쁜 일정"),
    ("Be packed with", "스케줄이 꽉 찬/붐비는"),
    ("Squeeze in", "짬을 내서 ~하다"),
    ("Procrastinate", "할 일을 미루다/늑장 부리다"),
    ("Pull an all-nighter", "밤을 새우다"),
    ("Burn the midnight oil", "밤늦게까지 공부/일하다"),
    ("Cram for an exam", "벼락치기 하다"),
    ("Pass with flying colors", "우수한 성적으로 통과하다"),
    ("Slacker", "게으름뱅이/농땡이"),
    ("Couch potato", "소파와 한 몸이 되어 TV만 보는 사람"),
    ("Lead a sedentary lifestyle", "주로 앉아서 생활하다"),
    ("Get back in shape", "몸을 다시 만들다/건강을 되찾다"),
    ("Work out", "운동하다"),
    ("Eat a balanced diet", "균형 잡힌 식사를 하다"),
    ("Call in sick", "아파서 결근/병가 내다"),
    ("Feel under the weather", "컨디션이 안 좋은"),
    ("Come down with the flu", "감기/독감 기운이 있다"),
    ("Recover from", "~로부터 회복하다"),
    ("Keep up with", "~을 따라잡다/유행을 쫓다"),
    ("Fall behind", "뒤처지다"),
    ("Struggle with", "고생하다/애먹다"),
    ("Get the hang of it", "요령을 터득하다/감을 잡다"),
    ("Down to earth", "털털하고 현실적인, 허세가 없는 성격"),
    ("Easy-going", "느긋하고 성격이 좋은, 까탈스럽지 않은"),
    ("Outgoing", "외향적이고 사교적인"),
    ("Extroverted", "외향적이고 사교적인"),
    ("Introverted", "내향적이고 내성적인"),
    ("Life of the party", "분위기 메이커"),
    ("Party pooper", "분위기를 망치는 사람"),
    ("People person", "사람을 좋아하고 사교적인 사람"),
    ("Short-tempered", "다혈질인, 성격이 급한"),
    ("Picky", "까탈스러운, 편식이 심한"),
    ("Picky eater", "편식이 심한 사람"),
    ("Close-knit", "사이가 끈끈하고 가까운"),
    ("Drift apart", "사이가 멀어지다, 소원해지다"),
    ("Keep in touch", "연락하고 지내다"),
    ("Lose touch", "연락이 끊기다"),
    ("Bump into", "우연히 마주치다"),
    ("Hit it off", "죽이 잘 맞다, 금방 친해지다"),
    ("See eye to eye", "의견이 일치하다"),
    ("Have a falling out", "다투다, 사이가 틀어지다"),
    ("Make up", "화해하다"),
    ("Look up to", "존경하다"),
    ("Take after", "성격 등을 닮다"),
    ("Role model", "롤모델"),
    ("Something came up", "갑자기 일이 생기다"),
    ("Slipped my mind", "깜빡 잊어버리다"),
    ("My mind went blank", "머릿속이 하얘지다"),
    ("On the tip of my tongue", "입가에서 맴돌다"),
    ("Screw up", "망치다"),
    ("Mess up", "망치다"),
    ("Fix a problem", "문제를 해결하다"),
    ("Sort it out", "문제를 해결하다/정리하다"),
    ("Deal with", "다루다, 처리하다"),
    ("Come up with", "아이디어를 생각해내다"),
    ("Figure out", "이해하다, 알아내다"),
    ("Make it up to you", "미안한 마음을 보상하다/만회하다"),
    ("Ask for a refund", "환불을 요청하다"),
    ("Exchange A for B", "A를 B로 교환하다"),
    ("Run out of", "~이 다 떨어지다/고갈되다"),
    ("Out of order", "고장 난"),
    ("Second-hand", "중고의"),
    ("In stock", "재고가 있는"),
    ("Out of stock", "품절된"),
    ("Reschedule", "일정을 변경하다"),
    ("Postpone", "미루다"),
    ("At the last minute", "막판에, 마지막 순간에"),
    ("Give me a hand", "도와주다"),
    ("Do me a favor", "부탁을 하나 들어주다"),
    ("I was wondering if you could", "~해주실 수 있는지 궁금합니다"),
    ("Play a significant role", "중요한 역할을 하다"),
    ("Have a major impact on", "~에 큰 영향을 미치다"),
    ("Pros and cons", "장단점"),
    ("A double-edged sword", "양날의 검"),
    ("Take something for granted", "~을 당연하게 여기다"),
    ("Pay attention to", "~에 주의를 기울이다"),
    ("Raise awareness", "경각심을 높이다"),
    ("Eco-friendly", "친환경적인"),
    ("Advancement of technology", "기술의 발전"),
    ("Cutting-edge", "최첨단의"),
    ("Information overload", "정보 과부하"),
    ("Invade privacy", "사생활을 침해하다"),
    ("Identity theft", "명의 도용"),
    ("Convenient but dangerous", "편리하지만 위험한"),
    ("Global warming", "지구 온난화"),
    ("Climate change", "기후 변화"),
    ("Separate trash", "분리수거"),
    ("Recycling", "재활용"),
    ("Real estate market", "부동산 시장"),
    ("Skyrocket", "가격 등이 폭등하다"),
    ("Competitive society", "경쟁 사회"),
    ("Freezing job market", "얼어붙은 취업 시장"),
    ("Generation gap", "세대 차이"),
    ("Make ends meet", "근근이 먹고살다/수지를 맞추다"),
    ("Once in a blue moon", "가뭄에 콩 나듯이, 아주 가끔"),
    ("A piece of cake", "식은 죽 먹기, 아주 쉬운 일"),
    ("A walk in the park", "누워서 떡 먹기, 매우 쉬운 일"),
    ("Cost an arm and a leg", "등골이 휠 정도로 비싸다"),
    ("Break the bank", "파산할 정도로 비싸다, 큰돈이 들다"),
    ("Save for a rainy day", "만약을 위해 저축하다"),
    ("Hit the books", "공부하다"),
    ("Hit the sack", "자러 가다"),
    ("Call it a day", "오늘 일과를 마치다, 퇴근하다"),
    ("Ring a bell", "들어본 적 있다, 낯이 익다"),
    ("Play by ear", "상황 봐서 하다, 임기응변하다"),
    ("Go with the flow", "대세를 따르다"),
    ("Sit on the fence", "결정을 못 내리고 관망하다"),
    ("Cut to the chase", "본론으로 들어가다"),
    ("Beat around the bush", "빙빙 돌려 말하다"),
    ("Spill the beans", "비밀을 누설하다"),
    ("Let the cat out of the bag", "무심코 비밀을 말하다"),
    ("Pull someone's leg", "놀리다, 농담하다"),
    ("Break a leg", "공연 전 행운을 빌어"),
    ("Under the radar", "눈에 띄지 않게 조용히"),
    ("Keep an eye on", "주시하다, 봐주다"),
    ("Give it a shot", "한 번 시도해 보다"),
    ("Get used to", "~에 익숙해지다"),
    ("Take advantage of", "~을 잘 활용하다"),
    ("Look forward to", "~을 고대하다, 기대하다"),
    ("End up", "결국 ~하게 되다"),
    ("Used to", "~하곤 했다"),
    ("Be supposed to", "~하기로 되어 있다"),
    ("Be likely to", "~할 것 같다"),
    ("Have no choice but to", "~할 수밖에 없다"),
    ("Can't help", "~하지 않을 수 없다"),
    ("Renovate", "리노베이트 - 소규모 개조"),
    ("Remodel", "리모델 - 큰 규모의 개조"),
    ("Spacious", "넓은"),
    ("Roomy", "넓은"),
    ("Cramped", "매우 좁고 답답한"),
    ("Well-ventilated", "환기가 잘 되는"),
    ("Studio apartment", "원룸"),
    ("Fully furnished", "가구가 모두 갖춰진"),
    ("Amenities", "편의 시설"),
    ("Within walking distance", "걸어서 갈 수 있는 거리"),
    ("Residential area", "주거 지역"),
    ("Soundproof", "방음이 되는"),
    ("Waterproof", "방수가 되는"),
    ("Monthly rent", "월세"),
    ("Landlord", "집주인"),
    ("Lease contract", "임대 계약서"),
    ("Move in", "이사 들어오다"),
    ("Move out", "이사 나가다"),
    ("Utility bills", "공과금"),
    ("Maintenance fee", "관리비"),
    ("Floor noise", "층간 소음"),
    ("Housework", "집안일"),
    ("Chores", "집안일"),
    ("Mop the floor", "바닥을 대걸레질하다"),
    ("Vacuum the floor", "청소기를 돌리다"),
    ("Air out the room", "환기하다"),
    ("Dust off", "먼지를 털다"),
    ("Declutter", "잡동사니를 정리하다/처분하다"),
    ("Messy", "지저분한"),
    ("Spotless", "티끌 하나 없이 깨끗한"),
    ("Mold", "곰팡이"),
    ("Leak", "물이 새다"),
]

# 주제 데이터 (OPIC 준비용: 일상 주제만)
TOPICS_DATA = [
    # === 일상 주제 (OPIC 스피킹 준비) ===
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
