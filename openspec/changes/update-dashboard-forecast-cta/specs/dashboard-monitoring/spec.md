## MODIFIED Requirements

### Requirement: Forecast Preview CTA and Layout
The dashboard AI forecast preview SHALL present a hero-style card consistent with the AI forecast visual language and provide a clear CTA to the full forecast experience.
**Acceptance Criteria:**
- Hero card uses the modernized dashboard styling (electric blue accent, charcoal/slate base, soft shadow, minimal borders)
- Displays headline forecast metric (e.g., next 30 days incidents) with supporting trend/confidence text
- Includes a prominent CTA labeled "View full forecast" that routes to the forecast page (`/forecasts`)
- CTA is keyboard-focusable and visually distinct from secondary text
- Layout remains responsive: single-column on mobile, aligned CTA in header area on desktop

#### Scenario: Forecast CTA Visible
- **GIVEN** the dashboard renders the forecast preview
- **WHEN** the component finishes loading successfully
- **THEN** the hero card shows headline forecast info with supporting text
- **AND** a visible "View full forecast" CTA is displayed in the header area
- **AND** the CTA points to the `/forecasts` route

### Requirement: Forecast Preview States
The forecast preview SHALL provide consistent loading, error, and empty states that match the dashboard modernization style.
**Acceptance Criteria:**
- Loading shows a skeleton matching the hero card layout (no layout shift)
- Error state shows a concise message and a retry affordance
- Empty state shows neutral messaging with subdued iconography; CTA remains visible if navigation still makes sense
- State transitions are smooth (no flicker) and honor existing data-fetch intervals

#### Scenario: Loading State
- **GIVEN** the forecast preview is fetching data
- **WHEN** the component has not yet received a response
- **THEN** a skeleton matching the hero card structure is displayed
- **AND** no sudden layout shift occurs

#### Scenario: Error State With Retry
- **GIVEN** the forecast preview fetch fails
- **WHEN** the component enters error state
- **THEN** it shows an error message with retry control
- **AND** preserves CTA navigation if the full forecast page is still accessible

#### Scenario: Empty State
- **GIVEN** the forecast preview receives no forecast data
- **WHEN** the component renders the empty state
- **THEN** it displays neutral messaging and iconography
- **AND** the CTA remains available to reach the full forecast page

### Requirement: Accessibility and Interaction
The forecast preview CTA and hero card SHALL be accessible and interactive across devices.
**Acceptance Criteria:**
- CTA is reachable via keyboard and shows focus outline
- Text and accent colors meet WCAG AA contrast
- Hover/focus states use subtle scale or shadow without hindering readability
- Mobile view keeps tap targets ≥44px high and maintains readable typography

#### Scenario: Keyboard Navigation
- **GIVEN** a keyboard-only user is on the dashboard
- **WHEN** they tab to the forecast preview
- **THEN** the CTA receives focus visibly
- **AND** Enter/Space activates navigation to the forecast page
