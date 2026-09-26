"""Generate the paper tables (markdown) from the frozen v2 analysis outputs.
Usage: python make_tables.py <analysis_dir> > tables.md
analysis_dir = experiment_Files/Stage2/results/mechanism_comparison_v2/analysis (commit a4a34a5)."""
import sys, json, pandas as pd
A = sys.argv[1]
f = lambda x, d=3: f"{x:.{d}f}"
ci = lambda r, c, d=3: f"{f(r[c+'_mean'],d)} [{f(r[c+'_lo'],d)}, {f(r[c+'_hi'],d)}]"
out = []
P = lambda s="": out.append(s)
NAMES = {"instantaneous":"Instantaneous","moving_average":"Moving average","ewma":"EWMA","majority_vote":"Majority vote",
 "debounce":"Debounce (dwell)","margin_dual_threshold":"Margin (dual threshold)","hysteresis":"Margin + dwell",
 "trust_model":"Trust model (dual τ)","trust_model_single":"Trust model (single τ)","sprt":"SPRT"}

# ---- Table 1: primary
pt = pd.read_csv(f"{A}/primary/primary_tests.csv")
P("### Table 1. Primary confirmatory test (target FAR 0.05; participant-level; Holm within family)"); P()
P("| Quantity | cell_H vs cell_D | cell_H vs cell_M |"); P("|---|---|---|")
g = {r.comparison: r for r in pt.itertuples()}
H, M = g["cell_H vs cell_D"], g["cell_H vs cell_M"]
rows = [("Participants paired", lambda r: f"{r.n_users_paired}"),
 ("Excluded: no feasible H / comparator cell", lambda r: f"{r.n_users_without_H} / {r.n_users_without_comparator}"),
 ("Excess transitions per sequence, H vs comparator", lambda r: f"{f(r.excess_H_mean)} vs {f(r.excess_comp_mean)}"),
 ("Paired difference, mean (median)", lambda r: f"{f(r.excess_diff_mean)} ({f(r.excess_diff_median)})"),
 ("Wilcoxon W; p; Holm p", lambda r: f"{r.wilcoxon_W:.1f}; {f(r.p_value)}; {f(r.p_holm)}"),
 ("C1 fewer excess transitions", lambda r: "met" if r.c1_fewer_excess_significant else "**not met**"),
 ("FRR difference [95% CI]", lambda r: f"{r.FRR_diff_mean:+.3f} [{f(r.FRR_diff_lo)}, {f(r.FRR_diff_hi)}]"),
 ("C2 FRR non-inferior (upper bound < +0.02)", lambda r: "met" if r.c2_FRR_noninferior else "**not met**"),
 ("Detection-failure difference [95% CI]", lambda r: f"{r.detfail_diff_mean:+.3f} [{f(r.detfail_diff_lo)}, {f(r.detfail_diff_hi)}]"),
 ("C3 detection failure non-inferior", lambda r: "met" if r.c3_detfail_noninferior else "**not met**")]
for n, fn in rows: P(f"| {n} | {fn(H)} | {fn(M)} |")
P(); P("Source: `primary/primary_tests.csv`. Criterion requires C1–C3 against both comparators.")
for t in ("0.03", "0.07"):
    s = pd.read_csv(f"{A}/secondary/factorial_far_{t}/primary_tests.csv")
    P(); P(f"Sensitivity, target FAR {t}: " + "; ".join(
      f"{r.comparison}: n={r.n_users_paired}, excess diff {r.excess_diff_mean:+.3f}, Holm p {f(r.p_holm)}, FRR diff {r.FRR_diff_mean:+.3f} [{f(r.FRR_diff_lo)}, {f(r.FRR_diff_hi)}], C1/C2/C3 = {'Y' if r.c1_fewer_excess_significant else 'N'}/{'Y' if r.c2_FRR_noninferior else 'N'}/{'Y' if r.c3_detfail_noninferior else 'N'}"
      for r in s.itertuples()) + f" (`secondary/factorial_far_{t}/primary_tests.csv`).")

