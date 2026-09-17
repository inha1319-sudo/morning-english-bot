import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "Be on cloud nine": "When I got the job offer, I was literally on cloud nine.",
    "Over the moon": "My sister was over the moon when she found out she was pregnant.",
    "Feel blue": "I usually feel blue on rainy days.",
    "Be burned out": "After working on the project for months without a break, I was completely burned out.",
    "Drive me crazy": "You are driving me crazy.",
    "Get on my nerves": "It really gets on my nerves when people talk loudly in the library.",
    "Freak out": "I totally freaked out when I saw a huge cockroach in my room.",
    "Have butterflies in my stomach": "I always have butterflies in my stomach before a big presentation.",
    "Be scared to death": "I was scared to death.",
    "That's a bummer": "The concert was canceled due to heavy rain. It was such a bummer.",
    "Let someone down": "I don't wanna let my parents down.",
    "Make one's day": "Your subscription really made my day.",
    "Blow off some steam": "I usually go to the karaoke to blow off some steam.",
    "Chill out": "On weekends I just want to stay home, watch Netflix, and chill out.",
    "Recharge my battery": "My dog helps me recharge my battery.",
    "Feel refreshed": "A walk in the park made me feel refreshed and energized.",
    "Mixed feelings": "I had mixed feelings about graduating from college.",
    "Torn between A and B": "I was torn between buying a laptop and a tablet.",
    "Second to none": "When it comes to fried chicken, Korea is second to none.",
    "Out of this world": "The steak at the restaurant was out of this world.",
    "Breathtaking": "The night view of Seoul from Namsan Tower is breathtaking.",
    "Mind-blowing": "The special effects in the movie were absolutely mind-blowing.",
    "Mediocre": "Honestly, the food was mediocre.",
    "Tedious": "The lecture was so tedious that I almost fell asleep.",
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
