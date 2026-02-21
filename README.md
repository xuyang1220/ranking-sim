# Result summary

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