from ci_integration.policy_simulator import compute_policy_cost, confusion_parts


def test_confusion_parts_conserves_total_decisions() -> None:
    tp, fp, fn, tn = confusion_parts(precision=0.7, recall=0.8, prevalence=0.4, total=1000)
    assert round(tp + fp + fn + tn, 6) == 1000.0
    assert tp >= 0 and fp >= 0 and fn >= 0 and tn >= 0


def test_policy_cost_penalizes_false_negatives_more() -> None:
    low_fn_cost = compute_policy_cost(tp=200, fp=80, fn=20, tn=700)
    high_fn_cost = compute_policy_cost(tp=200, fp=40, fn=60, tn=700)
    assert high_fn_cost > low_fn_cost
