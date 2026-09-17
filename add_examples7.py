import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑
EXAMPLES = {
    "Once in a blue moon": "I go to the library once in a blue moon.",
    "A piece of cake": "The exam was a piece of cake.",
    "A walk in the park": "Compared to my last job, this one is a walk in the park.",
    "Cost an arm and a leg": "Buying a house in Seoul costs an arm and a leg.",
    "Break the bank": "You can travel abroad without breaking the bank if you plan.",
    "Save for a rainy day": "My mom always told me to save money for a rainy day.",
    "Hit the books": "I have to hit the books.",
    "Hit the sack": "I'm going to hit the sack early tonight.",
    "Call it a day": "Let's call it a day and go home.",
    "Ring a bell": "The name rings a bell but I can't remember his face.",
    "Play by ear": "Let's just play by ear.",
    "Go with the flow": "I just decided to go with the flow.",
    "Sit on the fence": "Stop sitting on the fence and pick a side.",
    "Cut to the chase": "Let me just cut to the chase and tell you what happened.",
    "Beat around the bush": "Stop beating around the bush and tell me what you want.",
    "Spill the beans": "Who spilled the beans about the surprise party?",
    "Let the cat out of the bag": "I accidentally let the cat out of the bag about her promotion.",
    "Pull someone's leg": "Are you serious or are you pulling my leg?",
    "Under the radar": "I want to keep this project under the radar until finished.",
    "Keep an eye on": "Can you keep an eye on my bag while I go to the restroom?",
    "Give it a shot": "I'll give it a shot.",
    "Get used to": "It took me a while to get used to the spicy food in Korea.",
    "Take advantage of": "You should take the advantage of the free membership.",
    "Look forward to": "I'm looking forward to hearing some positive news from you.",
    "End up": "We planned to go hiking but ended up watching a movie.",
    "Used to": "I used to be slim but I'm not slim anymore.",
    "Be supposed to": "The train was supposed to arrive at 9, but it's late.",
    "Be likely to": "It is likely to rain this afternoon.",
    "Have no choice but to": "I had no choice but to take a taxi.",
    "Can't help": "The baby was so cute that I couldn't help smiling.",
    "Cramped": "My previous studio was so cramped that I could barely move.",
    "Well-ventilated": "It has a large window, so the room is well-ventilated.",
    "Fully furnished": "Is the room fully furnished?",
    "Amenities": "The apartment complex has great amenities including a gym and a library.",
    "Within walking distance": "The gym is within walking distance.",
    "Landlord": "My landlord is very kind and helpful.",
    "Utility bills": "Utility bills are getting higher these days.",
    "Housework": "I try to split the housework with my brother.",
    "Mop the floor": "I just have to mop the floor.",
    "Air out the room": "Open the windows to air out the room.",
    "Dust off": "I need to dust off the bookshelves.",
    "Declutter": "I decided to declutter my room.",
    "Messy": "Sorry, my room is a little bit messy right now.",
    "Spotless": "My mom keeps the house spotless.",
    "Leak": "The ceiling is leaking; I need to call a plumber.",
    "Soundproof": "The walls are not soundproof, so I can hear everything.",
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