# ---- Table 2: cell selection
cs = pd.read_csv(f"{A}/primary/cell_selection.csv")
P(); P("### Table 2. Calibration-selected cells per participant (target FAR 0.05)"); P()
for c in ("cell_H", "cell_D", "cell_M"):
    vc = cs[c].fillna("infeasible").value_counts()
    P(f"- **{c}**: " + ", ".join(f"{k} ({v})" for k, v in vc.items()))
P(); P("Source: `primary/cell_selection.csv`. Cell label `m<margin>_k<dwell>`.")

# ---- Table 3: response surface
rs = pd.read_csv(f"{A}/factorial/response_surface.csv"); rs = rs[rs.target == 0.05]
P(); P("### Table 3. Factorial response surface at target FAR 0.05 (θ-only tuning; cells are not paired — feasible participant sets differ)"); P()
P("| m | k | Class | n feasible | Excess / seq | FRR | Test FAR | Recovery failure | Recovery latency (censored, frames) |"); P("|---|---|---|---|---|---|---|---|---|")
for r in rs.sort_values(["margin", "dwell"]).itertuples():
    P(f"| {r.margin:g} | {r.dwell} | {r.cell_class} | {r.n_users_feasible} | {f(r.excess_transitions)} | {f(r.FRR)} | {f(r.FAR)} | {f(r.recovery_failure)} | {f(r.recovery_latency_censored,1)} |")
P(); P("Source: `factorial/response_surface.csv`.")

# ---- Table 4: families
def fam(path, target):
    mm = pd.read_csv(path)
    P(); P(f"### Table 4{'' if target=='0.05' else ('a' if target=='0.03' else 'b')}. Tuned stabiliser families at target FAR {target} (participant-level means [95% bootstrap CI])"); P()
    P("| Mechanism | n | Excess / seq | FRR | Test FAR | Recovery failure | Detection failure | Recovery latency (censored) | Detection latency (censored) |"); P("|---|---|---|---|---|---|---|---|---|")
    for r in mm.to_dict("records"):
        d = 2 if target != "0.05" else 3
        P(f"| {NAMES.get(r['mechanism'], r['mechanism'])} | {r['n_users_feasible']} | {ci(r,'excess_transitions',2)} | {ci(r,'FRR')} | {f(r['FAR_mean'])} | {f(r['recovery_failure_mean'])} | {f(r['detection_failure_mean'])} | {f(r['recovery_latency_censored_mean'],1)} | {f(r['detection_latency_censored_mean'],1)} |")
    P(); P(f"Source: `{path.split('analysis/')[-1]}`.")
    return mm
m05 = fam(f"{A}/families/mechanism_metrics.csv", "0.05")
# Table 5: tests vs instantaneous
st = pd.read_csv(f"{A}/families/statistical_tests.csv")
P(); P("### Table 5. Paired tests against instantaneous thresholding (target FAR 0.05; Holm within metric family)"); P()
P("| Mechanism | Δ excess (Holm p) | Δ FRR (Holm p) | Δ test FAR (Holm p) |"); P("|---|---|---|---|")
for mech in [m for m in NAMES if m != "instantaneous"]:
    cells = []
    for met in ("excess_transitions", "FRR", "FAR"):
        r = st[(st.metric == met) & (st.mechanism == mech)]
        cells.append("n.a." if r.empty else f"{r.mean_difference.iloc[0]:+.3f} ({r.p_holm.iloc[0]:.4f}){'*' if r.significant_holm_005.iloc[0] else ''}")
    P(f"| {NAMES[mech]} | " + " | ".join(cells) + " |")
