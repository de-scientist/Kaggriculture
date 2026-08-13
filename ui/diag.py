import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.CRITICAL, filename=os.devnull)

from agent.adapters import ObservationAdapter, ActionAdapter
from agent.config import get_config
from agent.decision import DecisionContext, decision_engine
from agent.decision import action_generator, action_filter, action_validator
from agent.domain.position import Position
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 6})
env.run(["starter", "random"])
steps = env.toJSON()["steps"]
obs = steps[1][0]["observation"]

settings = get_config()
adapter = ObservationAdapter()
gs = adapter.parse(obs)
ctx = DecisionContext(
    obs=obs, player=0, game_state=gs, config=settings, step=1, day=1, hour=1,
    remaining_turns=720, strategy_name=settings.strategy_name,
)

cands = action_generator.generate_candidates(ctx)
print("generated candidates:", len(cands))
from collections import Counter
print("types:", Counter(c.action_type for c in cands))

money = gs.available_money()
workers = len(gs.available_workers())

filt_empty = action_filter.filter_pre_validation(cands, money, workers, set())
print("after filter (owned_tiles=EMPTY):", len(filt_empty), Counter(c.action_type for c in filt_empty))

# compute real owned tiles
grid = obs["farms"][0]["tiles"]
size = len(grid)
half = size // 2
quads = set(gs.farm.quadrants())
owned = set()
for y in range(size):
    for x in range(size):
        q = "NW" if (x < half and y < half) else "NE" if (x >= half and y < half) else "SW" if (x < half and y >= half) else "SE"
        if q in quads:
            owned.add(Position(x, y))
print("owned tiles count:", len(owned), "quads:", quads)

filt_owned = action_filter.filter_pre_validation(cands, money, workers, owned)
print("after filter (REAL owned):", len(filt_owned), Counter(c.action_type for c in filt_owned))

val = action_validator.validate_actions(filt_owned, gs)
valid = [v for v in val if v.is_valid]
print("validated valid:", len(valid), Counter(v.action.action_type for v in valid))
