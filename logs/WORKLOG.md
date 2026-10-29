# WORKLOG

## 2026-10-27T16:33Z · d06f8d1
- Replaced `assets/pdf/Ibrahim_Resume.pdf` with the Oct 25 2026 resume (146,313 B, LaTeX/PDFTeX, 1p A4). Same path keeps `/assets/pdf/Ibrahim_Resume.pdf` nav link stable.
- Pushed to `main`; GitHub Pages build `d06f8d1` = `built`.
- Verified: live PDF HTTP 200, 146,313 bytes, sha256 `9040fb4…0e5466` identical to repo file; homepage nav still emits the PDF link.
- Worked. No site-content changes needed (resume referenced only by `_data/navigation.yml`).

## 2026-10-29T17:41Z · profile bio rewrite
- `_data/profile.yml`: replaced the abstract operator-level `short_bio` with a 95-word bio naming the research as function-space analysis of sequence models, defining it (operator a network's parameters denote, how it acts on inputs, not the arrangement of weights), then use (explore/design modifications, establish preservation of behaviour) and scope (conditioning, low-precision training, MoE routing, PEFT).
- Dropped "under the data's native measure", "coordinate frame", "invariant a transformation must respect", "empirical hope"; no em or en dashes.
- Verified locally: `jekyll build` clean, rendered index.html carries the new string, 0 dash characters.
- Worked.
