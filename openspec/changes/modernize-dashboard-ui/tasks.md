# Implementation Tasks: Modernize Dashboard UI

## Phase 1: Setup shadcn/ui & Framer Motion

### Task 1.1: Install Dependencies
- [ ] Run `npx shadcn-ui@latest init` in frontend directory
- [ ] Answer prompts:
  - TypeScript: Yes
  - Style: Default
  - Base color: Slate
  - CSS variables: Yes
  - Tailwind config: Yes
  - Components: src/components/ui
  - Utils: src/lib/utils
  - React Server Components: No
  - Write config: Yes
- [ ] Install Framer Motion: `npm install framer-motion`
- [ ] Verify installations in package.json

### Task 1.2: Add Core UI Components
- [ ] Add Card: `npx shadcn-ui@latest add card`
- [ ] Add Button: `npx shadcn-ui@latest add button`
- [ ] Add Badge: `npx shadcn-ui@latest add badge`
- [ ] Add Tabs: `npx shadcn-ui@latest add tabs`
- [ ] Add Select: `npx shadcn-ui@latest add select`
- [ ] Add Skeleton: `npx shadcn-ui@latest add skeleton`
- [ ] Verify all components in src/components/ui/

### Task 1.3: Configure Design Tokens
- [ ] Update tailwind.config.js with custom colors:
  - Primary: Blue scale for main actions
  - Destructive: Red scale for high-risk states
  - Warning: Amber scale for medium-risk states
  - Success: Green scale for improvements
- [ ] Add custom spacing scale
- [ ] Add custom animation keyframes
- [ ] Test design tokens compile correctly

## Phase 2: Redesign StateAnalysis Component

### Task 2.1: Component Structure Refactor
- [ ] Import shadcn components (Card, CardHeader, CardTitle, CardContent)
- [ ] Import Framer Motion (motion, AnimatePresence)
- [ ] Create loading skeleton component
- [ ] Create empty state component
- [ ] Extract reusable StatCard component

### Task 2.2: Header Section Enhancement
- [ ] Replace div with Card component
- [ ] Add Framer Motion fade-in animation
- [ ] Improve typography (use design tokens)
- [ ] Add subtitle with last update time
- [ ] Ensure responsive on mobile

### Task 2.3: Controls Section Redesign
- [ ] Replace dropdowns with shadcn Select components
- [ ] Add consistent spacing with Tailwind spacing scale
- [ ] Add hover states to filter buttons
- [ ] Improve visual hierarchy
- [ ] Add active state indicators

### Task 2.4: Forecast Cards Overhaul
- [ ] Replace div cards with shadcn Card components
- [ ] Add Framer Motion stagger animation (delay: i * 0.1s)
- [ ] Redesign with icon + title + metric layout
- [ ] Add gradient backgrounds (from-blue-500 to-indigo-600)
- [ ] Improve confidence interval display
- [ ] Add hover scale animation (scale: 1.02)
- [ ] Create loading skeleton for forecast cards

### Task 2.5: Chart Styling Enhancement
- [ ] Create custom color palette for Recharts:
  - incidents: #3b82f6 (blue)
  - fatalities: #ef4444 (red)
  - grid: #e5e7eb (light gray)
- [ ] Add gradient fills to bar charts
- [ ] Soften grid lines (strokeDasharray="3 3", opacity: 0.3)
- [ ] Round corners on bars (radius: [4, 4, 0, 0])
- [ ] Improve tooltip styling (custom background, border)
- [ ] Add smooth animation on chart load (animationDuration: 800)

### Task 2.6: Table Redesign
- [ ] Wrap table in Card component
- [ ] Add alternating row colors (even:bg-slate-50)
- [ ] Improve cell padding and spacing
- [ ] Add hover state on rows (hover:bg-slate-100)
- [ ] Replace pulsing indicators with Badge component
- [ ] Improve sparkline integration
- [ ] Add empty state for no data

### Task 2.7: Loading & Empty States
- [ ] Create loading skeleton matching final layout
- [ ] Add shimmer animation to skeleton
- [ ] Design empty state with illustration
- [ ] Add "No data available" messaging
- [ ] Include call-to-action (e.g., "Adjust filters")

