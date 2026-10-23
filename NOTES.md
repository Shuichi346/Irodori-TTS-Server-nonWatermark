# Notes

## 2026-10-23 — Inference fork dependency

The inference dependency is `Shuichi346/Irodori-TTS-nonWatermark`. Its distribution name (`irodori-tts`) and Python namespace (`irodori_tts`) match upstream, so the server's imports and runtime integration require no changes. `Aratako/...` identifiers in `src/irodori_openai_tts/config.py` and `.env.example` identify Hugging Face model and codec assets, not the Git library source.

`uv.lock` pins the fork commit and is consumed by Docker's `uv sync --locked` steps. Changing only `pyproject.toml` would leave those builds inconsistent. Regeneration removed `silentcipher`, `blinker`, `flask`, `itsdangerous`, and `pyaml` without changing the versions of retained packages. uv 0.13.5 also updated the lockfile format and normalized dependency markers.

Migration verification passed: 109 tests, Ruff checks, bytecode compilation, and `uv lock --check --offline`. The installed distribution's Git origin and commit, required runtime symbols, absence of the `silentcipher` package, and absence of watermark references in the installed inference runtime were checked. Actual model synthesis and performance benchmarks were not run.
