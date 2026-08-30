from anomaly.scoring import calculate_health_score


def test_health_score_perfect_with_no_anomalies():
    profiles = [{"quality_score": 100.0}, {"quality_score": 100.0}]
    assert calculate_health_score(profiles, []) == 100.0


def test_health_score_penalises_by_severity():
    profiles = [{"quality_score": 100.0}]
    critical = calculate_health_score(profiles, [{"severity": "critical"}])
    warning = calculate_health_score(profiles, [{"severity": "warning"}])
    info = calculate_health_score(profiles, [{"severity": "info"}])

    assert critical < warning < info < 100.0


def test_health_score_never_negative():
    profiles = [{"quality_score": 0.0}]
    anomalies = [{"severity": "critical"}] * 20
    score = calculate_health_score(profiles, anomalies)
    assert score == 0.0
