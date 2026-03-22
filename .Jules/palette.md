## 2025-05-14 - [Deletion Confirmation Pattern]
**Learning:** Destructive actions like deleting a project should always have a confirmation step to prevent accidental data loss. Using Radix UI's AlertDialog provides an accessible and styled way to implement this without custom modals.
**Action:** Always wrap delete buttons in an AlertDialog or similar confirmation component in this repository.

## 2025-05-14 - [Icon-Only Button Accessibility]
**Learning:** Icon-only buttons (e.g., Lucide-react icons used inside a button tag) are completely invisible to screen readers without an explicit aria-label.
**Action:** Audit all icon-only buttons and ensure they have descriptive aria-labels.

## 2025-05-15 - [Tooltip Implementation Pattern]
**Learning:** When wrapping Shadcn UI `Button` components or native `button` tags with Radix UI `TooltipTrigger`, the `asChild` prop is mandatory. This prevents invalid nested button markup which breaks accessibility and keyboard navigation.
**Action:** Always use `asChild` on `TooltipTrigger` when it contains another button-like element.

## 2025-05-15 - [Automated Tooltip Verification]
**Learning:** Visual verification of Radix tooltips with Playwright requires triggering the tooltip via `page.hover(selector)` followed by a short wait before asserting visibility, as tooltips are usually hidden until interaction.
**Action:** Use `.hover()` and `wait_for_timeout` in Playwright scripts to verify tooltip content visibility.
