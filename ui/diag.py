import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.CRITICAL, filename=os.devnull)

from agent.adapters import ObservationAdapter
from agent.config import get_config
from agent.decision import DecisionContext, decision_engine
from agent.decision.decision_engine import _owned_tiles
from agent.decision import action_generator, action_filter, action_validator
from agent.strategies import strategy_manager
from collections import Counter
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 6})
env.run(["starter", "random"])
obs = env.toJSON()["steps"][1][0]["observation"]

settings = get_config()
gs = ObservationAdapter().parse(obs)
ctx = DecisionContext(
    obs=obs, player=0, game_state=gs, config=settings, step=1, day=1, hour=1,
    remaining_turns=720, strategy_name=settings.strategy_name,
)

cands = action_generator.generate_candidates(ctx)
print("generated:", len(cands), Counter(c.action_type for c in cands))
for c in cands:
    print("   cand:", c.action_type, "target:", c.target_position, "cost:", getattr(c, "estimated_cost", "?"))

print("available_money():", gs.available_money(), "available_workers():", gs.available_workers())
print("farm workers:", gs.farm.workers)
print("farm quadrants:", gs.farm.quadrants)

owned = _owned_tiles(obs, 0)
money = gs.available_money()
workers = len(gs.available_workers())
filt = action_filter.filter_pre_validation(cands, money, workers, owned)
print("filtered:", len(filt), Counter(c.action_type for c in filt))

val = action_validator.validate_actions(filt, gs)
valid = [v for v in val if v.is_valid]
print("validated valid:", len(valid), Counter(v.action.action_type for v in valid))
for v in valid:
    print("   valid action:", v.action.action_type, "reason:", getattr(v, "reason", ""))

strategy = strategy_manager.get_strategy(settings.strategy_name)
scored = strategy.evaluate(ctx, [v.action for v in valid])
print("scored by strategy:", len(scored))
for s in scored[:5]:
    print("   score:", getattr(s, "score", "?"), "action:", getattr(s.action, "action_type", s.action))
