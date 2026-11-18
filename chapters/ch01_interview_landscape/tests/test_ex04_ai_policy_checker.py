from datetime import date

TODAY = date(2026, 11, 18)


def test_verified_and_forum_ignored(load):
    m = load("ex04_ai_policy_checker")
    ev = [m.Evidence("coding", "forbidden", "recruiter_email", date(2026, 11, 10)),
          m.Evidence("coding", "allowed", "candidate_forum", date(2026, 11, 17))]
    assert m.assess(ev, TODAY) == {"coding": ("verified", "forbidden")}


def test_forum_only_is_unverified(load):
    m = load("ex04_ai_policy_checker")
    ev = [m.Evidence("coding", "allowed", "candidate_forum", date(2026, 11, 17))]
    assert m.assess(ev, TODAY) == {"coding": ("unverified", None)}


def test_conflict_and_likely(load):
    m = load("ex04_ai_policy_checker")
    ev = [m.Evidence("design", "forbidden", "interviewer_guide", date(2026, 11, 1)),
          m.Evidence("design", "allowed", "recruiter_email", date(2026, 11, 3)),
          m.Evidence("practical", "allowed", "recruiter_call", date(2026, 11, 12)),
          m.Evidence("practical", "partial", "recruiter_call", date(2026, 11, 16))]
    res = m.assess(ev, TODAY)
    assert res == {"design": ("conflicting", None), "practical": ("likely", "partial")}
    assert list(res) == sorted(res)


def test_stale_written_evidence(load):
    m = load("ex04_ai_policy_checker")
    ev = [m.Evidence("take_home", "allowed", "recruiter_email", date(2026, 6, 1))]
    assert m.assess(ev, TODAY) == {"take_home": ("unverified", None)}
    assert m.assess(ev, TODAY, max_age_days=365) == {"take_home": ("verified", "allowed")}


def test_questions(load):
    m = load("ex04_ai_policy_checker")
    qs = m.questions_to_ask({"a": ("verified", "allowed"), "b": ("unverified", None)})
    assert qs == ["Are AI assistants (chat or autocomplete) allowed in the b round?"]
