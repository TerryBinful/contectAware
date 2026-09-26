"""Outcome definitions (docs/Stage2/METRIC_DEFINITIONS.md is the prose mirror of this file).

Notation: a session (stream) is a contiguous run; S[t] in {AUTH=True, LOCKED=False} is the
mechanism output after frame t; every session starts from a VIRTUAL AUTH state before its first
frame (a device that has just been unlocked), so a LOCKED first frame counts as a lock event.

Genuine-side (pure genuine streams; truth = genuine everywhere):
  transition at t      : S[t] != S[t-1]                      (S[-1] := AUTH)
  false lock at t      : S[t-1] = AUTH and S[t] = LOCKED
  FRR_time             : locked genuine frames / genuine frames
  ping-pong event      : a state EPISODE that starts with a transition at t and ends with another
                         transition at t' with t' - t <= W_pp (an interior episode of <= W_pp frames).
                         Each episode is counted once (events are non-overlapping by construction).
                         ping-pong lock = such an episode whose state is LOCKED (a brief false lock
                         that is undone within W_pp frames).
  rates                : per genuine hour, hours = frames x frame_period / 3600
  lockout (mean false-lock duration) = locked genuine frames / false locks

Transition side (spliced sequence, switch column C, impostor block of L frames, return C+L):
  FAR_frame            : impostor-block frames in AUTH / L   (false-accept frames, "access fraction")
  locked_at_switch     : S[C-1] = LOCKED (the impostor arrives at an already-locked device)
  first-lock delay     : min{t-C : t in [C, C+L), S[t] = LOCKED}; censored at L if none
  sustained detection  : first t in [C, C+L) with S LOCKED on [t, min(t+n_sustain, C+L));
      ANIA (frames)    : t - C;   miss if none, ANIA censored at L
  recovery latency     : min{t-(C+L) : t >= C+L, S[t] = AUTH}; censored at the suffix length if none
  lock at return       : S[C+L-1] = LOCKED  (the genuine user returns to a locked device)
"""
from __future__ import annotations

import numpy as np

GEN_FIELDS = ("frames", "locks", "unlocks", "transitions", "locked_frames", "pp_events", "pp_locks")
SEQ_FIELDS = ("far_auth_frames", "locked_at_switch", "first_lock", "ania", "miss",
              "recovery", "recovery_censored", "locked_at_return", "block_transitions")


def _prev_state(S: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """State before each frame, with a virtual AUTH before the first valid frame of the row."""
    prev = np.ones_like(S)
    prev[..., 1:] = S[..., :-1]
    first = valid & ~np.concatenate([np.zeros(valid.shape[:-1] + (1,), bool), valid[..., :-1]], axis=-1)
    return np.where(first, True, prev)


def transitions(S: np.ndarray, valid: np.ndarray) -> np.ndarray:
    return valid & (S != _prev_state(S, valid))


def genuine_stream_metrics(S: np.ndarray, valid: np.ndarray, W_pp: int) -> dict:
    """S: (K, n, T) states for n single-stream rows. Returns {field: (K, n) int arrays}."""
    V = np.broadcast_to(valid, S.shape)
    Tr = transitions(S, V)
    locks = Tr & ~S
    nxt = np.zeros_like(Tr)
    for j in range(1, int(W_pp) + 1):
        if j < Tr.shape[-1]:
            nxt[..., :-j] |= Tr[..., j:]
    pp = Tr & nxt
    return {
        "frames": np.broadcast_to(V.sum(-1), S.shape[:-1]).astype(np.int64),
        "locks": locks.sum(-1),
        "unlocks": (Tr & S).sum(-1),
        "transitions": Tr.sum(-1),
        "locked_frames": (V & ~S).sum(-1),
        "pp_events": pp.sum(-1),
        "pp_locks": (pp & ~S).sum(-1),
    }


def transition_sequence_metrics(S: np.ndarray, valid: np.ndarray, C: int, L: int, n_sustain: int) -> dict:
    """S: (K, n, T) for n spliced sequences that share switch column C and block length L."""
    K, n, T = S.shape
    V = np.broadcast_to(valid, S.shape)
    block = S[..., C:C + L]                                    # (K, n, L)
    locked = ~block
    far_auth = block.sum(-1)
    locked_at_switch = ~S[..., C - 1]
    any_lock = locked.any(-1)
    first_lock = np.where(any_lock, np.argmax(locked, axis=-1), L)
    # run length of LOCKED starting at each block frame, truncated at the block end
    r = np.zeros(locked.shape, dtype=np.int32)
    run = np.zeros((K, n), dtype=np.int32)
    for t in range(L - 1, -1, -1):
        run = np.where(locked[..., t], run + 1, 0)
        r[..., t] = run
    need = np.minimum(int(n_sustain), L - np.arange(L))[None, None, :]
    sustained = r >= need
    detected = sustained.any(-1)
    ania = np.where(detected, np.argmax(sustained, axis=-1), L)
    # recovery after return
    after = S[..., C + L:]
    after_valid = V[..., C + L:]
    auth_after = after & after_valid
    suf_len = after_valid.sum(-1)
    has = auth_after.any(-1)
    first_auth = np.argmax(auth_after, axis=-1) if after.shape[-1] else np.zeros((K, n), dtype=int)
    recovery = np.where(has, first_auth, suf_len)
    Tr = transitions(S, V)[..., C:C + L]
    return {
        "far_auth_frames": far_auth,
        "locked_at_switch": locked_at_switch,
        "first_lock": first_lock,
        "ania": ania,
        "miss": ~detected,
        "recovery": recovery,
        "recovery_censored": ~has,
        "locked_at_return": ~S[..., C + L - 1],
        "block_transitions": Tr.sum(-1),
    }


def rate_per_hour(count, frames, frame_period_s: float):
    hours = np.asarray(frames, dtype=float) * frame_period_s / 3600.0
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(hours > 0, np.asarray(count, dtype=float) / hours, np.nan)
