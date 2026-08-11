# Model Card

- **Model ID:** `m1786485429-98dac4`
- **Feature version:** 1
- **Environment version:** runtime-defaults-v1
- **Dataset version:** d-smoke
- **Features:** 58 (day_norm, hour_norm, remaining_days_norm, money_norm, money_log1p, opp_money_norm, ...)
- **Value model:** ridge regression (bias=22821.000)
- **Policy model:** multinomial logistic over 6 action types
- **OOD detector:** mean-abs-z distance (train distance 0.576)

## Metrics

- **feature_version:** 1
- **n_episodes_test:** 2
- **n_episodes_train:** 2
- **n_episodes_val:** 0
- **n_rows_test:** 1438
- **n_rows_train:** 1438
- **n_rows_val:** 0
- **ood_train_distance:** 0.5764
- **policy_best_step:** 384
- **policy_epochs:** 400
- **policy_lr:** 0.5
- **policy_reg:** 0.0001
- **policy_test_acc:** 0.4423
- **policy_test_mean_confidence:** 0.5139
- **policy_train_acc:** 0.5494
- **policy_val_acc:** 0.5494
- **seed:** 0
- **train_time_s:** 3.99
- **value_alpha:** 1
- **value_test_mae:** 400.3
- **value_test_r2:** -0.2366
- **value_test_rmse:** 419.2
- **value_train_mae:** 2.852
- **value_train_r2:** 0.9439
- **value_train_rmse:** 4.265
- **value_val_mae:** 2.852
- **value_val_r2:** 0.9439
- **value_val_rmse:** 4.265

## Limitations

- Predictions are only valid on states near the training distribution.
