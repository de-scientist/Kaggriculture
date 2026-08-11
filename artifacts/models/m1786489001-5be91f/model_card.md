# Model Card

- **Model ID:** `m1786489001-5be91f`
- **Feature version:** 1
- **Environment version:** runtime-defaults-v1
- **Dataset version:** d1
- **Features:** 58 (day_norm, hour_norm, remaining_days_norm, money_norm, money_log1p, opp_money_norm, ...)
- **Value model:** ridge regression (bias=18378.900)
- **Policy model:** multinomial logistic over 6 action types
- **OOD detector:** mean-abs-z distance (train distance 0.615)

## Metrics

- **feature_version:** 1
- **n_episodes_test:** 5
- **n_episodes_train:** 20
- **n_episodes_val:** 4
- **n_rows_test:** 3595
- **n_rows_train:** 1.438e+04
- **n_rows_val:** 2876
- **ood_train_distance:** 0.6149
- **policy_best_step:** 99
- **policy_epochs:** 400
- **policy_lr:** 0.5
- **policy_reg:** 0.0001
- **policy_test_acc:** 0.4804
- **policy_test_mean_confidence:** 0.4232
- **policy_train_acc:** 0.4723
- **policy_val_acc:** 0.4791
- **seed:** 0
- **train_time_s:** 10.72
- **value_alpha:** 1
- **value_test_mae:** 1085
- **value_test_r2:** 0.8941
- **value_test_rmse:** 1403
- **value_train_mae:** 941.3
- **value_train_r2:** 0.931
- **value_train_rmse:** 1337
- **value_val_mae:** 1393
- **value_val_r2:** 0.8518
- **value_val_rmse:** 1789

## Limitations

- Predictions are only valid on states near the training distribution.
