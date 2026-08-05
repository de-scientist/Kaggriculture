# Kaggriculture AI Platform Engineering Blueprint

**Version:** 1.0 (Stage 0 — Technical Discovery)
**Status:** Complete specification
**Sources of truth:** `kaggle_environments/envs/kaggriculture/kaggriculture.py` (engine), `README.md`, `AGENTS.md` (official docs)

---

## Executive Summary

Kaggriculture is a two-player farming simulation competition where agents compete to maximize their income over a 30-day season by managing crops, animals, land expansion, market trading, and town building.

This document provides the **complete engineering blueprint** for building an AI agent platform that can evolve from deterministic baselines through advanced RL/MCTS methods while maintaining compatibility with the official Kaggle engine.

**Key Insight:** The game has fully documented mechanics, deterministic market pricing functions, and clear yield calculations — making it ideal for model-based optimization before requiring complex RL.

---

## 1. Project Overview

### Mission
Develop a competitive AI agent for Kaggriculture that consistently outperforms baseline strategies through systematic optimization and intelligent decision-making.

### Vision
Create a modular, extensible platform that enables rapid iteration from simple deterministic strategies to sophisticated RL agents, while maintaining debuggability and explainability throughout development.

### Objectives
- Create production-ready observation adapter for the official engine
- Build a robust domain model with all game mechanics
- Implement a decision pipeline with 9 stages of AI complexity
- Establish comprehensive testing and validation framework
- Deliver a submission-ready `main.py` with deterministic Stage 1 baseline

### Success Metrics
- Agent consistently scores >2000 more than random baseline over 100 matches
- Execution under 1 second per turn on Kaggle infrastructure
- <1% bug regression rate after each stage
- All components tested against official engine parity

### Scope
- Pure observation adaptation and domain modeling
- Decision pipeline architecture (Stage 1-9 strategy roadmap)
- Multiple planner implementations (crop, animal, market, expansion, workers)
- Strategy evaluation with utility scoring and lookahead
- Complete testing suite with replay verification
- Submission packaging system

### Out-of-Scope
- External data sources or ML frameworks beyond stdlib + kaggle-environments
- Game rule changes or modifications to official engine
- Non-deterministic agent behavior (deterministic required for testing)

### Stakeholders
- AI Engineers: Build and evolve agents
- Systems Engineers: Maintain infrastructure and testing
- Competition Organizers: Understand solution architecture
- Future Contributors: Extend with new features

### Constraints
- Must use official Kaggle environment protocol
- Zero modification to official engine code
- 1-second per-turn budget on Kaggle infrastructure
- Backward compatibility across stages
- Deterministic execution for testing

### Risks
- Engine changes mid-project
- Performance bottlenecks
- Incorrect mechanical assumptions
- Market model misunderstanding

---

## 2. Repository Structure

```
kaggriculture-ai/
├── main.py                    ← OFFICIAL submission surface (agent(obs))
├── config/                    ← Strategy configuration
│   └── defaults.yaml
├── interfaces/                ← Protocols (public contracts)
│   ├── observation_adapter.py
│   ├── action_serializer.py
│   └── domain_models.py
├── adapters/                  ← Direct engine interface
│   ├── observation_adapter.py
│   └── action_serializer.py
├── domain/                     ← DDD layer (pure logic)
│   ├── entities.py
│   ├── value_objects.py
│   ├── resources.py
│   └── invariants.py
├── decision/                   ← Planning and execution
│   ├── engine.py
│   ├── planners/
│   │   ├── crop_planner.py
│   │   ├── animal_planner.py
│   │   ├── market_planner.py
│   │   ├── expansion_planner.py
│   │   └── worker_scheduler.py
│   ├── strategies/           ← Stage implementations
│   │   ├── deterministic.py
│   │   ├── heuristic.py
│   │   ├── economic.py
│   │   └── utility.py
├── economy/                   ← Market and pricing
│   ├── price_model.py
│   ├── ro_analyzer.py
│   └── risk_analyzer.py
├── simulation/                ← Fast clone engine for lookahead
├── optimization/              ← MCTS, beam search, genetic (Stages 5-8)
├── testing/                   ← Comprehensive test suite
├── experiments/               ← A/B and parameter sweeps
├── benchmarks/                ← Baseline comparison
└── packaging/                 ← Submission builder
```

