# Push this scaffold to GitHub

Everything for the Trend Intelligence Engine is in this folder. To put it on
GitHub, create an EMPTY repo on github.com (no README/gitignore/license), copy
its URL, then run the helper below from inside this folder.

## Option A — one command (recommended)
```bash
bash push.sh https://github.com/<owner>/<repo>.git
```
It will git-init, commit everything, set `main`, and push.

## Option B — manual
```bash
git init -b main
git add .
git commit -m "Scaffold Trend Intelligence Engine"
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

## Verify it works (no credentials needed)
```bash
pip install -e ".[dev]"
python scripts/audit_static.py     # architecture invariants
pytest -q                          # unit tests
python -m trendengine.pipeline --dry-run   # full loop, prints a brief
```
