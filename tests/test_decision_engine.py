from agent.decision import decision_context, decision_engine


def test_decide_returns_action() -> None:
    context = decision_context.DecisionContext(obs={}, player=0)
    action = decision_engine.decide(context)
    assert "farmer" in action