---

## 3. Technology Stack

**Core Requirements:**
- Python 3.11+
- kaggle-environments (pinned version)
- stdlib only for Stage 1-4
- Minimal dependencies (ruff, mypy, pytest)

**Architecture Principles:**
- Clean Architecture with isolated layers
- Domain-Driven Design with pure domain model
- Protocol-based interfaces for extensibility
- Dependency injection for testability
- Type safety with full type hints

---

## 4. Development Workflow

### CI/CD Pipeline
1. **Lint & Type Check**: ruff + mypy gates
2. **Unit Tests**: pytest with coverage
3. **Integration Tests**: Full engine parity verification
4. **Benchmarks**: Compare against pass/random/starter baselines
5. **Replay Tests**: Deterministic seed reproducibility
6. **Performance**: Per-step latency profiling

### Branch Strategy
- `main`: Production-ready Stage 1 baseline
- `stage-2`: Heuristic improvements
- `stage-3`: Economic models
- `stage-4`: Utility optimization
- Feature branches for experimental stages

### Commit Conventions
- Conventional commits (feat:, fix:, docs:, refactor:, test:, ci:)
- Detailed PR descriptions
- Reviewers required for production changes

### Code Review Standards
- Architecture decisions documented
- Test coverage requirements
- Performance budget compliance
- Maintainability review

---

## 5. Project Roadmap

### Stage 0 (Current): Technical Discovery
- ✅ Complete game mechanics reverse-engineering
- ✅ Domain model and architecture design
- ✅ Testing strategy definition
- ✅ Risk assessment and mitigation
- ✅ Engineering standards documentation

### Stage 1: Deterministic Baseline
- Build observation adapter
- Implement domain model
- Create deterministic crop loop matching `starter`
- Establish CI and testing framework
- Deliver first submission

### Stage 2: Heuristic Improvements
- Window-watering planner
- Feed-first animal care
- Hand job scheduler
- Shed capacity management

### Stage 3: Economic Models
- Price model implementation
- ROI analysis
- Sell batching strategies
- Expansion timing rules

### Stage 4: Utility Optimization
- Multi-objective scoring
- Short lookahead simulation
- Tunable strategy weights
- Explainability logging

### Stage 5-9: Advanced AI
- MCTS with simulation
- Beam search planning
- Genetic parameter tuning
- Reinforcement learning
- Hybrid AI integration

---

## 6. Implementation Plan

### Milestone 1: Repository Setup
- Clone and analyze official engine
- Create project structure
- Establish Python environment
- Set up CI/CD pipeline
- Write contribution guide

### Milestone 2: Observation Adapter
- Implement `ObservationAdapter` class
- Convert raw obs to domain objects
- Validate schema and provenance
- Cache last raw observation

### Milestone 3: Domain Model
- Implement all entities (GameState, Farm, Market, Town)
- Create value objects (Crop, Animal, Resource)
- Enforce invariants and rules
- Add helper utilities

### Milestone 4: Decision Engine
- Create `DecisionEngine` orchestrating planners
- Implement planner interface
- Add candidate generation
- Handle action conflicts

### Milestone 5: Baseline Strategy
- Implement deterministic baseline
- Match `starter` behavior
- Add explainability logging
- Benchmark against official

### Milestone 6: Testing Framework
- Unit tests for all components
- Integration parity harness
- Replay verification
- Performance profiling

### Milestone 7: Validation
- Multiseed benchmark suites
- Regression testing
- Stress testing
- Acceptance criteria verification

