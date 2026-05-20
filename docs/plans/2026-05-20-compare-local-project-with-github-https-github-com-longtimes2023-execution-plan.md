# compare local project with GitHub https://github.com/Longtimes2023/llm-wiki iden...

## Execution Summary
Governed runtime execution plan for `vibe` in mode interactive_governed.

## Frozen Inputs
- Requirement doc: /home/steven/llm-wiki/docs/requirements/2026-05-20-compare-local-project-with-github-https-github-com-longtimes2023.md
- Runtime input packet: /home/steven/llm-wiki/outputs/runtime/vibe-sessions/20260520T054106Z-c8c3438c/runtime-input-packet.json
- Source task: compare local project with GitHub https://github.com/Longtimes2023/llm-wiki iden... Deliverable: Governed implementation artifacts, verification evidence, and cleanup receipts. Constraints: Do not bypass the fixed six-stage governed runtime.; Do not widen scope silently beyond the frozen requirement document.. Update: execute merge: git merge origin/main, resolve conflicts per frozen strategy, git push origin main

- Governance scope: root
- Root run id: 20260520T054106Z-c8c3438c
- Entry intent: vibe
- Requested stop stage: phase_cleanup
- Requested grade floor: none
- Frozen route pack: ai-llm
- Frozen route skill: openai-docs
- Frozen route mode: pack_overlay
- Router/runtime skill mismatch: True
- Execution topology companion: /home/steven/llm-wiki/outputs/runtime/vibe-sessions/20260520T054106Z-c8c3438c/execution-topology.json
## Anti-Proxy-Goal-Drift Controls
Prefill from the frozen requirement doc where available. Only diverge with explicit justification.

### Primary Objective
compare local project with GitHub https://github.com/Longtimes2023/llm-wiki iden...

### Non-Objective Proxy Signals
- single sample pass only
- current test green only
- demo success only

### Validation Material Role
validation_only

### Declared Tier
Tier C

### Intended Scope
scenario_specific

### Abstraction Layer Target
_author_to_declare_

### Completion State Target
partial

### Generalization Evidence Plan
- Reuse the requirement-declared proof boundary as the starting point.
- cases: []
- note: add independent evidence before generalized completion claims

## Internal Grade Decision
- Grade: L
- User-facing runtime remains fixed; grade is internal only.
- `vibe` remains the governor and final authority for execution flow.

## Wave Plan
- Wave 1: design confirmation and implementation preparation
- Wave 2: implementation and targeted verification
- Wave 3: cleanup and residual-risk review

## Delivery Acceptance Plan
- Freeze downstream product acceptance inside the governed requirement doc and reuse it rather than inventing closeout claims later.
- Emit a per-run delivery-acceptance report during `phase_cleanup` so runtime/process success is kept separate from project-delivery success.
- Delivery-acceptance report: /home/steven/llm-wiki/outputs/runtime/vibe-sessions/20260520T054106Z-c8c3438c/delivery-acceptance-report.json
- If manual spot checks are declared in the requirement doc, final completion wording stays blocked until they are cleared or explicitly downgraded to manual review.
- Release truth aggregation remains an outer-layer gate; this run emits the per-run delivery-truth report only.

## Artifact Review Strategy
- If the frozen requirement doc declares `Artifact Review Requirements`, execution must leave behind explicit artifact-review evidence rather than relying on generic completion wording.
- Artifact review may be recorded inline in `phase-execute.json` or through a dedicated `artifact-review.json` sidecar, but one of those governed surfaces must exist when direct artifact review is required.
- Product acceptance stays blocked when required artifact review remains missing, partial, degraded, or manual-review-only.

## Code Task TDD Evidence Plan
- Reuse the frozen `Code Task TDD Evidence Requirements` section from the requirement doc rather than inventing late closeout claims.
- Reuse the frozen `Code Task TDD Exceptions` section when strict failing-first sequencing is intentionally exempted.
- Map each frozen requirement or exception to an implementation step, a targeted verification command, and a proof artifact.
- If strict failing-first sequencing is blocked, execution must record the bounded reason and fallback evidence explicitly.

## Baseline Document Quality Mapping
- Use the frozen `Baseline Document Quality Dimensions` section in the requirement doc as the authoritative list of document-artifact quality dimensions that artifact review must cover before a document delivery can claim full completion.
- Track each baseline document dimension through artifact-review annotations so the delivery-acceptance report can show which structure, formatting, completeness, reference integrity, layout stability, and output fidelity expectations were inspected.
- Treat missing document-dimension coverage as a manual-review-required hit and keep this mapping separate from UI baselines and code-task TDD evidence.

