# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

This guide covers **financial aid navigation at Ohio State University** — the lived realities of FAFSA timing, aid appeals, lesser-known scholarships, work-study vs. part-time work, and bridging the gap when tuition is due before aid disburses. Official aid pages publish procedures and deadlines but not *outcomes*: which appeals actually get approved, realistic processing timelines, and the workarounds students rely on. That practical knowledge is scattered across Reddit, College Confidential, and student Q&A forums, is often contradictory, and rarely surfaces through official channels.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

The corpus is registered in [sources.py](sources.py) and built by `ingest.py → clean.py → chunk.py`. These **12 sources were collected** (scraped into `documents/clean/`) and are what the system was evaluated on:

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | OSU Student Financial Aid — Appeals | Official university page | https://sfa.osu.edu/current-student/accept-aid/appeals |
| 2 | OSU SFA — How aid is applied | Official university page | https://sfa.osu.edu/current-student/manage-aid/how-aid-applied |
| 3 | The Lantern — "Leftover funds: $615K unawarded" | OSU student newspaper | https://www.thelantern.com/2020/02/leftover-funds-unused-scholarships-amount-to-615000/ |
| 4 | The Lantern — "DeWine's budget revamps grants" | OSU student newspaper | https://www.thelantern.com/2023/02/dewines-budget-revamps-government-grant-opportunities-expected-to-help-students-most-in-need/ |
| 5 | The Lantern — "How to pay for graduate school" | OSU student newspaper | https://www.thelantern.com/2019/02/how-to-pay-for-graduate-school/ |
| 6 | Claimyr Q&A — Professional Judgment Appeal | Community Q&A forum | https://claimyr.com/financial-services/fafsa/FAFSA-Professional-Judgment-Appeal-experiences-Success-rates-for-special-circumstances/2025-03-28 |
| 7 | Claimyr Q&A — Disbursement timing vs. due date | Community Q&A forum | https://claimyr.com/financial-services/fafsa/FAFSA-disbursement-timing-vs-tuition-due-date-getting-bill-despite-approval/2025-03-28 |
| 8 | Claimyr Q&A — Aid disbursement delays | Community Q&A forum | https://claimyr.com/financial-services/fafsa/FAFSA-aid-disbursement-delays-when-should-financial-aid-actually-hit-student-accounts/2025-03-28 |
| 9 | FinAid.org — Financial Aid Appeal | Financial-aid guide | https://finaid.org/financial-aid-applications/financial-aid-appeal/ |
| 10 | Fastweb — When award letters arrive | Financial-aid guide | https://www.fastweb.com/financial-aid/articles/when-will-the-financial-aid-award-letter-arrive |
| 11 | College Essay Guy — Federal Work-Study | Financial-aid guide | https://www.collegeessayguy.com/blog/federal-work-study-program |
| 12 | Sallie — Hidden Gem Scholarships | Financial-aid guide | https://www.sallie.com/resources/scholarships/hidden-gems |

**Identified but not yet collected** (JS-rendered, login-, or bot-blocked — registered in `sources.py` for manual collection into `documents/manual/`): r/OSU, r/financialaid · r/scholarships · r/StudentLoans, two College Confidential appeal-letter threads, and the studentaid.gov Work-Study page. These are the **student-voice** sources; their absence is central to the failure case below.

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 600 characters (≈ 150 tokens).

**Overlap:** 100 characters (≈ 17%).

**Why these choices fit your documents:** The embedding model `all-MiniLM-L6-v2` truncates input at **256 word-piece tokens**, so any chunk much larger than ~150 tokens would be silently cut before embedding — 600 characters leaves safe headroom. The corpus is forum/Q&A-heavy, where individual posts run from one sentence to a few paragraphs, so a 600-char chunk captures a typical single post or a coherent slice of a longer thread. The 100-char overlap keeps a single fact (e.g. "job-loss appeals are approved ~80% of the time") from being split across a boundary. **Preprocessing:** `clean.py` strips scripts/nav/footers and *small* boilerplate elements with BeautifulSoup (it deliberately keeps large content wrappers, since layout classes like `sidebar-right` were wrapping whole articles), filters junk lines ("Related Posts", "X comments"), and decodes raw bytes with a utf-8→cp1252 fallback to avoid smart-quote mojibake. `chunk.py` snaps both the start and end of each chunk to a sentence/space boundary so chunks never begin or end mid-word, and prepends a source tag (e.g. `[OSU SFA - official]`) to every chunk for attribution.

