# Kaggriculture AI Platform — Contributing Guidelines

**Version:** 1.0 (Stage 0)
**Status:** Complete specification
**Governs:** All contributor interactions and code quality standards

---

## Executive Summary

This document defines the contributing guidelines for the Kaggriculture AI platform development. It establishes the standards, processes, and best practices that ensure consistent, high-quality contributions while maintaining the integrity and performance requirements of the platform.

**Core philosophy:** Balance of structure and flexibility, with clear expectations and transparent processes.

---

## Contributing Philosophy

### Welcome Policy

- **All contributions are welcome:** code, documentation, testing, research, and infrastructure improvements
- **Diverse perspectives:** contributions from all experience levels and backgrounds are valued
- **Knowledge sharing:** encourage learning and mentorship
- **Inclusive environment:** respect diverse viewpoints and working styles

### Quality Standards

- **Performance-first:** all code must meet strict performance budgets
- **Testable:** every component must be comprehensively tested
- **Documented:** all public APIs and decisions documented
- **Reviewed:** all changes undergo peer review
- **Compatible:** changes must maintain backward compatibility

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Development environment:**
   - Python 3.11+
   - Git 2.0+
   - Recommended: Docker for local testing

2. **Development tools:**
   - Code editor with Python support
   - Text editor with Markdown support
   - Terminal/command line access

3. **Access:**
   - GitHub account for pull requests
   - Local fork of the repository

### Local Setup

#### Clone the Repository

```bash
# Create a working directory
cd /path/to/your/projects

# Clone the Kaggriculture AI repository
git clone https://github.com/your-username/kaggriculture-ai.git

# Navigate to the repository
cd kaggriculture-ai
```

#### Install Development Dependencies

```bash
# Create and activate a virtual environment
cd kaggriculture-ai
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies  
pip install -r requirements-dev.txt
```

#### Set Up Local Configuration

```bash
# Copy example configuration
cp config/example.yaml config/defaults.yaml

# Configure for your environment if needed
# Edit config/defaults.yaml as needed
```

#### Verify Installation

```bash
# Test the environment
python -c "import kaggle_environments; print('Environment available')"

# Run linting
ruff check --diff

# Run type checking
mypy --strict

# Run tests
pytest tests/ --cov=.
```

---

## Branch Strategy

### Branch Naming Convention

| Branch Type | Pattern | Examples |
|-------------|---------|----------|
| Feature | `feature/<name>` | `feature/crop-planner` |
| Bug Fix | `fix/<name>` | `fix/shed-cap-violation` |
| Documentation | `docs/<name>` | `docs/architecture-decisions` |
| Research | `research/<name>` | `research/mcts-optimization` |
| Experiment | `experiment/<name>` | `experiment/weight-sweeps` |
| Hotfix | `hotfix/<name>` | `hotfix/emergency-budget-fix` |
| Release | `release/<version>` | `release/1.0.0` |

### Branch Workflow

1. **Development Branch**
   - `main`: Production-ready releases
   - `staging`: Pre-production integration
   - `dev`: Daily development integration

2. **Feature Branches**
   - Created from `dev` or `staging`
   - Work in isolation
   - Submit pull request to `dev`

3. **Hotfix Branches**
   - Created from `main`
   - Merged directly to `main` after review

### Branch Protection Rules

```yaml
# .github/workflows/branch-protection.yaml
branches:
  - name: main
    protection:
      required_status_checks:
        contexts:
          - "lint"
          - "type-check"
          - "unit-tests"
          - "integration-tests"
          - "parity-harness"
      required_pull_request_reviews:
        required_approving_review_count: 2
      enforce_admins: true
      require_linear_history: true

  - name: dev
    protection:
      required_status_checks:
        contexts:
          - "lint"
          - "type-check"
          - "unit-tests"
```

---

## Git Workflow

### Commit Conventions

#### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Commit Types

| Type | Description | Examples |
|------|-------------|----------|
| feat | New feature | `feat(crop_planner): add window-watering optimization` |
| fix | Bug fix | `fix(adapters): correct observation parsing` |
| docs | Documentation | `docs(architecture): update ADR-001` |
| style | Code style | `style(interfaces): enforce type hints` |
| refact | Refactoring | `refactor(domain): simplify entity relationships` |
| perf | Performance | `perf(engine): optimize decision pipeline` |
| test | Testing | `test(adapters): add parity validation` |
| ci | CI/CD | `ci(config): update GitHub Actions` |
| chore | Maintenance | `chore(deps): update dependencies` |
| revert | Revert | `revert(commit): fix breaking changes` |

