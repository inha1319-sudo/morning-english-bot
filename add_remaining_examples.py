import sys
sys.stdout.reconfigure(encoding="utf-8")

# 남은 42개 표현의 예문 (자동 생성)
EXAMPLES = {
    "In a nutshell": "In a nutshell, the project was a success.",
    "You know what I mean?": "You know what I mean? It's really frustrating.",
    "Honestly": "Honestly, I don't know what to do.",
    "Actually": "Actually, I changed my mind.",
    "Party pooper": "Don't be a party pooper; come and have fun.",
    "Slipped my mind": "I'm sorry, it completely slipped my mind.",
    "Second-hand": "I bought a second-hand car to save money.",
    "Postpone": "Let's postpone the meeting to next week.",
    "Cutting-edge": "The technology is cutting-edge.",
    "Identity theft": "Identity theft is a serious crime.",
    "Global warming": "Global warming is affecting our planet.",
    "Climate change": "Climate change is a major concern.",
    "Separate trash": "We need to separate trash for recycling.",
    "Recycling": "Recycling helps the environment.",
    "Break a leg": "Break a leg! You'll do great on stage!",
    "Renovate": "We're going to renovate the house next year.",
    "Remodel": "They decided to remodel the kitchen.",
    "Spacious": "The apartment is very spacious and bright.",
    "Roomy": "The car has a roomy interior.",
    "Studio apartment": "I rented a studio apartment in the city.",
    "Residential area": "This is a quiet residential area.",
    "Waterproof": "The bag is waterproof so your stuff won't get wet.",
    "Monthly rent": "The monthly rent is expensive in this area.",
    "Lease contract": "I signed a lease contract for one year.",
    "Move in": "I'm moving in next week.",
    "Move out": "I have to move out by the end of the month.",
    "Maintenance fee": "The maintenance fee is included in the rent.",
    "Floor noise": "There's too much floor noise from upstairs.",
    "Chores": "I have to do my chores every day.",
    "Vacuum the floor": "I need to vacuum the floor this weekend.",
    "Mold": "There's mold in the bathroom.",
    "Director": "The director made a great film.",
    "Touching": "The movie was very touching and emotional.",
    "Concert venue": "The concert venue was packed with fans.",
    "Electric": "The atmosphere at the stadium was electric.",
    "Top-notch": "The service at the restaurant was top-notch.",
    "Trendsetter": "She's a trendsetter in the fashion industry.",
    "Steal": "This coat is a real steal for the price.",
    "For sale": "The house is for sale at a good price.",
    "BOGO": "The store is having a BOGO deal this week.",
    "Receipt": "Don't forget to keep your receipt for the warranty.",
    "Customer service": "The customer service was excellent.",
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
