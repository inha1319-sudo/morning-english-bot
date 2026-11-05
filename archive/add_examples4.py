import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "Be a creature of habit": "I'm a creature of habit so I always order the same coffee every morning.",
    "Morning person": "I'm definitely not a morning person.",
    "Night owl": "I'm a night owl. I focus better at late at night when it's quiet.",
    "Have a hectic schedule": "I have a hectic schedule this week.",
    "Be packed with": "My day is packed with meetings from 9 to 6.",
    "Squeeze in": "I try to squeeze in workout during my lunch break.",
    "Procrastinate": "I always procrastinate.",
    "Pull an all-nighter": "I had to pull an all-nighter to finish the report on time.",
    "Burn the midnight oil": "Students are burning the midnight oil for the final exams.",
    "Cram for an exam": "I spent all night cramming for the history exam.",
    "Pass with flying colors": "You will pass the interview with flying colors.",
    "Slacker": "He is such a slacker.",
    "Couch potato": "On Sundays I turn into a couch potato and watch Netflix all day.",
    "Lead a sedentary lifestyle": "More people have a sedentary lifestyle which is bad for health.",
    "Get back in shape": "I joined the gym to get back in shape before summer comes.",
    "Work out": "I try to work out at least three times a week to stay healthy.",
    "Eat a balanced diet": "It's important to maintain a balanced diet for your health.",
    "Call in sick": "I felt terrible this morning, so I called in sick.",
    "Feel under the weather": "I'm feeling a bit under the weather today.",
    "Come down with the flu": "I think I'm coming down with the flu.",
    "Recover from": "It took a week to fully recover from the surgery.",
    "Keep up with": "Fashion trends, they change so fast. So hard to keep up with.",
    "Fall behind": "If you skip classes, you will fall behind quickly.",
    "Struggle with": "I'm currently struggling with back pain from sitting too long.",
    "Get the hang of it": "Driving was hard at first, but now I'm getting the hang of it.",
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
