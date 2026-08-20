# Literature Review: Physical-Manifold Quantum Data Augmentation

**Reason for existence:** establish the defensible basis, closest prior art, and unresolved novelty risk before authorizing P1. Search performed for this bootstrap; links were checked against publisher, DOI, arXiv, or repository records. Absence from this bounded search is not proof of novelty.

## Audit Method

Search clusters:

```text
gapped Hamiltonian path; adiabatic/quasi-adiabatic continuation; spectral flow
Fubini-Study; quantum geometric tensor; fidelity susceptibility; TFIM criticality
symmetry-preserving/equivariant quantum learning; equivariant QCNN; label-preserving group action
adiabatic gauge potential; local/variational counterdiabatic; nested commutator
quantum state/data augmentation; Hamiltonian/manifold/physics-informed augmentation; QCNN augmentation
```

Sources searched included Crossref/DOI and publisher pages, arXiv, Google-indexed scholarly results, and the archived predecessor repository. Candidate inclusion required identifiable authors/title/venue or arXiv record and relevance to at least one proposed component. Classical-only image augmentation, quantum-inspired augmentation of classical pixels, error-mitigation-only methods, and generic QGAN sample generation were retained only as exclusions or broad related work when they did not transport physical quantum states.

## Evidence Map

### Gapped paths and quasi-adiabatic continuation

