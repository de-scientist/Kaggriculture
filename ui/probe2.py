import sys, os, traceback, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.DEBUG)
from agent.agent import agent
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 6})
try:
    env.run([agent, "random"])
except Exception:
    traceback.print_exc()

steps = env.toJSON()["steps"]
obs = steps[1][0]["observation"]
print("=== calling agent on real obs ===")
try:
    out = agent(obs)
    print("agent returned:", out)
except Exception:
    traceback.print_exc()
