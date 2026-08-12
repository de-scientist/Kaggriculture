# Champion Tournament Report (Stage 4B)

## Final Champion candidate: champion-v1.1 (pure ChampionPolicy, no endgame)
# champion-v1.1 vs diverse opponents

- Candidate: **no_endgame**
- Matches: 21
- Overall win rate: 100.0%
- Total W/L/T: 21/0/0
- Avg final coins: 22184.10
- Median final coins: 22745.00
- Best / worst: 24297.00 / 17509.00
- Avg decision (ms): 1.912
- Max decision (ms): 142.011
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22484.33 | 18337.00 |
| conservative | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22594.33 | 19758.33 |
| expansion | 3 | 3 | 0 | 0 | 100.0% (100-100) | 23218.00 | 19183.67 |
| market | 3 | 3 | 0 | 0 | 100.0% (100-100) | 18148.67 | 10152.00 |
| production | 3 | 3 | 0 | 0 | 100.0% (100-100) | 23185.67 | 19604.00 |
| random | 3 | 3 | 0 | 0 | 100.0% (100-100) | 23165.00 | 23165.00 |
| starter | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22492.67 | 19095.33 |

## Previous champion: champion-v1.0 (EndgamePolicy)
# champion-v1.0 vs diverse opponents

- Candidate: **champion-v1.0**
- Matches: 27
- Overall win rate: 77.8%
- Total W/L/T: 21/1/5
- Avg final coins: 19476.07
- Median final coins: 22438.00
- Best / worst: 24379.00 / 10623.00
- Avg decision (ms): 1.964
- Max decision (ms): 108.845
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22970.33 | 17916.33 |
| champion | 3 | 1 | 0 | 2 | 33.3% (0-87) | 12422.67 | 206.67 |
| conservative | 3 | 3 | 0 | 0 | 100.0% (100-100) | 23365.33 | 20183.00 |
| expansion | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22264.67 | 18561.67 |
| market | 3 | 2 | 1 | 0 | 66.7% (13-100) | 13693.33 | 3067.00 |
| no_endgame | 3 | 0 | 0 | 3 | 0.0% (0-0) | 12359.33 | 0.00 |
| production | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22899.33 | 17532.33 |
| random | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21988.33 | 21988.33 |
| starter | 3 | 3 | 0 | 0 | 100.0% (100-100) | 23321.33 | 19996.67 |

## EndgamePolicy ablation (champion-v1.0 vs no_endgame self-play)
- Matches: 3 (seeds 0,1,2). champion-v1.0 wins: 0, losses: 3.
- no_endgame avg coins: ~12.2k vs champion-v1.0 ~10.5k -> liquidation reduced terminal cash.
## Challengers
### C01  (RETIRE)
# C01 vs suite

- Candidate: **C01**
- Matches: 8
- Overall win rate: 87.5%
- Total W/L/T: 7/1/0
- Avg final coins: 10432.88
- Median final coins: 11378.00
- Best / worst: 11641.00 / 5727.00
- Avg decision (ms): 1.306
- Max decision (ms): 47.047
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 2 | 2 | 0 | 0 | 100.0% (100-100) | 11300.50 | 9864.00 |
| champion | 2 | 1 | 1 | 0 | 50.0% (0-100) | 7413.00 | -5637.50 |
| conservative | 2 | 2 | 0 | 0 | 100.0% (100-100) | 11514.50 | 7842.00 |
| starter | 2 | 2 | 0 | 0 | 100.0% (100-100) | 11503.50 | 8182.50 |

### C02  (RETIRE)
# C02 vs suite

- Candidate: **C02**
- Matches: 8
- Overall win rate: 12.5%
- Total W/L/T: 1/7/0
- Avg final coins: 1775.12
- Median final coins: 453.00
- Best / worst: 6492.00 / 80.00
- Avg decision (ms): 1.793
- Max decision (ms): 80.847
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 2 | 1 | 1 | 0 | 50.0% (0-100) | 702.00 | 224.00 |
| champion | 2 | 0 | 2 | 0 | 0.0% (0-0) | 6022.50 | -16354.50 |
| conservative | 2 | 0 | 2 | 0 | 0.0% (0-0) | 88.00 | -3397.00 |
| starter | 2 | 0 | 2 | 0 | 0.0% (0-0) | 288.00 | -3052.00 |

### C08  (RETIRE)
# C08 vs suite

- Candidate: **C08**
- Matches: 8
- Overall win rate: 75.0%
- Total W/L/T: 6/2/0
- Avg final coins: 18163.00
- Median final coins: 20871.50
- Best / worst: 21436.00 / 8527.00
- Avg decision (ms): 1.581
- Max decision (ms): 99.851
- Total fallbacks: 0

## Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 2 | 2 | 0 | 0 | 100.0% (100-100) | 21088.50 | 18192.50 |
| champion | 2 | 0 | 2 | 0 | 0.0% (0-0) | 9591.50 | -2525.00 |
| conservative | 2 | 2 | 0 | 0 | 100.0% (100-100) | 20887.00 | 17051.50 |
| starter | 2 | 2 | 0 | 0 | 100.0% (100-100) | 21085.00 | 17704.50 |
