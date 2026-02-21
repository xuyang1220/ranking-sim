from __future__ import annotations

import math
from typing import List


def _discount(i: int) -> float:
    # i is 0-based position; rank = i+1
    return 1.0 / math.log2(2.0 + i)


def dcg(rels: List[float], k: int) -> float:
    s = 0.0
    for i, rel in enumerate(rels[:k]):
        # linear gain; stable for rel in [0,1]
        s += float(rel) * _discount(i)
    return s


def ndcg(rels_in_rank_order: List[float], k: int) -> float:
    d = dcg(rels_in_rank_order, k)
    ideal = sorted(rels_in_rank_order, reverse=True)
    id_ = dcg(ideal, k)
    return 0.0 if id_ <= 0.0 else d / id_