## Baseline UI Quality Mapping
- Use the frozen `Baseline UI Quality Dimensions` section in the requirement doc as the authoritative list of dimensions that artifact review must cover before a UI delivery can claim full completion.
- Track each baseline dimension through execution and artifact-review annotations so the delivery-acceptance report can show which structure, interaction, state, consistency, responsiveness, and fidelity expectations were inspected.
- Treat missing dimension coverage as a manual-review-required hit and include explicit mapping steps or targeted verification units that drive reviewers to capture the evidence the requirement doc established.

## Task-Specific Acceptance Mapping
- Reuse frozen task-specific acceptance extensions from the requirement doc instead of inventing late closeout criteria.
- Keep base delivery truth separate from task-specific expectations so each can be inspected independently during review.

## Research Augmentation Plan
- Preserve any frozen research augmentation sources from the requirement doc so later reviewers can tell which external standards strengthened the brief.
- Research augmentation may strengthen rough asks, but it must not replace the user-owned requirement surface.

## Execution Topology Snapshot
- Delegation mode: serial_child_lanes
- Review mode: two_stage_after_unit
- Specialist execution mode: native_bounded_units
- Max parallel units: 1
- Wave `wave-1` has 3 executable step(s).
  Step `wave-1-step-1` -> mode `sequential`, units `1`.
  Step `wave-1-step-2` -> mode `sequential`, units `1`.
  Step `wave-1-specialist-in_execution-group-1-serial-1` -> mode `sequential`, units `1`.

## Skill Execution Decision Plan
- The governed runtime must keep one explicit skill execution decision surface from freeze through delivery acceptance.
- Frozen decision state: approved_dispatch
- Frozen resolution mode: approved_dispatch
- Frozen decision notes: Bounded specialist recommendations were surfaced and promoted into effective approved dispatch.

## Selected Skill Execution Plan
- Selected skill execution is mandatory and bounded inside governed `vibe`; it does not transfer runtime authority away from vibe.
- This section lists only skills selected into the six-stage work through `skill_routing.selected`.
- Before specialist execution starts, governed `vibe` emits one unified disclosure for selected skills using each skill's real `skill_md_path` or `native_skill_entrypoint`.
- Each selected skill must be invoked through its native workflow, input contract, and validation style.
- Selected skill outputs remain subordinate to the frozen requirement and the governed plan.
- Dispatch openai-docs as specialist_assist.
  Binding profile: default; dispatch phase: in_execution; lane policy: inherit_grade; parallel in XL: True
  Write scope: specialist:openai-docs; review mode: native_contract; execution priority: 50
  Reason: internal specialist recommender selected a bounded specialist candidate for governed execution
  Required inputs: bounded specialist subtask contract, frozen requirement context, relevant source files or domain artifacts
  Expected outputs: bounded specialist findings or code changes, verification notes aligned with the specialist skill
  Verification: Preserve the specialist skill's native workflow, boundaries, and validation style.

## Skill Routing And Usage Evidence This disclosure records selected skills and material-use evidence. A selected skill is not a `used` claim; material use requires `skill_usage.used` plus `skill_usage.evidence`.  ### discussion_routing - Skill: openai-docs   State: routed   Why now: internal specialist recommender selected a bounded specialist candidate for governed execution   Loaded from: /home/steven/.claude/skills/vibe/bundled/skills/openai-docs/SKILL.runtime-mirror.md

## Binary Skill Usage Plan
- Used skill candidate: `openai-docs`.
- Execution must preserve the loaded skill workflow and report final use only from `skill_usage.used` / `skill_usage.unused`.
- Legacy routing fields remain audit data, not usage proof.

## Completion Language Rules
- Do not report runtime completion as downstream project delivery unless the delivery-acceptance report returns `PASS`.
- `completed_with_failures`, degraded execution, or pending manual actions must downgrade completion wording.
- Child-governed completion remains local-scope only and cannot justify root-level completion language.

## Ownership Boundaries
- One owner per artifact set.
- Parallel work must use disjoint write scopes.
- Subagent prompts must end with `$vibe`.
- Specialist help stays bounded and native-mode; it must not become a second planner or a second runtime.

## Verification Commands
- Run targeted repo verification for changed surfaces.
- Run runtime contract gate before claiming completion.
- Review the delivery-acceptance report emitted during `phase_cleanup` before using full completion language.
- Re-run mirror sync and parity validation before release claims.

## Rollback Plan
- Revert only the governed-runtime change set if verification fails.
- Do not roll back unrelated user changes.

## Phase Cleanup Contract
- Remove temp artifacts created by the wave.
- Run node audit and cleanup when needed.
- Write cleanup receipt before completion.
