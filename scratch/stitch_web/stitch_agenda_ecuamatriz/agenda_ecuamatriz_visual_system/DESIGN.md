---
name: Agenda Ecuamatriz Visual System
colors:
  surface: '#faf9fb'
  surface-dim: '#dbd9dc'
  surface-bright: '#faf9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f6'
  surface-container: '#efedf0'
  surface-container-high: '#e9e8ea'
  surface-container-highest: '#e3e2e4'
  on-surface: '#1a1c1e'
  on-surface-variant: '#43474d'
  inverse-surface: '#2f3032'
  inverse-on-surface: '#f2f0f3'
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
  error: '#ba1a1a'
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
  background: '#faf9fb'
  on-background: '#1a1c1e'
  surface-variant: '#e3e2e4'
typography:
  page-title:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  card-title:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  table-cell:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  table-header:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
  button-text:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  sidebar-width: 260px
  topbar-height: 64px
  container-padding: 24px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style
The design system is engineered for **Agenda Ecuamatriz**, focusing on a corporate, modern, and sober aesthetic. The target audience consists of professionals requiring high-efficiency administrative tools where clarity and reliability are paramount.

The design style follows a **Modern Corporate** approach:
- **Cleanliness:** High use of white space and a structured hierarchy to prevent cognitive overload.
- **Sobriety:** A restricted color palette that uses deep blues and muted greens to convey authority and growth.
- **Precision:** Systematic alignment and consistent use of the Inter typeface to ensure a utilitarian yet sophisticated feel.
- **Functionality:** Every element serves a purpose, avoiding decorative flourishes in favor of clear data presentation and intuitive navigation.

## Colors
This design system utilizes a high-trust palette rooted in industrial professionalism.

- **Foundations:** The background uses a cool-toned light gray (`#F5F7FA`) to reduce eye strain, while cards and panels are pure white (`#FFFFFF`) to create distinct content zones.
- **Brand Actions:** The primary blue (`#0F2A44`) is reserved for main actions and branding, providing a stable anchor. The secondary green (`#2E7D61`) is used for success states and secondary growth-oriented actions.
- **Typography & UI:** Primary text uses a deep slate-gray for maximum legibility without the harshness of pure black. Borders are kept subtle to maintain a "frameless" feel.

## Typography
The system relies exclusively on **Inter** to ensure a systematic and neutral tone. 

- **Hierarchy:** Use `page-title` for main dashboard views and `card-title` for modular section headers.
- **Tables:** For data-heavy views, use `table-cell` and `table-header` to maximize information density while maintaining readability.
- **Weighting:** Semibold (600) is used for emphasis and headers, Medium (500) for interactive elements like buttons, and Regular (400) for standard reading text.

## Layout & Spacing
The layout follows a structured **Fixed Sidebar** model to facilitate rapid navigation between administrative modules.

- **Sidebar:** A fixed left-hand rail (260px) containing the primary navigation tree. It should use a subtle dark or very light contrast against the main background.
- **Main Canvas:** Content is housed within a fluid area with a standard 24px padding (`container-padding`). 
- **Grid:** Content cards should align to a 12-column grid system.
- **Top Bar:** A 64px fixed header manages utility actions (notifications, profile, search).
- **Responsiveness:** On tablets, the sidebar should collapse into an icon-only rail or a drawer. On mobile, the layout reflows into a single column with a bottom navigation bar or a top "hamburger" menu.

## Elevation & Depth
Depth is created through **Tonal Layers** rather than heavy shadows to maintain a clean, sober look.

- **Level 0 (Background):** `#F5F7FA` - The base of the application.
- **Level 1 (Cards/Panels):** `#FFFFFF` - Used for all primary content containers. These use a very soft, 2px blur shadow with 5% opacity to separate from the background.
- **Level 2 (Dropdowns/Modals):** `#FFFFFF` - These use a more pronounced shadow (8px to 16px blur) to indicate they are floating above the UI.
- **Outlines:** All cards and inputs feature a 1px border of `#E5E7EB` to ensure crisp definition even on screens with poor contrast.

## Shapes
The design system adopts a **Rounded** shape language to soften the corporate atmosphere.

- **Standard Radius:** 12px (0.5rem) is the default for cards, input fields, and large buttons.
- **Small Elements:** Chips and tags should use a 4px or 6px radius.
- **Large Components:** Modals and main content containers use 16px (1rem) for a more modern, friendly appearance.

## Components
- **Buttons:** 
  - *Primary:* Solid `#0F2A44` with white text. 12px radius.
  - *Secondary:* Outline `#E5E7EB` with `#1F2933` text.
  - *Success:* Solid `#2E7D61` for final confirmations.
- **Input Fields:** 1px border `#E5E7EB`, 12px radius, 14px text. On focus, the border changes to the primary blue with a soft glow.
- **Tables:** No vertical borders. Horizontal separators only (`#E5E7EB`). The header row should have a subtle gray background (`#F9FAFB`).
- **Cards:** White background, 12px radius, 1px border. Used to group related data or form sections.
- **Chips/Badges:** Small labels with 4px radius, using low-saturation versions of the system colors for status (e.g., a very light green background for "Success" labels).
- **Sidebar Items:** Clear active state using a vertical 4px bar on the left edge in the primary color.