# Harness compaction formats: Pi, Claude Code, Codex

Research for Slides 7.5a–d (review 2, annotation 4). Each format uses strategies from Slides 7.4a–f.
The primary sources are Pi's docs, Claude Code's docs, and the Codex source repository.

## Pi

**Source.** Pi `docs/compaction.md`, bundled with the installed agent. Source files sit under
`packages/coding-agent/src/core/compaction/`.

- **Trigger.** Automatic compaction starts when `contextTokens > contextWindow - reserveTokens`.
  The default reserve is 16384 tokens. The user can also enter `/compact [instructions]`.
- **Mechanism.** Pi keeps recent messages up to about `keepRecentTokens`, 20k estimated tokens by default. The
  setting is a target rather than a cap, because Pi cuts at the nearest valid message.
  It summarizes the older messages with an LLM. When the cut falls inside one user message's span, Pi also summarizes
  the start of that span (Original Request, Progress So Far, Context Needed to Continue) and appends it as a Turn
  Context section. With earlier messages to summarize as well, that takes a second call, and Pi merges the two summaries.
  It appends a `CompactionEntry` with the summary and `firstKeptEntryId`.
  It rebuilds context from the system prompt, summary, and recent messages.
- **Summary format.** Pi uses fixed sections: Goal, Constraints and Preferences, Progress, Key Decisions,
  Next Steps, and Critical Context. Progress contains Done, In Progress, and Blocked.
  Pi also appends cumulative file lists (`readFiles`, `modifiedFiles`). Repeated compaction includes the previous summary.
- **Strategies used.** Pi combines an abstractive summary, a recency window, and structured notes.
  The fixed sections and file lists supply the structured notes.

## Claude Code

**Source.** Claude Code docs, `context-window.md` ("What survives compaction") and
`how-claude-code-works.md` ("When context fills up").

- **Trigger.** Automatic compaction runs as the window fills. The user can also enter `/compact [focus]`.
  `/autocompact <tokens>` sets the threshold. `/rewind` summarizes from or up to a chosen message.
- **Mechanism.** Claude Code replaces conversation history with a structured summary.
  The summary request inherits the session's extended-thinking setting.
- **What it keeps.** After compaction, Claude Code reads up to five recently touched files again.
  A file over 5000 tokens returns as a path reference rather than content.
  `SessionStart` hooks with the `compact` source add their output again.
  Claude Code also restores skill text, with a limit for each skill, and removes the oldest text when it exceeds the budget.
  Subagents keep large reads outside the main context.
- **Strategies used.** Claude Code combines an abstractive summary with retrieval of recent files.
  It also adds hook output and skill text again, and uses sub-agent delegation.

## Codex

**Source.** The `openai/codex` repository. See `codex-rs/prompts/templates/compact/prompt.md` and
`summary_prefix.md`, plus `codex-rs/core/src/compact*` and `compact_retained_tool_outputs.rs`.

- **Trigger.** Automatic compaction starts when token use reaches the auto-compact limit
  (`model_auto_compact_token_limit`, or the model's default). The user can also enter `/compact`.
- **Mechanism.** The prompt calls this "context checkpoint compaction".
  It requests a handoff summary for another LLM that will resume the task.
  Codex rebuilds the history from that summary and the user's most recent messages, up to 20,000 tokens
  (`core/src/compact.rs`). `summary_prefix.md` tells the next model that it "also has access to the state of the
  tools", which persists outside the context.
- **Local and remote.** The handoff summary is the local path. With the default OpenAI provider (and Azure Responses
  providers) Codex uses the Responses API's remote compaction instead (`model-provider/src/capabilities.rs`).
- **Summary format.** The template asks for progress and key decisions, important context and user preferences,
  next steps, and critical data or references.
- **Beyond compaction.** Codex keeps resume metadata for its sessions. Its memories pipeline, off by default,
  extracts structured memory across sessions when it is enabled.
- **Strategies used.** Codex combines an abstractive handoff summary with the user's retained recent messages and,
  when enabled, structured cross-session notes.

*Correction, 2026-11-04, while building the slides: the earlier version of this section said that the next model
"receives the state of tools the previous model used" and grouped Codex under "retain tool outputs". The code at
commit de6e72a shows neither: `compact_retained_tool_outputs.rs` keeps only explicitly marked, client-authored
function outputs, and the tools' state stays outside the context. The trigger identifier was also wrong.*

*Correction, 2026-11-04, from the deck review: the Pi section said that Pi summarizes older messages "with one LLM
call" and keeps 20k tokens. Pi 1.2.0's docs/compaction.md ("Split user-message spans": "Pi generates two summaries and
merges them") and `dist/core/compaction/compaction.js` (`findProjectedCutPoint`, "keeps approximately
keepRecentTokens") show a second call for a split span and a target rather than a cap.*

## Grouping (for Slide 7.5)

| Harness | Core | Second strategy | Also |
| --- | --- | --- | --- |
| Pi | Abstractive structured summary | Recency window (keepRecentTokens) | File lists |
| Claude Code | Abstractive structured summary | Read recent files again (retrieve) | Hook output, skill text, subagents |
| Codex | Abstractive handoff summary (local path) | Retain the user's recent messages | Resume metadata, opt-in memories |

**Takeaway for the slide.** All three use an abstractive, structured summary. They combine it with
other context strategies.

Pi keeps a recent window. Claude Code reads recent files again. Codex keeps the user's recent messages.
These examples connect the strategies in Slides 7.4a–f to actual harness formats.

*Dates: Pi docs as installed 2026-11. Claude Code docs retrieved 2026-11-04. Codex `main` retrieved
2026-11-04. Treat specific defaults, such as the token thresholds and the five-file re-read, as
current values that can change.*
