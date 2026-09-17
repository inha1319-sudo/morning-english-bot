import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "Down to earth": "Despite being a famous celebrity, she is very down to earth.",
    "Easy-going": "My boss is pretty easy-going about deadlines.",
    "Outgoing": "My sister is very outgoing and loves meeting new people.",
    "Extroverted": "My sister is very outgoing and loves meeting new people.",
    "Introverted": "I'm quite introverted, so I don't really like crowded places.",
    "Life of the party": "He is always the life of the party; he makes everyone laugh.",
    "People person": "You need to be a people person to work in sales.",
    "Short-tempered": "My boss is so short-tempered.",
    "Picky": "I am such a picky eater and I do not eat any non-Korean food.",
    "Picky eater": "I am such a picky eater and I do not eat any non-Korean food.",
    "Close-knit": "I grew up in a very close-knit family.",
    "Drift apart": "We used to be best friends, but we drifted apart after high school.",
    "Keep in touch": "Let's keep in touch after you move abroad.",
    "Lose touch": "I regret losing touch with my college roommate.",
    "Bump into": "I bumped into my ex-boyfriend at the mall yesterday.",
    "Hit it off": "We hit it off immediately because we both love jazz.",
    "See eye to eye": "My father and I don't see eye to eye on politics.",
    "Have a falling out": "I had a falling out with my friend over money issues.",
    "Make up": "We argued last night, but we made up this morning.",
    "Look up to": "I've always looked up to my mother.",
    "Take after": "I take after my dad in personality.",
    "Role model": "My English teacher is my role model.",
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
