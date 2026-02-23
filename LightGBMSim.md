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

 - Observed CTR closely matches:

 - CTR\_i ≈ avg\_pCTR\_i × position\_bias\_i
 
2. **Ranking Quality**

 - Average pCTR decreases monotonically with position, confirming correct ranking behavior.

3. **Selection Effects**

 - Although bids are generated independently of pCTR, average bid decreases with position due to selection induced by:
 - $score = bid × pCTR^α$  

4. **Revenue Concentration**

- Slot 0 contributes the majority of revenue
- Lower slots provide diminishing but non-trivial incremental revenue
- This mirrors real-world ads systems

---

## 6. Performance W.R.T alpha(alpha sweep)


α controls the tradeoff between **monetization (bid)** and **relevance (pCTR)**.

---

### 6.1 Sweep Results

| α | Clicks / Imp | CTR / Slot | Revenue | eCPM | mean NDCG@4 |
|--:|-------------:|-----------:|--------:|-----:|------------:|
| 0.20 | 0.8260 | 0.2065 | 107,388 | 2147.76 | 0.8676 |
| 0.40 | 0.9930 | 0.2483 | 118,082 | 2361.63 | 0.8951 |
| 0.60 | 1.1247 | 0.2812 | 123,958 | 2479.16 | 0.9142 |
| 0.80 | 1.2236 | 0.3059 | 126,237 | 2524.73 | 0.9282 |
| **1.00** | **1.3020** | **0.3255** | **126,897** | **2537.95** | **0.9387** |
| 1.20 | 1.3610 | 0.3403 | 126,669 | 2533.37 | 0.9469 |
| 1.40 | 1.4084 | 0.3521 | 125,519 | 2510.38 | 0.9535 |
| 1.60 | 1.4431 | 0.3608 | 124,178 | 2483.55 | 0.9588 |
| 1.80 | 1.4729 | 0.3682 | 122,809 | 2456.17 | 0.9631 |

---

### 6.2 Observations

#### 1. User Engagement (CTR)
- **Clicks per impression** and **CTR per slot** increase monotonically with α
- Higher α prioritizes high-pCTR ads more aggressively
- This improves user engagement across all slots

#### 2. Ranking Quality (NDCG)
- mean NDCG@4 increases smoothly from **0.87 → 0.96**
- This reflects increasingly relevance-optimal rankings
- As α → ∞, ranking approaches pure pCTR sorting

#### 3. Revenue & eCPM
- Revenue and eCPM **peak around α ≈ 1.0**
- Beyond this point:
  - CTR continues to increase
  - Revenue begins to decline gradually

This occurs because:
- Bids are generated independently of pCTR
- Very high α favors highly relevant but lower-bid ads
- Revenue depends on both **click probability** and **willingness to pay**

---

### 6.3 Key Tradeoff

The sweep highlights a fundamental ranking tradeoff:

- **Low α**  
  - Bid-heavy ranking  
  - Lower CTR, suboptimal relevance  
- **High α**  
  - Relevance-optimal ranking (high NDCG, high CTR)  
  - Reduced monetization due to lower bids  
- **Intermediate α (~1.0)**  
  - Best balance between relevance and revenue  

**Revenue-optimal ≠ Relevance-optimal**

---

### 6.4 Practical Implication

This experiment mirrors real production behavior:

- Ranking systems do **not** optimize pure relevance
- They optimize a **composite objective** balancing:
  - user satisfaction
  - advertiser value
  - platform revenue

Offline simulation makes these tradeoffs explicit and measurable **before online deployment**.

---

### 6.5 Summary

- α provides a smooth control knob between monetization and relevance
- Real pCTR produces sharper, more realistic tradeoff curves
- NDCG, CTR, and revenue must be evaluated together
- The optimal operating point depends on business objectives

This α sweep demonstrates how **offline ranking simulation with a real CTR model** can guide principled ranking policy design.

---

## 7. Ranking Quality vs Business Tradeoff

- Increasing α makes ranking more **relevance-driven**
- NDCG increases monotonically as α increases
- Revenue peaks at an intermediate α due to the tradeoff between:
  - click probability (pCTR)
  - advertiser willingness to pay (bid)

**Key insight**

> The ranking that maximizes relevance (NDCG) is not necessarily the ranking that maximizes revenue.

---

## 8. Limitations & Assumptions

- Logged data contains one shown ad per impression; candidate sets are synthetically constructed
- First-price CPC is used (GSP pricing is not yet implemented, although we 
implemented 2nd price auction for single slot, see README.md)
- No budget constraints or pacing
- pCTR is treated as the ground-truth relevance signal for NDCG

These simplifications are intentional to isolate ranking effects.

---

## 9. Key Takeaways

- Offline simulation enables controlled evaluation of ranking policies
- Real pCTR models can be safely reused for multi-candidate ranking analysis
- Ranking quality, user engagement, and revenue are related but distinct objectives
- Selection effects naturally emerge from ranking functions
- This framework supports principled exploration before online deployment

---

## 10. Future Work

Planned extensions include:

- Counterfactual evaluation (IPS / SNIPS)
- Budget constraints and pacing
- Multi-slot GSP pricing