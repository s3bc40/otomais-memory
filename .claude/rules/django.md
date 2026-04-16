---
paths:
  - "**/models.py"
  - "**/views.py"
  - "**/urls.py"
  - "**/admin.py"
  - "**/serializers.py"
---

# Django Conventions

- Always define `__str__` and `class Meta` (verbose_name, verbose_name_plural, ordering) on models
- Prefer CBV (ListView, DetailView, CreateView…) over FBV
- App URLs in `<app>/urls.py`, included with a namespace in the root router
- Always use `select_related` / `prefetch_related` to avoid N+1 queries
- Register all models in `admin.py` using `@admin.register`
