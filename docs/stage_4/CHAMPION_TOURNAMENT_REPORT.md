# Champion Tournament Report (Stage 4B)

## Final Champion candidate: champion-v1.1 (pure ChampionPolicy, no endgame)
# champion-v1.1 vs diverse opponents

- Candidate: **no_endgame**
- Matches: 42
- Overall win rate: 100.0%
- Total W/L/T: 42/0/0
- Avg final coins: 22184.10
- Median final coins: 22745.00
- Best / worst: 24297.00 / 17509.00
- Avg decision (ms): 1.912
- Max decision (ms): 142.011
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 6 | 6 | 0 | 0 | 100.0% (100-100) | 22484.33 | 18337.00 |
| conservative | 6 | 6 | 0 | 0 | 100.0% (100-100) | 22594.33 | 19758.33 |
| expansion | 6 | 6 | 0 | 0 | 100.0% (100-100) | 23218.00 | 19183.67 |
| market | 6 | 6 | 0 | 0 | 100.0% (100-100) | 18148.67 | 10152.00 |
| production | 6 | 6 | 0 | 0 | 100.0% (100-100) | 23185.67 | 19604.00 |
| random | 6 | 6 | 0 | 0 | 100.0% (100-100) | 23165.00 | 23165.00 |
| starter | 6 | 6 | 0 | 0 | 100.0% (100-100) | 22492.67 | 19095.33 |

## Previous champion: champion-v1.0 (EndgamePolicy)
# champion-v1.0 vs diverse opponents

- Candidate: **champion-v1.0**
- Matches: 27
- Overall win rate: 74.1%
- Total W/L/T: 20/4/3
- Avg final coins: 17755.00
- Median final coins: 20798.00
- Best / worst: 22243.00 / 8193.00
- Avg decision (ms): 1.607
- Max decision (ms): 345.325
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21267.33 | 19385.33 |
| champion | 3 | 0 | 0 | 3 | 0.0% (0-0) | 10036.67 | 0.00 |
| conservative | 3 | 3 | 0 | 0 | 100.0% (100-100) | 20913.67 | 18039.00 |
| expansion | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21056.00 | 20474.67 |
| market | 3 | 2 | 1 | 0 | 66.7% (13-100) | 13406.00 | 3006.67 |
| no_endgame | 3 | 0 | 3 | 0 | 0.0% (0-0) | 9889.00 | -2355.67 |
| production | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21002.33 | 17250.33 |
| random | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21424.67 | 21421.33 |
| starter | 3 | 3 | 0 | 0 | 100.0% (100-100) | 20799.33 | 17423.67 |

## EndgamePolicy ablation (champion-v1.0 vs no_endgame self-play)
- Matches: 3 (seeds 0,1,2). champion-v1.0 wins: 0, losses: 3.
- no_endgame avg coins: ~12.2k vs champion-v1.0 ~10.5k -> liquidation reduced terminal cash.
## Challengers
### C01  (RETIRE)
# C01 vs suite

- Candidate: **C01**
- Matches: 8
- Overall win rate: 75.0%
- Total W/L/T: 6/2/0
- Avg final coins: 9667.38
- Median final coins: 10672.00
- Best / worst: 11505.00 / 5591.00
- Avg decision (ms): 1.283
- Max decision (ms): 79.451
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 2 | 2 | 0 | 0 | 100.0% (100-100) | 10672.00 | 8571.50 |
| champion | 2 | 0 | 2 | 0 | 0.0% (0-0) | 5652.50 | -10274.50 |
| conservative | 2 | 2 | 0 | 0 | 100.0% (100-100) | 11433.00 | 8357.50 |
| starter | 2 | 2 | 0 | 0 | 100.0% (100-100) | 10912.00 | 7460.00 |

### C02  (RETIRE)
# C02 vs suite

- Candidate: **C02**
- Matches: 8
- Overall win rate: 25.0%
- Total W/L/T: 2/6/0
- Avg final coins: 560.12
- Median final coins: 83.00
- Best / worst: 3900.00 / 80.00
- Avg decision (ms): 1.972
- Max decision (ms): 94.647
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 2 | 2 | 0 | 0 | 100.0% (100-100) | 87.00 | 36.00 |
| champion | 2 | 0 | 2 | 0 | 0.0% (0-0) | 1990.00 | -18885.00 |
| conservative | 2 | 0 | 2 | 0 | 0.0% (0-0) | 80.00 | -3042.00 |
| starter | 2 | 0 | 2 | 0 | 0.0% (0-0) | 83.50 | -3236.00 |

### C08  (RETIRE)
# C08 vs suite

- Candidate: **C08**
- Matches: 8
- Overall win rate: 75.0%
- Total W/L/T: 6/2/0
- Avg final coins: 17794.75
- Median final coins: 20499.50
- Best / worst: 21287.00 / 8637.00
- Avg decision (ms): 1.636
- Max decision (ms): 71.372
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 2 | 2 | 0 | 0 | 100.0% (100-100) | 20955.50 | 17943.50 |
| champion | 2 | 0 | 2 | 0 | 0.0% (0-0) | 8839.50 | -313.50 |
| conservative | 2 | 2 | 0 | 0 | 100.0% (100-100) | 20893.00 | 17942.00 |
| starter | 2 | 2 | 0 | 0 | 100.0% (100-100) | 20491.00 | 17075.50 |
