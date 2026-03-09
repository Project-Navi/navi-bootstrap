# Contributing

How to set up a development environment, run tests, and submit changes.

---

## Development setup

```bash
git clone https://github.com/Project-Navi/navi-bootstrap.git
cd navi-bootstrap

# Install all dependencies (creates venv, installs package + dev deps)
uv sync

# Verify everything works
uv run pytest tests/ -v
```

---

## Quality checks

Run all checks before submitting a PR:

```bash
# Lint
uv run ruff check src/navi_bootstrap/ tests/

# Format
uv run ruff format --check src/navi_bootstrap/ tests/

# Type check (strict mode)
uv run mypy src/navi_bootstrap/

# Security scan
uv run bandit -r src/navi_bootstrap -ll

# All tests
uv run pytest tests/ -v

# Pre-commit hooks (all at once)
pre-commit run --all-files
```

### Standards

- **Line length:** 100 characters
- **Linter:** ruff (select: E, F, I, N, W, UP, B, RUF, C4)
- **Type checking:** mypy strict mode
- **Security:** bandit + detect-secrets with baseline

---

## Testing

Tests live in `tests/`. The adversarial suite lives in `tests/adversarial/`.

```bash
# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ -v --cov=src/navi_bootstrap --cov-report=term-missing

# Single test file
uv run pytest tests/test_engine.py -v
```

- All new code must have tests
- Aim for meaningful coverage, not 100% line coverage
- Adversarial tests (`tests/adversarial/`) cover security edge cases --- don't weaken them

---

## Code style

- Use type hints on all public functions and methods
- Keep functions focused --- one responsibility per function
- Prefer explicit over implicit
- Document non-obvious behavior with comments (not obvious code)
- Avoid premature abstraction --- three similar lines is better than a premature helper

---

## Commit conventions

Use conventional commits:

| Prefix | Use for |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `test:` | Test additions or changes |
| `docs:` | Documentation |
| `chore:` | Maintenance, dependencies |
| `refactor:` | Code restructuring without behavior change |

Keep commits atomic --- one logical change per commit. Write messages that explain *why*, not just *what*.

---

## Pull request process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run the full quality check suite
4. Submit a PR with a clear description
5. Address review feedback

### PR checklist

- [ ] Code follows the project style guidelines
- [ ] Tests added for new functionality
- [ ] All existing tests pass
- [ ] Linting and type checking pass
- [ ] Documentation updated if needed

---

## Scope guidelines

- Do not modify files outside `src/navi_bootstrap/`, `tests/`, and `packs/` without discussion
- Do not bump dependency version constraints without discussion
- Do not modify `.github/workflows/` without discussion --- CI changes affect branch protection
- Document pre-existing violations rather than fixing them silently

---

## Reporting issues

- Search existing issues before creating a new one
- Use the issue templates when available
- Include reproduction steps for bugs
- Be specific about expected vs actual behavior
