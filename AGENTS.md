# Repository Guidelines

## Project Structure & Module Organization
Core processing blocks, executors, and data utilities live in `src/datatrove/`. FineWeb-Data orchestration, publishing scripts, and ontology prompts sit in `finewebdata/`. UI code resides in `web/`, APIs in `api/`, infra glue in `docker-compose.yml`, `docker-start.sh`, and `nginx/`. Reusable scripts live in `tools/`, with runnable samples in `examples/` and regression tests in `tests/`. Reference configs (`env.example`, `init-db.sql`, S3/IAM policies) stay version-controlled; never place raw datasets in the repo.

## Build, Test & Development Commands
Install dev dependencies via `pip install -e ".[dev]"` (Python 3.10+). Run `make quality` for lint/format checks and `make style` to auto-fix. Execute `make test` or `python -m pytest -sv tests/` before any push. Use `python finewebdata.py --domain education --mode local` to exercise the FineWeb pipeline, and `./docker-start.sh && docker-compose up web api` to mirror the production stack.

## Coding Style & Naming Conventions
Python follows 4-space indentation, Ruff-enforced 119-character lines, and `snake_case` functions with `PascalCase` classes. Keep imports sorted per Ruff’s config, include type hints, and add docstrings for public entry points. React/TypeScript files under `web/src/` follow the `DomainForm.tsx` pattern with SCSS modules nearby. Configuration belongs in `.env` files generated from `env.example`; never embed secrets in code.

## Testing Guidelines
Pytest is the single framework. Name files `test_<module>.py` and functions `test_feature_expectedBehavior` to aid filtering. Favor fast unit tests colocated with `src` modules plus scenario tests for pipelines and API routes. Run `pytest -k finewebdata` for targeted suites, and prefer `docker-test.sh` when validating containerized dependencies. There is no numeric coverage gate, but new logic must ship with regression tests that cover success and failure paths.

## Commit & Pull Request Guidelines
Recent history uses `<type>: <summary>` prefixes (`feat`, `fix`, `cleanup`). Keep the subject ≤72 chars, add details and breaking-change notes in the body, and reference GitHub issues. Pull requests must describe motivation, list manual or automated test output (`make quality && make test`), and attach UI screenshots or API logs when relevant. Flag new environment variables, migrations, or dataset destinations so reviewers can reproduce locally.

## Security & Configuration Tips
Load credentials through `.env` files and secret managers, not `git`. When handling large ontology exports or datasets, sync them to the S3 buckets described in `finewebdata/config/*.yaml` and consult `fineweb_med_iam_policy.json` or `s3_bucket_policy.json` before changing access. Rotate API keys exposed during debugging and scrub logs prior to sharing.
