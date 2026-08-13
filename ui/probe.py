import sys, traceback
sys.path.insert(0, ".")
try:
    from agent.agent import agent
    print("agent callable:", callable(agent))
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 40})
    env.run([agent, "random"])
    steps = env.toJSON()["steps"]
    print("num steps:", len(steps))
    obs = steps[1][0]["observation"]
    print("obs keys:", list(obs.keys()))
    print("farms0 keys:", list(obs["farms"][0].keys()))
    print("private keys:", list(obs.get("private", {}).keys()))
    print("market keys:", list(obs["market"].keys()))
    print("tile sample:", obs["farms"][0]["tiles"][0][0])
    print("action p0 step5:", steps[5][0]["action"])
    print("rewards:", env.toJSON()["rewards"])
except Exception:
    traceback.print_exc()