**Final chunk count:** **372 chunks** across the 12 collected documents (sizes 294–632 chars; all under the 256-token cap, comfortably inside the healthy 50–2,000 band).

### Sample Chunks

Five chunks pulled straight from `documents/chunks.jsonl` (printed by `python chunk.py`), each labeled with its source document and `chunk_index`. The leading `[tag]` is prepended to every chunk for attribution:

1. **`osu_sfa_appeals` #0** — *[OSU SFA - official]*
   > [OSU SFA - official] While attending Ohio State University, there are several types of appeals you may utilize to address special or unusual circumstances, educationally related costs that may exceed the standard cost of attendance, and loss of university-administered scholarships. Change of Circumstances Special Circumstances - If you or your family's financial situation has changed from what is reflected…

2. **`finaid_appeal` #0** — *[FinAid.org - general guide]*
   > [FinAid.org - general guide] As thorough as the FAFSA is in its line of questioning, there are certain financial circumstances that it is unable to capture. Students and their families also face unforeseen events the year that they apply for the FAFSA, making it ineligible to include for that application cycle. In these instances, the financial aid package that is distributed to students is not enough to meet their…

3. **`claimyr_disbursement_timing` #0** — *[Claimyr Q&A - general]*
   > [Claimyr Q&A - general] FAFSA disbursement timing vs. tuition due date - getting bill despite approval? I'm totally confused about FAFSA disbursement timing. I submitted my FAFSA back in January, got approved with a decent SAI, and my college financial aid office confirmed everything was good to go for fall semester. But today I just got this scary email saying I owe $3200 for my classes??…

4. **`collegeessayguy_work_study` #0** — *[College Essay Guy - general guide]*
   > [College Essay Guy - general guide] A Guide to the Federal Work-Study Program. Want to minimize student loan debt while attending college or graduate school? A work-study job can help. The federal work-study program ensures part-time jobs are available to undergraduate and graduate students with financial need. How do you apply for the program?…

5. **`lantern_leftover_funds` #0** — *[The Lantern - OSU student news]*
   > [The Lantern - OSU student news] Ten colleges within Ohio State did not award more than $615,000 worth of scholarships. Fifty in-state students could have attended Ohio State tuition-free this past year with the amount of scholarship money colleges left unspent. Ten colleges within Ohio State did not award $615,000 worth of undergraduate scholarships in fiscal year 2019…

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, with vectors stored in **ChromaDB** configured for **cosine distance** (`hnsw:space: cosine`). It runs locally with no API key or rate limits, produces 384-dim embeddings, is fast on CPU (372 chunks embedded in ~20s), and performs well on the short English passages that dominate this corpus.

**Production tradeoff reflection:** If cost weren't a constraint I'd evaluate a hosted model such as OpenAI `text-embedding-3-large` or Voyage `voyage-3`. The tradeoffs I'd weigh: (1) **context length** — MiniLM's 256-token cap forces small chunks; a larger input window could embed whole forum threads and reduce boundary-splitting; (2) **accuracy on domain-specific text** — financial-aid jargon (SAI, COA, professional judgment, Title IV) may embed more distinctly in a larger model, which could have helped the Q2 retrieval miss below; (3) **latency & dependency** — API models add network latency and a key/quota dependency that a local model avoids; (4) **multilingual** — not needed here (English-only sources), so I wouldn't pay for it. For this project the local model is the right call; at production scale I'd A/B it against `text-embedding-3-large` on the 5 eval questions before switching.

---

## Retrieval Test Examples

Captured from `python retrieve.py` (top-k = 4, cosine distance — lower is closer). For each query, the top returned chunks are shown with their `source_id #chunk_index` and distance.

