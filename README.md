# fusion-skill-testing · Skill Quality Testing

> © 2026 Bangbang fusion · Licensed under CC BY-NC-SA 4.0

Put any skill (single-file or multi-file package) through its paces: static review, full-path behavioral testing, tiered fixes, and regression — then get an evidence-backed defect list and a clear verdict: usable as-is, or fix these first. Platform-agnostic by design: it serves the user's goal of shipping a skill that is genuinely good and actually works, not any single platform's review rules.

## What problem it solves

| Scenario | The trap | What it does |
|:--|:--|:--|
| You just finished a new skill | It always looks fine while you're writing it, then falls apart on first use | Static review catches rule/reference errors first, then full-path testing shows real behavior |
| You just modified an old skill | You fixed A, but have no idea whether it broke B | Regression testing re-runs key paths to confirm no new regressions |
| An old skill needs a health check / polish before release | You don't know how good it actually is | Scores against maturity criteria (including a 4-level token-efficiency rating) and gives a direct verdict: usable / fix first |
| You worry about "fake passes" | The AI improvises on the fly to cover gaps, and it looks like it passed | The validity check distinguishes "faithful to spec" from "on-the-fly reinvent"; the latter does not count as passing |

## Who it's for

- People who write, modify, and maintain skills on any agent platform (WorkBuddy, Claude, self-hosted, etc.)
- People who want to polish a skill until it is good and safe to hand over
- Teams with shared skills that want one unified quality bar

## Getting started (no setup, just talk)

You don't need to read code — every report section has a plain-language summary, and the verdict (usable / fix first) is enough to make decisions; technical details are for the person doing the fixing.

- "Test this skill" → tests the current or specified skill (Standard mode, default)
- "Quick check" → form-level gate only (seconds, like a linter)
- "Deep test / full audit" → full deep evaluation (baseline comparison + five-dimension summary)
- "Run a regression test" → re-runs after fixes to confirm convergence
- "Can this skill be trusted?" → runs the full flow and gives a verdict
- When you don't name one, it defaults to the skill in the current conversation / most recently modified

**Which of the three modes? (one-line analogy)**

| Mode | Analogy | When to use |
|:--|:--|:--|
| Quick (gate) | Taking temperature: seconds-level format gate | Early drafts, after every iteration (like lint) |
| Standard (default) | Regular checkup: format + full-path behavior + token | Most of the time |
| Deep | Full exam + imaging: adds baseline comparison + five-dimension summary | Audit before release/publishing |

**With and without Python — what actually differs (transparent degradation)**

| Check layer | With Python | Without Python |
|:--|:--|:--|
| Form level (frontmatter/links/anchors/orphans/security) | Script runs automatically | Manual AI review item by item — slower, may miss details |
| Behavior level (paths/failure paths/regression) | Runs | Runs |
| Verdict reliability | Complete | Slightly discounted; report notes "script not run" |

Oversized packages (>50 files) automatically degrade to gate + main-path testing, or can be split with the "batched" method in the FAQ — limits stated upfront, not hidden

## Triggering it

- Triggered by plain words (test this skill, review skill, audit skill, check this skill, evaluate this skill, diagnose this skill, skill quality check, regression test)
- Works out of the box; no configuration needed
- Under the hood it runs `tools/formcheck.py` and reads the standards in `reference/` itself

## Quick example (a real conversation)

**You**: Test this skill
**It**: Sure — testing my-skill in Standard mode. Form-level check first; found 2 issues:
1. 🔴 SKILL.md L24 links to a file that doesn't exist (P0, must fix)
2. 🟡 Menu formatting is inconsistent in the README (P2, minor)
After the form level, I'll run the full-path behavioral tests — complete report in a few minutes.

**You**: How bad is it? Can I use it now?
**It**: One P0, verdict: fix first — a broken link means the model reads empty content during execution. Every defect lists which file to change and how, so just follow it.

**You**: Fixed it. Run the regression for me
**It**: Re-ran the fixed paths + adjacent paths + main flow — P0 eliminated, no new regressions, verdict: usable. Report generated with the defect list and evidence lines.

> Mode selection (Quick/Standard/Deep) is covered by the analogy table in "Getting started" above.

## When NOT to use it

- **Not about skill quality**: coding, translation, general Q&A — it won't trigger, and you shouldn't force it
- **Host can't read files / run scripts**: falls back to static review only (model knowledge + pasted content); behavioral testing isn't possible
- **Target is not a skill package**: plain documents, websites, and spreadsheets are out of scope
- **Purely subjective creative judgment**: with no objective criteria, "is it good" can't be tested

## Author's self-check list (avoid common mistakes)

Run through these 8 while writing a skill — most rework is avoidable (full criteria in reference/defects.md):

