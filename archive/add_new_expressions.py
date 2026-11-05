import sys
sys.stdout.reconfigure(encoding="utf-8")

# 새로 추가할 표현들
NEW_EXPRESSIONS = [
    ("Smartphone addiction", "스마트폰 중독", "Smartphone addiction is a serious problem among teenagers."),
    ("Glue to the screen", "화면에 눈을 떼지 못하는", "Everyone on the subway is glued to the screen of their phones."),
    ("Laggy", "렉 걸리는, 버벅거리는", "My phone is so old that it's laggy."),
    ("Frozen screen", "멈춘 화면", "My computer crashed and I'm staring at a frozen screen."),
    ("Reboot", "재부팅하다", "Have you tried rebooting your routers?"),
    ("Restart", "재시작하다", "Have you tried rebooting your routers?"),
    ("Battery life", "배터리 수명", "The battery life of this phone is amazing."),
    ("Portable charger", "보조 배터리", "Portable charger is a must-have item for heavy phone users."),
    ("Wireless earphones", "무선 이어폰", "Wireless earphones are convenient but easy to lose."),
    ("Noise cancelling", "소음 제거", "Noise cancelling headphones are great when studying in noisy places."),
    ("Social media", "소셜 미디어", "I use social media to keep up with my friends' lives."),
    ("Post", "게시하다/올리다", "I posted a photo of my lunch on Instagram."),
    ("Upload", "올리다", "How often do you upload videos to your channel?"),
    ("Leave a comment", "댓글을 남기다", "Don't forget to like and leave a comment below."),
    ("Viral", "화제가 된, 떡상한", "The dance cover became a viral video overnight."),
    ("Influencer", "인플루언서", "Influencers have a huge impact on marketing trends."),
    ("Subscribe", "구독하다", "Please subscribe for more updates."),
    ("Stream", "스트리밍하다", "I use Spotify to stream music."),
    ("Wi-Fi connection", "와이파이 연결", "The Wi-Fi connection is unstable."),
    ("Signal", "신호", "I can't hear you well because the signal is weak."),
    ("User interface", "사용자 환경/UI", "The new update has a cleaner user interface."),
    ("Security breach", "보안 침해", "We need to prevent security breaches."),
    ("Hack", "해킹하다", "It's scary how hackers can easily hack personal devices."),
]

# 파일 읽기
with open('pronunciation_morning_bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# EXPRESSIONS_DATA = [ 찾기
start_idx = -1
for i, line in enumerate(lines):
    if 'EXPRESSIONS_DATA = [' in line:
        start_idx = i
        break

# 배열 끝 ] 찾기
end_idx = -1
for i in range(start_idx + 1, len(lines)):
    if lines[i].strip() == ']':
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # 새 항목들 생성
    added = 0
    new_lines_to_add = []

    for expr, meaning, example in NEW_EXPRESSIONS:
        # 이미 파일에 있는지 확인
        exists = any(f'("{expr}",' in line for line in lines)
        if not exists:
            new_lines_to_add.append(f'    ("{expr}", "{meaning}", "{example}"),\n')
            added += 1
            print(f"✓ {expr}")

    # 배열 끝 바로 전에 추가
    new_lines = lines[:end_idx] + new_lines_to_add + lines[end_idx:]

    # 파일 쓰기
    with open('pronunciation_morning_bot.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"\n완료! {added}개 표현 추가됨")
else:
    print("배열을 찾을 수 없습니다!")
