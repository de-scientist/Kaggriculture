import json, sys, traceback
sys.path.insert(0, "kaggriculture_ai")
try:
    import main as A
    print("agent callable:", callable(getattr(A, "agent", None)))
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 30})
    env.run([A.agent, "random"])
    steps = env.toJSON()["steps"]
    print("num steps:", len(steps))
    obs = steps[1][0]["observation"]
    print("obs keys:", list(obs.keys()))
    print("farms0 keys:", list(obs["farms"][0].keys()))
    print("private keys:", list(obs.get("private", {}).keys()))
    print("market keys:", list(obs["market"].keys()))
    print("tile sample:", obs["farms"][0]["tiles"][0][0])
    print("action p0 step5:", steps[5][0]["action"])
except Exception:
    traceback.print_exc()
