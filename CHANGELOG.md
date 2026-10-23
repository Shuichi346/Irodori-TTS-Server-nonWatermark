# Changelog

## 2026-10-23

### Added

- Added macOS metadata and filesystem management exclusions to `.gitignore`.
- Added a README explanation of the server and inference forks, their upstream repositories, and the scope of watermark removal.
- Added repository maintenance guidance and technical notes for the inference dependency migration.

### Changed

- Switched the `irodori-tts` Git dependency to `Shuichi346/Irodori-TTS-nonWatermark` and regenerated `uv.lock` at commit `0e984c21294ab699476c4b78e2f117b07a485163`, removing `silentcipher` and its unused dependencies.
- Updated the README to describe the fork without audio watermark processing and clone this server fork. Retained the `irodori_tts` Python imports and existing Hugging Face model and codec repositories.
