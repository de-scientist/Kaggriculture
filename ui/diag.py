import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.CRITICAL, filename=os.devnull)

from agent.adapters import ObservationAdapter
from agent.config import get_config
from agent.decision import DecisionContext, decision_engine
from agent.decision.decision_engine import _owned_tiles
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

owned = _owned_tiles(obs, 0)
print("owned tiles computed by engine helper:", len(owned))
print("unlocked_quadrants in obs:", obs["farms"][0].get("unlocked_quadrants"))

res = decision_engine.decide(ctx)
print("engine decide result:", res)
