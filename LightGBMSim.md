# Ranking Simulation with Real pCTR Model (LightGBM)

This project implements an **offline ads ranking simulator** that integrates a **real pCTR model (LightGBM)** with a **multi-slot ranking environment**, position bias, revenue modeling, and ranking-quality metrics (NDCG).

The objective is to study **tradeoffs between ranking quality, user engagement, and revenue** under different ranking policies in a controlled simulation setting.

---

## 1. System Overview

### Core Components

- **pCTR Model**
  - LightGBM trained on real logged data
  - Input format: pandas DataFrame with 94 features
  - Output: calibrated click-through probability (pCTR)

- **Ranking Policy**
  - $score = bid × pCTR^α$

- **Auction / Pricing**
  - First-price CPC
  - Advertiser pays bid only if the ad is clicked

- **Ad Slots**
  - 4 slots per impression

- **User Click Model**  
  - P(click | position_i) = pCTR × position\_bias[i]   
  - position\_bias = [1.0, 0.7, 0.5, 0.3]

---

## 2. Candidate Generation

- Each simulated impression contains **multiple candidate ads**
- Candidate features are sampled from a **feature bank** created from the real training/validation DataFrame
- Each candidate row matches the exact feature schema used during model training
- Bids are sampled independently from a log-normal distribution

**Important design choice**

- Bids are **independent of pCTR by construction**
- Any correlation between bid and pCTR is **induced purely by ranking**
- This isolates the effect of the ranking function

---

## 3. Metrics Definitions (Multi-slot)

Because this is a **multi-slot ranking setup**, metrics differ slightly from standard single-slot CTR definitions.

### Global Metrics

This can exceed 1 when multiple slots are shown. So we define:

- clicks\_per\_impression = total\_clicks / impressions  

- ctr\_per\_slot = total\_clicks / (impressions × number\_of\_slots)  

- **revenue**
  - Sum of realized CPC payments
  - CPC is paid only if the ad is clicked
  - $eCPM = (revenue / impressions) × 1000$  

- **mean_ndcg@K**
  - NDCG computed per impression using **pCTR as graded relevance**
  - Averaged across impressions
  - K equals the number of slots (K = 4)

---

## 4. Overall Results (Real pCTR Model)

### Aggregate Metrics
| Metric | Value |
| :--- | :--- |
| **Clicks per Impression** | 1.3020 |
| **CTR per Slot** | 0.3255 |
| **Total Revenue** | 126,897 |
| **eCPM** | 2,537.95 |
| **Mean NDCG@4** | 0.9387 |

### Interpretation

- **High NDCG (~0.94)** indicates near-ideal ordering by predicted relevance
- **Clicks per impression > 1** is expected due to the multi-slot layout
- Revenue is dominated by top slots but augmented by lower slots
- The real pCTR model is well calibrated, as observed CTR closely matches
  - pCTR × position\_bias

---

## 5. Position-Level Diagnostics

| Position | CTR   | Avg pCTR | Avg Bid | Avg Revenue / Impression |
|---------:|------:|---------:|--------:|-------------------------:|
| 0 | 0.5678 | 0.5677 | 2.661 | 1.3918 |
| 1 | 0.3599 | 0.5140 | 2.001 | 0.6277 |
| 2 | 0.2399 | 0.4792 | 1.712 | 0.3461 |
| 3 | 0.1344 | 0.4476 | 1.550 | 0.1723 |

### Key Observations

1. **Position Bias Validation**

 Observed CTR closely matches:

 CTR\_i ≈ avg\_pCTR\_i × position\_bias\_i
 
2. **Ranking Quality**

Average pCTR decreases monotonically with position, confirming correct ranking behavior.

3. **Selection Effects**

Although bids are generated independently of pCTR, average bid decreases with position due to selection induced by:
$score = bid × pCTR^α$  


4. **Revenue Concentration**

- Slot 0 contributes the majority of revenue
- Lower slots provide diminishing but non-trivial incremental revenue
- This mirrors real-world ads systems

---

## 6. Ranking Quality vs Business Tradeoff

- Increasing α makes ranking more **relevance-driven**
- NDCG increases monotonically as α increases
- Revenue peaks at an intermediate α due to the tradeoff between:
- click probability (pCTR)
- advertiser willingness to pay (bid)

**Key insight**

> The ranking that maximizes relevance (NDCG) is not necessarily the ranking that maximizes revenue.

---

## 7. Limitations & Assumptions

- Logged data contains one shown ad per impression; candidate sets are synthetically constructed
- First-price CPC is used (GSP pricing is not yet implemented)
- No budget constraints or pacing
- pCTR is treated as the ground-truth relevance signal for NDCG

These simplifications are intentional to isolate ranking effects.

---

## 8. Key Takeaways

- Offline simulation enables controlled evaluation of ranking policies
- Real pCTR models can be safely reused for multi-candidate ranking analysis
- Ranking quality, user engagement, and revenue are related but distinct objectives
- Selection effects naturally emerge from ranking functions
- This framework supports principled exploration before online deployment

---

## 9. Future Work

Planned extensions include:

- α sweep with real pCTR (tradeoff curves)
- Counterfactual evaluation (IPS / SNIPS)
- Budget constraints and pacing
- Multi-slot GSP pricing
- Pareto analysis of NDCG, CTR, and revenue