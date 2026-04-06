## 2025-05-14 - [Deletion Confirmation Pattern]
**Learning:** Destructive actions like deleting a project should always have a confirmation step to prevent accidental data loss. Using Radix UI's AlertDialog provides an accessible and styled way to implement this without custom modals.
**Action:** Always wrap delete buttons in an AlertDialog or similar confirmation component in this repository.

## 2025-05-14 - [Icon-Only Button Accessibility]
**Learning:** Icon-only buttons (e.g., Lucide-react icons used inside a button tag) are completely invisible to screen readers without an explicit aria-label.
**Action:** Audit all icon-only buttons and ensure they have descriptive aria-labels.

## 2025-05-15 - [Tooltip Trigger on Disabled Elements]
**Learning:** In Radix UI, tooltips will not trigger on elements with `disabled={true}` because they do not emit pointer events. To show a tooltip for a disabled button, wrap the button in a `span` and attach the `TooltipTrigger` to that wrapper.
**Action:** When adding tooltips to disabled buttons, always use a `span` wrapper inside `TooltipTrigger`.
