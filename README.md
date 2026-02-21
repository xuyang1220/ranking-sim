# Result summary

## Single slot, 2nd price auction.

Here is what I get from python -m scripts.run_sim 
| Metric | Value |
| :--- | :--- |
| **Impressions** | 50,000 |
| **Clicks** | 10,797 |
| **CTR** | 21.59% |
| **Revenue** | 10,837.97 |
| **eCPM** | 216.76 |
| **Avg. Winner pCTR** | 0.2157 |
| **Avg. Price (CPC)** | 1.27 |

OK, here is what I get from python -m scripts.sweep_alpha 
| Alpha ($\alpha$) | CTR | Revenue |
| :--- | :--- | :--- |
| 0.20 | 0.0934 | 13,607.40 |
| 0.40 | 0.1381 | 16,002.21 |
| 0.60 | 0.1728 | 16,001.77 |
| 0.80 | 0.1979 | 14,077.48 |
| 1.00 | 0.2159 | 10,837.97 |
| 1.20 | 0.2282 | 7,810.35 |
| 1.40 | 0.2379 | 5,790.56 |
| 1.60 | 0.2448 | 4,375.74 |
| 1.80 | 0.2496 | 3,371.62 |
| 2.00 | 0.2537 | 2,643.42 |

## Multiple slot, 1st price auction
``` bash
python -m scripts.run_sim 
```
position_bias=[1.0, 0.7, 0.5, 0.3]  

| Metric | Value |
| :--- | :--- |
| **Impressions** | 50,000 |
| **Clicks** | 21,327 |
| **CTR** | 42.65% |
| **Revenue** | 32,745.83 |
| **eCPM** | 654.92 |
| **Avg. Ads Shown** | 4.0 |

``` bash
python -m scripts.sweep_alpha
```

| Alpha ($\alpha$) | CTR | Revenue |
| :--- | :--- | :--- |
| 0.20 | 0.2156 | 25,516.93 |
| 0.40 | 0.2952 | 29,865.34 |
| 0.60 | 0.3550 | 31,897.65 |
| 0.80 | 0.3986 | 32,691.17 |
| 1.00 | 0.4265 | 32,745.83 |
| 1.20 | 0.4471 | 32,648.12 |
| 1.40 | 0.4626 | 32,411.46 |
| 1.60 | 0.4727 | 32,242.52 |
| 1.80 | 0.4803 | 32,033.87 |
| 2.00 | 0.4861 | 31,777.97 |


## Added position-level metrics to multi-slot simulator
position_bias=[1.0, 0.7, 0.5, 0.3]  

| Position | Impressions | CTR | Avg. pCTR | Avg. Bid | Avg. Rev/Imp |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | 50,000 | 0.2169 | 0.2157 | 2.106 | 0.3931 |
| 1 | 50,000 | 0.1124 | 0.1600 | 1.732 | 0.1514 |
| 2 | 50,000 | 0.0637 | 0.1301 | 1.563 | 0.0741 |
| 3 | 50,000 | 0.0336 | 0.1106 | 1.460 | 0.0364 |

### Key takeaways
* pCTR decreases monotonically with rank
* CTR decays according to both position bias and ranking quality
* average bid declines with position due to selection effects from the ranking score
* The observed revenue per position matched CTR × bid expectations.