#### Commit Rules

1. **Conventional Commits:** Use the conventional commit format
2. **Descriptive Subjects:** Subject must describe what changed
3. **Clear Scope:** Scope indicates affected component
4. **Exploratory Body:** Body explains why and what changed
5. **Footer Context:** Co-authored-by if from external contributor

### Commit Best Practices

#### Meaningful Commits

```bash
# Good: Specific and descriptive
git add adapters/observation_adapter.py
git commit -m "feat(adapters): add provenance tracking for raw observations"

# Better: Includes context
git add adapters/observation_adapter.py
git commit -m "feat(adapters): add provenance tracking

This commit adds provenance tracking to the observation adapter to enable
round-trip fidelity validation and debugging. The adapter now caches the
last raw observation and includes metadata about data sources.

Co-authored-by: Developer Name <dev@example.com>"
```

#### Commit Size

- **Small commits:** Feature commits should be small and focused
- **Logical grouping:** Related changes in same commit
- **Atomic changes:** Each commit should be independently reviewable

### Pull Request Process

#### PR Lifecycle

1. **Draft Phase:** Work in progress
   - Keep `draft: true` in PR title
   - Allow feedback during development
   - Run CI tests locally

2. **Review Phase:** Ready for review
   - Set appropriate labels
   - Request specific reviewers
   - Run full CI pipeline

3. **Approval Phase:** Approved for merge
   - All required approvals
   - CI checks passing
   - No conflicts

4. **Merge Phase:** Integrated into codebase
   - Squash or merge commit strategy
   - Update CHANGELOG
   - Tag release if applicable

#### PR Checklist

```markdown
## Pull Request Checklist

### Code Quality
- [ ] Linting passes (`ruff check`)
- [ ] Type checking passes (`mypy --strict`)
- [ ] Code follows project style guide
- [ ] Added unit tests for new code
- [ ] Updated documentation
- [ ] Added integration tests

### Testing
- [ ] All existing tests pass
- [ ] Added new test coverage
- [ ] Parity tests with official engine
- [ ] Performance tests pass
- [ ] Edge cases covered

### Documentation
- [ ] API documentation updated
- [ ] Architecture decisions documented
- [ ] User guides updated
- [ ] Examples added/updated

### Dependencies
- [ ] Dependencies updated in requirements files
- [ ] Security vulnerabilities checked
- [ ] No breaking changes

### Performance
- [ ] Performance budget met
- [ ] No memory leaks
- [ ] Efficient algorithms

## Review Checklist

### Technical Review
- [ ] Code architecture aligns with design
- [ ] Interface contracts followed
- [ ] Domain invariants enforced
- [ ] Performance requirements met
- [ ] Dependencies justified

### Code Review
- [ ] Readable and maintainable
- [ ] Appropriate variable/naming conventions
- [ ] Proper error handling
- [ ] Comments explain complex logic
- [ ] No TODO comments in production code

### Integration Review
- [ ] Integrates with existing systems
- [ ] No breaking changes to public APIs
- [ ] Follows project patterns and conventions
- [ ] Performance impacts evaluated

### Testing Review
- [ ] Tests comprehensive and accurate
- [ ] Test cases representative
- [ ] Edge cases covered
- [ ] Test performance acceptable
- [ ] Documentation of test coverage
```

---

## Code Review Process

### Reviewer Responsibilities

#### Technical Review
- **Architecture Alignment:** Verify changes follow project architecture
- **Interface Compliance:** Ensure public interfaces are correct
- **Performance Considerations:** Check performance impact and compliance
- **Security Analysis:** Review for security vulnerabilities
- **Maintainability:** Assess code quality and maintainability

#### Code Review
- **Code Quality:** Review style, readability, and maintainability
- **Testing:** Verify test coverage and quality
- **Documentation:** Check documentation completeness
- **Dependencies:** Validate dependency usage and updates

### Review Comments Categories

