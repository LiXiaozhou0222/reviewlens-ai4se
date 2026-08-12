# ReviewLens Accessibility Contract

**Task:** T13.1  
**Applies to:** the later Review workspace, current report and private-only Vault workspace  
**Design review basis:** `web-design-guidelines`, using its pinned local guideline snapshot

## 1. Keyboard and focus

- The full core flow is keyboard-operable: choose paste/upload, enter/select Diff, submit, read the current report, and export Markdown.
- All interactive controls must expose a visible `:focus-visible` style with sufficient contrast. Do not remove focus outlines unless an equally visible replacement is present.
- Input mode controls use a keyboard-accessible native pattern. File selection remains a labeled native file input or an equivalent control with the same keyboard behavior.
- When submit begins, focus stays predictable; disabling the submit button cannot strand focus. A duplicate activation while pending produces no second request.
- On a blocking validation or request error, move focus to the error summary or the first invalid control. The summary includes links/buttons that lead to the relevant input when more than one error is present.
- When a report arrives, do not force-focus a long report. Announce completion and provide a focused "skip to review result" target for a keyboard user who chooses it.
- Dialogs used for destructive Vault clear actions must trap focus, expose an accessible name/description, support Escape where safe, and restore focus to the invoking control after close.

## 2. Semantics, labels, and announcements

- Each page uses one `h1`; subsections use a non-skipping heading order. Findings are structured lists or tables with headers rather than visually grouped plain text.
- Every form field has a programmatic label. Required constraints (UTF-8, unified Diff, 500 KB, 5,000 lines) are connected with help text using `aria-describedby` or equivalent semantics.
- Status changes use bounded `aria-live` regions: a polite region for validating/reviewing/completion, and an assertive region only for submission-blocking errors. Do not announce raw Diff, redacted secret content, API keys, master passwords, or upstream error text.
- Buttons name their action ("Start review", "Export Markdown", "Lock Vault"), not just an icon. Icon-only controls, if any, require accessible names.
- Severity and source are communicated as text, for example "High - deterministic general rule" or "Medium - AI supplemental advice"; color alone is never the carrier of meaning.

## 3. Error, loading, and result accessibility

| Situation | Accessible behavior |
| --- | --- |
| Empty/invalid/oversize input | Distinct mapped error, linked to the input, announced once; no raw content echoed. |
| Pending review | Clear text status, disabled duplicate submit, no endlessly animated-only indication. |
| Deterministic result | Textual overall level and limitation statement; deterministic findings precede AI advice in reading order. |
| AI failure | Deterministic result remains readable; AI region gives a concise public reason without exposing provider details. |
| Unsupported language | Explicit capability limitation appears alongside the affected file, not only in a tooltip. |
| Demo mode | Persistent text that AI output is Mock and the current result disappears on refresh. |
| Private Vault error | Uniform safe message; no distinction that leaks whether password, ciphertext, or authentication tag failed. |

## 4. Visual readability and responsive floor

- The primary target is a common desktop browser, but narrow windows must retain input, submit, mode state, errors and result reading without horizontal clipping of essential content.
- Use adequate contrast for text, focus states, borders, and all status indicators. Test default, hover, disabled and focus-visible states; do not rely on low-contrast gray placeholder text as the only label.
- Use readable line length and non-overlapping spacing. Technical tables/lists may scroll horizontally only when they retain headers and an accessible alternative reading order.
- Honor browser zoom and text reflow without hiding the primary action or error summary. Do not lock font size or prevent zoom.

## 5. Privacy-preserving accessibility boundary

Accessibility support must not weaken ReviewLens data boundaries. Announcements, labels, browser export and copied report text consume only the sanitized response model. They must never expose raw Diff, full credentials, master passwords, original AI prompt/response or private error bodies.

## 6. Later verification obligations

Later task tests and manual evidence must verify at least: keyboard input/submit/export flow; focus placement for a validation error; visible textual severity/source labels; `aria-live` announcement of request state; Demo/private distinction; and that AI failure leaves the deterministic result available. Any implementation that cannot satisfy this contract needs a spec-compliance review before broadening scope.
