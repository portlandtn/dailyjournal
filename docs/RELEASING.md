# Releasing downloads

`.github/workflows/build.yml` builds standalone downloads on every pull request and on `main`. They are attached to the workflow run as artifacts. Pushing a version tag publishes them as a GitHub Release.

## Cut a release

1. Set `APP_VERSION` in `app.py` and `version` in `pyproject.toml` to the same value.
2. Merge to `main`.
3. Tag and push: `git tag v0.2.0 && git push origin v0.2.0`

The release job refuses to publish if the tag and `APP_VERSION` differ.

## What gets published

Eight archives plus `SHA256SUMS.txt`:

| Edition | Windows | Mac (Apple silicon) | Mac (Intel) | Linux |
|---|---|---|---|---|
| No AI | `dailyjournal-noai-windows-x64.zip` | `dailyjournal-noai-macos-arm64.zip` | `dailyjournal-noai-macos-intel.zip` | `dailyjournal-noai-linux-x64.tar.gz` |
| OpenAI | `dailyjournal-openai-windows-x64.zip` | `dailyjournal-openai-macos-arm64.zip` | `dailyjournal-openai-macos-intel.zip` | `dailyjournal-openai-linux-x64.tar.gz` |

Stable links for the website use `https://github.com/portlandtn/dailyjournal/releases/latest/download/<file name>`.

The two editions come from the same source. The no-AI build passes `--exclude-module` for `openai`, `coach`, `keyring`, and `dj_secrets`, so that code is not in the download at all. `engine.py` notices the missing `coach` module and routes every session through `plain.py`.

## Signing

- **Windows:** unsigned. SmartScreen shows "Windows protected your PC"; users click "More info" then "Run anyway". `packaging/README.txt` explains this.
- **Linux:** there is nothing to sign. The archive keeps the executable bit.
- **macOS:** signed and notarized when the repository secrets below exist. Without them the Mac builds are unsigned and users have to approve them in System Settings.

### macOS secrets

Add these under Settings > Secrets and variables > Actions:

| Secret | Value |
|---|---|
| `MACOS_CERTIFICATE_P12_BASE64` | Your "Developer ID Application" certificate exported from Keychain Access as a `.p12`, then base64-encoded (`base64 -i cert.p12 \| pbcopy`) |
| `MACOS_CERTIFICATE_PASSWORD` | The password you set when exporting the `.p12` |
| `MACOS_SIGN_IDENTITY` | The certificate's full name, for example `Developer ID Application: Your Name (TEAMID)` |
| `APPLE_ID` | The Apple ID email on the developer account |
| `APPLE_APP_PASSWORD` | An app-specific password for that Apple ID, created at account.apple.com |
| `APPLE_TEAM_ID` | Your ten-character team ID |

The signing and notarization steps have not been run yet, because the secrets did not exist when the workflow was written. Expect to adjust them on the first signed build.
