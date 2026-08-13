import sys, os, traceback, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.CRITICAL, filename=os.devnull)

from agent.adapters import ObservationAdapter, ActionAdapter
from agent.config import get_config
from agent.decision import DecisionContext, decision_engine
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 6})
env.run(["starter", "random"])
steps = env.toJSON()["steps"]
obs = steps[1][0]["observation"]

settings = get_config()
adapter = ObservationAdapter()
action_adapter = ActionAdapter()

print("=== parse ===")
try:
    gs = adapter.parse(obs)
    print("parse OK; type:", type(gs))
except Exception:
    traceback.print_exc()
    sys.exit(1)

step = int(obs.get("step", 0)); day = int(obs.get("day", 0)); hour = int(obs.get("hour", 0))
ctx = DecisionContext(
    obs=obs, player=0, game_state=gs, config=settings, step=step, day=day, hour=hour,
    remaining_turns=int(obs.get("remaining_turns", 720)), strategy_name=settings.strategy_name,
)
print("=== decide ===")
try:
    action = decision_engine.decide(ctx)
    print("decide OK:", action)
    print("converted:", action_adapter.convert(action))
except Exception:
    traceback.print_exc()
