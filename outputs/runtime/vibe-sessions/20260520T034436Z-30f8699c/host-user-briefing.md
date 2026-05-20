Governed runtime host briefing:

Bounded governed stop reached. Return control to the user now.
- terminal stage: `requirement_doc`
- source run id: `20260520T034436Z-30f8699c`
- allowed follow-up entries: `vibe`
- next governed stage after approval: `xl_plan`
- approval kind: `requirement_confirmation`
- preferred structured approval action: `approve_requirement`
- approval instruction: Review the frozen requirement document with the user and wait for an explicit approve/revise reply before planning. Do not auto-continue into `xl_plan` in the same assistant turn.
- do not continue in the same assistant turn; wait for a new user message before consuming re-entry credentials
- if you intentionally continue, forward `--continue-from-run-id 20260520T034436Z-30f8699c` and `--bounded-reentry-token 9f20495c891443f581ff61a4c5541f65` from the latest runtime summary
