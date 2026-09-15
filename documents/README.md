# documents/ — career source materials

Drop raw materials here, then run `/setup` (Path A: documents folder) to build
the profile. Re-runnable and idempotent as you add more.

```
documents/
├── cv/            # master CV (PDF or .tex)
├── diplomas/      # degree certificates, transcripts
├── references/    # reference letters, referee details
└── applications/  # per-application archive, one folder each:
                   #   <lab>_<role>/
                   #     posting.txt   (verbatim posting text)
                   #     cv.tex / cv.pdf
                   #     sop.md
                   #     email.md
                   #     outcome.md
```

## Subfolder naming
Derive `<lab>_<role>` once per application and reuse it for the CV file, the SOP,
the email, and the archive folder. Lowercase, hyphens, no spaces. If the derived
name is empty, stop before creating anything.

## Privacy
`/setup` writes the private candidate profile and personalized queries to ignored
paths. All documents (except this README), trackers, reports, state, and credentials
must remain ignored. Never share candidate/referee contact details. Ignore rules
do not untrack existing files or erase history; audit before publishing.
