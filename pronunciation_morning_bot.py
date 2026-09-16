import os
import sys
import json
import random
from datetime import datetime
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
CHATGPT_INSTRUCTION_FILE = SCRIPT_DIR / "ChatGPT발음지시문.md"

# 목표 표현 데이터 (기존 표현들 재사용)
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
    ("All-time favorite", "역대 최고로 좋아하는"),
    ("Plot", "줄거리"),
    ("Storyline", "줄거리"),
    ("Plot twist", "(줄거리가 꼬인) 반전"),
    ("Spoiler", "스포일러 (내용 유출)"),
    ("Cinematography", "영상미, 촬영 기법"),
    ("Cast", "출연진"),
    ("Director", "감독"),
    ("Genre", "장르"),
    ("Action-packed", "액션이 가득한"),
    ("Tear-jerker", "눈물을 쏙 빼놓는 영화/노래"),
    ("Thought-provoking", "시사하는 바가 큰, 생각하게 만드는"),
    ("Soundtrack", "사운드트랙"),
    ("Catchy", "귀에 맴도는, 중독성 있는"),
    ("Upbeat", "경쾌한, 빠른 리듬의"),
    ("Soothing", "마음을 진정시키는, 편안한"),
    ("Lyrics", "가사"),
    ("Touching", "감동적인"),
    ("Relatable", "공감 가는"),
    ("Sing along", "따라 부르다, 떼창하다"),
    ("Live performance", "라이브 공연"),
    ("Concert venue", "공연장"),
    ("Packed with", "~로 꽉 찬"),
    ("Atmosphere", "분위기"),
    ("Electric", "(분위기가) 열광적인, 짜릿한"),
    ("Goose bumps", "닭살, 소름"),
    ("Second to none", "누구에게도 뒤지지 않는, 최고인"),
    ("Top-notch", "최고의, 일류의"),
    ("Online shopping", "온라인 쇼핑"),
    ("Browse the internet", "인터넷을 구경하다/둘러보다"),
    ("Add to the cart", "장바구니에 담다"),
    ("Place an order", "주문하다"),
    ("Delivery service", "배송 서비스"),
    ("Rocket delivery", "로켓 배송"),
    ("Try on", "(옷 등을) 입어보다"),
    ("Fit perfectly", "딱 맞다"),
    ("Too tight", "너무 꽉 끼는"),
    ("Too loose", "너무 헐렁한"),
    ("Fashion conscious", "패션에 민감한"),
    ("Trendsetter", "유행을 선도하는 사람"),
    ("Impulse buying", "충동구매"),
    ("Window shopping", "아이쇼핑"),
    ("Bargain", "흥정(한 물건), 득템"),
    ("Steal", "거저 얻은 것"),
    ("On sale", "세일 중인"),
    ("For sale", "판매용인"),
    ("Buy one get one free", "1+1 행사"),
    ("BOGO", "Buy One Get One free 약자"),
    ("Refund policy", "환불 정책"),
    ("Receipt", "영수증"),
    ("Customer service", "고객 서비스"),
    ("Grocery shopping", "장보기"),
    ("In bulk", "대량으로"),
    ("Sold out", "매진된"),
    ("Limited edition", "한정판"),
    ("Brand name clothes", "유명 브랜드 옷"),
    ("Knock-off", "짝퉁/모조품"),
]

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

def get_five_expressions():
    """Get 5 random expressions"""
    return random.sample(EXPRESSIONS_DATA, 5)

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
    """Escape HTML special characters"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def create_message(expressions):
    """Create the message with expressions"""
    lines = []

    lines.append("<b>오늘의 발음 연습 표현 5개</b>")
    lines.append("")

    for i, (eng, kor) in enumerate(expressions, 1):
        lines.append(f"{i}. {escape_html(eng)}")
        lines.append(f"   뜻: {escape_html(kor)}")

    lines.append("")
    lines.append("<b>학습법:</b>")
    lines.append("1. 다음 메시지 상자 눌러 복사")
    lines.append("2. ChatGPT 새 대화에 붙여 넣고 전송")
    lines.append("3. Ready. 오면 start 보내고 음성 켜기")
    lines.append("4. 각 표현마다 여러 번 따라 말하기")
    lines.append("5. 끝나면 wrap up 보내기")
    lines.append("6. 나온 피드백을 복사해서 이 봇에게 보내기")

    return "\n".join(lines)

def send_telegram_message(token, chat_id, text, parse_mode="HTML"):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    chunks = []
    if len(text) > 4000 and "<code>" not in text:
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

        if i < len(chunks) - 1:
            import time
            time.sleep(1)

def main():
    """Main function"""
    load_env()
    token, chat_id = get_telegram_credentials()

    # Select 5 random expressions
    expressions = get_five_expressions()

    # Create main message
    main_message = create_message(expressions)
    send_telegram_message(token, chat_id, main_message)

    # Create ChatGPT instruction message
    template = read_chatgpt_instruction_template()

    # Format expressions for template
    expr_lines = []
    for eng, kor in expressions:
        expr_lines.append(f"• {eng} = {kor}")
    expr_text = "\n".join(expr_lines)

    context = {
        "내이름": "Me",
        "상대이름": "Your English Pronunciation Coach",
        "표현5개": expr_text
    }

    filled_instruction = fill_instruction_template(template, context)
    escaped = escape_html(filled_instruction)
    instruction_message = f"<pre><code>{escaped}</code></pre>"

    send_telegram_message(token, chat_id, instruction_message, "HTML")

    print(f"Sent pronunciation practice for {len(expressions)} expressions")

if __name__ == "__main__":
    main()
