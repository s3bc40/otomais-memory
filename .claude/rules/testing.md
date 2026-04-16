---
paths:
  - "**/tests/**"
  - "**/test_*.py"
  - "**/*_test.py"
---

# Testing Conventions

- Framework: pytest + pytest-django
- Test naming: `test_should_<expected>_when_<condition>`
- Model fixtures via `factory_boy`
- Never mock the database: use `@pytest.mark.django_db`
- One test file per source file: `models.py` → `tests/test_models.py`
- Always clean up side effects (created files, sent emails via outbox)
