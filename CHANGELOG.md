# Changelog

## 0.1.0-alpha.2 — 2026-10-03

- Reject requests to `/library-desk/*` whose Host header is not `localhost` or a loopback IP address (DNS rebinding protection). Previously a rebound web page could read the current prompt/settings and model file paths through `status` and `catalog`.
- Bind the panel buttons even when Forge creates the header controls before the Library Desk tab.
- Add tests that run without Forge (`python -m unittest discover -s tests`) and a GitHub Actions workflow.

- Verify the updated extension after a real Forge restart on Windows: loopback Host requests succeed, foreign Host names are rejected, and all saved generation settings persist and restore exactly.

## 0.1.0-alpha.1 — 2026-10-02

First public preview for Windows and Forge Neo. Source and ZIP distributions contain no personal library data.
