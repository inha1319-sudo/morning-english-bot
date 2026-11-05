import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "All-time favorite": "Inception is my all-time favorite movie.",
    "Plot": "The plot was a bit confusing, but the action was great.",
    "Storyline": "The plot was a bit confusing, but the action was great.",
    "Plot twist": "What I like about the movie was that it had a really crazy plot twist.",
    "Spoiler": "I hate spoilers. They ruin the fun.",
    "Soundtrack": "I like the soundtrack.",
    "Cinematography": "The cinematography was breathtaking.",
    "Acting skills": "His acting skills are top-notch.",
    "Cast": "The movie has a star-studded cast.",
    "Genre": "What is your favorite movie genre? Action or romance?",
    "Catchy": "It's catchy.",
    "Upbeat": "What I like about the movie music is that it has an upbeat rhythm.",
    "Soothing": "Her voice is so soothing that it helps me sleep.",
    "Lyrics": "The lyrics are very touching and relatable.",
    "Sing along": "It was so fun to sing along with the crowd at the concert.",
    "Relatable": "The story was very relatable to people in their 20s.",
    "Live performance": "Their performance is even better than the recording.",
    "Packed with": "The concert venue was packed with fans.",
    "Atmosphere": "The atmosphere at the stadium was absolutely electric.",
    "Goose bumps": "His high notes gave me goose bumps.",
    "Tear-jerker": "The movie is a total tear-jerker.",
    "Action-packed": "If you like action-packed movies, you should watch Mission Impossible.",
    "Thought-provoking": "It was a thought-provoking documentary about climate change.",
    "Online shopping": "I prefer online shopping because it's more convenient.",
    "Browse the internet": "I try to browse the internet until I find the one that I like.",
    "Add to the cart": "I add to my cart and then finally I just place an order.",
    "Place an order": "Finally, I just place an order.",
    "Delivery service": "I get delivery service.",
    "Rocket delivery": "Thanks to rocket delivery, I received the package the next morning.",
    "Try on": "Sometimes I don't like it because I can't try it on.",
    "Fit perfectly": "I can try to find the clothes that fit perfectly.",
    "Too tight": "Sometimes if they are too tight or too loose, I just don't need to buy.",
    "Too loose": "Sometimes if they are too tight or too loose, I just don't need to buy.",
    "Fashion conscious": "Teenagers are very fashion conscious these days.",
    "Impulse buying": "I have a habit of impulse buying when I'm stressed.",
    "Window shopping": "We went window shopping at the department store.",
    "Bargain": "This coat was a real bargain.",
    "On sale": "Is it on sale?",
    "Buy one get one free": "The convenience store has a buy one get one free deal on ice cream.",
    "Refund policy": "Please check the refund policy before purchasing.",
    "Grocery shopping": "I try to buy items in bulk for grocery shopping.",
    "In bulk": "I try to buy items in bulk.",
    "Sold out": "Sometimes when they are sold out, I can just order online.",
    "Limited edition": "I decided to buy the shoes which was a limited edition.",
    "Brand name clothes": "She only wears brand name clothes.",
    "Knock-off": "Be careful not to buy knock-offs online.",
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
