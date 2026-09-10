import re
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def _clean_art_num(val):
    if val is None:
        return ""
    digits = re.findall(r'\d+', str(val))
    return digits[0] if digits else str(val).strip()

print("Test 'Điều 15':", _clean_art_num("Điều 15"), "== 15?", _clean_art_num("Điều 15") == "15")
print("Test 15:", _clean_art_num(15), "== 15?", _clean_art_num(15) == "15")
print("Test 'Điều 35':", _clean_art_num("Điều 35"), "== 35?", _clean_art_num("Điều 35") == "35")
print("Test '56':", _clean_art_num(56), "== 56?", _clean_art_num(56) == "56")
