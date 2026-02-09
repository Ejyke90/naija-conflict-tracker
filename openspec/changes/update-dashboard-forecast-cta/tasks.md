# Tasks: Update Dashboard Forecast CTA

## Stage 1: Design Alignment
- [x] Confirm target route for the full forecast page (`/forecasts`).
- [ ] Locate the current forecast preview/AI Predictions component file and note layout constraints.
- [ ] Align tokens (accent, background, shadow) with the modernized dashboard palette.

## Stage 2: Spec Delta
- [ ] Ensure `specs/dashboard-monitoring/spec.md` captures hero preview, CTA, and state requirements (already drafted; adjust if route changes).
- [ ] Include scenarios for load/error/empty and CTA navigation.

## Stage 3: Implementation Prep
- [ ] Map data bindings from the forecast API hook/query to headline metric, trend, and interval text.
- [ ] Plan CTA placement (header-aligned pill/button) and link target.
- [ ] Define loading skeleton and error fallback matching the hero layout style.

## Stage 4: Validation
- [ ] Run `openspec validate update-dashboard-forecast-cta --strict --no-interactive`.
- [ ] Fix any validation issues.
