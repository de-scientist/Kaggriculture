import pytest
from kaggriculture_ai.agent import agent, build_agent


def test_agent_returns_valid_dict(sample_observation):
    result = agent(sample_observation)
    assert isinstance(result, dict)
    assert "farmer" in result
    assert "hands" in result
    assert "market" in result


def test_agent_returns_list_actions(sample_observation):
    result = agent(sample_observation)
    assert isinstance(result["farmer"], list)
    assert isinstance(result["hands"], list)
    assert isinstance(result["market"], list)


def test_agent_deterministic(sample_observation):
    result1 = agent(sample_observation)
    result2 = agent(sample_observation)
    assert result1 == result2


def test_build_agent(sample_observation):
    agent_fn = build_agent({})
    result = agent_fn(sample_observation)
    assert isinstance(result, dict)
    assert "farmer" in result