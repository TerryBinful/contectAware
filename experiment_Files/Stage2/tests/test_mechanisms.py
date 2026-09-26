"""Each mechanism behaves according to its mathematical definition on the §24 fixtures."""
import numpy as np
import pytest

from ca_stability.mechanisms import REFERENCE, ScoreDensity
from fixtures import ALTERNATING, BOUNDARY, RECOVERY, STABLE_AUTH, STABLE_IMPOSTOR, TRANSITION

A, L = True, False


def run(name, seq, density=None, **p):
    cls = REFERENCE[name]
    m = cls(density=density, **p) if name in ("sprt", "hmm") else cls(**p)
    return list(m.run(seq))


@pytest.fixture
def density():
    # smooth densities: genuine mass rises linearly with the score, impostor mass falls
    return ScoreDensity(np.arange(1, 11), np.arange(10, 0, -1))


def test_interface_reset_update_state_diagnostics():
    for name, cls in REFERENCE.items():
        kw = {"theta": 0.5, "k": 3, "alpha": 0.3, "T": 2, "m": 0.2, "r": 0.2, "tau": 0.5, "beta": 0.05, "rho": 0.01}
        if name in ("sprt", "hmm"):
            m = cls(density=ScoreDensity([1, 5], [5, 1]), **kw)
        else:
            m = cls(**kw)
        assert m.state() is True                       # initial state AUTH
        m.update(0.1)
        assert isinstance(m.diagnostics(), dict)
        m.reset()
        assert m.state() is True and m.diagnostics()["t"] == 0


def test_threshold_definition():
    assert run("threshold", STABLE_AUTH, theta=0.5) == [A] * 5
    assert run("threshold", STABLE_IMPOSTOR, theta=0.5) == [L] * 5
    assert run("threshold", ALTERNATING, theta=0.5) == [A, L, A, L, A, L]
    assert run("threshold", BOUNDARY, theta=0.5) == [A, L, A, A, L]      # >= is AUTH
    assert run("threshold", TRANSITION, theta=0.5) == [A, A, A, L, L, L]
    assert run("threshold", RECOVERY, theta=0.5) == [L, L, L, A, A, A]


def test_moving_average_definition():
    # k=2: q = [.9, .5, .505, .5, .505, .5]
    assert run("moving_average", ALTERNATING, k=2, theta=0.5) == [A, A, A, A, A, A]
    assert run("moving_average", ALTERNATING, k=2, theta=0.51) == [A, L, L, L, L, L]
    # k=3 on TRANSITION: q = .92, .915, .91, .7367, .5433, .31
    assert run("moving_average", TRANSITION, k=3, theta=0.5) == [A, A, A, A, A, L]


def test_ewma_definition():
    # alpha=0.5 on TRANSITION: q = .92,.915,.9075,.65375,.486875,.3484375
    assert run("ewma", TRANSITION, alpha=0.5, theta=0.5) == [A, A, A, A, L, L]
    m = REFERENCE["ewma"](alpha=0.5, theta=0.5)
    m.run(TRANSITION)
    assert m.diagnostics()["q"] == pytest.approx(0.3484375)


def test_majority_vote_definition_and_ties():
    # k=3 on ALTERNATING votes A,L,A,L,A,L -> n=1:A(1>0.5); n=2: tie keep A; n=3: 2/3 A; then windows (L,A,L)->L ...
    assert run("majority_vote", ALTERNATING, k=3, theta=0.5) == [A, A, A, L, A, L]
    assert run("majority_vote", STABLE_IMPOSTOR, k=3, theta=0.5) == [L, L, L, L, L]


def test_debounce_definition():
    # T=2: needs 2 consecutive disagreeing raw decisions
    assert run("debounce", ALTERNATING, T=2, theta=0.5) == [A] * 6        # never 2 in a row
    assert run("debounce", TRANSITION, T=2, theta=0.5) == [A, A, A, A, L, L]
    assert run("debounce", RECOVERY, T=2, theta=0.5) == [A, L, L, L, A, A]


def test_margin_definition():
    # theta=.5, m=.2 -> lock below .4, unlock at >= .6
    assert run("margin", BOUNDARY, theta=0.5, m=0.2) == [A] * 5           # never leaves the band
    assert run("margin", TRANSITION, theta=0.5, m=0.2) == [A, A, A, A, L, L]  # .40 is not < .40
    assert run("margin", RECOVERY, theta=0.5, m=0.2) == [L, L, L, A, A, A]


def test_hysteresis_definition():
    # margin (.4/.6) AND dwell T=2
    assert run("hysteresis", TRANSITION, theta=0.5, m=0.2, T=2) == [A, A, A, A, A, L]
    assert run("hysteresis", RECOVERY, theta=0.5, m=0.2, T=2) == [A, L, L, L, A, A]
    assert run("hysteresis", ALTERNATING, theta=0.5, m=0.2, T=2) == [A] * 6
    # T=1 reduces to margin
    for seq in (TRANSITION, RECOVERY, BOUNDARY, ALTERNATING):
        assert run("hysteresis", seq, theta=0.5, m=0.2, T=1) == run("margin", seq, theta=0.5, m=0.2)


def test_trust_definition():
    # r=1, theta=.5, tau=.5: trust 1 -> 1 (clipped) ... TRANSITION: +.42,+.41,+.4 (clipped 1), -.1 -> .9, -.18 -> .72, -.29 -> .43
    assert run("trust", TRANSITION, r=1.0, theta=0.5, tau=0.5) == [A, A, A, A, A, L]
    m = REFERENCE["trust"](r=1.0, theta=0.5, tau=0.5)
    m.run(TRANSITION)
    assert m.diagnostics()["trust"] == pytest.approx(0.43)
    # bounded
    m.run(STABLE_IMPOSTOR * 0)
    assert m.diagnostics()["trust"] == 0.0


def test_sprt_definition(density):
    # stable impostor drives LLR down -> LOCKED; stable genuine keeps AUTH
    assert run("sprt", STABLE_AUTH, density, alpha=0.05, beta=0.05)[-1] == A
    out = run("sprt", STABLE_IMPOSTOR, density, alpha=0.05, beta=0.05)
    assert out[0] == A and out[-1] == L        # one frame (LLR ~ -1.2..-1.7) is not enough; two are
    m = REFERENCE["sprt"](density=density, alpha=0.05, beta=0.05)
    m.run(STABLE_IMPOSTOR)
    assert m.diagnostics()["llr"] <= 0


def test_hmm_definition(density):
    assert run("hmm", STABLE_AUTH, density, rho=0.01, theta=0.5) == [A] * 5
    out = run("hmm", np.r_[TRANSITION, STABLE_IMPOSTOR], density, rho=0.05, theta=0.5)
    assert out[:3] == [A, A, A] and out[-1] == L
    m = REFERENCE["hmm"](density=density, rho=0.05, theta=0.5)
    post = []
    for p in np.r_[TRANSITION, STABLE_IMPOSTOR]:
        m.update(p)
        post.append(m.diagnostics()["posterior_genuine"])
    assert all(np.diff(post[3:]) < 0)                                   # evidence against g accumulates


def test_sprt_thresholds_have_expected_signs():
    a, b = 0.05, 0.1
    assert np.log((1 - b) / a) > 0 > np.log(b / (1 - a))