1. **Hastings, M. B.; Wen, X.-G. (2005). “Quasi-Adiabatic Continuation of Quantum States: The Stability of Topological Ground-State Degeneracy and Emergent Gauge Invariance.” _Physical Review B_ 72, 045141.** [DOI](https://doi.org/10.1103/PhysRevB.72.045141), [arXiv](https://arxiv.org/abs/cond-mat/0503554).
   - **Establishes:** a quasi-local continuation construction for local Hamiltonians under a suitable gap condition, with applications to stability of topological structures.
   - **Motivates:** treating ground states connected along a valid gapped Hamiltonian path as a physically meaningful family.
   - **Does not establish:** a data-augmentation algorithm, label preservation, QCNN improvement, or validity across a gap closing.
   - **Role:** theoretical foundation.

2. **Bachmann, S.; Michalakis, S.; Nachtergaele, B.; Sims, R. (2012). “Automorphic Equivalence within Gapped Phases of Quantum Lattice Systems.” _Communications in Mathematical Physics_ 309, 835–871.** [DOI](https://doi.org/10.1007/s00220-011-1380-0), [arXiv](https://arxiv.org/abs/1102.0842).
   - **Establishes:** quasi-local spectral flow/automorphic equivalence along uniformly gapped paths in the thermodynamic setting.
   - **Motivates:** an explicit path-validity and gap audit rather than treating any parameter displacement as physical transport.
   - **Does not establish:** that finite-size TFIM samples improve learning or that endpoints across phases are connected by the required gapped path.
   - **Role:** theoretical foundation.

3. **Kato, T. (1950). “On the Adiabatic Theorem of Quantum Mechanics.” _Journal of the Physical Society of Japan_ 5, 435–439.** [DOI](https://doi.org/10.1143/JPSJ.5.435).
   - **Establishes:** foundational adiabatic transport of isolated spectral subspaces under regularity and separation conditions.
   - **Motivates:** tracking the isolated ground-state branch and recording spectral gaps.
   - **Does not establish:** locality, efficient preparation, or augmentation utility.
   - **Role:** theoretical foundation.

### Quantum geometry, fidelity, and TFIM sensitivity

4. **Provost, J. P.; Vallée, G. (1980). “Riemannian Structure on Manifolds of Quantum States.” _Communications in Mathematical Physics_ 76, 289–301.** [DOI](https://doi.org/10.1007/BF02193559).
   - **Establishes:** the gauge-invariant Riemannian geometry of rays underlying the Fubini–Study metric/quantum geometric tensor.
   - **Motivates:** measuring projective displacement between neighboring ground states.
   - **Does not establish:** a useful distance band, labels, or learning improvement.
   - **Role:** theoretical foundation.

5. **Zanardi, P.; Paunković, N. (2006). “Ground State Overlap and Quantum Phase Transitions.” _Physical Review E_ 74, 031123.** [DOI](https://doi.org/10.1103/PhysRevE.74.031123), [arXiv](https://arxiv.org/abs/quant-ph/0512249).
   - **Establishes:** ground-state overlap/fidelity as a diagnostic of quantum critical change, including finite lattice systems.
   - **Motivates:** using overlap-derived locality diagnostics along the Hamiltonian family.
   - **Does not establish:** that fidelity should generate arbitrary augmented states or preserve labels.
   - **Role:** methodological precedent.

6. **You, W.-L.; Li, Y.-W.; Gu, S.-J. (2007). “Fidelity, Dynamic Structure Factor, and Susceptibility in Critical Phenomena.” _Physical Review E_ 76, 022101.** [DOI](https://doi.org/10.1103/PhysRevE.76.022101), [arXiv](https://arxiv.org/abs/quant-ph/0701077).
   - **Establishes:** relations between fidelity susceptibility, correlation functions, and critical phenomena; analyzes standard many-body examples.
   - **Motivates:** smaller parameter steps where the state is geometrically sensitive.
   - **Does not establish:** a downstream-optimal sampling rule.
   - **Role:** theoretical foundation/methodological precedent.

7. **Gu, S.-J. (2010). “Fidelity Approach to Quantum Phase Transitions.” _International Journal of Modern Physics B_ 24, 4371–4458.** [DOI](https://doi.org/10.1142/S0217979210056335), [arXiv](https://arxiv.org/abs/0811.3127).
   - **Establishes:** a review and synthesis of fidelity and fidelity-susceptibility diagnostics, including transverse-field Ising-type models.
   - **Motivates:** TFIM-specific geometry checks and finite-size caution.
   - **Does not establish:** a universal divergence at finite size or augmentation benefit.
   - **Role:** related work.

8. **Venuti, L. C.; Zanardi, P. (2007). “Quantum Critical Scaling of the Geometric Tensors.” _Physical Review Letters_ 99, 095701.** [DOI](https://doi.org/10.1103/PhysRevLett.99.095701), [arXiv](https://arxiv.org/abs/0705.2211).
   - **Establishes:** scaling relations for geometric tensors near quantum critical points.
   - **Motivates:** predeclared gap/critical-region diagnostics and geometry-adaptive P2.
   - **Does not establish:** that critical sensitivity implies useful synthetic data.
   - **Role:** theoretical foundation.

### Symmetry and equivariant QML

9. **Meyer, J. J.; Mularski, M.; Gil-Fuster, E.; Mele, A. A.; Arzani, F.; Wilms, A.; Eisert, J. (2023). “Exploiting Symmetry in Variational Quantum Machine Learning.” _PRX Quantum_ 4, 010328.** [DOI](https://doi.org/10.1103/PRXQuantum.4.010328), [arXiv](https://arxiv.org/abs/2205.06217).
   - **Establishes:** a framework for encoding symmetries in variational QML and analyzes consequences for hypothesis classes and learning.
   - **Motivates:** distinguishing data invariance from model equivariance before constructing symmetry arms.
   - **Does not establish:** that every Hamiltonian symmetry preserves a dataset label.
   - **Role:** methodological precedent/related work.

10. **Larocca, M. et al. (2022). “Group-Invariant Quantum Machine Learning.” _PRX Quantum_ 3, 030341.** [DOI](https://doi.org/10.1103/PRXQuantum.3.030341), [arXiv](https://arxiv.org/abs/2205.02261).
    - **Establishes:** constructions and learning implications for group-invariant quantum models.
    - **Motivates:** a frozen symmetry-only baseline if the task label is invariant under the chosen representation.
    - **Does not establish:** label invariance from Hamiltonian commutation alone, nor augmentation benefit.
    - **Role:** methodological precedent.

11. **Nguyen, Q. T. et al. (2024). “Theory for Equivariant Quantum Neural Networks.” _PRX Quantum_ 5, 020328.** [DOI](https://doi.org/10.1103/PRXQuantum.5.020328), [arXiv](https://arxiv.org/abs/2210.08566).
    - **Establishes:** theoretical constructions and properties of equivariant QNNs for group-structured data.
    - **Motivates:** testing model equivariance separately from data augmentation.
    - **Does not establish:** that an equivariant QCNN is required or superior for this TFIM task.
    - **Role:** related work/methodological precedent.

**Required distinction:** `U_g H U_g† = H` (Hamiltonian symmetry), `U_gρU_g† = ρ` (state symmetry), closure of the empirical dataset under `U_g` (dataset symmetry), `y(U_gρU_g†)=y(ρ)` (label invariance), and `f(U_gρU_g†)=τ_g f(ρ)` (model equivariance) are separate predicates. A symmetry augmentation is legitimate only after the fourth is justified for the frozen operational label.

### Adiabatic gauge potentials and approximate transport

12. **Sels, D.; Polkovnikov, A. (2017). “Minimizing Irreversible Losses in Quantum Systems by Local Counterdiabatic Driving.” _Proceedings of the National Academy of Sciences_ 114, E3909–E3916.** [DOI](https://doi.org/10.1073/pnas.1619826114), [arXiv](https://arxiv.org/abs/1607.05687).
    - **Establishes:** a variational principle for approximate local adiabatic gauge potentials/counterdiabatic terms.
    - **Motivates:** a later efficient approximation to exact manifold targets.
    - **Does not establish:** accurate state transport in this setting, augmentation benefit, or favorable cost.
    - **Role:** methodological precedent for P4.

13. **Claeys, P. W.; Pandey, M.; Sels, D.; Polkovnikov, A. (2019). “Floquet-Engineering Counterdiabatic Protocols in Quantum Many-Body Systems.” _Physical Review Letters_ 123, 090602.** [DOI](https://doi.org/10.1103/PhysRevLett.123.090602), [arXiv](https://arxiv.org/abs/1904.03209).
    - **Establishes:** nested-commutator approximations and Floquet realization of counterdiabatic protocols in many-body examples.
    - **Motivates:** a controlled local/commutator AGP approximation arm after an oracle PASS.
    - **Does not establish:** equivalence to exact targets, low cost on all hardware, or downstream utility.
    - **Role:** methodological precedent for P4.

14. **Kolodrubetz, M.; Sels, D.; Mehta, P.; Polkovnikov, A. (2017). “Geometry and Non-Adiabatic Response in Quantum and Classical Systems.” _Physics Reports_ 697, 1–87.** [DOI](https://doi.org/10.1016/j.physrep.2017.07.001), [arXiv](https://arxiv.org/abs/1602.01062).
    - **Establishes:** a broad synthesis connecting gauge potentials, geometry, and response.
    - **Motivates:** a common vocabulary and metrics for P2/P4.
    - **Does not establish:** a QML augmentation method.
    - **Role:** theoretical review.

### Quantum-state data augmentation and closest work

15. **West, M. T. et al. (2024). “Towards Quantum Enhanced Adversarial Robustness in Machine Learning.”** [arXiv](https://arxiv.org/abs/2306.10390).
    - **Establishes:** a quantum-learning robustness setting involving transformed/adversarial data, not the proposed exact ground-state oracle protocol.
    - **Motivates:** robustness controls and careful threat definitions.
    - **Does not establish:** Hamiltonian-manifold augmentation or blocked-parameter improvement.
    - **Role:** broad related work; not a direct baseline.

16. **Hur, T.; Kim, L.; Park, D. K. (2022). “Quantum Convolutional Neural Network for Classical Data Classification.” _Quantum Machine Intelligence_ 4, 3.** [DOI](https://doi.org/10.1007/s42484-021-00061-x), [arXiv](https://arxiv.org/abs/2108.00661).
    - **Establishes:** a QCNN-style classifier benchmark for encoded classical data.
    - **Motivates:** keeping downstream architecture fixed and reporting task-specific performance.
    - **Does not establish:** augmentation of physical quantum states.
    - **Role:** model-related work, not an augmentation precedent.

17. **Archived Conditional_QuDDPM TFIM augmentation program (2025).** [repository](https://github.com/faransansj/Conditional_QuDDPM), [authoritative archive at result commit](https://github.com/faransansj/Conditional_QuDDPM/blob/1e3ac703ff34444de473b6ecf2e5b8641c73213b/docs/tfim_state_augmentation_final_archive.md).
    - **Establishes:** a bounded negative result for q50 local-random-tangent augmentation under its frozen Protocol v2.3; also records exploratory physics- and geometry-aware controls.
    - **Motivates:** the generic/random and predecessor-style controls, pairing, split geometry audit, and minimum-effect gate.
    - **Does not establish:** failure of physical-manifold sampling or quantum augmentation in general.
    - **Role:** baseline and provenance.

## Candidate Exclusions

| Candidate class | Exclusion from closest-prior-work set |
|---|---|
| QGAN/QCBM augmentation of classical feature distributions | Generates classical samples or unconstrained distributions, not transported physical quantum states. |
| Classical image augmentation before quantum encoding | Changes classical inputs; does not test a Hamiltonian ground-state manifold. |
| Noise injection/error mitigation | Targets hardware robustness or denoising rather than train-only label-preserving OOD augmentation. |
| Symmetry-only augmentation | Potentially relevant P3 baseline, but lacks Hamiltonian-parameter transport and geometry-controlled locality. |
| Fidelity susceptibility as a phase detector | Supplies a metric/diagnostic, not an augmentation-and-downstream-evaluation pipeline. |
| Counterdiabatic state preparation | Supplies possible transport machinery, not evidence that transported states help QML. |
| The predecessor's “Hamiltonian-assisted” naming | Its archived evidence describes state-space perturbation followed by physics/geometry checks; it did not run the exact `g→g'→H(g')→|ψ₀(g')⟩` oracle proposed here. |

## Closest Combination and Novelty Risk

The closest pieces are distributed across separate literatures: gapped-path transport, fidelity geometry, symmetry-aware QML, counterdiabatic approximation, and application-specific augmentation. This audit did **not verify** a publication combining all of:

```text
Hamiltonian-parameter transport
+ exact ground-state oracle baseline
+ geometry-controlled on-manifold locality
+ physical and operational-label validation
+ train-only provenance
+ blocked-parameter downstream QCNN evaluation
```

Potential conflicts remain:

1. terminology searches may miss work described as parameter interpolation, Hamiltonian learning, curriculum sampling, phase-data enrichment, or counterdiabatic state preparation;
2. recent preprints may not be indexed consistently;
3. exact parameter resampling may be viewed as ordinary acquisition/interpolation rather than “augmentation”; the project must compare against equal-budget new-label acquisition and clearly state its operational setting;
4. symmetry and equivariance literature can preempt broad claims about “physics-aware” augmentation even if the exact combination differs;
5. the predecessor already explored physics/geometry-aware state perturbations, so novelty must be limited to the oracle-first manifold-transport question and gated sequence.

**Conclusion:** no obvious preemption was found, but novelty is unproven. P0 should run citation chaining from references 1, 5–8, 10–14 and a second database search before any novelty statement.

## Verification

```bash
grep -c '^## Evidence Map' docs/literature_review.md
grep -c 'Does not establish' docs/literature_review.md
```
