# Literature to Add — papers the refined gap depends on

These were surfaced by adversarial search during the pivot audit and are absent from the current reference list. Verify each against the full text before citing; the annotations below record *what the paper is cited for*, which is what the examiner will check.

## Evaluation standard (must cite — kills the "non-standard metrics" clause of the old gap)

- **Bours, P. A. H. et al. (2015).** Performance evaluation of continuous authentication systems. *IET Biometrics.*
  Cited for: ANGA/ANIA as the CA performance indicators; the distinction between periodic and continuous authentication; the reporting method. https://consensus.app/papers/details/9a94e638497550739397a806385478dc/

- **Mondal, S. & Bours, P. (2017).** A study on continuous authentication using a combination of keystroke and mouse biometrics. *Neurocomputing.*
  Cited for: a modality-agnostic dynamic trust model as a post-processing layer; a CA performance reporting technique; lockout/detection counts. **Closest structural prior art to the February 2026 contribution claims.** https://consensus.app/papers/details/a31eaf282d045b95950c3e01c9ec3fa3/

- **Kiyani, A. et al. (2020).** Continuous user authentication featuring keystroke dynamics based on robust recurrent confidence model and ensemble learning. *IEEE Access.*
  Cited for: two-threshold (alert/final) confidence recurrence evaluated with ANGA/ANIA — i.e., dual thresholds in CA already published. Include as a comparison arm. https://consensus.app/papers/details/0d58ae55220951f88239003b114b84a5/

## Comparative-gap support (must cite — the surviving clause)

- **Ryu, R. et al. (2021).** Continuous multimodal biometric authentication schemes: a systematic review. *IEEE Access.*
  Cited for: "lack of comparative analysis" of fusion/decision models; security and usability under-addressed. https://consensus.app/papers/details/a64624f1282052169df7fcacc527bfe8/

- **Raghu, S. T. P. et al. (2023).** Decision-change informed rejection improves robustness in pattern recognition-based myoelectric control. *IEEE J. Biomedical and Health Informatics.*
  Cited for: the methodological template — eight post-processing schemes compared under dynamic class transitions, measuring error and decision-stream volatility; explicit statement that schemes had previously been tested individually. **Frame your contribution as transferring this comparative methodology to CA.** https://consensus.app/papers/details/67adefa95029585297f2e295ef238ac9/

## Intrusion-window quantification (cite to show it is measured per mechanism, not compared)

- **Mahbub, U. et al. (2018).** Continuous authentication of smartphones based on application usage. *IEEE TBIOM.* HMM-based CA; intrusion detected within ~2.5 min. https://consensus.app/papers/details/91a5ffa1b22654819139c9ebe90e68eb/
- **Zhang, Y. et al. (2025).** Trustworthy interaction model: continuous authentication using time–frequency joint analysis of mouse biometrics. *Behaviour & Information Technology.* Dynamic trust model; 1,344 simulated attacks; mean 1.63 min to lockout. https://consensus.app/papers/details/efa2960bf8915e08a168b9783383fa75/
- **Garabato, D. et al. (2022).** AI-based user authentication reinforcement by continuous extraction of behavioural interaction features. *Neural Computing and Applications.* Weighted sliding windows; session-hijack detection protocol — precedent for the splice benchmark. https://consensus.app/papers/details/e75ac2c25f725853b6cc1d6b02193ab0/
- **Fonseca, A. et al. (2026, arXiv, unreviewed).** VIGIL: verifying identity via gated intermittent likelihoods. Dual-state transition machine; three-zone decision; time-to-detect focus. Cite cautiously as a preprint. https://consensus.app/papers/details/8d6335cdae475aa0baec7b2e394d4438/

## Sequential decision baselines

- **Allano, L. et al. (2010).** Tuning cost and performance in multi-biometric systems: a consistent view of fusion strategies based on the SPRT. *Pattern Recognition Letters.* SPRT with automatically tuned thresholds. https://consensus.app/papers/details/94722f8099df509f844eb5e6c5d20cb5/
- **Shen, C. et al. (2017).** Performance analysis of multi-motion sensor behavior for active smartphone authentication. *IEEE TIFS.* Markov-based decision procedure for the authentication decision. https://consensus.app/papers/details/8c1bf595c89455a9a42b2047d2ed8c68/
- **Zhang, X. et al. (2022).** sAuth: a hierarchical implicit authentication mechanism for service robots. *J. Supercomputing.* Sliding-window trust explicitly to damp fluctuating identification. https://consensus.app/papers/details/dfa46d13a6915fc3b0963a87cb37e8d0/

## Same-dataset comparator (must cite)

- **Kaur, D. et al. (2026).** Novel explainable CNN-LightGBM model for smartphone continuous authentication. *IEEE Access.* ExtraSensory; average accuracy 98.7%; average EER 2.07%; per-user reporting. https://consensus.app/papers/details/165f40d679cd5fe3b5acf4f16bb1b759/

## Reference hygiene (from Review 1)

- Resolve Vaizman 2017 (IEEE Pervasive 16(4)) vs 2018 (17(4), different DOI) — one is wrong.
- "Khan et al. (2020)" — locate or remove.
- Replace the `aimjournals.com` source for hysteresis-in-security with 3GPP TS 36.331 + a control-systems text.
- Move Google Colab / SciSpace / Gemini / Claude from References to an AI- and tools-use declaration.
- Two different "Liang et al." (2020 IoT survey; 2021 Auth+Track) — disambiguate.
