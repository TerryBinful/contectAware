# Pivot Support Pack — Continuous Authentication Decision-Layer Stability

Assembled 15 September 2026 from the reviewed project materials plus scaffolding for the recommended pivot ("PIVOT BUT PRESERVE THE EXISTING FRAMEWORK").

## Structure

```
00_audit/                              The two reviews (verdicts, findings, decision)
  MSc_Pivot_Audit.md                   Full 20-section pivot audit
  Review_1_Key_Findings.md             Condensed findings from the first review (A–D, C1–C13)

01_preserved_source_docs/              Your documents that survive the pivot (with repairs noted)
  Partial_fulfilment.docx              Problem statement, literature table, pipeline, results (results to be corrected)
  Semester_Exams_Polished_Final.docx   Dataset justification, Big Data critique, feature engineering
  22427613_-_First_Semester_Exams.docx Same as above, with Table 1 intact
  Van_Der_Walt.docx                    Reference list (resolve Vaizman duplicate; move AI tools to a declaration)
  Continuous_Authentication_Research_Paper_Draft.docx   Paper skeleton

02_superseded_for_evolution_record/    Kept ONLY as evidence for the research-evolution statement
  Extended_Abstract.docx               S1: ambient noise + magnetometer critique (RQ never tested)
  Abstract.docx                        S2: hysteresis grafted onto S1 template
  CSCD601_Rewritten_22427613.docx      S3: both RQs; H1 untested

03_pivot_scaffolding/                  New working files for the pivot
  01_preregistration_template.md       RQs, hypotheses, falsification criteria — fill BEFORE running Exp 2
  02_splice_benchmark_spec.md          Construction rules for the identity-transition benchmark
  03_mechanism_reference.md            The eight stabilisation policies, parameters, pseudocode, ANGA/ANIA-time
  04_experiment_plan.md                Exp 1–5 with order, inputs, outputs, statistics
  05_cadence_check.py                  THE FIRST THING TO RUN — verifies frame period from timestamps
  06_literature_to_add.md              External papers the refined gap depends on
```

## Deliberately excluded

`Context-Aware_Implicit_Authentication__A_Methodological_Critique_of_Cellular_Handover_Hysteresis_L.pdf`
— describes a within-subjects human-participant study, on-device processing and consent that no other document indicates was conducted. It must not travel with the pivot pack. If any part of it is reused, it must be rewritten explicitly as a hypothetical design exercise.

## Order of work

1. Run `03_pivot_scaffolding/05_cadence_check.py` on one ExtraSensory user file. Everything downstream depends on the frame period.
2. Fill `01_preregistration_template.md` and freeze it (date it, commit it).
3. Exp 1 (per-user, subject-disjoint verification baseline).
4. Build the splice benchmark per `02_splice_benchmark_spec.md`.
5. Exp 2 (mechanism bake-off at matched lockout rate).
6. Exp 3 (component ablation). Exp 4 if time.
7. Only then: write.
