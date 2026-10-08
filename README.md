# Veda — Your Health Journey, Understood

A single-page personal health records app (static HTML/CSS/JS, no build step).

## Publish on GitHub Pages
1. Create a new GitHub repository (e.g. `veda`).
2. Upload everything in this folder to the **root** of the repo (`index.html` must be at the top level, not inside a subfolder).
3. Go to **Settings → Pages**. Under *Build and deployment*, choose **Deploy from a branch**, branch **main**, folder **/ (root)**, then Save.
4. Wait 1–2 minutes. Your site will be at `https://<your-username>.github.io/<repo-name>/`.

## What works on GitHub Pages
- All screens, the timeline, medicine cabinet, appointments, Doctor Brief, family sharing preview, emergency card, privacy tools and data export.
- Data is saved in the visitor's own browser (localStorage). Nothing is uploaded anywhere.
- Report/medicine photo scanning and the AI copilot need an AI backend. They are switched off automatically here, and the app falls back to manual entry plus simple record search.

## Adding real AI later
Add a small server (never put an API key in front-end code) that accepts an image or text and returns JSON, then point the `SAMPLE.json(...)` calls in `index.html` at it.

Veda organizes and explains your own records. It does not diagnose or replace a healthcare professional.
