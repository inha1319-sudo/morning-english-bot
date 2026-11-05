import sys
sys.stdout.reconfigure(encoding="utf-8")

# 예시문장 매핑 (마지막 배치)
EXAMPLES = {
    "Take a stroll": "I like to take a stroll along the river after dinner.",
    "Jogging trail": "There is a well-maintained jogging trail in the park.",
    "Fresh air": "I went outside to get some fresh air.",
    "Greenery": "Looking at the greenery helps me relax my eyes.",
    "Bench": "We sat on a bench and watched people passing by.",
    "Fountain": "Kids love playing in the water at the fountain.",
    "Playground": "I used to play at the playground until the sunset when I was young.",
    "Walk my dog": "My daily routine includes walking my dog in the morning.",
    "On a leash": "In a public park, you must keep your dog on a leash.",
    "Enjoy the breeze": "We sat by the river to enjoy the cool breeze.",
    "Cherry blossoms": "The park is famous for beautiful cherry blossoms in spring.",
    "Foliage": "The foliage in the mountain is breathtaking.",
    "Picnic": "We packed some sandwiches for a picnic.",
    "Ride a bike": "I learned how to ride a bike when I was seven.",
    "Han River Park": "My go-to place for jogging is Han River Park.",
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
