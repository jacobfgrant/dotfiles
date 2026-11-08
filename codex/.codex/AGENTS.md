# Global Conventions

## Working Together

Senior engineer, mostly self-taught. Talk to me like a peer, not a tutorial. Explain non-obvious tradeoffs and the reasoning behind decisions without teaching the basics.

When I ask a question, I'm asking a question, not prompting you to start working. Treat questions, exploration, and requests for advice as discussion: inspect relevant files to inform your answer, but wait for explicit authorization before implementing. If you think we're ready, stop and ask. Once implementation is authorized, proceed through the agreed scope without repeatedly asking whether to continue. Ask when a consequential decision falls outside that scope.

Suggest switching models only when the task specifically warrants it, explain why, and let me choose.

- Prefer a few small, readable commands over a long script. If a job needs a script, keep it short enough to read in the approval prompt; the command rules can't see inside scripts.
- If implementation shows the agreed approach won't work, stop and say so. Don't substitute a different design.
- Never run anything that prints a whole environment or `.env` file (`printenv`, `docker compose config`, `env` inside a container). Check a variable by name.
- Use explicit command names for infrastructure and destructive git operations, with the subcommand first. Global options such as `git -C` and `terraform -chdir=` sit between the command and the subcommand and get past the permission rules.


## Languages and Tools

- Python is my default language; Terraform is my infrastructure-as-code tool.
- AWS is my primary cloud; I also use SAM, Docker, and Homebrew on macOS.
- Prefer POSIX-compatible shell scripts where practical. Zsh-specific features are fine for personal tooling and interactive configuration.
- Follow a repo's existing Python tooling; for new projects, use uv (`uv add`, `uv run`; `uvx` for one-off tools).
- Install project dependencies into project-local environments during authorized implementation. The sandbox has no network, so an install needs an approval; ask for it rather than working around it. Ask before global installs.
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
- Tests should cover the behavior, not the exact implementation. Each test should earn its keep.
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
- Never force-push, hard-reset, clean untracked files, drop stashes, force-delete branches, force-remove worktrees, or discard changes you didn't make. Reverting your own change to a file is fine with approval. These restrictions also apply to aliases such as git puf, git reh, and git wrf.
- Pushing, pull requests, and merging are mine. Don't do them unless I ask.
- Use git switch for branch work. Reset, restore, and checkout all prompt for review, so reserve them for when I ask to undo something.


## AWS

- The sandbox has no network and denies `~/.aws`, and an escalation keeps the read denial, so `aws` cannot run here. If a task needs AWS data, give me the command (`aws --profile read ...`, flag first) and I'll run it and share the output.
- Never work around that. If something needs write access, stop and tell me.
- A plan isn't permission to apply, deploy, or delete. Hand me the command.


## Infrastructure and Sensitive Data

- Plans and inspection do not authorize applying, deploying, destroying, or deleting infrastructure. Obtain explicit authorization for those actions.
- Never use sudo; hand me the command instead.
- Ask before making recursive permission changes.
- Don't inspect private keys, credential stores, tokens, or secrets. The sandbox blocks `.env` files; don't ask for an escalation to read one, ask me for the variable you need. Use redacted examples when possible.
- If a tool needs credentials to authenticate, use its normal authentication flow without printing or reading credential contents into the conversation.


## Deleting Files

Deletes are rare and deliberate. Each one should be explainable in a sentence, and most work shouldn't need any.

- Temp files go in a `mktemp -d` directory, never in the repo. In codex-delegate runs, `TMPDIR` is a per-run directory the wrapper removes afterward; don't clean it up yourself.
- For test fixtures, use self-cleaning temp dirs (pytest's `tmp_path`, `tempfile.TemporaryDirectory`) instead of creating and deleting directories by hand.
- Spell out literal paths in delete commands: no variables, `~`, or broad globs. The approval prompt only helps if it shows the real target.
- Deleting from inside a script (`shutil.rmtree`, `os.remove`, `find -delete`) is still deleting and needs the same approval; only a leading `rm` prompts on its own.
- If a delete touches anything unexpected, stop and tell me. Don't assess your own damage and decide it was fine.
