# Landing Page Redesign - Engaging Data Visualization & Impact

**Status:** Proposed  
**Created:** 2026-01-25  
**Author:** Product Team  
**Type:** Feature Enhancement  
**Priority:** High  
**Estimated Effort:** 3-5 days

---

## Problem Statement

The current landing page (login screen) lacks visual engagement and doesn't communicate the platform's purpose or impact before requiring authentication. Users see a generic login form without understanding:
- What the platform does (conflict tracking, predictive analytics)
- The scale and importance of the data (real-time Nigeria-wide monitoring)
- The value proposition (save lives through early warning)
- Trust indicators (Nextier branding, data sources, credibility)

This creates a poor first impression and may reduce conversion rates for new users.

---

## Proposed Solution

Transform the landing page into a **public-facing hero section** with:

### 1. **Animated Hero Section with Real-Time Data**
```
┌─────────────────────────────────────────────────────────────┐
│  [Nextier Logo]                       [Login] [Get Access]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│    NIGERIA CONFLICT TRACKER                                  │
│    Real-time monitoring and predictive analytics             │
│    to prevent violence and save lives                        │
│                                                               │
│    [Animated Nigeria Map with Heat Zones] ←── Live updates   │
│                                                               │
│    ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐              │
│    │  342  │  │  89   │  │  12   │  │  36   │              │
│    │Events │  │Deaths │  │Active │  │States │              │
│    │30 days│  │30 days│  │Hotspots│ │Affected│             │
│    └───────┘  └───────┘  └───────┘  └───────┘              │
│                                                               │
│    [Get Access CTA]                                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2. **Key Visual Elements**

**A. Animated Nigeria Map**
- SVG-based map of Nigeria with all 36 states
- Color-coded heat zones (green→yellow→red) based on conflict intensity
- Pulsing dots for recent incidents (last 7 days)
- Smooth transitions and subtle animations
- Click to zoom into state-level detail (public preview)

**B. Real-Time Statistics Counter**
- Animated number counters (count-up effect)
- Last 30-day metrics from public dashboard endpoint
- Updates every 60 seconds
- Micro-interactions (pulse on update)

**C. Conflict Timeline Visualization**
- Horizontal timeline showing incident trends (6 months)
- Mini sparklines for each conflict type
- Gradient backgrounds reflecting severity
- Scrollable/swipeable on mobile

**D. Impact Stories Carousel**
- 3-4 rotating cards with:
  - "Early warning prevented escalation in Kaduna" (with icon)
  - "Forecasting accuracy: 82% for hotspot detection"
  - "Monitoring 36 states, 774 LGAs in real-time"
- Auto-rotate every 5 seconds
- Subtle parallax effect

### 3. **Visual Design System**

**Color Palette:**
- Primary: `#1E40AF` (Trust blue)
- Danger: `#DC2626` (High-risk red)
- Warning: `#F59E0B` (Medium-risk orange)
- Success: `#10B981` (Low-risk green)
- Background: `#F9FAFB` → `#EEF2FF` gradient
- Text: `#1F2937` (dark gray)

**Typography:**
- Headings: Inter Bold, 48px → 32px (responsive)
- Body: Inter Regular, 16px
- Stats: Space Grotesk Bold, 36px

**Motion Design:**
- Page load: Fade in + slide up (800ms, ease-out)
- Map: Pulse animation for hotspots (2s loop)
- Counters: Count-up animation (1.5s, ease-out)
- Hover states: Scale(1.05) + shadow increase
- Smooth scrolling between sections

### 4. **Content Hierarchy**

**Above the Fold (Hero):**
1. Logo + Navigation (Login/Register)
2. Headline: "Nigeria Conflict Tracker"
3. Subheading: Value proposition
4. Animated map visualization
5. Live statistics grid
6. Primary CTA: "Get Access" (links to registration)

**Below the Fold (Trust & Credibility):**
7. Impact metrics carousel
8. Data sources section (ACLED, news outlets, social media)
9. Technology stack badges (ML-powered, Real-time, Geospatial)
10. Nextier branding + footer

### 5. **Responsive Behavior**

**Desktop (1920px):**
- Full-width animated map (60% of viewport height)
- 4-column statistics grid
- Side-by-side content sections

**Tablet (768px):**
- Map scales to 50% viewport height
- 2-column statistics grid
- Stacked content sections

**Mobile (375px):**
- Map scales to 40% viewport height
- Single-column statistics (vertical cards)
- Simplified animations (reduce motion for performance)
- Bottom sheet navigation

### 6. **Technical Implementation**

**Libraries & Tools:**
```json
{
  "mapping": "react-simple-maps (SVG Nigeria boundaries)",
  "animations": "framer-motion (page transitions, counters)",
  "charts": "recharts (sparklines, mini charts)",
  "icons": "lucide-react (conflict type icons)",
  "3d-effects": "react-three-fiber (optional: 3D map for hero)"
}
```

**Performance Optimizations:**
- Lazy load below-fold content
- Debounce real-time updates (1min intervals)
- SVG optimization (compress Nigeria map)
- Image optimization (next/image for hero)
- Prefetch login/register routes

