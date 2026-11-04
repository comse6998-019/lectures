# Harness compaction formats: Pi, Claude Code, Codex

Research for Slide 7.5 (review 2, annotation 4). Each format maps to the strategies in Slide 7.4.
Sources are primary: Pi's own docs, Claude Code's docs, and the Codex source repository.

## Pi

**Source.** Pi `docs/compaction.md`, bundled with the installed agent. Source files sit under
`packages/coding-agent/src/core/compaction/`.

- **Trigger.** Auto-compaction fires when `contextTokens > contextWindow - reserveTokens`, where the
  default reserve is 16384. Manual `/compact [instructions]` also runs it.
- **Mechanism.** Pi walks back to `keepRecentTokens`, a 20k default. It summarizes the older span
  with one LLM call. It appends a `CompactionEntry` that holds the summary and `firstKeptEntryId`.
  It rebuilds context as the system prompt, then the summary, then the kept recent messages.
- **Summary format.** A structured document with fixed sections. The sections are Goal, Constraints
  and Preferences, Progress (Done / In Progress / Blocked), Key Decisions, Next Steps, and Critical
  Context. Pi also appends cumulative file lists (`readFiles`, `modifiedFiles`). Repeated compaction
  passes the previous summary in.
- **Strategies used (per Slide 7.4).** Core is an abstractive summary. It adds a recency window and
  structured notes, which are the fixed sections and the file lists.

## Claude Code

**Source.** Claude Code docs, `context-window.md` ("What survives compaction") and
`how-claude-code-works.md` ("When context fills up").

- **Trigger.** Auto-compact runs as the window fills. `/compact [focus]` runs it by hand.
  `/autocompact <tokens>` sets the threshold. `/rewind` summarizes from or up to a chosen message.
- **Mechanism.** The conversation history becomes a structured summary. The summary request inherits
  the session's extended-thinking setting.
- **What it keeps.** Right after compaction, Claude Code re-reads up to five files touched most
  recently. A file over 5000 tokens returns as a path reference rather than content. `SessionStart`
  hooks with the `compact` source re-inject their output. Skill bodies re-inject too, truncated to a
  per-skill cap, with the oldest dropped over budget. Subagents keep large reads out of the main
  context.
- **Strategies used.** Core is an abstractive summary. It adds a recent-file re-read (retrieve),
  structured re-injection through hooks and skills, and sub-agent delegation.

## Codex

**Source.** The `openai/codex` repository. See `codex-rs/prompts/templates/compact/prompt.md` and
`summary_prefix.md`, plus `codex-rs/core/src/compact*` and `compact_retained_tool_outputs.rs`.

- **Trigger.** Auto-compaction near a token-limit window (`auto_compact_window`). Manual `/compact`
  also runs it.
- **Mechanism.** The prompt frames it as a "context checkpoint compaction", a handoff summary for
  another LLM that will resume the task. The resuming model also receives the state of the tools the
  previous model used.
- **Summary format.** The template asks for four things. They are progress and key decisions,
  important context and user preferences, the next steps, and any critical data or references.
- **Beyond compaction.** Codex keeps compaction checkpoints and resume metadata. It also runs a
  separate memories pipeline that extracts structured memory across sessions.
- **Strategies used.** Core is an abstractive handoff summary. It adds retained tool outputs and
  structured cross-session notes.

## Grouping (for Slide 7.5)

| Harness | Core | Second strategy | Also |
| --- | --- | --- | --- |
| Pi | Abstractive structured summary | Recency window (keepRecentTokens) | File lists |
| Claude Code | Abstractive structured summary | Re-read recent files (retrieve) | Hook and skill re-inject, subagents |
| Codex | Abstractive handoff summary | Retain tool outputs | Resume metadata, memories |

**Takeaway for the slide.** All three lead with an abstractive, structured summary. Each then adds a
different second strategy.

Pi keeps a recent window. Claude Code re-reads recent files. Codex retains tool state. This is the
Slide 7.4 taxonomy seen in shipped systems.

*Dates: Pi docs as installed 2026-11. Claude Code docs retrieved 2026-11-04. Codex `main` retrieved
2026-11-04. Treat specific defaults, such as the token thresholds and the five-file re-read, as
current values that can change.*
