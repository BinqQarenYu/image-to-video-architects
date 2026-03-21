## 2025-05-14 - [Deletion Confirmation Pattern]
**Learning:** Destructive actions like deleting a project should always have a confirmation step to prevent accidental data loss. Using Radix UI's AlertDialog provides an accessible and styled way to implement this without custom modals.
**Action:** Always wrap delete buttons in an AlertDialog or similar confirmation component in this repository.

## 2025-05-14 - [Icon-Only Button Accessibility]
**Learning:** Icon-only buttons (e.g., Lucide-react icons used inside a button tag) are completely invisible to screen readers without an explicit aria-label.
**Action:** Audit all icon-only buttons and ensure they have descriptive aria-labels.

## 2025-05-14 - [Tooltip Trigger Nesting]
**Learning:** When using Radix UI Tooltips with other interactive components like AlertDialog, the `TooltipTrigger` must wrap the `AlertDialogTrigger`. Both should use the `asChild` prop to ensure the underlying button receives all necessary attributes and event handlers without invalid nesting.
**Action:** Use nested `asChild` triggers when combining tooltips with dialogs or alerts.
