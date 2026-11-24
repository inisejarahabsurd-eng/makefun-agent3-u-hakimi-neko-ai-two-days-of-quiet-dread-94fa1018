# Transcripts

Place the session bundle produced by `node cli/makefun.mjs bundle` here as
`<name>.tar.gz`, then verify with `node cli/makefun.mjs check <name>.tar.gz`.

Bundle every session that worked on this entry: the top-level session and every
subagent/worker/child it started, each whole, after subagents finish. Use
`--session <file>` to add files; `--no-discover` to take exactly those.

Redact only personal details of the person this was built for (full name, email,
phone, address, DOB, government ID or bank account numbers) via `--redact "<text>"`
or `--redact-file <path>`. Never redact code, shipped files, commands, tool output,
or your reasoning.