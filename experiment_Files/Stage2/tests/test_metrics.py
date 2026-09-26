"""Metric definitions (docs/Stage2/METRIC_DEFINITIONS.md) on hand-constructed state sequences."""
import numpy as np
import pytest

from ca_stability.mechanisms import BATCH, StreamBatch
from ca_stability.metrics import genuine_stream_metrics, rate_per_hour, transition_sequence_metrics
from fixtures import TRANSITION

A, L = True, False


def gen(states, W_pp=5):
    S = np.array(states, dtype=bool)[None, None, :]
    v = np.ones((1, len(states)), dtype=bool)
    return {k: int(x[0, 0]) for k, x in genuine_stream_metrics(S, v, W_pp).items()}


def test_single_brief_false_lock_is_one_pingpong():
    m = gen([A, L, A, A, A, A])
    assert m["locks"] == 1 and m["unlocks"] == 1 and m["transitions"] == 2
    assert m["pp_events"] == 1 and m["pp_locks"] == 1 and m["locked_frames"] == 1


def test_locked_first_frame_counts_as_lock():
    m = gen([L, L, A])
    assert m["locks"] == 1 and m["transitions"] == 2 and m["pp_locks"] == 1


def test_pingpong_boundary_is_inclusive():
    assert gen([A] + [L] * 5 + [A], W_pp=5)["pp_events"] == 1       # episode of exactly W_pp frames
    assert gen([A] + [L] * 6 + [A], W_pp=5)["pp_events"] == 0       # W_pp + 1 frames: not ping-pong


def test_unterminated_episode_is_not_pingpong():
    assert gen([A, A, L, L])["pp_events"] == 0


def test_alternation_counts_every_interior_episode_once():
    m = gen([A, L, A, L, A, L])        # interior episodes: L(1) A(2) L(3) A(4); last L unterminated
    assert m["transitions"] == 5 and m["pp_events"] == 4 and m["pp_locks"] == 2


def test_padding_is_ignored():
    S = np.array([[A, A, L, A]], dtype=bool)[None]
    v = np.array([[False, True, True, True]])
    m = genuine_stream_metrics(S, v, 5)
    assert m["frames"][0, 0] == 3 and m["locks"][0, 0] == 1 and m["pp_events"][0, 0] == 1


def seq(states, C, Lb, n=3, valid=None):
    S = np.array(states, dtype=bool)[None, None, :]
    v = np.ones((1, len(states)), bool) if valid is None else np.array([valid])
    return {k: x[0, 0] for k, x in transition_sequence_metrics(S, v, C, Lb, n).items()}


def test_detection_recovery_and_far():
    m = seq([A, A, A, A, L, L, L, L, A], C=3, Lb=4)
    assert m["first_lock"] == 1 and m["ania"] == 1 and not m["miss"]
    assert m["far_auth_frames"] == 1 and m["recovery"] == 1 and not m["recovery_censored"]
    assert m["locked_at_return"] and not m["locked_at_switch"]


def test_sustained_requirement_truncates_at_block_end():
    m = seq([A, A, A, A, L, A, A], C=2, Lb=3)          # lock only on the last block frame
    assert m["ania"] == 2 and not m["miss"]


def test_brief_lock_is_not_sustained_detection():
    m = seq([A, A, L, A, A, A, A, A, A], C=1, Lb=6)    # 1-frame lock at block start, rest AUTH
    assert m["first_lock"] == 1 and m["miss"] and m["ania"] == 6


def test_miss_and_censored_recovery():
    m = seq([A, A, A, A, A, L, L], C=2, Lb=2)
    assert m["miss"] and m["ania"] == 2 and m["far_auth_frames"] == 2
    m = seq([A, A, L, L, L, L, L], C=2, Lb=2)
    assert m["recovery_censored"] and m["recovery"] == 3


def test_locked_at_switch():
    m = seq([A, L, L, L, A], C=2, Lb=2)
    assert m["locked_at_switch"] and m["ania"] == 0


def test_threshold_on_spec_transition_fixture():
    sb = StreamBatch.from_arrays([TRANSITION])
    S = BATCH["threshold"](sb, {}, np.array([0.5]))
    m = transition_sequence_metrics(S, sb.valid[None], 3, 3, 3)
    assert m["ania"][0, 0] == 0 and m["far_auth_frames"][0, 0] == 0


def test_rate_per_hour():
    assert rate_per_hour(2, 120, 60.0) == pytest.approx(1.0)
    assert np.isnan(rate_per_hour(1, 0, 60.0))