**API Integration:**
```typescript
// Public endpoint for landing page stats (no auth required)
GET /api/v1/public/landing-stats
Response: {
  total_incidents_30d: 342,
  total_fatalities_30d: 89,
  active_hotspots: 12,
  states_affected: 36,
  last_updated: "2026-01-25T14:30:00Z",
  timeline_sparkline: [12, 15, 18, 14, 22, 19], // Last 6 months
  top_states: [
    { name: "Kaduna", incidents: 45, severity: "high" },
    { name: "Borno", incidents: 38, severity: "high" }
  ]
}
```

### 7. **Accessibility (WCAG 2.1 AA)**

- Alt text for all visualizations
- Keyboard navigation support
- Focus indicators (visible outlines)
- Reduced motion preference respected (`prefers-reduced-motion`)
- Color contrast ratios ≥ 4.5:1
- Screen reader announcements for live updates
- Semantic HTML5 structure

### 8. **Animation Examples**

**Page Load Sequence:**
```
1. Logo fade in (200ms delay)
2. Headline slide up (400ms delay)
3. Map fade in + scale (600ms delay)
4. Statistics count-up (800ms delay)
5. CTA button pulse (1000ms delay)
```

**Micro-interactions:**
```
- Hover on map state → Tooltip with state name + incident count
- Hover on statistic card → Lift shadow, slight scale
- Click hotspot → Modal with incident details (preview)
- Scroll → Parallax effect on background gradient
```

---

## User Experience Flow

### Current Flow (Problematic):
```
User lands → Sees login form → Confused (what is this?) → Bounces
```

### Proposed Flow:
```
User lands → Sees animated map + stats → Understands value → 
Clicks "Get Access" → Register → Login → Dashboard
```

---

## Success Metrics

**Quantitative:**
- Reduce bounce rate by 40% (target: <30%)
- Increase registration conversion by 50%
- Average time on landing page: 45+ seconds (from current ~5s)
- Click-through rate on "Get Access" CTA: >25%

**Qualitative:**
- User surveys: "I understand what this platform does" (>90% agree)
- First impression score: 4.5+/5.0
- Trust perception: 4.0+/5.0

---

## Implementation Plan

### Phase 1: Foundation (Day 1-2)
- [ ] Design Nigeria SVG map with state boundaries
- [ ] Create public landing stats API endpoint
- [ ] Setup framer-motion and react-simple-maps
- [ ] Build responsive layout skeleton

### Phase 2: Core Animations (Day 3-4)
- [ ] Implement map heat zone visualization
- [ ] Add animated statistics counters
- [ ] Create timeline sparkline component
- [ ] Build impact carousel

### Phase 3: Polish & Performance (Day 5)
- [ ] Optimize animations for mobile
- [ ] Add loading states and skeleton screens
- [ ] Implement accessibility features
- [ ] Performance audit (Lighthouse score >90)
- [ ] Cross-browser testing

---

## Dependencies

- **Backend:** New public endpoint `/api/v1/public/landing-stats`
- **Design Assets:** Nigeria state boundary SVG, conflict type icons
- **Content:** 3-4 impact statements, data source logos
- **Testing:** User acceptance testing with 5-10 target users

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Animations cause poor mobile performance | High | Detect device capabilities, disable heavy animations on low-end devices |
| Real-time data delays | Medium | Cache last successful response, show stale data with timestamp |
| Map complexity slows initial load | Medium | Lazy load map after hero text, use progressive enhancement |
| Nigeria map SVG too large | Low | Simplify boundaries, use SVGO compression |

---

## Alternatives Considered

1. **Static image hero** - Rejected: Less engaging, doesn't showcase real-time capability
2. **Video background** - Rejected: Heavy, accessibility issues, poor mobile performance
3. **3D WebGL map** - Deferred: Overkill for MVP, can add later
4. **Chatbot intro** - Rejected: Gimmicky, doesn't fit serious use case

---

## Open Questions

1. Should unauthenticated users see actual data or demo/anonymized data?
   - **Recommendation:** Show real aggregate data (builds trust)

2. How often should map update with new incidents?
   - **Recommendation:** Every 60 seconds (balance between real-time feel and performance)

3. Should we add video testimonials from Nextier researchers?
   - **Recommendation:** Phase 2 enhancement

4. Language support (English, Hausa, Yoruba, Igbo)?
   - **Recommendation:** Start with English, add i18n in Phase 2

---

## References

- [Framer Motion Documentation](https://www.framer.com/motion/)
- [React Simple Maps](https://www.react-simple-maps.io/)
- [Web Animation Best Practices](https://web.dev/animations/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

## Approval Checklist

- [ ] Product Owner sign-off
- [ ] Design review completed
- [ ] Technical feasibility confirmed
- [ ] Security review (public endpoint doesn't leak sensitive data)
- [ ] Budget approved
- [ ] Timeline accepted

---

**Next Steps:**
1. Review and approve this proposal
2. Create high-fidelity mockups in Figma
3. Break down into implementation tasks
4. Create feature branch: `feature/landing-page-redesign`
5. Begin development
