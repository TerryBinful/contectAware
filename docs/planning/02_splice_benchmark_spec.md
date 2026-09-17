# Splice Benchmark Specification — Identity-Transition Sequences from ExtraSensory

**Purpose.** ExtraSensory contains no identity changes; the responsiveness axis (ANIA-time) cannot be measured on it natively. This benchmark constructs evaluation sequences with known, timestamped identity transitions from the existing data. Precedent for spliced session-hijack evaluation: Mondal et al. 2018 (closed/open-set impostor injection), Garabato et al. 2022 (weighted sliding windows on hijacked sessions), Zhang et al. 2025 (1,344 simulated attacks).

**Assumption to state in the thesis:** transfer of the device is abrupt (theft / unattended pickup). Gradual co-use is out of scope.

---

## 1. Inputs

- Per-user feature files `<uuid>.features_labels.csv` with `timestamp`, feature columns, `label:*` columns.
- Verified frame period Δt from `05_cadence_check.py`.
- User partition from Experiment 1: for each genuine user *g*, the set of **held-out impostor users** I(g) not used in g's training.
- The fixed classifier for *g*, producing P(genuine | frame).

## 2. Genuine segments

For user *g*, take the **test-period** chronological stream only (final 20%). Define *contiguous runs* as sequences where consecutive timestamp gaps ≤ 2·Δt (do not splice across recording gaps — the gap itself would act as a change cue).

## 3. Impostor blocks

For impostor *i* ∈ I(g), extract contiguous runs of length ≥ L_max from *i*'s **test-period** stream (never training, to keep the impostor unseen).

Block lengths **L ∈ {3, 10, 30, 60} minutes** → convert to frames as ⌈L / Δt⌉.

## 4. Two attack conditions

### Condition X — cross-context (unconstrained)
Choose any impostor run of length L. Represents theft with the attacker leaving the environment. Optimistic bound on detection.

### Condition M — context-matched
At the splice index in *g*'s stream, compute g's **dominant activity label** over the preceding W frames (W = ⌈5 min / Δt⌉) from a fixed label set:

```
CONTEXT_LABELS = [
  "label:SITTING", "label:LYING_DOWN", "label:FIX_walking", "label:FIX_running",
  "label:STANDING", "label:PHONE_IN_POCKET", "label:PHONE_IN_HAND",
  "label:PHONE_ON_TABLE", "label:IN_A_CAR", "label:AT_HOME", "label:AT_WORK"
]
```
(Verify exact column names in your files; ExtraSensory labels are prefixed `label:` and are sparse — many frames are unlabelled.)

Choose an impostor run whose dominant label over its first W frames matches. If no match exists for that (g, i, L), skip and log it. Report **coverage** = fraction of (g, L) combinations for which ≥1 matched impostor was found.

Labels are used **only for alignment**. They are never features.

## 5. Sequence assembly

```
seq = g_run[0 : s] ++ i_block[0 : Lf] ++ g_run[s : ]
truth = [1]*s ++ [0]*Lf ++ [1]*(len(g_run) - s)
switch_idx  = s
return_idx  = s + Lf
```

- Splice index *s* drawn uniformly from [W, len(g_run) − W] so that both genuine flanks are ≥ W frames.
- Generate **≥ 10 sequences per (g, condition)**, cycling across impostors in I(g) and across L. Fix the RNG seed; store `(g, i, L, s, condition, seed)` in a manifest CSV.
- Do **not** recompute features across the splice boundary; the classifier is applied frame-wise to the pre-computed feature vectors, so no artefact is introduced at the seam.

## 6. Outputs per sequence

The classifier gives `p[t]`. Each mechanism gives a state sequence `state[t] ∈ {LOCKED, AUTH}`. From `state` and `truth`:

- **False locks (genuine segments):** count of AUTH→LOCKED transitions where truth = 1 (excluding the return_idx region of ⌈2 min/Δt⌉ frames after return, which is counted under recovery).
- **ANGA-time** = total genuine minutes / false locks (per user, pooled over their sequences).
- **Detection frame** = first t ≥ switch_idx such that state[t..t+n) = LOCKED for n consecutive frames (n from pre-registration).
- **ANIA-time** = (detection frame − switch_idx) · Δt. If no detection before return_idx → **miss**.
- **Recovery time** = first t ≥ return_idx with state = AUTH, minus return_idx, · Δt.
- **Ping-pong rate** = sign-alternating transitions within W_pp frames, per genuine hour.

## 7. Validation / test partition of sequences

Sequences are partitioned by **genuine user**, not by sequence: parameter sweeps use sequences from a validation subset of users; final results use sequences from the remaining users. Alternatively use the validation-period frames of each user for sweeps and test-period frames for results — state which.

## 8. Manifest schema

```
manifest.csv
seq_id, genuine_uuid, impostor_uuid, condition (X|M), L_min, L_frames,
splice_idx, return_idx, dominant_label_g, dominant_label_i, seed, partition (val|test)
```

## 9. Sanity checks before use

1. Distribution of Δt within every sequence: no gap > 2·Δt across the seam.
2. Instantaneous-threshold ANIA-time in condition X should be short (sanity: the room changed). If it is not, the classifier is not seeing the impostor at all — stop and investigate.
3. Condition M ANIA-time ≥ condition X for the instantaneous threshold. If not, matching is not working.
4. Coverage report for M.
