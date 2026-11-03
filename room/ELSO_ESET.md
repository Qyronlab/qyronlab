# First room case (draft; opens as a *Claim* issue when the room goes live)

**Context.** A public post described a closed loop between a classical fluid simulation (a 2D Gross–Pitaevskii solver) and a
superconducting processor: each iteration the fluid state sets gate angles on a few qubits, 1024 shots are measured, the result
feeds back into the simulation. Reported: without the fluid the loop settles at f ≈ 3.75; with the fluid, at f ≈ 2.22 with a
stable amplitude ≈ 0.89, and the difference is called a "macroscopic feedback interaction" with a classical nonlinear system.
Code, job identifiers and a preregistration are public. The author states the classical control arm is still underway.

**The claim the room would test.** *The attractor at f ≈ 2.22 depends on the quantum processor.*

**Recipe (two controls, fixed before the run).**
1. Same loop, same seeds, same 50 iterations, the processor replaced by an exact-expectation evaluator (no sampling).
2. Same loop, the processor replaced by a sampler with the vendor's published noise model of the same day (1024 shots).
3. Same loop on the processor, with the vendor calibration snapshot before and after, its `last_update` recorded.

**What would refute the claim.** If run 1 or run 2 reaches f = 2.22 ± 0.13 (the reported spread) and A = 0.89 ± 0.05, the
attractor is a property of the feedback map, and the processor's role is that of a noisy sampler.

**What would support it.** Run 3 differs from runs 1 and 2 by more than the shot-noise band in the same direction on two
different calibration days.

**Recheck.** A person reads the loop code and states what f and A are; an agent of another family reruns runs 1 and 2 from the
repository alone and reports its numbers before seeing the author's.

**Note on the t-test.** Comparing the with-fluid and without-fluid loops answers whether they differ; they differ by
construction. The test that matters is run 3 against runs 1 and 2.
