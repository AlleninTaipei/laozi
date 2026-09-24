import re, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(__file__).resolve().parent.parent / ".claude" / "skills" / "laozi"
src = (root/"references"/"daodejing.md").read_text(encoding="utf-8")
chap = {}
cur = None
for line in src.splitlines():
    m = re.match(r"^## (第.+章)$", line)
    if m: cur = m.group(1); continue
    if cur and line.startswith("> "): chap[cur] = line[2:]
alltext = "\n".join(chap.values())
errors = []
FW = "，。：；？！、「」"
def check(q, ch, where):
    if ch:
        if ch not in chap: errors.append(f"{where}: unknown chapter {ch}"); return
        if q not in chap[ch]: errors.append(f"{where}: not in {ch}: {q}")
    elif q not in alltext: errors.append(f"{where}: not in source: {q}")
files = ["SKILL.md","references/mental-models.md","references/situations.md","references/examples.md","references/eval-cases.md"]
quotes = 0
for f in files:
    lines = (root/f).read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        where = f"{f}:{i+1}"
        if line.startswith("> "):
            q = line[2:]
            m = re.search(r"\s*\((第.+?章)\)\s*$", q)
            ch = None
            if m: ch = m.group(1); q = q[:m.start()]
            else:
                for nxt in lines[i+1:i+8]:
                    mm = re.search(r"(?:章次|出處): (第.+?章)", nxt)
                    if mm: ch = mm.group(1); break
            check(q, ch, where); quotes += 1
            continue
        for q in re.findall(r'"([^"]+)"', line):
            if any(c in FW for c in q):
                mm = re.search(r'"'+re.escape(q)+r'"\s*\((第.+?章)\)', line)
                check(q, mm.group(1) if mm else None, where); quotes += 1
        stripped = re.sub(r'"[^"]*"', "", line)
        stripped = re.sub(r"`[^`]*`", "", stripped)
        bad = [c for c in stripped if c in FW] + (["**"] if "**" in stripped else []) + (["——"] if "——" in stripped else [])
        if bad: errors.append(f"{where}: style {bad}: {line}")
sit = (root/"references"/"situations.md").read_text(encoding="utf-8")
cats = re.findall(r"^### (\S+)-\d+$", sit, re.M)
from collections import Counter
c = Counter(cats)
print("quotes checked:", quotes)
print("situations:", len(cats), dict(c))
print("\n".join(errors) if errors else "no errors")
