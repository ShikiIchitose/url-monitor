# URL Monitor

A small URL monitoring CLI that checks endpoints via HTTP GET and generates a Markdown report (and optional JSON output).

## Features

- Validate input URLs (http/https + netloc required)
- Perform HTTP checks with latency measurement
- Summarize results:
  - OK / FAIL counts and error rate
  - Status-class breakdown (2xx/3xx/4xx/5xx/other)
  - Latency stats for **success** and **failure** samples (avg / p95 when available)
  - Slowest endpoints (top N)
  - Separate reporting for:
    - HTTP failures (non-OK HTTP status)
    - Exceptions (request errors)
- Generate human-readable `report.md`
- (Optional) Save machine-readable `results.json`

## Why this project

This project is built as a portfolio-quality Python CLI with:
- reproducible environments (`uv.lock`)
- automated checks (Ruff + pytest)
- CI (GitHub Actions)
- network-independent tests (HTTP is mocked)

## Quickstart

### Requirements
- Python 3.13
- `uv` installed

### Install / Sync dependencies

```bash
uv sync --locked
```

### Run

Create `urls.txt` (one URL per line). Example:

```txt
https://example.com
https://httpbin.org/status/200
https://httpbin.org/status/404
```

Generate a Markdown report:

```bash
uv run url-monitor --input urls.txt --out report.md
```

Write both `report.md` and `results.json` into a directory:

```bash
uv run url-monitor --input urls.txt --out-dir out/
```

## CLI

```bash
uv run url-monitor --help
```

Common options:

- `--input PATH` : input file path (default: `urls.txt`)
- `--out PATH` : output Markdown path (default: `report.md`)
- `--out-dir DIR` : output directory (writes `report.md` + `results.json`)
- `--timeout SECONDS` : request timeout (default: `5.0`)
- `--strict` : fail fast on invalid input lines

## Output

### `report.md`
The report includes:
- Summary (counts, error rate, sample sizes)
- Status breakdown
- Slowest URLs
- HTTP failures (non-OK status)
- Exceptions
- Invalid input lines (when `--strict` is not used)

### `results.json` (optional)
When `--out-dir` is used, a JSON file is written:

- `source`: input file name/path
- `summary`: aggregated metrics
- `results`: list of per-URL check results

This format is intended for further analysis (e.g., time-series aggregation, dashboards).

## Development

### Lint / Format

```bash
uv run ruff check .
uv run ruff format --check .
```

(Format locally if needed)

```bash
uv run ruff format .
```

### Test

```bash
uv run pytest -q
```

### Notes on testing
Tests do **not** rely on external network access.
HTTP behavior is mocked to keep CI stable and reproducible.

## Project structure

```text
url-monitor/
  src/
    url_monitor/
      cli.py
      pipeline.py
      outputs.py
      model.py
      validate.py
      io.py
      http.py
      stats.py
      report.py
  tests/
  pyproject.toml
  uv.lock
  .github/workflows/ci.yml
```

## Roadmap (optional)

- [ ] Persist historical runs (SQLite / Parquet)
- [ ] Add concurrency with rate limiting
- [ ] Add configurable retries/backoff
- [ ] Add richer statistical reporting (distribution plots, trend analysis)

## License

MIT License (SPDX: MIT). See `LICENSE`.
