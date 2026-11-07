"""Seed made-up products into the Redis Cloud free database for the Context Surface.
usage: ../../cloud/01-free-database/.venv/bin/python seed.py     (REDIS_URL from cloud/01-free-database/.env)
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cloud" / "01-free-database"))
from limits import client  # noqa: E402

random.seed(7)
cats = {"lamp": ["desk lamp", "floor lamp", "reading lamp"], "chair": ["office chair", "stool", "armchair"],
        "desk": ["standing desk", "writing desk", "corner desk"], "shelf": ["bookshelf", "wall shelf", "cube shelf"]}
r = client()
n = 0
for cat, names in cats.items():
    for name in names:
        for colour in ("black", "white", "oak"):
            if n >= 30:
                break
            n += 1
            r.hset(f"product:{n:03d}", mapping={"name": f"{colour} {name}", "category": cat, "colour": colour,
                                                 "price": random.choice([29, 49, 79, 99, 149, 199, 299]),
                                                 "stock": random.randint(0, 40)})
print("products:", n, "example:", r.hgetall("product:001"))
