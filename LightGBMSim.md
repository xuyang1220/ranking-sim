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
  $score = bid × pCTR^α$

- **Auction / Pricing**
- First-price CPC
- Advertiser pays bid only if the ad is clicked

- **Ad Slots**
- 4 slots per impression

- **User Click Model**
$P(click | position i) = pCTR × position_bias[i]$  
$position_bias = [1.0, 0.7, 0.5, 0.3]$

---

