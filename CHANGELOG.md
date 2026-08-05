# Changelog

All significant architectural changes to the Kaggriculture AI platform are recorded here.

## [Unreleased]

### Added
- Initial repository structure per Stage 1 specification
- Agent package with adapters, decision, strategies, domain, services, planning, economy, market, inventory, crops, animals, workers, utilities, exceptions, and config subpackages
- Configuration directory with development, production, strategy, logging, market, and simulation configs
- Documentation directory with architecture, decision engine, strategy engine, market service, inventory service, worker service, crop service, animal service, observation adapter, action adapter, testing, deployment, and API docs
- Test suite with unit, integration, performance, fixtures, and replays directories
- CI/CD workflows for formatting, linting, type checking, and testing
- Docker and docker-compose support for reproducible development