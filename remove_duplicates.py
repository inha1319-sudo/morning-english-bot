import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BOT_FILE = SCRIPT_DIR / "pronunciation_morning_bot.py"

# 파일 읽기
with open(BOT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# EXPRESSIONS_DATA 섹션 추출
match = re.search(r'(EXPRESSIONS_DATA = \[\n)(.*?)(\n\])', content, re.DOTALL)
if not match:
    print("EXPRESSIONS_DATA를 찾을 수 없습니다")
    exit(1)

header = match.group(1)
expressions_text = match.group(2)
footer = match.group(3)

# 각 표현 파싱
lines = expressions_text.split('\n')
seen_expressions = set()
unique_lines = []

for line in lines:
    if line.strip() and line.strip().startswith('("'):
        # 표현명 추출
        expr_match = re.search(r'^\s*\("([^"]+)"', line)
        if expr_match:
            expr = expr_match.group(1)
            if expr not in seen_expressions:
                seen_expressions.add(expr)
                unique_lines.append(line)
            else:
                print(f"중복 제거: {expr}")
    elif line.strip():
        unique_lines.append(line)
    else:
        unique_lines.append(line)

new_expressions_text = '\n'.join(unique_lines)
new_content = content.replace(
    header + expressions_text + footer,
    header + new_expressions_text + footer
)

# 파일 쓰기
with open(BOT_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"완료! {len(seen_expressions)}개 고유 표현 유지")
