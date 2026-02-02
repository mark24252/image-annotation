import random
from typing import List


CLASSES = ["person", "car", "dog", "cat", "bicycle"]


def fake_predict() -> List[dict]:
    results = []

    for _ in range(random.randint(1, 4)):
        x = random.uniform(0.05, 0.6)
        y = random.uniform(0.05, 0.6)
        w = random.uniform(0.1, 0.3)
        h = random.uniform(0.1, 0.3)

        results.append({
            "bbox": [x, y, w, h],
            "category": random.choice(CLASSES),
            "score": round(random.uniform(0.5, 0.99), 2)
        })

    return results
