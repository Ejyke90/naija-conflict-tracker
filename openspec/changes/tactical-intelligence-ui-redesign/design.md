## Context

The Nigeria Conflict Tracker currently uses a standard business dashboard aesthetic with bright blue primary colors, generic gray backgrounds, and conventional card designs. This undermines the platform's credibility as a professional intelligence system. The current Tailwind configuration uses standard blue color schemes and lacks the sophisticated visual hierarchy expected in C4ISR systems.

Current technical constraints:
- Next.js 14 with TypeScript and Tailwind CSS
- Component-based architecture with shadcn/ui components
- Existing color palette defined in tailwind.config.js
- Multiple dashboard components requiring consistent styling
- Real-time data visualization with charts and maps

## Goals / Non-Goals

**Goals:**
- Transform the visual identity from "business blue" to "Tactical Professional" intelligence aesthetic
- Implement a signal-based color system where vibrant colors are reserved exclusively for data status
- Create glassmorphism effects or flat-sophisticated design with micro-borders
- Establish intelligence-grade typography hierarchy
- Ensure all components reflect high-authority, mission-critical interface standards
- Maintain accessibility and performance while upgrading visual design

**Non-Goals:**
- Changing the underlying data architecture or API structure
- Modifying map functionality or data sources
- Altering authentication or user management systems
- Changing responsive layout patterns (keep current responsive design)

## Decisions

### 1. Color System Architecture
**Decision**: Implement a "Tactical Professional" palette with deep navy (#0B1120) as primary background, charcoal greys for surfaces, and "E-Ink" off-whites (#F8F9FA) for content areas.

**Rationale**: Deep navy backgrounds are standard in intelligence systems (ACLED, CrisisWatch, IHS Markit) and convey authority. The E-Ink off-white provides excellent readability while maintaining professional appearance. This moves away from generic business aesthetics while maintaining accessibility.

**Alternatives considered**:
- Pure black background - too harsh for extended use
- Light gray theme - lacks authority and professional feel
- Dark blue gradient - too complex and distracting

### 2. Signal Color Framework
**Decision**: Reserve vibrant colors (Red #DC2626, Amber #EA580C, Green #22C55E) exclusively for risk levels, status indicators, and alerts. All UI elements use neutral tactical colors.

**Rationale**: Intelligence systems use color as information, not decoration. When everything is blue, nothing is urgent. Signal colors create immediate visual hierarchy for critical information.

**Alternatives considered**:
- Using blue for primary actions - confused with status information
- Multiple accent colors - creates visual noise and reduces authority
- Monochromatic only - loses critical status communication

### 3. Visual Effects Strategy
**Decision**: Implement glassmorphism effects with backdrop-filter blur and subtle transparency for cards and overlays, combined with 1px micro-borders for section definition.

**Rationale**: Glassmorphism provides modern sophistication while maintaining readability. Micro-borders create clear information hierarchy without heavy shadows that can look dated.

**Alternatives considered**:
- Heavy shadows and elevation - looks dated and less professional
- Flat design without borders - lacks information hierarchy
- Material design elevation - too consumer-focused for intelligence systems

### 4. Typography System
**Decision**: Use Inter font with tighter letter-spacing for headings, increased contrast ratios, and clear hierarchy (H1: 2.5rem, H2: 2rem, H3: 1.5rem, Body: 0.875rem).

**Rationale**: Intelligence systems require high information density with excellent readability. Inter performs well at small sizes and maintains clarity with tight spacing.

**Alternatives considered**:
- System fonts - inconsistent across platforms
- Monospace for everything - poor readability for longer content
- Decorative fonts - unprofessional and slower loading

### 5. Component Architecture
**Decision**: Update all existing components through CSS custom properties and Tailwind extensions rather than creating new components.

**Rationale**: Maintains existing component architecture while enabling systematic visual updates. CSS custom properties allow for theme switching and consistent application.

**Alternatives considered**:
- Complete component rewrite - unnecessary complexity and risk
- Inline styles - inconsistent and hard to maintain
- Multiple theme systems - over-engineering for current needs

## Risks / Trade-offs

**Risk**: Dark theme may reduce readability in bright environments
→ **Mitigation**: Ensure high contrast ratios (WCAG AAA) and provide user preference detection

**Risk**: Glassmorphism effects may impact performance on older devices
→ **Mitigation**: Implement CSS @supports queries and fallback to solid backgrounds

**Risk**: Existing users may find the new design too dramatic
→ **Mitigation**: Implement gradual rollout and maintain functional parity

**Trade-off**: Reduced use of color for decoration vs. enhanced information hierarchy
→ **Acceptance**: Intelligence systems prioritize information clarity over decorative aesthetics

**Trade-off**: More sophisticated styling vs. increased CSS complexity
→ **Acceptance**: CSS custom properties and systematic approach maintain maintainability

## Migration Plan

1. **Phase 1**: Update Tailwind configuration with new color palette and CSS custom properties
2. **Phase 2**: Create base theme CSS file with tactical styling rules
3. **Phase 3**: Update core dashboard components (ConflictDashboard, navigation, headers)
4. **Phase 4**: Update data visualization components (charts, maps, alerts)
5. **Phase 5**: Update remaining UI components and ensure consistency
6. **Phase 6**: Testing, accessibility validation, and performance optimization

**Rollback Strategy**: Maintain current color palette in CSS comments and use feature flags for rapid rollback if critical issues arise.

## Open Questions

- Should we implement user theme preferences (light/dark mode toggle) or enforce tactical theme?
- What level of animation and micro-interactions supports the intelligence aesthetic without being distracting?
- How do we balance modern glassmorphism effects with accessibility requirements for color vision deficiency?
- Should we implement a "high-contrast" mode for operations in challenging viewing conditions?