### Task 2.8: Micro-Interactions
- [ ] Add hover scale to all clickable elements
- [ ] Add transition-all to interactive components
- [ ] Implement smooth sort animation (Framer Motion layout)
- [ ] Add button press feedback (active:scale-95)
- [ ] Stagger animation for table rows on load

## Phase 3: Create Reusable Components

### Task 3.1: StatCard Component
- [ ] Create src/components/ui/stat-card.tsx
- [ ] Props: title, value, trend, trendPercent, icon, color
- [ ] Use shadcn Card as base
- [ ] Add Lucide icon support
- [ ] Include trend indicator with arrow
- [ ] Add optional sparkline slot
- [ ] Make fully responsive

### Task 3.2: MetricDisplay Component
- [ ] Create src/components/ui/metric-display.tsx
- [ ] Props: label, value, unit, trend, color
- [ ] Large number display with formatting
- [ ] Small label text
- [ ] Optional trend badge
- [ ] Color-coded by metric type

### Task 3.3: TrendBadge Component
- [ ] Create src/components/ui/trend-badge.tsx
- [ ] Props: trend, percent, variant
- [ ] Use shadcn Badge
- [ ] Color variants (success/warning/destructive)
- [ ] Icon + percentage display
- [ ] Animated arrow icon

## Phase 4: Dashboard-Wide Consistency

### Task 4.1: Apply to Other Dashboard Sections
- [ ] Update MonthlyTrends component with new design
- [ ] Update ConflictMap component styling
- [ ] Update PipelineMonitor with new components
- [ ] Ensure consistent spacing across all sections
- [ ] Standardize color usage

### Task 4.2: Create Design System Documentation
- [ ] Document color usage patterns
- [ ] Document spacing conventions
- [ ] Document typography scale
- [ ] Create component usage examples
- [ ] Add Storybook stories (optional)

## Phase 5: Polish & Testing

### Task 5.1: Responsive Design
- [ ] Test on mobile (375px, 414px)
- [ ] Test on tablet (768px, 1024px)
- [ ] Test on desktop (1280px, 1920px)
- [ ] Fix any layout breaks
- [ ] Ensure charts are readable on small screens

### Task 5.2: Accessibility Audit
- [ ] Run Lighthouse accessibility audit
- [ ] Fix color contrast issues (WCAG AA)
- [ ] Test keyboard navigation
- [ ] Add proper ARIA labels
- [ ] Test with screen reader (VoiceOver/NVDA)

### Task 5.3: Performance Optimization
- [ ] Measure bundle size impact
- [ ] Enable tree-shaking for shadcn components
- [ ] Lazy load Framer Motion animations
- [ ] Optimize Recharts bundle
- [ ] Run Lighthouse performance audit

### Task 5.4: Cross-Browser Testing
- [ ] Test in Chrome/Edge
- [ ] Test in Firefox
- [ ] Test in Safari
- [ ] Fix any rendering issues
- [ ] Verify animations work everywhere

### Task 5.5: User Acceptance Testing
- [ ] Get feedback from stakeholders
- [ ] Address any UX concerns
- [ ] Verify all Quick Win features still work
- [ ] Test error states
- [ ] Test loading states

## Phase 6: Documentation & Deployment

### Task 6.1: Update Documentation
- [ ] Update DASHBOARD_WALKTHROUGH.md
- [ ] Document new component architecture
- [ ] Add screenshots of new design
- [ ] Document design tokens
- [ ] Create migration guide for other devs

### Task 6.2: Deployment Checklist
- [ ] Run full test suite
- [ ] Build production bundle
- [ ] Verify bundle size is acceptable
- [ ] Deploy to staging
- [ ] Smoke test on staging
- [ ] Deploy to production
- [ ] Monitor for errors

### Task 6.3: Archive Proposal
- [ ] Mark all tasks as complete
- [ ] Run `openspec archive modernize-dashboard-ui --yes`
- [ ] Update specs if needed
- [ ] Create GitHub release notes
- [ ] Close related issues

## Validation Checklist

Before marking complete, verify:
- [ ] All shadcn components installed correctly
- [ ] Framer Motion animations work smoothly
- [ ] Charts render with professional styling
- [ ] Loading states display properly
- [ ] Empty states are helpful
- [ ] Responsive on all breakpoints
- [ ] Accessibility score > 90
- [ ] Performance score > 85
- [ ] No console errors
- [ ] All Quick Win features functional
