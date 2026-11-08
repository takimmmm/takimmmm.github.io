#!/usr/bin/env python3
"""ينقل أقدم مقال من queue إلى content بتاريخ اليوم، ثم يعيد البناء."""
import os, glob, datetime, subprocess
R = os.path.dirname(os.path.abspath(__file__))
q = sorted(glob.glob(os.path.join(R, "queue", "*.md")))
if not q: print("queue empty"); raise SystemExit(0)
src = q[0]; t = open(src, encoding="utf-8").read()
t = t.replace("date: AUTO", f"date: {datetime.date.today().isoformat()}", 1)
open(os.path.join(R, "content", os.path.basename(src)), "w", encoding="utf-8").write(t)
os.remove(src)
subprocess.run(["python3", os.path.join(R, "build.py")], check=True)
if os.path.isdir(os.path.join(R, ".git")):
    subprocess.run("git add -A && git commit -qm 'daily post' && git push -q", shell=True, cwd=R)
print("published", os.path.basename(src))
