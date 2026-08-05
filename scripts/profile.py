import cProfile
import pstats
from agent.agent import agent


def profile_agent():
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
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(100):
        agent(obs)
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(20)


if __name__ == "__main__":
    profile_agent()