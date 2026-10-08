# Veda — Your Health Journey, Understood

A single-page personal health records app (static HTML/CSS/JS, no build step).

## What works on GitHub Pages
- All screens, the timeline, medicine cabinet, appointments, Doctor Brief, family sharing preview, emergency card, privacy tools and data export.
- Data is saved in the visitor's own browser (localStorage). Nothing is uploaded anywhere.
- Report/medicine photo scanning and the AI copilot need an AI backend. They are switched off automatically here, and the app falls back to manual entry plus simple record search.

## Adding real AI later
Add a small server (never put an API key in front-end code) that accepts an image or text and returns JSON, then point the `SAMPLE.json(...)` calls in `index.html` at it.

Veda organizes and explains your own records. It does not diagnose or replace a healthcare professional.
