---
name: Agenda Ecuamatriz Enterprise
colors:
  surface: '#FFFFFF'
  surface-dim: '#d1dbe8'
  surface-bright: '#f7f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#edf4ff'
  surface-container: '#e4effd'
  surface-container-high: '#dfe9f7'
  surface-container-highest: '#d9e3f1'
  on-surface: '#121d26'
  on-surface-variant: '#43474d'
  inverse-surface: '#27313c'
  inverse-on-surface: '#e8f2ff'
  outline: '#74777e'
  outline-variant: '#c3c6ce'
  surface-tint: '#48607d'
  primary: '#00152a'
  on-primary: '#ffffff'
  primary-container: '#0f2a44'
  on-primary-container: '#7992b1'
  inverse-primary: '#b0c9ea'
  secondary: '#166b50'
  on-secondary: '#ffffff'
  secondary-container: '#a4f3d0'
  on-secondary-container: '#1f7156'
  tertiary: '#201100'
  on-tertiary: '#ffffff'
  tertiary-container: '#3c2300'
  on-tertiary-container: '#af895a'
  error: '#C0392B'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d1e4ff'
  primary-fixed-dim: '#b0c9ea'
  on-primary-fixed: '#001d36'
  on-primary-fixed-variant: '#304864'
  secondary-fixed: '#a4f3d0'
  secondary-fixed-dim: '#88d6b5'
  on-secondary-fixed: '#002116'
  on-secondary-fixed-variant: '#00513b'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ebbf8c'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#5f4119'
  background: '#F5F7FA'
  on-background: '#121d26'
  surface-variant: '#d9e3f1'
  warning: '#F2C94C'
  text-secondary: '#6B7280'
  status-available: '#2E7D61'
  status-busy: '#C0392B'
  status-conflict: '#F2C94C'
  status-inactive: '#9CA3AF'
typography:
  headline-sm:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0.01em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  baseline: 4dp
  margin-mobile: 16dp
  margin-tablet: 24dp
  gutter: 12dp
  card-padding: 16dp
---

## Brand & Style

This design system is engineered for a high-performance enterprise environment, specifically tailored for the Android ecosystem. The brand personality is **sober, reliable, and efficient**. It prioritizes clarity and functional density over decorative elements, ensuring that "Agenda Ecuamatriz" serves as a robust tool for professional scheduling and coordination.

The visual style follows a **Modern Corporate** approach, heavily influenced by Material Design 3 (M3) principles. It utilizes a restrained color palette, systematic spacing, and clear hierarchy to reduce cognitive load for users managing complex calendars and participant lists. The aesthetic is clean and institutional, evoking a sense of stability and precision.

## Colors

The palette is anchored by **Deep Navy (#0F2A44)**, providing a strong sense of authority and professional grounding. **Emerald Green (#2E7D61)** is used as a secondary accent to denote growth, action, and positive states.

The color system is strictly functional:
- **Primary:** Used for key action buttons, active states in navigation, and primary branding.
- **Surface & Background:** A subtle distinction between the light grey background and pure white cards creates depth without heavy shadows.
- **Semantic Statuses:** These are critical for the agenda's utility. Use the named status colors for real-time availability indicators.
- **Text:** High contrast is maintained using a near-black for primary information and a medium grey for metadata and secondary labels.

## Typography

The design system utilizes **Inter** to provide a highly legible, neutral, and systematic typographic experience. It is optimized for screen readability at small sizes, which is essential for data-heavy enterprise applications.

- **Headlines:** Reserved for screen titles and major section headers. The semibold weight ensures a clear entry point for the eye.
- **Body:** Use `body-lg` (16px) for main content descriptions and `body-md` (14px) for dense data lists or secondary descriptions.
- **Buttons:** Always use `label-md` (14px Medium) to ensure action items are distinct from body text.
- **Captions:** Used for timestamps, legal text, or metadata under input fields.

## Layout & Spacing

The layout follows a **4dp baseline grid** to ensure mathematical alignment across all UI elements. 

- **Grid System:** A fluid 12-column grid is used for desktop/tablet, while a 4-column grid is standard for mobile. 
- **Margins:** 16dp horizontal margins are the standard for mobile screens to provide breathing room.
- **Density:** As an enterprise tool, vertical spacing is moderate (12dp–16dp between cards) to allow more information to be visible on the screen without feeling cluttered.
- **Alignment:** All text elements and icons should be center-aligned vertically within their respective containers to maintain a disciplined professional look.

## Elevation & Depth

This design system uses a **Tonal Layering** approach combined with subtle ambient shadows. 

- **Level 0 (Background):** #F5F7FA. The lowest layer.
- **Level 1 (Cards/Surface):** #FFFFFF with a soft, diffused shadow (Blur: 8dp, Y-Offset: 2dp, Opacity: 4% Black). This elevation is used for schedule items, participant lists, and containers.
- **Level 2 (Modals/Menus):** Elevated with a more pronounced shadow (Blur: 16dp, Y-Offset: 4dp, Opacity: 8% Black) to indicate interaction priority.

We avoid heavy "Floating Action Button" (FAB) shadows to maintain the sober, business-oriented aesthetic.

## Shapes

The shape language is defined by **functional softness**. 

- **Cards:** Use a strict 12dp corner radius. This is large enough to feel modern and approachable but structured enough for a professional enterprise tool.
- **Inputs & Buttons:** Follow the 8dp (Soft) or 12dp (Rounded) standard to maintain consistency with the card geometry.
- **Chips:** Fully rounded (pill-shaped) to distinguish them from rectangular buttons and card elements.

## Components

### Cards
Cards are the primary container for agenda items. They must include 16dp internal padding. When displaying a conflict, the left border should be accented with the `warning` yellow (4dp stroke).

### Input Fields
Inputs use an "Outlined" Material 3 style. The label should float to the top border on focus. Error states must change the stroke and helper text to `error` red.

### Chips
Used for selected participants. Chips include a small avatar or initials and a "remove" icon. They should have a light grey background (#E5E7EB) to remain neutral.

### Bottom Navigation
The bottom bar uses the `primary` navy for active icons and labels. Inactive states use `text-secondary`. The container background is white with a thin top stroke (#E5E7EB) rather than a heavy shadow.

### Status Indicators
Status is conveyed via a small 8dp circular dot or a subtle "badge" with a 10% opacity background of the status color and a 100% opacity foreground text.
- **Available:** Green
- **Busy:** Red
- **Conflict:** Yellow
- **Out of Hours:** Grey