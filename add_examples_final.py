import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑 (마지막 배치)
EXAMPLES = {
    "Smartphone addiction": "Smartphone addiction is a serious problem among teenagers.",
    "Glue to the screen": "Everyone on the subway is glued to the screen of their phones.",
    "Laggy": "My phone is so old that it's laggy.",
    "Frozen screen": "My computer crashed and I'm staring at a frozen screen.",
    "Reboot": "Have you tried rebooting your routers?",
    "Restart": "Have you tried rebooting your routers?",
    "Battery life": "The battery life of this phone is amazing.",
    "Portable charger": "Portable charger is a must-have item for heavy phone users.",
    "Wireless earphones": "Wireless earphones are convenient but easy to lose.",
    "Noise cancelling": "Noise cancelling headphones are great when studying in noisy places.",
    "Social media": "I use social media to keep up with my friends' lives.",
    "Post": "I posted a photo of my lunch on Instagram.",
    "Upload": "How often do you upload videos to your channel?",
    "Leave a comment": "Don't forget to like and leave a comment below.",
    "Viral": "The dance cover became a viral video overnight.",
    "Influencer": "Influencers have a huge impact on marketing trends.",
    "Subscribe": "Please subscribe for more updates.",
    "Stream": "I use Spotify to stream music.",
    "Wi-Fi connection": "The Wi-Fi connection is unstable.",
    "Signal": "I can't hear you well because the signal is weak.",
    "User interface": "The new update has a cleaner user interface.",
    "Security breach": "We need to prevent security breaches.",
    "Hack": "It's scary how hackers can easily hack personal devices.",
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
