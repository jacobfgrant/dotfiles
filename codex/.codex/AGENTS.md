# Global Conventions

## Working Together

Senior engineer, mostly self-taught. Talk to me like a peer, not a tutorial. Explain non-obvious tradeoffs and the reasoning behind decisions without teaching the basics.

When I ask a question, I'm asking a question, not prompting you to start working. Treat questions, exploration, and requests for advice as discussion: inspect relevant files to inform your answer, but wait for explicit authorization before implementing. If you think we're ready, stop and ask. Once implementation is authorized, proceed through the agreed scope without repeatedly asking whether to continue. Ask when a consequential decision falls outside that scope.

Suggest switching models only when the task specifically warrants it, explain why, and let me choose.


## Languages and Tools

- Python is my default language; Terraform is my infrastructure-as-code tool.
- AWS is my primary cloud; I also use SAM, Docker, and Homebrew on macOS.
- Prefer POSIX-compatible shell scripts where practical. Zsh-specific features are fine for personal tooling and interactive configuration.
- Install project dependencies freely in virtualenvs or equivalent isolated environments during authorized implementation. Ask before global installs.
- No Makefiles.


## Code Style

- Prefer explicit, readable code and meaningful names over cleverness.
- Functions should do one thing. Split files when they become unwieldy.
- Start simple and iterate; avoid speculative abstractions and dependencies.
- Explain intent or surprising behavior in comments, not obvious code.


## Python

- Use type hints, f-strings, and pathlib.
- Prefer dataclasses for simple structured data; use Pydantic for validation.
- Prefer the standard library where reasonable. Well-maintained libraries are welcome when justified; don't add a dependency to save a few lines.
- Write brief docstrings; omit parameter and return documentation already covered by type hints.
- Use pytest.


## Testing

I'm building testing habits. For non-trivial code:

- Suggest a testing approach alongside the implementation.
- Write tests as we go, not as an afterthought.
- Keep tests readable; they're documentation too.
- Run relevant checks before finishing.


## Git

- Work on a feature branch. Ask before committing to main or master.
- During authorized implementation, commit each coherent, validated unit of work as you go; don't accumulate uncommitted changes. A new file alone is not necessarily a commit boundary.
- An explicit request not to commit overrides that default. Leave changes uncommitted until I authorize committing; don't interpret approval to edit as permission to lift a commit prohibition.
- If commits were skipped during a session, offer logical groupings before finishing.
- Stage only changes belonging to the task; preserve unrelated work.
- Keep commits atomic and independently understandable.
- Commit subjects: imperative mood, capitalized, no trailing period, at most 50 characters. Test: "If applied, this commit will [subject]". Separate the body with a blank line and wrap it at 72 characters.
- Commit bodies explain what and why, not a narration of the implementation.
- Don't add AI attribution or Co-Authored-By trailers.
- Never force-push, hard-reset, clean untracked files, discard existing changes, drop stashes, or force-delete branches. These restrictions also apply to aliases such as git puf and git reh.
- Ask before pushing unless the current task explicitly authorizes it.
- Use git switch for branch work and git restore for files. Any git checkout invocation prompts for review, so reserve it for cases the other two can't express.


## AWS

- Every aws call requires approval. For inspection, write `aws --profile read` or `aws --profile view` with the flag first so the intent is obvious.
- Never work around that. If something needs write access, stop and tell me.
- Only when I explicitly ask for a write: `aws --profile admin ...`, for that command only. Verify the account and role first.


## Infrastructure and Sensitive Data

- Plans and inspection do not authorize applying, deploying, destroying, or deleting infrastructure. Obtain explicit authorization for those actions.
- Never use sudo; hand me the command instead.
- Ask before deleting files or making recursive permission changes.
- Don't inspect private keys, credential stores, tokens, or secrets. Ask before reading project .env files. Use redacted examples when possible.
- If a tool needs credentials to authenticate, use its normal authentication flow without printing or reading credential contents into the conversation.
- Use explicit command names for infrastructure and destructive Git operations so the action and any permission rule are clear.
