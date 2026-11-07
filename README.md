# gametest

This repository contains a lightweight checklist for testing Codex plugins used in browser-based games.

## Scope

Validate that a plugin:

- Loads correctly in modern desktop browsers
- Does not break core gameplay loops
- Handles network interruptions and reconnects
- Fails safely when required APIs are unavailable

## Minimal test matrix

Run each plugin scenario on:

- Chrome (latest)
- Firefox (latest)
- Edge (latest)

Test at least:

1. Fresh load of the game and plugin initialization
2. Mid-session plugin enable/disable
3. Save/load flows with plugin state present
4. Simulated slow network and offline recovery

## Codex plugin validation checklist

- [ ] No uncaught errors in browser console during startup
- [ ] Plugin UI elements remain responsive during gameplay
- [ ] Plugin hooks do not block rendering or input
- [ ] Game state remains consistent after plugin-triggered actions
- [ ] Plugin cleanup runs on unload/reload without memory leaks

## Reporting

For each test run, capture:

- Browser and version
- Plugin version or commit hash
- Scenario steps
- Expected result vs actual result
- Console/network logs for failures