### Example 1 — "What makes a financial aid appeal more likely to be approved?"

| Rank | Chunk | Distance | Snippet |
|---|---|---|---|
| 1 | `finaid_appeal` #2 | 0.288 | "…reserved for special circumstances. Reasons to Appeal Your Financial Aid Package: Job loss or decrease in income, Divorce or separation…" |
| 2 | `claimyr_pj_appeal` #1 | 0.316 | "…something about a 'Professional Judgment Appeal'… Has anyone successfully appealed their financial aid decision? What kind of documentation did you need?…" |
| 3 | `finaid_appeal` #1 | 0.319 | "…they can ask their college about appealing financial aid. A financial aid appeal, also referred to as a professional judgment, is the process by which a student and their family…" |
| 4 | `claimyr_pj_appeal` #13 | 0.337 | "…Make sure you understand exactly what qualifies a…" |

**Why these chunks are relevant:** The query asks what improves an appeal's odds, and the #1 hit (`finaid_appeal` #2) is the single most on-point passage in the corpus — it literally enumerates the qualifying reasons ("Job loss or decrease in income, Divorce or separation…"). The #3 hit defines what a professional-judgment appeal *is*, providing the framing, and the two `claimyr_pj_appeal` chunks add real applicant experiences about documentation. Retrieval surfaced both the authoritative "what qualifies" list and the lived "how it went" context, which is exactly the spread the question needs.

### Example 2 — "What should I do if my tuition bill is due before financial aid disburses?"

| Rank | Chunk | Distance | Snippet |
|---|---|---|---|
| 1 | `claimyr_disbursement_timing` #27 | 0.299 | "…check if your school offers a 'financial aid deferment' on your student account - it's different from…" |
| 2 | `claimyr_disbursement_timing` #3 | 0.307 | "…the billing system sees you owe money, while the financial aid system knows you have pending aid…" |
| 3 | `claimyr_disbursement_timing` #55 | 0.329 | "…try calling the student accounts/billing office directly. They can often see your pending aid status and confirm your registration is protected while you wait for disbursement…" |
| 4 | `claimyr_disbursement_timing` #8 | 0.330 | "…As long as the aid is showing as pending in your account, you're fine. Most schools won't d[rop you]…" |

**Why these chunks are relevant:** Every returned chunk comes from the disbursement-timing thread, which is precisely the scenario in the query (bill due before money arrives). The #1 hit names the concrete action — request a "financial aid deferment" — while #3 and #4 reassure that pending aid protects registration and tell the student exactly who to call. Together they give an actionable answer (deferment + contact billing) plus the reassurance the worried student is looking for.

### Example 3 — "How does work-study differ from a regular part-time job for financial aid?"

| Rank | Chunk | Distance | Snippet |
|---|---|---|---|
| 1 | `collegeessayguy_work_study` #1 | 0.308 | "…Are work-study jobs better than traditional part-time jobs?…" |
| 2 | `collegeessayguy_work_study` #3 | 0.352 | "…The federal work-study program is a government-funded program that helps undergraduate and graduate students secure part-time jobs to pay for educat[ion]…" |
| 3 | `collegeessayguy_work_study` #20 | 0.356 | "…the money you get from a work-study job isn't calculated into your FAFSA. That means the money you earn from work-study won't reduce your eligibility for financial aid…" |
| 4 | `collegeessayguy_work_study` #17 | 0.380 | "…Some part-time jobs pay more than work-study jobs. So, why would you consider applying for this type of job?…" |

The retrieved chunks correctly isolate the work-study vs. part-time comparison, including the key distinguishing fact in #3 (work-study income is excluded from the FAFSA).

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt (in [generate.py](generate.py)) instructs the model to *"Answer the question using ONLY the information in the numbered context documents…"* with explicit rules: *"Use only facts stated in the context. Do NOT use outside or prior knowledge. Do not speculate, generalize, or fill in gaps. If the context does not contain enough information, reply with exactly: 'I don't have enough information on that.'"* The call uses `temperature=0` for deterministic, low-drift output.

