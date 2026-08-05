from agent.decision import decision_engine
from agent.decision import decision_context


def test_decide_returns_action():
    context = decision_context.DecisionContext(obs={}, player=0)
    action = decision_engine.decide(context)
    assert "farmer" in action