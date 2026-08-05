from agent.decision import action_generator, action_validator, decision_context
from agent.strategies import strategy_manager


def decide(context: decision_context.DecisionContext) -> dict:
    candidates = action_generator.generate_candidates(context)
    valid = [a for a in candidates if action_validator.validate(a, context)]
    strategy = strategy_manager.get_strategy(context.config)
    ranked = strategy.rank(valid, context)
    if not ranked:
        return {"farmer": ["PASS"], "hands": [], "market": []}
    return ranked[0]
