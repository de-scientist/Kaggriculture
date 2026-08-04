# ROLE

You are an elite engineering organization consisting of:

• Principal Software Architect
• Principal AI Engineer
• Principal Reinforcement Learning Researcher
• Principal Operations Research Scientist
• Senior Python Engineer
• Senior Systems Engineer
• Senior Backend Engineer
• Senior Data Engineer
• Senior Machine Learning Engineer
• Senior DevOps Engineer
• Senior Game AI Engineer
• Senior Algorithm Designer
• Senior Technical Writer

You have been tasked with designing an enterprise-grade autonomous AI system for the Kaggriculture Kaggle Competition.

Your responsibility is NOT to implement the AI yet.

Your responsibility is to completely understand the competition, reverse engineer the official repository, study every game mechanic, and design the complete software architecture that every future stage will follow.

Treat this as the Technical Discovery and System Design phase of a multi-million dollar software project.

The output should be detailed enough that another engineering team could build the entire project using only this document.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIMARY OBJECTIVE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Study the following as the ONLY authoritative sources:

• README.md
• agent.md
• Official Kaggriculture documentation
• Official competition rules
• Official observation schema
• Official action schema
• Official environment API
• Starter project source code
• Local testing workflow

DO NOT redesign or replace the Kaggle architecture.

Instead:

Understand it.

Document it.

Preserve it.

Extend it.

Everything we build in future stages must remain 100% compatible with the official repository.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT GOALS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build an AI platform that can eventually support:

• Baseline deterministic agents
• Rule-based systems
• Utility-based decision making
• Greedy optimization
• Monte Carlo Tree Search
• Beam Search
• Evolutionary algorithms
• Reinforcement Learning
• Self-play training
• Market prediction
• Experiment management
• Simulation
• Explainable AI
• Analytics
• Benchmarking

However—

Stage 0 writes ZERO production AI.

Instead it designs the complete blueprint.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 1

REPOSITORY ANALYSIS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Study the official repository in detail.

Document:

• Overall architecture
• Folder structure
• Entry point
• Agent lifecycle
• Observation pipeline
• Action pipeline
• Environment interaction
• Local testing workflow
• Submission workflow
• Validation process
• Helper utilities
• Existing abstractions
• Existing interfaces
• Existing models
• Existing constants
• Existing enumerations
• Existing helper functions

For every file explain:

Purpose

Responsibilities

Dependencies

Future extension opportunities

Never duplicate functionality that already exists.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 2

GAME ANALYSIS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reverse engineer every game mechanic.

Document:

Episode lifecycle

Turn processing

Daily cycle

Movement

Energy system

Crop lifecycle

Animal lifecycle

Worker lifecycle

Hiring system

Market system

Town demand

Inventory

Storage

Land expansion

Quadrants

Fertilizer

Selling

Buying

Weeds

Resource generation

Resource consumption

Winning conditions

Losing conditions

Unknown mechanics

Assumptions

Create diagrams wherever useful.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 3

OBSERVATION MODEL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Study the official observation schema.

Document every field.

Explain:

Purpose

Type

Meaning

Relationships

Ownership

Lifecycle

Mutability

Frequency of change

Do NOT redesign the observation.

Instead design an Adapter Layer.

Official Observation

↓

Observation Adapter

↓

Rich Domain Objects

The Adapter must preserve complete compatibility.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 4

ACTION MODEL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Study every official action.

Document:

Purpose

Inputs

Outputs

Preconditions

Postconditions

Constraints

Failure cases

State changes

Dependencies

Opportunity cost

Future reward

Expected ROI

Design an Action Adapter.

Official Action

↓

Domain Action

↓

Validation

↓

Execution

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 5

DOMAIN MODEL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Design a Domain Driven Design model.

Represent:

GameState

Player

Opponent

Farm

Tile

Crop

Animal

Inventory

Farmer

FarmHand

Market

Town

Shop

Quadrant

Prices

Resources

Turn

Season

Action

Every domain object should define:

Responsibilities

Attributes

Relationships

Business rules

Validation

Lifecycle

Ownership

Invariants

No infrastructure concerns.

No serialization logic.

No Kaggle API code.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 6

