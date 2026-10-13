---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when the user wants to stress-test a plan, get grilled on their design, says "grill me", or when offered as a deep dive during project discovery.
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

For each question, provide your recommended answer.

Ask the questions one at a time.

## Step-Based Integration

When used in a step-based project:

- Ask each question with the **AskUserQuestion** tool (a multiple-choice form), one
  question per form. Put your recommended answer first, marked "(Recommended)", with
  the reasoning in its description. The user can give a different answer through "Other".
  If a question needs a description rather than a choice, ask it in plain text.
- When invoked during discovery, focus on the project goal and the findings gathered
  so far in the discovery conversation.
- Prioritise probing architecture decisions, external dependencies,
  edge cases, and scope boundaries — these are where hidden complexity lives.
- Discovery runs in plan mode, so do not write files. Add new findings and changed
  decisions to the discovery content that `/start` writes to `plans/000-discovery.md`
  and `plans/step-000-initial.md` after approval.
- When the interview reaches shared understanding, hand control back to
  the discovery skill to complete the remaining phases.

> Credit: Core concept by [Matt Pocock](https://github.com/mattpocock/skills).
