"""Single source of truth for the document corpus (see planning.md → Documents).

Each source has:
  id    – short slug, used as the raw/clean filename
  url   – page to scrape, or None for sources collected manually (e.g. Reddit,
          which blocks automated fetching). Drop manual saves in documents/manual/<id>.txt
  tag   – source tag prepended to every chunk for attribution + to keep
          school-specific vs. general content distinguishable (planning.md → Chunking)
  scope – "school" (Ohio State-specific) or "general"
"""

SOURCES = [
    # ---- School-specific: Ohio State ----
    {
        "id": "osu_sfa_appeals",
        "url": "https://sfa.osu.edu/current-student/accept-aid/appeals",
        "tag": "[OSU SFA - official]",
        "scope": "school",
    },
    {
        "id": "osu_sfa_how_aid_applied",
        "url": "https://sfa.osu.edu/current-student/manage-aid/how-aid-applied",
        "tag": "[OSU SFA - official]",
        "scope": "school",
    },
    {
        "id": "lantern_leftover_funds",
        "url": "https://www.thelantern.com/2020/02/leftover-funds-unused-scholarships-amount-to-615000/",
        "tag": "[The Lantern - OSU student news]",
        "scope": "school",
    },
    {
        "id": "lantern_dewine_grants",
        "url": "https://www.thelantern.com/2023/02/dewines-budget-revamps-government-grant-opportunities-expected-to-help-students-most-in-need/",
        "tag": "[The Lantern - OSU student news]",
        "scope": "school",
    },
    {
        "id": "lantern_pay_grad_school",
        "url": "https://www.thelantern.com/2019/02/how-to-pay-for-graduate-school/",
        "tag": "[The Lantern - OSU student news]",
        "scope": "school",
    },
    # ---- General: experiential / unofficial ----
    {
        "id": "claimyr_pj_appeal",
        "url": "https://claimyr.com/financial-services/fafsa/FAFSA-Professional-Judgment-Appeal-experiences-Success-rates-for-special-circumstances/2025-03-28",
        "tag": "[Claimyr Q&A - general]",
        "scope": "general",
    },
    {
        "id": "claimyr_disbursement_timing",
        "url": "https://claimyr.com/financial-services/fafsa/FAFSA-disbursement-timing-vs-tuition-due-date-getting-bill-despite-approval/2025-03-28",
        "tag": "[Claimyr Q&A - general]",
        "scope": "general",
    },
    {
        "id": "claimyr_disbursement_delays",
        "url": "https://claimyr.com/financial-services/fafsa/FAFSA-aid-disbursement-delays-when-should-financial-aid-actually-hit-student-accounts/2025-03-28",
        "tag": "[Claimyr Q&A - general]",
        "scope": "general",
    },
    {
        "id": "finaid_appeal",
        "url": "https://finaid.org/financial-aid-applications/financial-aid-appeal/",
        "tag": "[FinAid.org - general guide]",
        "scope": "general",
    },
    {
        "id": "fastweb_award_timeline",
        "url": "https://www.fastweb.com/financial-aid/articles/when-will-the-financial-aid-award-letter-arrive",
        "tag": "[Fastweb - general guide]",
        "scope": "general",
    },
    {
        "id": "collegeessayguy_work_study",
        "url": "https://www.collegeessayguy.com/blog/federal-work-study-program",
        "tag": "[College Essay Guy - general guide]",
        "scope": "general",
    },
    {
        "id": "sallie_hidden_gems",
        "url": "https://www.sallie.com/resources/scholarships/hidden-gems",
        "tag": "[Sallie - general guide]",
        "scope": "general",
    },
    # ---- Manual collection: JS-rendered (requests gets only a shell) or
    #      blocked. Save as plain text in documents/manual/<id>.txt and the
    #      pipeline picks them up. ----
    {"id": "cc_appeal_letter_2017", "url": None, "tag": "[College Confidential - general]", "scope": "general"},
    {"id": "cc_appeal_letter_2009", "url": None, "tag": "[College Confidential - general]", "scope": "general"},
    {"id": "studentaid_work_study", "url": None, "tag": "[Federal Student Aid - official]", "scope": "general"},
    # ---- Manual collection (Reddit blocks automated fetching) ----
    # Save threads as plain text in documents/manual/<id>.txt and the pipeline
    # will pick them up automatically.
    {"id": "reddit_osu", "url": None, "tag": "[r/OSU]", "scope": "school"},
    {"id": "reddit_financialaid", "url": None, "tag": "[r/financialaid - general]", "scope": "general"},
]

# Convenience lookup: id -> source dict
BY_ID = {s["id"]: s for s in SOURCES}
