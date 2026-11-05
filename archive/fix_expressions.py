import re

with open('pronunciation_morning_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 모든 2-element tuple을 3-element로 변환
# ("expr", "meaning"), → ("expr", "meaning", ""),
# 이 방법은 라인 단위로 변환

lines = content.split('\n')
new_lines = []

for line in lines:
    # 2-element tuple 패턴: ("...", "..."),
    # 3-element tuple은 이미 ("...", "...", "..."),

    # 간단한 패턴 매칭: 따옴표 4개가 있고 , ), 로 끝나는 줄
    if re.match(r'^\s*\("[^"]+",\s*"[^"]*"\),\s*$', line):
        # 이것은 2-element tuple
        # ), 를 ), ""), 로 변경
        line = line.rstrip(',').rstrip() + ', ""),'

    new_lines.append(line)

new_content = '\n'.join(new_lines)

with open('pronunciation_morning_bot.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("변환 완료!")
