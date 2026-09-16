# Source catalog

Authoritative external sources, mapped to the skills they apply to. `scripts/build-sources.py` emits
a `references/sources.md` into each skill that has any, so an agent working inside a skill can find
what it should be checking against before it answers.

**References, never copies.** Nothing in this catalog reproduces source material. The catalog holds
a URL, who publishes it, what it is authoritative for, and what you are allowed to do with it. D3
and D6 settled that this repository carries no third-party licensed content, and a catalog of
pointers keeps that true while still putting the agent in front of the real document. It also keeps
the catalog live: a pointer to `ecfr.gov` is current the moment the regulation changes, and a copy
is wrong the moment it does.

## The license field is the point

Most of what a professional needs to cite is **not** open source. That is the single most important
thing this catalog records, because an agent that treats a free-to-read standard as reusable text
will reproduce it. The vocabulary is closed and `scripts/check-sources.py` enforces it:

| `license` | What it means | What an agent may do |
|---|---|---|
| `public-domain-usgov` | A work of the US federal government, 17 U.S.C. §105 | Quote, summarize, reuse freely |
| `public-domain` | Public domain for another reason, including government edicts | Quote, summarize, reuse freely |
| `cc0` | Dedicated to the public domain by its author | Quote, summarize, reuse freely |
| `cc-by` | Creative Commons Attribution | Quote and reuse with attribution |
| `cc-by-sa` | Attribution, **share-alike** | Quote with attribution; do not fold into this repository, the license is viral |
| `attribution-required` | Free to use under bespoke terms requiring credit | Quote with the publisher's required credit |
| `open-data` | Published as data under permissive bespoke terms | Use the data; read the terms before redistributing |
| `free-to-read` | Readable at no cost, all rights reserved | **Read and cite. Never reproduce.** |
| `registration-required` | Free but behind an account | Read and cite; the user must fetch it themselves |
| `paywalled` | Must be purchased | Cite the identifier only. Do not seek a copy |

`free-to-read`, `registration-required` and `paywalled` cover the sources most likely to be assumed
open and are not: ISO standards are sold, SANS white papers are copyrighted, and the FASB
Codification requires an account. A skill may name them as the authority and must not quote them.

## Format

One file per subject area. Each entry:

```toml
[[source]]
id = "nist-sp-800-53"                    # unique across the catalog, lowercase-hyphenated
title = "NIST SP 800-53 Rev. 5 — Security and Privacy Controls"
publisher = "NIST"
url = "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final"
license = "public-domain-usgov"          # from the table above
jurisdiction = "US"                      # or "EU", "global", a US state code, etc.
authoritative_for = "One sentence on what question this settles."
skills = ["security:security-architecture-review"]
data = "https://github.com/usnistgov/oscal-content"   # optional machine-readable form
checked = "2026-09-16"                   # last time the URL was verified reachable
```

Every `skills` entry must resolve to a real skill, every URL must be `https`, and every `license`
must be in the vocabulary. `python3 scripts/check-sources.py` enforces all three on every push;
`--online` additionally fetches each URL and is run on a schedule rather than per-push, because a
publisher being briefly down is not a reason to fail somebody's pull request.

## Adding a source

Prefer the publisher over an aggregator — `ecfr.gov` rather than a site that reprints it — because
the aggregator is where staleness and license ambiguity enter. Prefer a stable landing page over a
deep link to one revision, unless the revision is the point. Record what it is authoritative *for*
rather than what it is about; the agent is choosing between sources, and "what question does this
settle" is what makes that choice.