| Category | Priority | Description |
|----------|----------|-------------|
| Critical | P0 | Bugs, security issues, performance violations |
| Major | P1 | Architecture issues, API design problems |
| Minor | P2 | Style issues, documentation gaps |
| Suggestion | P3 | Improvements, best practices, optimizations |

### Review Response SLA

- **Critical Issues:** Response within 24 hours
- **Major Issues:** Response within 48 hours
- **Minor Issues:** Response within 1 week
- **Suggestions:** Response within 2 weeks

---

## Code Standards

### Python Standards

#### PEP 8 Compliance

```python
# Preferred
def calculate_optimal_action(state: GameState, intents: list) -> list:
    """Calculate optimal action based on state and intentions."""
    # Implementation

# Avoid too many spaces
def bad_example():
    x  =  5
    y =   10

# Use descriptive variable names
for i in range(len(items)):
    process_item(items[i])

# Use descriptive variable names
for item in items:
    process_item(item)
```

#### Type Hints

```python
# Required for all public functions
from typing import List, Dict, Optional, Tuple

class DecisionEngine:
    def __init__(self, config: Config) -> None:
        self.config = config
    
    def generate(self, state: GameState) -> List[Intent]:
        """Generate candidate intents from state."""
        pass
    
    def optimize(self, state: GameState, intents: List[Intent]) -> List[Intent]:
        """Optimize intent selection using utility function."""
        pass
```

#### Error Handling

```python
# Custom exceptions
class KaggricultureAIError(Exception):
    """Base exception for all Kaggriculture AI errors."""
    pass

class InvalidObservationError(KaggricultureAIError):
    """Raised when observation doesn't match expected schema."""
    pass

class IllegalActionError(KaggricultureAIError):
    """Raised when action violates engine preconditions."""
    pass

# Exception handling
class GameSimulator:
    def __init__(self, config: Config):
        self.config = config
    
    def step(self, state: GameState, plan: Plan) -> GameState:
        try:
            # Simulation logic
            return self._simulate(state, plan)
        except InvalidObservationError as e:
            raise GameSimulationError(f"Invalid state: {e}") from e
        except BudgetExceededError as e:
            raise GameSimulationError(f"Budget exceeded: {e}") from e
        except KaggricultureAIError as e:
            raise GameSimulationError(f"Simulation error: {e}") from e
```

#### Documentation

```python
# Google style docstrings
class ObservationAdapter:
    """Converts raw observations to domain objects.
    
    The ObservationAdapter is the only component that touches the official
    Kaggle environment observation dict. It converts raw observations into
    rich, typed domain objects for downstream use.
    
    Attributes:
        config: Configuration settings for the adapter
        _last_raw: Cache of the last raw observation
    
    Methods:
        adapt: Convert raw observation to domain object
        last_raw: Get the last raw observation
        _validate: Internal validation helper
    
    Raises:
        InvalidObservationError: If observation schema is invalid
    """
    
    def __init__(self, config: Config) -> None:
        """Initialize the observation adapter.
        
        Args:
            config: Configuration settings for the adapter
        """
        self.config = config
        self._last_raw: Optional[dict] = None
    
    def adapt(self, raw: dict) -> GameState:
        """Convert raw observation to domain object.
        
        Args:
            raw: Raw observation from the Kaggle environment
            
        Returns:
            GameState: Domain object representation of the observation
            
        Raises:
            InvalidObservationError: If observation schema is invalid
        """
        # Validation
        self._validate(raw)
        
        # Cache for round-trip fidelity
        self._last_raw = raw
        
        # Convert to domain objects
        return self._to_domain(raw)
    
    def _validate(self, raw: dict) -> None:
        """Validate observation schema.
        
        Args:
            raw: Raw observation to validate
            
        Raises:
            InvalidObservationError: If schema is invalid
        """
        # Schema validation logic
        pass
```

### File Organization

#### Directory Structure

