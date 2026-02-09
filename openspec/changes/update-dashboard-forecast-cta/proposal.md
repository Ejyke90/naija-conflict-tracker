# Change: Update Dashboard Forecast CTA

## Why
The AI Predictions area currently feels disconnected from the rest of the dashboard and does not clearly guide users to the full forecast experience. We need a modernized forecast preview that visually matches the AI forecast tone and includes a clear CTA to the full forecast page.

## What Changes
- Add a hero-style forecast preview card that mirrors the AI forecast styling (electric blue accent, glassy panels, minimal borders, soft shadows).
- Introduce a prominent "View full forecast" CTA/link aligned to the preview card that routes to the forecast page (assumed `/forecast`; confirm during implementation).
- Standardize loading/error/empty states for the forecast preview so it feels polished and consistent with the dashboard modernization effort.

## Impact
- Affected specs: dashboard-monitoring (UI/UX for forecast preview and CTA)
- Affected code: frontend dashboard page/section that renders the AI Predictions/forecast preview card, shared UI tokens, and CTA link target.
- Dependencies: Requires confirmation of the correct forecast route; uses existing data API for predictions.
