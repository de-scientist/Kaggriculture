import time
from agent.agent import agent


def benchmark_decision_latency(num_calls: int = 100) -> float:
    obs = {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "farms": [{"money": 3000, "tiles": [[None]], "farmer": [0, 0], "hands": [], "unlocked_quadrants": ["NW"], "hires_today": 0}],
        "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {}, "prices": {}},
        "town": {"unlocked_shops": []},
    }
    start = time.perf_counter()
    for _ in range(num_calls):
        agent(obs)
    elapsed = time.perf_counter() - start
    return (elapsed / num_calls) * 1000


if __name__ == "__main__":
    latency = benchmark_decision_latency()
    print(f"Average decision latency: {latency:.2f} ms")