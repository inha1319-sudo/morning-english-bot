import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "Something came up": "I'm sorry, but something came up at work.",
    "My mind went blank": "I was so nervous during the interview that my mind went blank.",
    "On the tip of my tongue": "His name is on the tip of my tongue, but I can't remember.",
    "Screw up": "So I messed up the test.",
    "Mess up": "So I messed up the test.",
    "Fix a problem": "I want to fix this problem.",
    "Sort it out": "I wanna sort it out.",
    "Deal with": "I have to deal with difficult customers every day.",
    "Come up with": "She came up with a brilliant idea for the marketing campaign.",
    "Figure out": "I can't figure out how to use this new coffee machine.",
    "Make it up to you": "I wanna make it up to you.",
    "Ask for a refund": "Can I ask for a refund if I lost a receipt?",
    "Exchange A for B": "I'd like to exchange this T-shirt for a large size.",
    "Run out of": "We ran out of milk.",
    "Out of order": "The elevator is out of order.",
    "In stock": "I want to know if you have any red shirts in stock.",
    "Out of stock": "I want to know if you have any red shirts in stock.",
    "Reschedule": "Can we reschedule the meeting to next week?",
    "At the last minute": "He always cancels at the last minute.",
    "Give me a hand": "Can you give me a hand with these heavy boxes?",
    "Do me a favor": "Can you do me a favor?",
    "I was wondering if you could": "I was wondering if you could help me with my homework.",
    "Play a significant role": "Smartphone plays a significant role in our daily lives.",
    "Have a major impact on": "Global warming is having a major impact on the ecosystem.",
    "Pros and cons": "Living in a big city has pros and cons.",
    "A double-edged sword": "AI technology is a double-edged sword; it is helpful but threatens jobs.",
    "Take something for granted": "We often take our health for granted until we get sick.",
    "Pay attention to": "People are paying more attention to environmental issues these days.",
    "Raise awareness": "We need to raise awareness of the dangers of drunk driving.",
    "Eco-friendly": "Electric cars are becoming popular because they are eco-friendly.",
    "Advancement of technology": "Thanks to the advancement of technology, our lives are much better.",
    "Information overload": "We live in an era of information overload.",
    "Invade privacy": "CCTV cameras help prevent crime but they can invade privacy.",
    "Convenient but dangerous": "Mobile banking is convenient but dangerous if you lose your phone.",
    "Real estate market": "The real estate market is crazy and the house price skyrocketed.",
    "Skyrocket": "The real estate market is crazy and the house price skyrocketed.",
    "Competitive society": "Korea is a highly competitive society.",
    "Freezing job market": "The job market is freezing cold right now.",
    "Generation gap": "I feel a generation gap when I talk to my parents about technology.",
    "Make ends meet": "With the rising cost of living, it is hard to make ends meet.",
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