1. **Path-skipping**: If the first message says "give me step 2 directly", does it skip the gate? → Add "first message still starts at the entry; stage words are hints only"
2. **Placeholder leakage**: Could a hardcoded "word" in a template be output as real content? → Force replacement before output
3. **Re-running**: When a deliverable already exists, re-run or claim it? → Add state reconciliation
4. **Dual-source duplication**: Is the same rule written in two places? → One authoritative source, pointers elsewhere
5. **Phantom parameters**: Doc says "configurable parameter" but the script never reads it? → Delete it, or demote to a one-line pointer
6. **Vague completion**: Does "understood well enough" count as done? → Make it checkable and exhaustive
7. **Over/under-triggering**: Missing triggers for what it should handle, or catching what it shouldn't? → Align trigger words with the capability boundary
8. **Missing degradation**: Does it crash naked when the user's environment lacks something? → Add a fallback message and alternative path

## Anti-patterns at a glance (what the 3 most common traps look like)

The checklist above is "what to check"; this is "what the mistake looks like and how the test catches you" (full criteria in reference/defects.md):

| Anti-pattern | Bad pattern (one-glance recognition) | How the test catches it | Correct pattern |
|:--|:--|:--|:--|
| **Path-skipping** | Only "mid-flow" rules exist, no "first-message" rule | First message says "give me step 2 directly"; the model skips the gate and delivers → 🔴 P0 | Add "first message still starts at the entry; stage words are hints only" |
| **Placeholder leakage** | Reply templates hardcode a placeholder word instead of real content | Output contains the placeholder itself → 🔴 P0 | Delete the placeholder, or force replacement before output |
| **Re-running** | No "claim / skip" state reconciliation after a deliverable exists | The model re-runs the whole thing after an interjection → 🔴 P0 | Add state reconciliation: already produced → claim + one-line skip |

> These three account for most P0s in real evaluations. Fix these first, then optimize.

## FAQ

- **What do I need to install to test a skill?** Nothing. The host just needs to read files and run Python; it can also work fully offline (model knowledge + skill files).
- **I can't understand the FAILs in the report?** Every FAIL carries file/line evidence and a fix hint; still stuck, paste the raw error to the AI or check the glossary below.
- **Can I test without Python?** Yes. The form-level check degrades to manual AI review (item by item against the checklist); slightly less thorough, but the flow still runs.
- **Does it need internet?** No, fully local. It only goes online when time-sensitive or external info needs verification.
- **Can it only test WorkBuddy skills?** No. Any agent platform's skill package works, as long as it contains a SKILL.md.
- **What do P0/P1/P2 mean?** Defect severity tiers — see the glossary.
- **It says "fix first" — can I fix it myself?** Yes. Every defect says which file to change and how; say "regression test" after fixing to verify convergence.
- **Can I trust the verdict?** It separates "on-the-fly reinvent" from "faithful to spec" and only counts the latter as passing — designed to catch fake passes.
- **How do I judge whether a skill is actually good?** Look at five things: gate (any P0 hard flaws), reliability (does it degrade gracefully on errors), adaptability (does it trigger when it should and decline when it shouldn't), convention (is the doc understandable), effectiveness (does it actually run by its rules, no fake passes). The report condenses these into one verdict: **usable / fix first**.
- **How large a skill can it test?** Up to 50 files with a SKILL.md under 400 lines → full flow. Larger packages: ① quick route — gate + main path first, then the full behavioral pass on a subset you specify; ② batched route — split the package into 2-3 batches by subdirectory/module, one sub-report per batch, merge the conclusions at the end. Pick one; don't force it.
- **Common FAILs, in plain words**
  - `Link target not found` → A document references a filename that isn't in the package. Usually the file was renamed, moved, or has a case mismatch.
  - `Anchor not found` → A link jumps to a `#heading`, but that heading no longer exists in the target file. Usually the heading was edited without updating the link.
  - `Orphan file` → A file sits in the package but no document mentions it — the model will never read it.
  - `Missing frontmatter` → SKILL.md lacks its identity block, so the model can't recognize the skill or know when to invoke it.

## Glossary

| Term | Meaning |
|:--|:--|
| **P0 / P1 / P2** | Defect severity: P0 gate (must fix; cannot ship if present); P1 reliability/authenticity issues; P2 coverage/UX issues |
| **Token-efficiency (4 levels)** | 🟢 optimal path / 🟡 mostly fine / 🟠 clearly redundant / 🔴 severe waste; N/A when a P0 exists (correctness first) |
| **Faithful to spec vs reinvent** | Running the path exactly as the skill's docs define = faithful; AI improvising a flow on the fly = reinvent, **not counted as passing** |
| **gate (quick mode)** | Form-level + security + cross-references + description truthfulness, seconds, like a linter |
| **Five-dimension summary** | Trust / Reliability / Adaptability / Convention / Effectiveness — optional export on deep-summary requests |

> README is for you; `SKILL.md` and `reference/` are the AI's internal spec — you don't need to read them.

## How it stays accurate

- **The tester doesn't rewrite the spec**: paths follow what the skill document says, not what "makes more sense"
- **Defects must carry evidence**: symptom + file/line; unproven suspicions go in the report, not in the defect list
- **Scores are thermometers, not targets**: ratings diagnose problems; they don't tag a skill forever, nor justify optimizing for a better rating
- **Validity beats quantity**: 10 faithful paths beat 20 improvised "passes"
