# mysite/import_csv.py
# Run from the project root (the folder that has manage.py):
#   (.venv) PS> python mysite/import_csv.py

from pathlib import Path
import os
import sys
import csv

# --- Django bootstrap ---
BASE_DIR = Path(__file__).resolve().parents[1]   # folder that has manage.py
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django  # noqa: E402
django.setup()

from django.utils.text import slugify  # noqa: E402
from main.models import Topic, Question, Option  # noqa: E402

# Where is the CSV? -> next to manage.py as "questions.csv"
csv_path = BASE_DIR / "questions.csv"
print("CSV:", csv_path, "exists?", csv_path.exists())
if not csv_path.exists():
    print("❌ CSV not found. Put questions.csv next to manage.py.")
    sys.exit(1)

# Optional: wipe old data so we start clean (dev only)
Option.objects.all().delete()
Question.objects.all().delete()
Topic.objects.all().delete()

created = 0
with csv_path.open(newline="", encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    for row in rdr:
        topic_name = row["topic"].strip()
        difficulty = row["difficulty"].strip().upper()
        text = row["text"].strip()
        opts = [
            row["opt1"].strip(),
            row["opt2"].strip(),
            row["opt3"].strip(),
            row["opt4"].strip(),
        ]
        correct = str(row["correct"]).strip()  # "1".."4"

        topic, _ = Topic.objects.get_or_create(
            name=topic_name,
            defaults={"slug": slugify(topic_name)},
        )
        q = Question.objects.create(topic=topic, difficulty=difficulty, text=text)
        for i, t in enumerate(opts, start=1):
            Option.objects.create(
                question=q,
                text=t,
                is_correct=(str(i) == correct),
            )
        created += 1

print(f"✅ Imported {created} questions.")

# Show counts by topic/difficulty to verify
for t in Topic.objects.order_by("name"):
    counts = {d: Question.objects.filter(topic=t, difficulty=d).count()
              for d in ["EASY", "MEDIUM", "HARD"]}
    print(f"- {t.name} -> {counts}")

