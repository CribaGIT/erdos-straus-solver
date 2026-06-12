# DEEPSEEK KAGGLE CODEWORK IMPROVEMENT PROMPT
## Intent: Tier 2 Relational Search Evolution

```text
### TASK: UPGRADE KAGGLE NEUROGOLF MASTER SOLVER
**Objective:** Transition from basic pattern builders to a "Tier 2" Relational Search Engine for ARC tasks.

**Current Substrate:**
- Builders: identity, color_remap, global_symmetry, scaling, kernel_rule
- Logic: Sequential batch search with basic ONNX verification.

**Evolution Requirements:**
1. **Kirigami Grid Decomposition:** Implement logic to decompose grids into symmetrical sub-units (Hinges). Solve for the sub-unit transformation and re-assemble the global grid.
2. **Torsion-Based Fitness:** Integrate the "Torsion/Resistive Index" metric from the Pipeline. Proposed solutions (ONNX paths) should be audited for logical density. A solution with excessively high torsion relative to the task complexity should be rejected as a "hallucination."
3. **Advanced Relational Search:** Add a new builder, `build_relational_onnx`, that identifies relationships between non-adjacent objects (e.g., "Color of Object A dictates the movement of Object B").
4. **Recursive Self-Correction:** On a `verify_onnx` failure, the solver should feed the error (the delta between expected and actual output) back into the analyzer to mutate the search parameters.

**Output Format:**
- A refined `kaggle_master_solver_v5.py` implementing the Tier 2 architecture.
- Maintain the 2-hour safety check and batch-saving integrity.

**Intent:** Dominant Algorithmic Resolution of ARC Manifolds.
```
