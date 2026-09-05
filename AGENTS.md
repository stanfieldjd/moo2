# Repository Instructions

Read `PROJECT_RULES.md` and `WORKBENCH.md` before changing this repository.

For reverse engineering:

- Preserve raw output unchanged.
- Put interpretation in `decompilation/annotated/`.
- Record symbols in `symbols/` with address, evidence, confidence, and status.
- Record behavioral conclusions in `docs/research/`.
- Create or update a decision record for every intentional departure from observed v1.31 behavior.
- Add deterministic regression coverage before treating behavior as implemented.
- Never commit original game files or reconstruct proprietary assets.
- Never invent recovered work.
- Never use a workaround where the root cause can be corrected.

Before reporting completion, verify tests, the Git commit, and the GitHub file state.