Grounding is also enforced **structurally**, not just by instruction: `retrieve()` returns the top-4 chunks, and `ask()` filters them to a cosine distance ≤ 0.70. If **no** chunk clears that bar (e.g. an off-domain question like "best pizza near campus"), the system returns the refusal string **without ever calling the LLM** — so it is structurally impossible to answer from training knowledge. Retrieved chunks are passed as a numbered list (`[1] (source: …)`) so the model can cite by number.

**How source attribution is surfaced in the response:** Attribution is built **programmatically** from the retrieved chunks' metadata — `ask()` collects each chunk's `source_id` and looks up its tag and URL from `sources.py`, dedupes them, and returns them as a `sources` list. This is guaranteed by code, not parsed from or trusted to the LLM. The model *additionally* cites the context numbers (`[1]`, `[2]`) inline for traceability, but even if it omitted them the source list would still be correct. When the answer is the refusal string, the sources list is suppressed so the UI never implies a document backed a non-answer. The Gradio UI ([app.py](app.py)) shows the answer and a separate "Retrieved from" panel listing those sources.

### Grounded Generation Examples

Verbatim output from `python generate.py`. Note the inline `[n]` citations in the answer text and the programmatic "Retrieved from" source list — both are visible attribution tying every claim back to a collected document.

**Example A — "What makes a financial aid appeal more likely to be approved?"**

```
A financial aid appeal is more likely to be approved if there are special circumstances
such as job loss, divorce, death of a parent, or unreimbursed medical expenses [1]. Valid
reasons for appeal include loss of employment, significant reduction in income, divorce or
separation of parents, death of parent or spouse, and extraordinary medical expenses [4].

Retrieved from:
  • [FinAid.org - general guide] finaid_appeal — https://finaid.org/financial-aid-applications/financial-aid-appeal/
  • [Claimyr Q&A - general] claimyr_pj_appeal — https://claimyr.com/financial-services/fafsa/FAFSA-Professional-Judgment-Appeal-experiences-Success-rates-for-special-circumstances/2025-03-28
```

**Example B — "What should I do if my tuition bill is due before financial aid disburses?"**

```
If your tuition bill is due before financial aid disburses, you should check if your school
offers a "financial aid deferment" on your student account, which defers the payment
deadline until your financial aid processes [1]. You can also try contacting the student
accounts/billing office directly to confirm your registration is protected while you wait
for disbursement [3]. Additionally, make sure you've accepted your financial aid package,
completed entrance counseling, and signed your Master Promissory Note if you're receiving
loans [2].

Retrieved from:
  • [Claimyr Q&A - general] claimyr_disbursement_timing — https://claimyr.com/financial-services/fafsa/FAFSA-disbursement-timing-vs-tuition-due-date-getting-bill-despite-approval/2025-03-28
```

**Out-of-scope example — "What's the best pizza place near campus?"**

```
I don't have enough information on that.
```

No source list is shown. This off-domain query never reaches the LLM: no retrieved chunk clears the cosine ≤ 0.70 relevance gate, so `ask()` returns the refusal string structurally. This is the grounding guarantee in action — the system cannot answer from training knowledge when the corpus has nothing relevant.

---

## Query Interface

The interface is a **Gradio** web app ([app.py](app.py)), launched with `python app.py` and served at `http://localhost:7860`.

**Input field**
- **"Your question"** — a single-line textbox (placeholder: *"e.g. How do I get a financial aid appeal approved?"*). Submitting with **Enter** or clicking the **"Ask"** button triggers the query. Empty input returns a "Please enter a question." prompt.

**Output fields**
- **"Answer"** (8-line textbox) — the grounded answer with inline `[n]` citations, or the refusal string.
- **"Retrieved from"** (4-line textbox) — the deduped source list (tag + `source_id` + URL), or *"(no sufficiently relevant sources)"* when the query is refused.

**Sample interaction transcript**