```
/kaggriculture_ai/
├── main.py                          # Entry point
├── config/                         # Configuration
│   ├── defaults.yaml              # Default configuration
│   └── environments/              # Environment-specific
├── interfaces/                     # Public contracts
│   ├── iobservation.py            # IObservationSource protocol
│   ├── iaction.py                 # BoardAction protocol
│   └── iplanner.py                # Planner protocol
├── adapters/                      # Direct engine interface
│   ├── observation_adapter.py
│   └── action_serializer.py
├── domain/                        # DDD layer
│   ├── entities.py
│   ├── value_objects.py
│   └── invariants.py
├── decision/                      # Planning engine
│   ├── engine.py
│   ├── planners/                 # Domain-specific planners
│   └── strategies/               # Stage implementations
├── economy/                       # Market modeling
│   ├── price_model.py
│   └── ro_analyzer.py
├── simulation/                   # Clone+advance engine
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/             # Integration tests
│   └── performance/             # Performance tests
├── experiments/                  # A/B testing
├── benchmarks/                   # Performance benchmarks
└── packaging/                    # Submission packaging
```

#### File Naming Conventions

- **Modules:** `module_name.py` (lowercase, descriptive)
- **Classes:** `ClassName` (CamelCase)
- **Functions:** `function_name` (snake_case)
- **Variables:** `variable_name` (snake_case)
- **Constants:** `CONSTANT_NAME` (UPPER_SNAKE_CASE)
- **Tests:** `test_module_name.py` (prefix 'test_')
- **Documentation:** `file_name.md` (lowercase, descriptive)

### Testing Strategy

#### Test Structure

```
/tests/
├── unit/
│   ├── adapters/              # Adapter unit tests
│   ├── domain/                # Domain model tests
│   ├── decision/             # Decision engine tests
│   └── economy/              # Economic model tests
├── integration/              # Integration tests
│   ├── parity/               # Parity with official engine
│   ├── full_pipeline/       # End-to-end tests
│   └── scenario/            # Scenario tests
├── performance/              # Performance tests
│   ├── latency/             # Latency tests
│   ├── memory/              # Memory tests
│   └── stress/              # Stress tests
└── conftest.py              # Pytest configuration
```

#### Test Naming Conventions

```python
# Unit test for observation adapter
def test_adapt_converts_raw_to_domain():
    # Test adapter conversion logic

# Integration test for parity
def test_parity_with_official_engine():
    # Test against official engine snapshots

# Performance test for speed
def test_per_step_latency_budget():
    # Verify performance budget
```

#### Test Best Practices

1. **Unit Tests:** Test individual components in isolation
2. **Integration Tests:** Test components working together
3. **Parity Tests:** Verify correctness against official engine
4. **Performance Tests:** Ensure performance requirements
5. **Edge Cases:** Test boundary conditions and error cases
6. **Property-based Tests:** Test invariants and properties

---

## Development Environment

### Local Development Setup

#### Docker Development

```dockerfile
# Dockerfile
dockerfile-django
    FROM python:3.11-slim
    
    WORKDIR /app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y \
        gcc \
        g++ \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy requirements and install Python dependencies
    COPY requirements.txt .
    COPY requirements-dev.txt .
    RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
    
    # Copy source code
    COPY . .
    
    # Set up development user
    RUN useradd -m -u 1000 developer && chown -R developer:developer /app
    USER developer
    
    # Expose port
    EXPOSE 8000
    
    # Default command
    CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### Development Commands

```bash
# Start development server (if applicable)
docker-compose up -d

# Run tests in Docker
docker-compose run --rm app pytest

# Run linting in Docker
docker-compose run --rm app ruff check

# Execute performance tests
docker-compose run --rm app pytest tests/performance/
```

### Local Development Workflow

#### Feature Development

```bash
# Create feature branch
git checkout dev
git pull origin dev
git checkout -b feature/crop-planner

# Make changes
# Write code, tests, documentation

# Test locally
ruff check
mypy --strict
pytest

# Commit changes
git add .
git commit -m "feat(crop_planner): add window-watering optimization"

# Push to feature branch
git push origin feature/crop-planner

# Create pull request
# Fill PR template
# Request reviews
```

#### Code Review Workflow

1. **Author Responsibilities:**
   - Address all comments within 5 business days
   - Update code to satisfy reviewer requirements
   - Commit changes and push updates

2. **Reviewer Responsibilities:**
   - Provide timely feedback (within SLA)
   - Suggest improvements and alternatives
   - Ensure code quality and maintainability

3. **Approver Responsibilities:**
   - Final sign-off on merged changes
   - Ensure all requirements met
   - Update project status

---

## Project Quality Gates

### CI/CD Pipeline

```yaml
# .github/workflows/quality-gate.yaml
name: Quality Gate
on:
  push:
    branches: [main, dev, staging]
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run linting
        run: |
          ruff check
          mypy --strict
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=.
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Run parity tests
        run: pytest tests/integration/parity/ -v
      - name: Run performance tests
        run: pytest tests/performance/ -v
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Quality Gate Criteria

