from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from ranking_sim.data.schema import SimStepResult


@dataclass
class MetricsAggregator:
    impressions: int = 0
    clicks: int = 0
    revenue: float = 0.0
    avg_shown: float = 0.0

    # Per-position accumulators
    pos_imps: Dict[int, int] = field(default_factory=dict)          # how many times pos existed
    pos_clicks: Dict[int, int] = field(default_factory=dict)        # clicks at pos
    pos_rev: Dict[int, float] = field(default_factory=dict)         # revenue at pos
    pos_pctr_sum: Dict[int, float] = field(default_factory=dict)    # sum pCTR at pos
    pos_bid_sum: Dict[int, float] = field(default_factory=dict)     # sum bid at pos

    def update(self, step: SimStepResult) -> None:
        self.impressions += 1
        self.clicks += int(step.total_clicks)
        self.revenue += float(step.total_revenue)
        self.avg_shown += float(len(step.shown_ad_ids))

        for s in step.slot_outcomes:
            pos = int(s.position)
            self.pos_imps[pos] = self.pos_imps.get(pos, 0) + 1
            self.pos_clicks[pos] = self.pos_clicks.get(pos, 0) + int(s.clicked)
            self.pos_rev[pos] = self.pos_rev.get(pos, 0.0) + float(s.revenue)
            self.pos_pctr_sum[pos] = self.pos_pctr_sum.get(pos, 0.0) + float(s.pctr)
            self.pos_bid_sum[pos] = self.pos_bid_sum.get(pos, 0.0) + float(s.bid_cpc)

    def finalize(self) -> dict:
        imps = max(1, self.impressions)
        ctr = self.clicks / imps
        ecpm = (self.revenue / imps) * 1000.0

        # Build position-level summary
        pos_summary = {}
        for pos in sorted(self.pos_imps.keys()):
            n = max(1, self.pos_imps[pos])
            pos_ctr = self.pos_clicks.get(pos, 0) / n
            pos_summary[pos] = {
                "imps": self.pos_imps[pos],
                "ctr": pos_ctr,
                "avg_pctr": self.pos_pctr_sum.get(pos, 0.0) / n,
                "avg_bid_cpc": self.pos_bid_sum.get(pos, 0.0) / n,
                "avg_rev_per_imp": self.pos_rev.get(pos, 0.0) / n,
            }

        return {
            "impressions": self.impressions,
            "clicks": self.clicks,
            "ctr": ctr,
            "revenue": self.revenue,
            "ecpm": ecpm,
            "avg_ads_shown": self.avg_shown / imps,
            "pos": pos_summary,  # <- nested dict keyed by position
        }