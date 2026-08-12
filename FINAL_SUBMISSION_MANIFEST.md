# Final Submission Manifest

- Champion version: champion-v1.1 (ChampionPolicy, no endgame)
- Commit hash: 018492be61e1773e1739caba10140ee930ccca0e
- Configuration: RuntimeSettings defaults; policy=champion
- Model version: none (model-free)
- Dependency versions: kaggle-environments (see environment)
- Test results: 721 passed (re-run after champion change)
- Mypy results: agent/ strict clean (198 files)
- Benchmark results: 21/21 wins vs diverse opponents, ~22.5k avg coins (see CHAMPION_TOURNAMENT_RESULTS.json)
- Compliance status: PASS (see COMPETITION_COMPLIANCE_CHECKLIST.md)
- Entrypoint: main.agent (FailSafeAgent, 2-arg Kaggle-safe)
- Validation status: 720-turn completion verified, 0 fallbacks

## Submit
```bash
tar -czf submission.tar.gz main.py agent
kaggle competitions submit kaggriculture -f submission.tar.gz -m "Stage 4B champion-v1.1"
```

## Out-of-repository (must confirm manually)
- [ ] Competition rules accepted
- [ ] Kaggle CLI authenticated
