# Architecture and Behavior Decisions

Decision records are append-only historical records. Supersede an earlier decision with a new numbered record; do not rewrite history.

Required fields:

- status;
- context;
- evidence;
- decision;
- alternatives;
- gameplay effect;
- risks;
- verification;
- supersedes/superseded-by.
