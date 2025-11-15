# Figma Wireframe Specification – Project Sigma UI Suite

## Shared Frame Setup
- Desktop frame `1440 x 900`, 12-column layout grid, 20 px margins, 16 px gutters.
- Background colour: `#F5F5F7`.
- Typeface Open Sans (or system equivalent); fallback system fonts acceptable.
- Base spacing scale increments of 8 px.

---

## Screen 1 · Landing Page (Marketing)
- **Hero Band (Top 480 px)**: full-width image placeholder with gradient overlay, left column contains headline “Match Learners with Ideal Projects”, supporting copy, primary CTA `Get Started`, secondary CTA `Explore Projects`; right column graphic placeholder 360 × 360.
- **Trust Indicators Strip**: horizontal logo row inside white card with subtle shadow; annotate reference to research on social proof.
- **How It Works Section**: three step cards on neutral background alternating `#FFFFFF` / `#EFF4FF`, include icons, numbered badges for sequence, arrow connectors optional.
- **Features Grid**: two-column layout; left bullet list, right screenshot placeholder; provide responsive tablet variant (768 px) duplicating frame.
- **Footer**: four columns (Product, Resources, Company, Contact) plus newsletter signup field.

## Screen 2 · Login & Onboarding
- **Centered Auth Modal** (480 px width, 24 px radius) on neutral background `#E7ECF3`; includes logo, welcome heading, inputs for Email + Password (48 px height), helper text placeholders, primary button `Sign In`, link `Forgot password?`.
- **Additional Options Row**: social login icon buttons, remember-me checkbox, security reminder text.
- **Progress Sidebar Variant**: optional frame with vertical stepper (Account → Profile → Preferences) for multi-step onboarding.
- **Annotation Layer**: callouts for password policy tooltip, error messaging placement, keyboard focus order (1 form, 2 remember, 3 submit, 4 help).

## Screen 3 · Recommendation Dashboard
- **Persistent Header** 80 px high; includes logo (120 × 40), page title “Dashboard”, search field, notification/help icons, avatar (40 px). Divider line `#E0E0E5`.
- **Left Navigation Rail** 240 px fixed; items Projects, Recommendations, Analytics, Settings; primary CTA `New Project` at bottom; highlight state uses `#2A5BFF` background with white text.
- **Primary Content Column** (grid columns 4-12):
  - **KPI Strip**: three cards 280 × 120 (Project Matches, Active Learners, Satisfaction Score) with trend indicator and sparkline placeholders.
  - **Recommended Projects Panel**: table-style card with filter pills [All][STEM][Creative][Humanities], rows containing project name, suitability %, tags, `View Brief` button.
  - **Upcoming Actions Widget**: right-aligned stack 320 × 300 with timeline bullets for deadlines and call to action.
- **Insights Panel** (right 320 px): scrollable feed of recent activity, support card “Need help? View resources”, empty-state variant note.

## Screen 4 · Search Results
- **Search Header**: back button, search field with inline filters, breadcrumb `Home / Projects / Results`, summary text “32 matches”.
- **Filter Drawer** left 280 px: discipline checkbox group, difficulty segmented control, duration slider, tags multi-select chips; `Apply` + `Reset` buttons anchored bottom.
- **Results Grid/List Toggle**: default three-column cards (width ~300 px) showing project title, suitability %, key facts, CTA `View Brief`, bookmark toggle; include list-view variant.
- **Feedback Elements**: saved state badge, inline messages for conflicting filters.
- **Empty State Frame**: illustration placeholder with guidance text “Adjust filters to discover more projects.”

## Shared Styling Tokens
- Primary colour `#2A5BFF`, secondary accent `#FFB400`.
- Neutral text `#101828` headings, `#475467` body, muted `#667085`.
- Cards radius 12 px, modal radius 24 px, icon size 20 px consistent stroke.
- Shadows: `0 4 12 rgba(0,0,0,0.08)` for cards, `0 8 24 rgba(0,0,0,0.12)` for modal.

## Annotation Guidance
- Maintain dedicated annotation layer per screen; use callout arrows tying back to research insights (e.g., recommended filters derived from user interviews).
- Include typography notes near major elements (header text size, button weight).
- Document interactive states via duplicate frames (hover, focus, disabled, empty).

## Accessibility & Interaction Notes
- Minimum touch target 44 × 44 px; login inputs 48 px height.
- Colour contrast validated (primary blue on white ≥ 5.9:1).
- Consistent keyboard order documented via numbered badges for each screen.
- Provide tooltip patterns for help icons, password hints, filter explanations.
- Reminder layer to export snapshots for documentation and link to requirement IDs.

