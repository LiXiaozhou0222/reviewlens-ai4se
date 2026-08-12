# ReviewLens UI Direction

**Task:** T13.1  
**Status:** Design contract for later UI implementation; no UI source code is created by this task.  
**Fixed design system:** Open Design `linear-app`  
**Review skill:** `web-design-guidelines` (pinned local guideline snapshot)

## 1. Purpose and boundaries

ReviewLens v1 is a desktop-first Git Diff risk review tool. The UI must make the deterministic conclusion understandable before showing optional AI advice, and must make the active runtime mode impossible to mistake.

This direction adopts the `linear-app` information hierarchy rather than copying its branding: compact desktop product framing, restrained surfaces, dense but readable technical information, and a single clearly primary action. MUI is an implementation component library only; it is not a second design system.

The following v1 surfaces are intentionally excluded and must not be introduced by later UI work:

- report history, persistent report detail pages, or cross-page recovery;
- AI retry controls or retry status history;
- finding filter controls;
- server-side export storage or download history;
- account, team, sharing, collaboration, or provider/base-URL configuration.

## 2. Page hierarchy

### 2.1 Review workspace (primary page)

1. **Persistent mode banner.** It appears before all task content. Demo reads that Mock advice is used, no real OpenAI call is made, and results disappear on refresh. Private identifies the local/private operating mode without exposing Vault secrets.
2. **Task header.** Product name, concise statement that only newly added Diff lines receive deterministic code findings, and the current language-support boundary.
3. **Input card.** Tabs or equivalent mutually exclusive controls for paste and one-file upload. It shows UTF-8 unified-Diff-only requirements and the 500 KB / 5,000-line limit before submission.
4. **Primary action.** One clearly labeled review action. It is the only primary button and becomes unavailable while the current request is pending.
5. **Request feedback.** Inline validation and public errors stay adjacent to the input/action; they do not replace the entire page or erase a completed result.
6. **Current report.** Rendered only for the current successful request. Order is: file/change summary, deterministic overall level, deterministic findings, then AI supplemental section.
7. **Browser export.** A secondary action creates Markdown from the current browser-held, already-sanitized report only. It does not imply report persistence.

### 2.2 Current report hierarchy

- Show the deterministic level with its text label (`Critical`, `High`, `Medium`, `Low`, or `None`) and the limitation: only new code in this Diff was checked. Never express `None` as approval or security certification.
- Put deterministic findings before AI findings and identify each source in text, not color alone.
- For unsupported-language files, state that only general deterministic rules were applied and that this is not a complete language review.
- If AI is unavailable, retain and display the deterministic result. The AI section contains only a mapped public status/reason, never an upstream response body.
- A finding's visible excerpt is the already-redacted excerpt supplied by the API. The UI must not reconstruct, reveal, or retain raw Diff text after the request flow completes.

### 2.3 Private Vault workspace

The Vault workspace exists only when the app runs in private mode through its loopback-only service boundary. It provides status, initialize/unlock, lock, update, and clear operations. It never displays a full key, master password, ciphertext, raw error detail, or a public-shareable management link.

Demo mode must not render this workspace or its controls. Its corresponding backend routes are absent, not merely visually hidden.

## 3. UI states and content contract

| State | Required presentation | Forbidden behavior |
| --- | --- | --- |
| Idle | Input instructions, mode banner, and disabled-result area or no result area. | Claiming prior results remain available. |
| Validating | Inline progress; input remains readable. | Sending invalid/oversize input. |
| Reviewing | Progress text; submit control disabled against duplicate requests. | Adding an AI-only blocking screen. |
| Input error | Mapped Chinese action-oriented error for empty, size, line, encoding, or Diff-format error. | Showing a stack trace, raw Diff, or undifferentiated generic failure. |
| Deterministic result + AI success | Deterministic and AI sections visibly separated. | Mixing AI advice into deterministic level/counts. |
| Deterministic result + AI unavailable | Complete deterministic section plus mapped AI status. | Hiding deterministic findings or implying the whole review failed. |
| Demo refresh/leave | Result is gone and mode banner remains. | Rehydrating a prior visitor report. |
| Private Vault locked | Review workflow remains usable; AI status states Vault is locked. | Asking a reviewer to enter a master password in the public review page. |

## 4. Content and visual rules

- Use semantic page landmarks, real headings, native buttons and form controls where possible; do not substitute non-semantic clickable `div` elements.
- Reserve color for reinforcement. Severity, provider source, mode, validation and AI state all require readable text/icon labels.
- Keep technical density deliberate: stable columns and short labels in finding lists, with descriptions and safe remediation visible on expand rather than a noisy dashboard.
- Loading motion is brief and non-essential. Respect `prefers-reduced-motion`; no state depends on animation finishing.
- Do not use toast-only errors for errors that block submission. Keep the actionable error near the responsible input and also announce it through the accessibility contract.

## 5. Implementation handoff

T14.1, T15.1 and T16.6 may implement only the above input, current-report/export, and private Vault/ModeGate surfaces. They must use the stable review API contract when available and add their own RED/GREEN evidence. This document does not authorize React source, tests, routes, or dependency changes.