SYSTEM ARCHITECTURE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Preserve the official repository.

Layer our architecture on top.

Example:

Official Kaggle Environment

↓

Official Observation

↓

Observation Adapter

↓

Domain Model

↓

Decision Engine

↓

Strategy Manager

↓

Action Validator

↓

Action Ranker

↓

Official Kaggle Action

↓

Official Environment

Document every layer.

Explain why each exists.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 7

PROJECT STRUCTURE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Design a modular architecture extending—not replacing—the official repository.

Suggested additions:

decision/

strategies/

planning/

market/

economy/

workers/

crops/

animals/

inventory/

analytics/

simulation/

optimization/

utilities/

config/

tests/

experiments/

benchmarks/

Explain:

Purpose

Dependencies

Public interfaces

Extension points

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 8

AI ARCHITECTURE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Design the future AI.

Create modular components:

Decision Engine

Strategy Manager

Action Generator

Action Validator

Action Ranker

Crop Planner

Animal Planner

Market Planner

Expansion Planner

Worker Scheduler

Inventory Manager

ROI Analyzer

Risk Analyzer

Simulation Interface

Explainability Engine

Future RL Interface

Future MCTS Interface

Future Evolutionary Interface

Each component should communicate through interfaces rather than concrete implementations.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 9

DECISION PIPELINE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Design the complete reasoning pipeline.

Official Observation

↓

Observation Adapter

↓

Domain Objects

↓

Generate Candidate Actions

↓

Validate Actions

↓

Evaluate Strategies

↓

Aggregate Scores

↓

Rank Actions

↓

Choose Best Action

↓

Convert to Official Kaggle Action

↓

Return Action

Document every stage.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 10

STRATEGY ROADMAP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Plan the evolution of strategies.

Stage 1

Baseline deterministic

Stage 2

Heuristic

Stage 3

Economic

Stage 4

Utility scoring

Stage 5

Monte Carlo Tree Search

Stage 6

Beam Search

Stage 7

Genetic Algorithms

Stage 8

Reinforcement Learning

Stage 9

Hybrid AI

Explain:

Purpose

Advantages

Limitations

Complexity

Integration plan

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 11

SOFTWARE ENGINEERING STANDARDS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Define:

Python version

Coding conventions

Naming conventions

Type hints

Docstrings

Logging

Exception hierarchy

Configuration

Dependency management

Linting

Formatting

Testing

CI/CD

Docker

Git workflow

Versioning

Documentation standards

Performance profiling

Benchmarking

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 12

TESTING STRATEGY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Design a complete testing framework.

Unit Tests

Integration Tests

Replay Tests

Regression Tests

Performance Tests

Stress Tests

Simulation Tests

Deterministic Seed Tests

Acceptance Tests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 13

RISK ANALYSIS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Identify technical risks.

Examples:

Repository changes

Competition rule changes

Incorrect assumptions

Market misunderstanding

Architecture drift

Performance bottlenecks

Decision latency

Memory usage

Simulation mismatch

RL instability

For every risk provide mitigation strategies.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIVERABLE 14

FINAL TECHNICAL DESIGN DOCUMENT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Produce a professional engineering specification including:

Executive Summary

Repository Analysis

Competition Analysis

Architecture Overview

Folder Structure

Component Diagrams

Sequence Diagrams

Data Flow Diagrams

Domain Model

Decision Pipeline

Strategy Roadmap

Engineering Standards

Testing Strategy

Risk Analysis

Implementation Roadmap

Future AI Roadmap

The document should be written as if it will guide a senior engineering team for the remainder of the project.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUALITY REQUIREMENTS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The final output must:

• Preserve compatibility with the official Kaggriculture repository.
• Never duplicate official functionality.
• Extend the existing architecture cleanly.
• Follow Clean Architecture and Domain-Driven Design.
• Be modular, testable, maintainable, and extensible.
• Provide clear extension points for advanced AI techniques.
• Serve as the authoritative blueprint for Stages 1 through 4.

Do not write production AI code in this stage unless it is required to illustrate an architectural concept.

The primary deliverable is a comprehensive technical and architectural specification that will guide the implementation of a competition-winning Kaggriculture AI agent.