P(); P("\\* Holm-adjusted p < 0.05. Source: `families/statistical_tests.csv`.")
# drift
fd = pd.read_csv(f"{A}/families/far_drift.csv")
P(); P("### Table 6. FAR drift, test minus calibration (target 0.05)"); P()
P("| Mechanism | Mean | Median | n |"); P("|---|---|---|---|")
for r in fd.itertuples(): P(f"| {NAMES.get(r.mechanism, r.mechanism)} | {r.mean:+.4f} | {r.median:+.4f} | {r.count} |")
P(); P("Source: `families/far_drift.csv`.")
# rank stability across operating points
P(); P("### Table 7. Rank of families by mean excess transitions and by FRR across operating points (1 = lowest)"); P()
ranks = {}
for t, p in (("0.03", f"{A}/secondary/far_0.03/mechanism_metrics.csv"), ("0.05", f"{A}/families/mechanism_metrics.csv"), ("0.07", f"{A}/secondary/far_0.07/mechanism_metrics.csv")):
    mm = pd.read_csv(p).set_index("mechanism")
    ranks[t] = (mm.excess_transitions_mean.rank(method="min").astype(int), mm.FRR_mean.rank(method="min").astype(int))
P("| Mechanism | Excess rank 0.03 / 0.05 / 0.07 | FRR rank 0.03 / 0.05 / 0.07 |"); P("|---|---|---|")
for mech in NAMES:
    P(f"| {NAMES[mech]} | " + " / ".join(str(ranks[t][0].get(mech, '–')) for t in ranks) + " | " + " / ".join(str(ranks[t][1].get(mech, '–')) for t in ranks) + " |")
from scipy.stats import spearmanr
e = pd.DataFrame({t: ranks[t][0] for t in ranks}); r_ = pd.DataFrame({t: ranks[t][1] for t in ranks})
P(); P(f"Spearman ρ of excess ranks: 0.03 vs 0.05 = {spearmanr(e['0.03'], e['0.05']).correlation:.2f}; 0.07 vs 0.05 = {spearmanr(e['0.07'], e['0.05']).correlation:.2f}. FRR ranks: {spearmanr(r_['0.03'], r_['0.05']).correlation:.2f}; {spearmanr(r_['0.07'], r_['0.05']).correlation:.2f}.")
for t in ("0.03", "0.07"): fam(f"{A}/secondary/far_{t}/mechanism_metrics.csv", t)
# ---- Table 8: concentration and score validity
sm = pd.read_csv(f"{A}/families/sequence_metrics.csv"); i = sm[(sm.target == 0.05) & (sm.mechanism == "instantaneous")]
pu = i.groupby("enrolled_user").excess_transitions.mean().sort_values(ascending=False)
sv = json.load(open(f"{A}/secondary/score_validity_summary.json")); v = pd.read_csv(f"{A}/secondary/score_validity_f3_f7.csv")
P(); P("### Table 8. Where instability sits, and what the score encodes"); P()
P("| Quantity | Value |"); P("|---|---|")
P(f"| Test sequences with zero excess transitions (instantaneous) | {(i.excess_transitions==0).sum()}/{len(i)} ({(i.excess_transitions==0).mean():.1%}) |")
P(f"| Share of per-participant mean excess transitions from top 5 of {len(pu)} participants | {pu.head(5).sum()/pu.sum():.1%} |")
P(f"| Same share on raw sequence sums | {i.groupby('enrolled_user').excess_transitions.sum().nlargest(5).sum()/i.excess_transitions.sum():.1%} |")
P(f"| Participants with any excess transition (per-participant mean > 0) | {(pu>0).sum()}/{len(pu)} |")
P(f"| Mean per-participant test AUC, F3 (full features) | {sv['mean_AUC_F3']:.3f} |")
P(f"| Mean per-participant test AUC, F7 (missingness only) | {sv['mean_AUC_F7']:.3f} |")
P(f"| Paired difference F3 − F7 [95% CI] | {sv['diff']['mean']:.3f} [{sv['diff']['lo']:.3f}, {sv['diff']['hi']:.3f}], n = {sv['diff']['n']} |")
P(); P(f"F7 columns available: {list(v.columns)}. Sources: `families/sequence_metrics.csv`, `secondary/score_validity_*`.")
print("\n".join(out))