```
┌─ Unofficial Guide — Ohio State Financial Aid ─────────────────────────────┐
│ Ask about appeals, FAFSA/disbursement timing, scholarships, or work-study.│
│                                                                           │
│ Your question:                                                            │
│ [ How does work-study differ from a regular part-time job for aid?     ]  │
│                                  [ Ask ]                                  │
│                                                                           │
│ Answer:                                                                   │
│ Work-study jobs differ from regular part-time jobs in that the money      │
│ earned from a work-study job isn't calculated into the FAFSA, which means │
│ it won't reduce eligibility for financial aid [3]. This is a key benefit  │
│ of work-study jobs, allowing students to earn income without risking      │
│ their financial assistance.                                               │
│                                                                           │
│ Retrieved from:                                                           │
│ • [College Essay Guy - general guide] collegeessayguy_work_study —        │
│   https://www.collegeessayguy.com/blog/federal-work-study-program         │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

Run via `python generate.py` / the Gradio app, with `k=4` and the 0.70 cosine relevance gate.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What reasons make a financial aid appeal at OSU more likely to be approved? | Documented change in circumstances (job loss, income drop, medical, divorce) with paperwork; vague requests fail | **"I don't have enough information on that."** — despite retrieving the OSU appeals page and FinAid's explicit list of valid appeal reasons (distances 0.29–0.34) | Relevant (best 0.286) | **Inaccurate** (false refusal) |
| 2 | How long between submitting the FAFSA and seeing the aid package at OSU? | ~3 days–3 weeks to process FAFSA, then 2–6 weeks for the award letter; faster if filed early | **"I don't have enough information on that."** — retrieved chunks were about *disbursement* timing (money hitting the account), not the FAFSA→award-letter timeline | Partially relevant (Fastweb timeline source not in top-4) | **Inaccurate** (refusal) |
| 3 | What to do if the tuition bill is due before aid disburses? | Request a financial-aid deferment / payment plan; pending aid generally protects you from being dropped | Recommends checking for a "financial aid deferment," visiting the aid office in person, and notes schools often wait until after add/drop to disburse [1,3,4] | Relevant (best 0.348) | **Accurate** |
| 4 | What scholarships/funding aren't widely advertised at OSU? | Departmental scholarships, under-applied awards (e.g. ~$615K unawarded), single ScholarshipUniverse application | **"I don't have enough information on that."** — despite retrieving the Lantern article stating $615K went unawarded from too few applicants (distance 0.27) | Relevant (best 0.270) | **Inaccurate** (false refusal) |
| 5 | What tradeoffs do students mention between work-study and a part-time job? | Work-study excluded from next year's FAFSA/SAI (doesn't cut aid); part-time pays more but counts as income | Correctly notes part-time can pay more while work-study offers flexibility, security, on-campus location — but **misses the key point that work-study income is excluded from the FAFSA** | Relevant (best 0.290) | **Partially accurate** |

**Summary:** 1 accurate, 1 partially accurate, 3 refusals (2 of them false refusals where the answer was in the retrieved context). Retrieval was relevant on 4/5; the dominant failure is at the **generation** stage — see below.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Q1 — "What reasons do students say make a financial aid appeal at Ohio State University more likely to be approved?" (Q4 fails the same way.)

**What the system returned:** "I don't have enough information on that." — a refusal, even though retrieval succeeded: the top results were `osu_sfa_appeals #0` (distance 0.286) and `finaid_appeal #2` (0.344), and `finaid_appeal #2` *literally lists* "Reasons to Appeal Your Financial Aid Package: Job loss or decrease in income, Divorce or separation… Death of a parent… Unreimbursed medical or dental expenses…" The exact answer was sitting in the retrieved context.

**Root cause (tied to a specific pipeline stage):** This is a **generation-stage false refusal**, not a retrieval failure. The cause is an interaction between the question's framing and the corpus composition. The question attributes the claim to *"students… at Ohio State University,"* but the collected corpus contains **no actual OSU student voices on appeals** — those are the Reddit/College Confidential sources that are JS-/bot-blocked and not yet collected. The retrieved evidence is official OSU and general FinAid prose. My strict grounding prompt ("use only facts stated in the context… if not enough, refuse") then led the model to judge that the context doesn't support *"what students say,"* so it refused — even though the underlying fact (the appeal reasons) is present. Confirming evidence: the **same question with neutral phrasing** ("What makes a financial aid appeal more likely to be approved?") produced a correct, grounded answer from the very same FinAid chunk during Milestone 5 testing. Only the "students say at OSU" framing triggered the refusal.

