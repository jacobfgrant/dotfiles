# Global Conventions

## About Me

Senior engineer, mostly self-taught. I know a lot but appreciate understanding the "why" not just the "how." Don't over-explain basics, but do explain non-obvious tradeoffs. Talk to me like a peer, not a tutorial.


## How We Work

When I ask a question, I want an answer and a discussion, not the start of implementation. I like to plan things out and understand the why and the how before code gets written, so wait until I tell you to build. If you think we're ready, say so and ask.

- Prefer a few small, readable commands over a long script. If a job needs a script, keep it short enough that I can read it in the prompt.
- If implementation shows the agreed approach won't work, stop and say so. Don't substitute a different design.
- Never run anything that prints a whole environment or `.env` file (`printenv`, `docker compose config`, `env` inside a container). Check a variable by name.
- When a tool needs credentials, use its normal authentication flow. Never print or read credential contents into the conversation.
- Use explicit command names for infrastructure and destructive git operations, with the subcommand first. The permission rules match literal text, so aliases and global options like `git -C` or `terraform -chdir=` slip past them.


## Languages & Tools

- Python is my default language, but I'm open to alternatives
- Follow a repo's existing Python tooling; for new projects, use uv (`uv add`, `uv run`; `uvx` for one-off tools)
- Terraform for infrastructure-as-code
- Shell scripts: POSIX-compatible where practical; zsh-specific fine for personal tooling and interactive config
- AWS is my primary cloud (familiar with SAM for Lambda)
- Homebrew for macOS package management
- Docker for containers
- Install project dependencies freely into project-local environments; ask before installing anything globally
- No Makefiles


## Code Style

- Explicit over clever
- Start simple and iterate; don't overengineer
- Comments explain why, not what, and only when necessary
- Keep files focused; split them when they get unwieldy


## Testing

I'm building testing habits. For non-trivial code, suggest a testing approach alongside the implementation and write tests as we go rather than afterward. Keep tests readable; they double as documentation. Tests should cover the functionality, not the exact implementation. Each test should earn its keep.


## Git

Pushing, pull requests, and merging are mine. Don't do them unless I ask.

Never force-push, hard-reset, clean untracked files, drop stashes, force-delete branches, or force-remove worktrees. The permission rules deny the common spellings; the rest is on you.


### Commit Messages

Follow the seven rules (cbea.ms/git-commit):
1. Separate subject from body with blank line
2. Limit subject to 50 chars (DO NOT go over)
3. Capitalize the subject
4. No period at end of subject
5. Imperative mood: "Add feature" not "Added feature"
6. Wrap body at 72 chars
7. The body explains what and why, not how

Test: "If applied, this commit will [your subject line]"

Prefer atomic (or at least regular and discrete) commits over kitchen-sink commits.


### Commits During Development

Commit after each discrete, working piece of functionality instead of saving everything for the end. Small, atomic commits are easier to review, revert, and squash.

- Work on branches; ask before committing to main/master
- Stage only the files that belong to the task; never `commit -a` past unrelated edits in the tree
- If I say not to commit, that stands until I lift it; approval to edit isn't approval to commit
- If changes have piled up, offer to split them into logical commits before we wrap up


## AWS

Sessions are pinned to read-only AWS profiles (`read`, `view`) on purpose.

- Write `aws --profile read ...` with the flag first; that form is pre-approved
- Never work around the pin. If something needs write access, stop and tell me.
- Only when I explicitly ask for a write: `AWS_CONFIG_FILE=~/.aws/config aws --profile admin ...`, for that command only. Confirm the account and role with `sts get-caller-identity` under that profile first.
- A plan isn't permission to apply, deploy, or delete. Hand me the command unless told otherwise.


## Deleting Files

Deletes are rare and deliberate. Each one should be explainable in a sentence, and most work shouldn't need any.

- The session scratchpad is disposable; don't clean it up. Need a fresh start? Make a new subdirectory.
- For test fixtures, use self-cleaning temp dirs (pytest's `tmp_path`, `tempfile.TemporaryDirectory`) instead of creating and deleting directories by hand.
- When something does need deleting, prefer `trash` (built into macOS, recoverable) over `rm` where it exists.
- Spell out literal paths in delete commands: no variables, `~`, or broad globs. Shell state doesn't carry between Bash calls, so a variable set earlier may be empty or point somewhere else.
- Deleting from inside a script (`shutil.rmtree`, `os.remove`, `find -delete`) is still deleting; the same rules apply.
- If a delete touches anything unexpected, stop and tell me. Don't assess your own damage and decide it was fine.


## Second Opinions

The `codex-delegate` skill is the contract for handing work to OpenAI models through Codex: run the wrapper directly for reviews, consults, and delegated implementation. Ask Sol for a review proactively once a substantive change is ready, and for an outside opinion when stuck. Two rules stand regardless: verify Codex's findings before acting on them, and never widen Codex's permissions to make a run succeed; surface the blocked operation instead.
