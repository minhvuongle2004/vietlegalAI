import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

path = r"C:\Users\vuong\.gemini\antigravity-ide\brain\d4e19d11-4f9f-41c0-a5d4-f7b6e3367760\.system_generated\steps\15031\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

pos78 = text.find('name="dieu_78"')
print("pos78:", pos78)
print("Text around Điều 78:\n", text[pos78:pos78+1500])

# Search for any "Phụ lục" in entire text
all_pl = re.findall(r'((?:PHỤ LỤC|Phụ lục|Mẫu số)\s+[^\n<]+)', text)
print(f"\nAll Phụ lục / Mẫu số mentions: {len(all_pl)}")
for p in set(all_pl[:20]):
    print(" ", p[:100])
