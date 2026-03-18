## 2025-05-14 - [Deletion Confirmation Pattern]
**Learning:** Destructive actions like deleting a project should always have a confirmation step to prevent accidental data loss. Using Radix UI's AlertDialog provides an accessible and styled way to implement this without custom modals.
**Action:** Always wrap delete buttons in an AlertDialog or similar confirmation component in this repository.

## 2025-05-14 - [Icon-Only Button Accessibility]
**Learning:** Icon-only buttons (e.g., Lucide-react icons used inside a button tag) are completely invisible to screen readers without an explicit aria-label.
**Action:** Audit all icon-only buttons and ensure they have descriptive aria-labels.

## 2025-05-15 - [Global Tooltip Provider Pattern]
**Learning:** In projects using Radix UI Tooltips, the `TooltipProvider` must be wrapped at the root level (e.g., in `App.js`) to enable tooltips across the entire application. Without this, individual `Tooltip` components will not render.
**Action:** Always verify `TooltipProvider` is present at the app root before implementing tooltips in individual pages.
