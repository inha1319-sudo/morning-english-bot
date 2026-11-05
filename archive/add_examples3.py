import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "To be honest with you": "To be honest with you, I've never been a big fan of hiking.",
    "Frankly speaking": "Frankly speaking, that movie was a total waste of time.",
    "As a matter of fact": "As a matter of fact, I go to the coffee shop almost every single day.",
    "Strictly speaking": "Strictly speaking, tomatoes are fruits, not vegetables.",
    "Speaking of which": "Speaking of which, I've been to Daejeon.",
    "Come to think of it": "Come to think of it, I haven't eaten anything all day.",
    "It just crossed my mind": "A great idea just crossed my mind for our next project.",
    "What I'm trying to say is": "What I'm trying to say is that intonation is really important.",
    "Long story short": "Long story short, I missed the last bus and had to walk home.",
    "For the time being": "I'm staying at my parents' house for the time being.",
    "In the meantime": "In the meantime, I'm trying to record this video.",
    "On top of that": "The hotel room was dirty and on top of that, the air conditioner was broken.",
    "Last but not least": "Last but not least, we need to consider the budget.",
    "Contrary to expectation": "Contrary to expectation, the sequel was actually better.",
    "Interestingly enough": "Interestingly enough, I ran into my teacher at the concert.",
    "Believe it or not": "Believe it or not, if you memorize scripts, you are likely to get NH.",
    "Does that make sense?": "Does that make sense?",
    "Let's put it this way": "Let's put it this way, if I buy this car, I'll be broke.",
    "Don't get me wrong": "Don't get me wrong, studying vocabulary is good.",
    "If I remember correctly": "If I remember correctly, the last time I visited Jeju was 5 years ago.",
    "Correct me if I'm wrong": "Correct me if I'm wrong, but didn't you subscribe to my channel?",
}

# 파일 읽기
with open('pronunciation_morning_bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 각 라인 처리
updated = 0
new_lines = []

for line in lines:
    updated_line = False

    # 각 표현 확인
    for expr, example in EXAMPLES.items():
        # 2-element 형식 찾기: ("표현", "의미"),
        if f'("{expr}",' in line and '"),' in line:
            # 의미 부분을 찾아서 예시문장 추가
            if line.count('"') == 4:  # 2-element
                # 마지막 "), 앞에 예시문장 추가
                new_line = line.rstrip()
                if new_line.endswith('),'):
                    new_line = new_line[:-2] + f', "{example}"),\n'
                    new_lines.append(new_line)
                    updated += 1
                    updated_line = True
                    print(f"✓ {expr}")
                    break

    if not updated_line:
        new_lines.append(line)

# 파일 쓰기
with open('pronunciation_morning_bot.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\n완료! {updated}개 표현 업데이트됨")