### Milestone 8: First Submission
- Package `main.py` with Stage 1 agent
- Build submission tar.gz
- Upload to Kaggle
- Verify metrics

### Milestone 9: Extension Points
- Register new planners
- Add simulation backends
- Extend strategy registry
- Optimize performance

---

## 7. Risk Analysis

### Technical Risks
1. **Engine Changes**: Pin `kaggle-environments` version, use adapter pattern
2. **Market Misunderstanding**: Analytic price model + parity tests
3. **Performance**: Budget enforcement, profiling hooks, lazy evaluation
4. **Architecture Drift**: Single adapter to official engine, protocol isolation

### Competition Risks
1. **Rule Changes**: Configuration-driven via observation, fail-loud adapter
2. **Meta-Competition**: Multiseed benchmarks, distributional testing
3. **Time Constraints**: Staged delivery, minimal baseline for early submission

### Simulation Risks
1. **Parity Errors**: Complete replay harness with official engine tag
2. **Random Seed Issues**: Reproduce engine RNG exactly
3. **State Explosion**: Efficient caching and incremental updates

### Market Assumptions
1. **Price Function**: Implement documented formula, test against engine output
2. **Town Demand**: Verify schedule and shop unlock mechanics
3. **Trading Mechanics**: Understand per-unit lockstep and inventory impact

### Performance Risks
1. **Per-Step Budget**: 1-second target, early pruning
2. **Memory Growth**: No unbounded caches, garbage collection friendly
3. **Lookup Costs**: Pre-compute price tables, fast data structures

### Future Compatibility
1. **Extensible Interfaces**: Protocol-based design
2. **Configurable Strategies**: Strategy registry with weights
3. **Simulation Reuse**: Single simulation backend for all stages

---

## 8. Engineering Standards

### Code Style
- PEP 8 compliance
- Full type hints
- Google docstring style
- snake_case functions, CamelCase classes
- UPPER_SNAKE constants

### Logging
- Structured logging with fields
- No console output in library code
- Debug-level only for performance
- Error path with dedicated logger

### Error Handling
- Root `KaggricultureAIError` hierarchy
- Typed validation errors
- Fail-loud on schema drift
- Budget exceeded exceptions

### Configuration
- YAML under `config/`
- Runtime overrides
- Immutable after build
- Strategy weight tuning

### Testing
- pytest with coverage
- Unit + integration + replay
- Deterministic seed testing
- Performance benchmarks

### Documentation
- README with purpose
- Architecture decisions in `decisions/`
- Module docstrings
- Cross-references where needed

---

## 9. Testing Strategy

### Unit Tests
- Observation adapter conversion
- Domain invariants (shed cap, money ≥ 0)
- Price model calculations
- Configuration validation
- Validator preconditions

### Integration Tests
- Full make runs against baselines
- Valid schema output
- Reward monotonic increases
- No exceptions in production

### Replay Tests
- Fixed seeds → byte-diff comparison
- Reproducibility vs official engine
- State space coverage
- Edge case validation

### Performance Tests
- Per-step latency budget
- Memory usage patterns
- Scalability with board size
- Stress with pathological configs

### Acceptance Tests
- Submission contract compliance
- Local make execution
- Against random opponent
- Self-play validation

---

## 10. Conclusion

This blueprint provides a complete foundation for building competitive Kaggriculture agents from deterministic baselines through advanced AI methods. The architecture is deliberately staged to allow incremental improvement while maintaining a stable interface throughout development.

Key differentiators:
- **Model-based foundation**: Exploit known mechanics early
- **Extensible protocols**: Enable advanced AI integration
- **Comprehensive testing**: Parity with official engine as single source of truth
- **Performance-first**: Respects Kaggle infrastructure constraints

The result is a platform that can deliver an early submission (Stage 1) while enabling evolution through all 9 strategy stages with minimal architectural changes.
