Governed runtime host briefing:

Bounded governed stop reached. Return control to the user now.
- terminal stage: `xl_plan`
- source run id: `20260520T040315Z-3aabeae6`
- allowed follow-up entries: `vibe`
- next governed stage after approval: `phase_cleanup`
- approval kind: `plan_confirmation`
- preferred structured approval action: `approve_plan`
- approval instruction: Review the frozen execution plan with the user and wait for an explicit approve/revise reply before execution. Do not auto-continue into `plan_execute` or `phase_cleanup` in the same assistant turn.
- do not continue in the same assistant turn; wait for a new user message before consuming re-entry credentials
- if you intentionally continue, forward `--continue-from-run-id 20260520T040315Z-3aabeae6` and `--bounded-reentry-token ecb16ec46e80494383a3ac830a22d099` from the latest runtime summary