**What you would change to fix it:** (1) **Close the corpus gap** — collect the student-voice sources (r/OSU, r/financialaid, the College Confidential appeal threads) into `documents/manual/`, so claims framed as "students say" are literally supported. (2) **Relax the prompt's framing sensitivity** — instruct the model to answer the *underlying factual question* from authoritative context regardless of whether the question attributes it to students, while still refusing when the fact itself is absent. (3) A secondary, retrieval-side fix surfaced by Q2: the more on-point `fastweb_award_timeline` source was out-ranked in the top-4 by the larger, lexically similar Claimyr *disbursement* thread — raising `k` to 6–8 or de-duplicating by source before truncating would let the timeline source through.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the Retrieval Approach and Chunking Strategy in planning.md *before* coding meant every parameter was already decided when I prompted the AI to generate code. The spec fixed the model (`all-MiniLM-L6-v2`), top-k (4), chunk size/overlap (600/100), and — critically — tied the chunk size to the model's 256-token cap. That last detail meant the generated `chunk_text()` was correct on the first pass instead of producing oversized chunks that would be silently truncated at embedding time. The spec's plan to prepend a source tag to each chunk also made programmatic source attribution in Milestone 5 trivial, because the metadata was designed in from the start.

**One way your implementation diverged from the spec, and why:** The spec leaned heavily on **unofficial student-voice sources** (Reddit, College Confidential) as the heart of the guide. During ingestion, those sources turned out to be JavaScript-rendered or bot-blocked, so `requests` could only retrieve empty shells. I diverged by demoting them to manual collection and swapping in three scrapeable, more **official/journalistic** sources (FinAid.org, Fastweb, College Essay Guy) to keep ≥10 collected documents. This kept the pipeline buildable, but it shifted the corpus away from the "what students say" framing the eval questions assume — which is the direct cause of the false-refusal failures in Q1 and Q4. I also added a structural relevance gate (cosine ≤ 0.70) that wasn't in the original spec, to make off-domain refusals reliable.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Ingestion & chunking**

- *What I gave the AI:* My Documents list and Chunking Strategy section from planning.md plus the pipeline diagram, asking it to implement scripts that load the sources, clean them, and chunk at 600/100.
- *What it produced:* A BeautifulSoup cleaner that removed any element whose class matched a boilerplate pattern (`sidebar`, `nav`, `share`, …), plus a sliding-window chunker.
- *What I changed or overrode:* The cleaner **deleted The Lantern's entire article** because its body sat inside `<div class="row-primary sidebar-right">` — a layout class that matched "sidebar." I directed it to only remove *small* boilerplate elements (keeping any wrapper with substantial text / multiple `<p>`), to move junk removal to the line level, and to add a utf-8→cp1252 byte-decode fallback after I spotted mojibake ("student�s"). I also had it snap chunk **starts** (not just ends) to word boundaries after seeing chunks like "ot a bunch more grants."

**Instance 2 — Embedding, retrieval & grounding**

- *What I gave the AI:* My Retrieval Approach section (all-MiniLM-L6-v2, ChromaDB, top-k=4) and the grounding requirement (answer only from context, with source attribution), asking it to build the embedding, retrieval, and generation code.
- *What it produced:* Working `embed.py`/`retrieve.py`/`generate.py`, but the ChromaDB collection used the **default L2 distance**, and source citation was initially left to the LLM to include in its prose.
- *What I changed or overrode:* I overrode the distance metric to **cosine** (`hnsw:space: cosine`) so scores landed on the 0–1 scale my 0.6–0.7 relevance thresholds assume; directed it to **strip the source tag before embedding** (so the repeated tag wouldn't skew similarity) while keeping it for display; made **source attribution programmatic** (built from chunk metadata, not parsed from the model); and added the cosine ≤ 0.70 **relevance gate** that refuses without calling the LLM on off-domain queries.
