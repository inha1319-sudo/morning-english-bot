import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "Be hooked on": "Lately, I'm totally hooked on watching YouTube.",
    "Be obsessed with": "My brother is obsessed with soccer.",
    "Be into": "I'm into movies these days.",
    "Have a thing for": "I have a thing for romantic comedies.",
    "Be a big fan of": "I'm a big fan of Marvel movies.",
    "Not my cup of tea": "Horror movies are not my cup of tea.",
    "It's not my thing": "It's not my thing. I hate bugs and sleeping outside.",
    "Go-to place": "This cafe is my go-to place whenever I need to focus.",
    "Regular haunt": "That pub used to be my regular haunt back in college.",
    "Kill time": "Playing mobile games is the best way to kill time on the subway.",
    "Lose track of time": "It was so fun that I lost track of time while binge-watching them.",
    "Spend quality time": "I spend quality time with my family on weekends.",
    "Vibe": "I really like the vibe of the restaurant.",
    "Cozy atmosphere": "The cafe has a warm and cozy atmosphere.",
    "Hustle and bustle": "I enjoy the hustle and bustle of the traditional market.",
    "Hidden gem": "I found a small bakery which is a hidden gem in my neighborhood.",
    "Hot spot": "Gangnam is a hot spot for nightlife in Seoul.",
    "A must-visit": "If you go to Paris, the Eiffel Tower is a must-visit.",
    "Tourist trap": "That market is a total tourist trap.",
    "Rip-off": "$15 for a coffee? That's a rip-off.",
    "Bang for the buck": "This laptop offers the best bang for the buck.",
    "Reasonable price": "The food was delicious and served at a reasonable price.",
    "User-friendly": "The app is very user-friendly.",
    "State-of-the-art": "The AI technology is state-of-the-art.",
    "Game changer": "Nowadays, AI is a game changer.",
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