| Gate | Requirement | Failure Action |
|------|-------------|----------------|
| Linting | All linting rules pass | Block PR, auto-fix where possible |
| Type Checking | All type checks pass | Block PR, fix type annotations |
| Unit Tests | 90%+ coverage, all pass | Block PR, run failing tests |
| Integration | All integration tests pass | Block PR, investigate failures |
| Parity | 100% parity with official engine | Block PR, investigate discrepancies |
| Performance | Within budget, no regressions | Block PR, profile and optimize |

---

## Documentation Standards

### Documentation Structure

```
/docs/
├── architecture/              # Architecture documentation
│   ├── system_overview.md
│   ├── component_architecture.md
│   └── domain_architecture.md
├── competition/               # Competition-specific documentation
│   ├── competition.md
│   ├── game_mechanics.md
│   └── observation_model.md
├── repository/                # Repository documentation
│   ├── repository_analysis.md
│   └── coding_standards.md
├── future/                   # Future development planning
│   ├── future_research.md
│   └── innovation_roadmap.md
└── api_reference/            # API documentation
    ├── observation_reference.md
    └── action_reference.md
```

### Documentation Guidelines

1. **Technical Documentation:** Detailed, comprehensive, include code examples
2. **User Documentation:** Concise, actionable, include examples
3. **Architecture Decisions:** Document in ADR format
4. **API Documentation:** Complete reference with examples
5. **Implementation Notes:** Common patterns, gotchas, best practices

---

## Project Operations

### Incident Response

#### Severity Levels

| Severity | Description | Response Time | Action |
|----------|-------------|--------------|--------|
| Critical | Production failure, security issue | 1 hour | Immediate response, escalate |
| High | Major functionality broken | 4 hours | Urgent response, deploy fix |
| Medium | Significant degradation | 1 day | Standard response, schedule fix |
| Low | Minor issues | 1 week | Normal response, schedule fix |

#### Incident Procedure

1. **Detection:** Monitor logs, alerts, and user reports
2. **Triage:** Assess severity and impact
3. **Response:** Execute appropriate response plan
4. **Resolution:** Implement fix
5. **Post-mortem:** Document lessons learned

### Maintenance Operations

#### Bug Fix Process

1. **Log Bug:** Document issue with reproduction steps
2. **Prioritize:** Assess impact and urgency
3. **Reproduce:** Verify bug exists
4. **Fix:** Implement solution
5. **Test:** Verify fix works
6. **Deploy:** Merge to main

#### Maintenance Releases

- **Patch Releases:** Bug fixes, security patches
- **Minor Releases:** New features, minor API changes
- **Major Releases:** Significant changes, breaking changes

---

## Success Metrics

### Code Quality Metrics

- **Test Coverage:** >90% on core components
- **Linting Compliance:** 100% of commits
- **Type Safety:** 0 type errors in CI
- **Documentation:** 100% of public APIs documented

### Development Metrics

- **Cycle Time:** <48 hours from PR to merge
- **Review Time:** <24 hours for critical issues
- **Bug Resolution:** <7 days for critical bugs
- **Feature Delivery:** Weekly incremental improvements

### Platform Metrics

- **Performance:** <500ms per-step execution
- **Reliability:** 99.9% uptime
- **Scalability:** Linear performance with input size
- **Compatibility:** 100% backward compatibility

---

## Conclusion

This contributing guidelines document provides the standards, processes, and best practices for contributing to the Kaggriculture AI platform. By following these guidelines, all contributors can:

1. **Deliver high-quality code:** Consistent, maintainable, and well-tested
2. **Contribute efficiently:** Clear processes and automation
3. **Maintain quality:** Continuous integration and strict quality gates
4. **Collaborate effectively:** Clear documentation and review processes
5. **Ensure success:** Well-defined standards and metrics

The key to successful collaboration is adherence to these standards while maintaining flexibility for innovation and creativity.

**Status:** Complete ✅ | **Next Review:** End of Stage 1 ✅

---

*These guidelines will be updated regularly as the project evolves and new best practices emerge.*
