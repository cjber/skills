# Evidence and decisions for documentation writing

The skill's workflow is a synthesis. Published style guides supply editorial
recommendations, accessibility standards supply specific requirements, and the
studies below describe measured effects in particular tasks. None validates this
skill end to end. Evaluate it by supported claims and reader success.

## Reader needs and document structure

[Diataxis](https://diataxis.fr/) distinguishes learning, accomplishing a task,
looking up information and understanding. These needs explain why a tutorial,
how-to, reference and explanation have different structures. Its
[incremental adoption guidance](https://diataxis.fr/how-to-use-diataxis/) rejects
imposing empty categories. Choose the relevant need, then improve the existing
page. Do not generate four pages or a universal section template.

[Google's procedures guidance](https://developers.google.com/style/procedures)
puts context before action and keeps necessary preparation in the path. Its
[notices guidance](https://developers.google.com/style/notices) cautions against
hiding required steps in callouts. [Microsoft's procedure guidance](https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions)
likewise makes sequence and finishing actions explicit. Their markup conventions
differ. Reuse the reader-facing purpose, while respecting local components.

[Progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/)
keeps frequently needed choices visible and defers specialised details, with a
cost to discovery. Our application to docs: link to optional background, but keep
prerequisites and serious consequences beside the relevant action. A rare failure
can still deserve visible treatment when its harm is high.

[Write the Docs principles](https://www.writethedocs.org/guide/writing/docs-principles/)
define completeness relative to scope and allow useful repetition. A canonical
explanation can coexist with a repeated warning or placeholder meaning at an
independent entry point. Keep those copies synchronised. Concision does not mean
removing the facts needed to finish the task.

## Evidence, availability and maintenance

[GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
are based on tags, but a tag and a release have separate dates. [GitLab's feature-flag guidance](https://docs.gitlab.com/development/documentation/feature_flags/)
distinguishes introduction, enablement and general availability. Neither provides
a universal rule that the newest tag is deployed for every reader.

Our evidence workflow therefore records the relevant artifact, client, service
configuration, permissions and rollout. Inspect the released behaviour, not only
commit ancestry: a revert or disabled flag can invalidate an apparently included
feature. A policy promise needs a policy owner or authoritative published policy.
A polished demo, help entry or another agent's assurance is not implementation proof.

[Google's timeless documentation](https://developers.google.com/style/timeless-documentation)
favours the supported state over unanchored novelty. Preserve version boundaries
when they change the reader's path; put historical narration into release or
migration material when that is its purpose.

[Docs as Code](https://www.writethedocs.org/guide/docs-as-code/) connects documentation
to version control, review and automated checks. [GitLab's documentation testing](https://docs.gitlab.com/development/documentation/testing/)
illustrates separate checks for prose, links, diagrams, metadata and generated
content. This supports layered validation, not installing the same stack everywhere.
A successful structural check cannot establish release availability or reader success.

## Accessibility, examples and recovery

[W3C's writing tips](https://www.w3.org/WAI/tips/writing/) cover semantic headings,
descriptive links, image alternatives and clear input instructions. [WCAG's sensory-characteristics explanation](https://www.w3.org/WAI/WCAG22/Understanding/sensory-characteristics.html)
explains why an instruction cannot depend solely on colour, position, shape or
sound. A supplementary visual cue is allowed. Naming the action or label is more
reliable than telling every reader to find a coloured icon.

[Google's sample guidance](https://developers.google.com/style/code-samples) marks
omitted code and treats incomplete copyable examples carefully. Its
[placeholder guidance](https://developers.google.com/style/placeholders) gives
replacement values meaningful names and explanations. Our extension for agents:
record which examples were executed, and distinguish illustrative output from an
observed result. AI transcripts demonstrate intent and an interaction, not a
promise of exact wording or perfect compliance.

[W3C's error-suggestion explanation](https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html)
covers known corrections for detected input errors, with security exceptions.
[Microsoft's legacy error-message guidance](https://learn.microsoft.com/en-us/windows/win32/uxguide/mess-error)
separates problem, cause and solution, and discourages invented explanations for
unknown failures. We apply that reasoning to troubleshooting: name a recognisable
symptom, distinguish a cause from a hypothesis, and provide a supported next step.
This is a synthesis, not a claim that WCAG mandates a troubleshooting section in
every document. The Microsoft page's Windows 7 UI conventions are not imported.

## Editorial quality and agent writing

[Google's tone guidance](https://developers.google.com/style/tone) prioritises
useful information and respectful, direct prose. It warns against repeated
openings, assumed ease, inflated language and empty introductions. [GOV.UK's user-needs guidance](https://www.gov.uk/guidance/content-design/user-needs)
requires a real reader need rather than inventing one to justify existing content.

Our editing test is whether a passage changes what the reader can do, decide or
understand. Generic praise often fails that test. Repeated technical names,
parallel steps, useful warnings and actual uncertainty can pass it. Do not replace
canonical terminology with synonyms merely to vary the prose.

The empirical evidence is more limited than a blacklist of supposed AI tells:

| Original study | Finding and scope | Implication for this skill |
|---|---|---|
| [Reinhart et al., grammatical and rhetorical variation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/) | Particular GPT and Llama models differed from human continuation samples across genres, including nominalisation and participial-clause rates. It did not study this skill or product docs. | Inspect constructions for concrete meaning and genre fit. A grammatical form alone is not a defect or authorship proof. |
| [Kobak et al., excess vocabulary](https://pmc.ncbi.nlm.nih.gov/articles/PMC12219543/) | Population-level vocabulary shifts appeared in biomedical abstracts. The method cannot identify individual LLM-processed abstracts. | Review repeated generic framing across pages. Do not infer individual authorship from one word. |
| [Padmakumar and He, content diversity](https://arxiv.org/html/2309.05196v3) | In an essay co-writing experiment, InstructGPT assistance reduced diversity; GPT-3 assistance did not show the same significant effect. | Ground outlines and examples in the actual reader problem. Do not generalise a model-dependent effect to every workflow. |
| [Doshi and Hauser, creativity and collective diversity](https://pmc.ncbi.nlm.nih.gov/articles/PMC11244532/) | GPT-4 ideas improved some ratings of short stories while increasing similarity among assisted stories. | Fluency and useful distinct information are separate questions. Technical consistency is still valuable. |
| [Xiong et al., expressed uncertainty](https://arxiv.org/html/2306.13063v2) | Confidence elicited from several models in question-answering tasks was often poorly calibrated. No method dominated across tasks. | Verify the source instead of accepting confident prose or a self-assigned probability. Blanket hedging is not verification. |
| [FActScore](https://aclanthology.org/2023.emnlp-main.741/) | Generated biographies can mix supported and unsupported atomic facts within one sentence. Precision is measured against a specified source. | Decompose material claims. Check task completeness separately: removing hard claims can improve precision while making a guide unusable. |
| [Liang et al., detector bias](https://arxiv.org/html/2304.02819v3) | Particular detectors misclassified many non-native English essays in the study's samples. This is not a present-day universal error rate. | Do not penalise clear, predictable English or accept detector scores as quality gates. |
| [Sadasivan et al., detection reliability](https://arxiv.org/html/2303.11156v4) | Detection robustness depends on the setting and can degrade under paraphrasing; theoretical bounds depend on distributional distance. | Optimising a rewrite to evade detection does not establish usefulness or truth. Provenance and watermarks are different mechanisms. |

These studies mainly concern English abstracts, essays, stories and question
answering with older model snapshots. Transfer to current software documentation
is our proposal. No cited study establishes an em dash, a three-item list, a
particular adjective or repeated sentence length as a reliable documentation
quality test. Local punctuation preferences may still be explicit house style.

## Illustrative rewrites

The following product details are invented for illustration. Use a rewrite only
when its labels, permissions, numbers and behaviour have been verified.

| Before | After | Decision |
|---|---|---|
| "Unlock effortless collaboration with powerful reporting." | "Share a saved report with your workspace. Recipients can view it; editors can change it." | Replace praise with a capability and access boundary. |
| "Click the green button on the right." | "Select **Export CSV**. Your browser downloads the file." | Name the action and recognisable result. |
| "Ensure the service is properly configured." | "Open **Service status** and check that **State** is **Running**." | Replace an undefined condition with a check. |
| "Automatic retries ensure uninterrupted delivery." | "After the third retry fails, the delivery status changes to **Failed**." | A bounded mechanism is different from a reliability guarantee. Never invent the retry count. |
| "The agent always produces accurate summaries." | "Ask for a summary with source links. Check the linked passages before publishing it." | Separate drafting from correctness. Verify source-link support. |
| "Export works across all devices." | "Export reports from the desktop app." | Narrow to proved scope; keep the missing mobile check in review notes. |
| "Select **Delete**. See advanced details for recovery." | "Deleting this report permanently removes it. Download a copy first if you need one, then select **Delete report**." | Keep a verified irreversible consequence before the action. |
| "In this section, we explain how to export." | Remove it when the heading already says **Export a report**. | Keep an introduction only when it adds scope, a prerequisite or another useful fact. |

A contrast can carry necessary meaning: "Pausing stops future runs; cancelling
stops the current run." Version history can also be necessary in a migration:
"In version 2.4, **Export** replaces **Download**." Preserve such distinctions
when verified. Removing every contrast or date would lose information.

## Evaluation and local ownership

Before making strong claims about the skill, compare outputs against fact sheets
for a capability guide, procedure, troubleshooting answer, explanation and migration.
Include tempting unsupported claims and cases needing repeated warnings or history.
Review unsupported additions, missing task facts, example usability, unnecessary
prose and honesty about verification separately. A static review is not a reader
study, and a single successful run is not a measured general improvement.

Keep product terminology, supported clients, release selection, MDX components,
metadata, publishing policy and exact gate commands in the repository. Keep
personal punctuation preferences in personal instructions. Agent-facing instruction
mechanics remain in `skill-writing`; this skill governs human-facing documentation.

## Attribution

This is original synthesis informed by the linked primary publications and guides.
It does not reproduce a third-party skill or import a publisher's entire house
style. Source recommendations, measured findings and our workflow are distinguished
above so they can be challenged or updated independently.

## Website and interface copy

[GOV.UK: Writing for user interfaces](https://www.gov.uk/service-manual/design/writing-for-user-interfaces)
recommends putting useful words first, keeping interface text short and direct, and
using descriptive headings and links. Apply this to labels and help text as well as
page prose. Its government-specific tone and typography rules do not override a
product's own style. This supports a coverage check and reader-focused editing,
not a forbidden-word list or a claim that polished prose proves AI authorship.
