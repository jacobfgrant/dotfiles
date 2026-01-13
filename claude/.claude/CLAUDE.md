# Global Conventions

## About Me

Senior engineer, mostly self-taught. I know a lot but appreciate understanding the "why" not just the "how." Don't over-explain basics, but do explain non-obvious tradeoffs. Talk to me like a peer, not a tutorial.


## Languages & Tools

- Python is my default language
- Terraform for infrastructure-as-code
- Shell scripts: POSIX-compatible where practical; zsh-specific fine for personal tooling and interactive config
- AWS is my primary cloud (familiar with SAM for Lambda)
- Homebrew for macOS package management
- Docker for containerization


## Code Style

- Prefer explicit over clever
- Meaningful variable names over comments explaining bad names
- Functions should do one thing
- Keep files focused—split when they get unwieldy
- Start simple, iterate. Don't overengineer.


## Python Specifics

- Use type hints
- f-strings over .format() or %
- pathlib over os.path
- Prefer dataclasses for simple structured data (Pydantic when validation matters)
- pytest for testing
- Docstrings: Brief one-liners describing what a function does. Skip the parameter/return documentation—it gets stale during development and the type hints cover it.
- Prefer stdlib over external dependencies, but well-maintained libraries are fine, especially when they're best practice (requests, boto3, etc.). Don't add a dependency to save seven lines of code.


## Testing

I'm building testing habits. For non-trivial code:
- Suggest a testing approach alongside implementation
- Write tests as we go, not as an afterthought
- Keep tests readable—they're documentation too


## Git Commit Messages

Follow the seven rules (cbea.ms/git-commit):
1. Separate subject from body with blank line
2. Limit subject to 50 chars
3. Capitalize the subject
4. No period at end of subject
5. Imperative mood: "Add feature" not "Added feature"
6. Wrap body at 72 chars
7. Body explains what and why, not how

Test: "If applied, this commit will [your subject line]"

Prefer atomic (or at least regular and discrete) commits over kitchen-sink commits.


## Commits During Development

**IMPORTANT:** Make commits as you work, not at the end. After completing each discrete piece of functionality (a new file, a working feature, a bug fix), commit it immediately. Don't accumulate uncommitted changes.

- Commit after each logical unit of work, not in batches
- Ask before committing to main/master (prefer to develop on branches)
- Use atomic commits that can be rolled back or squashed independently
- If you forget to commit during a session, offer to create logical groupings before finishing
- DO NOT include attribution (e.g., "Co-Authored-By: Claude...") in commit messages


## What NOT to Do

- Don't add extensive comments explaining obvious code
- Don't create virtualenvs or install dependencies without asking
