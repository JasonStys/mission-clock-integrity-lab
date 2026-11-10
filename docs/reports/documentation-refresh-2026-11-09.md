# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `1af9738149716f944cc74a3c577746bea35194db`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 | Bytes | SHA-256                                                            | Reviewed scope                                                                                                                      |
| ---------------------------------------------------- | ----: | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 83165 | `2c60fe37e41f5e599bbdba808c336a78c5515787b680b4430eb4d905f048ee67` | 4 pages, each viewed individually                                                                                                   |
| [validation-review.docx](validation-review.docx)     | 43709 | `cb813cb825f475a032b8d63b42bd23213fdef724e931ac37b0c8fee187fa45de` | 4 pages, each viewed individually                                                                                                   |
| [validation-evidence.xlsx](validation-evidence.xlsx) |  7377 | `83e68fa588e7624e5329cd799e2e69025578da2b1aa5dcf9dd318bf8e2bc9b16` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `1af9738149716f944cc74a3c577746bea35194db`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Local integration validation

The complete Python suite passed 435 tests at 98.01% combined statement/branch
package coverage, retaining the original 90% floor. Eight real Office ZIP regressions
are included: only the named edition paths are decoded with bounded bytes/members
and strict UTF-8 XML/relationships; text remains visible to the original privacy
scan. Malformed/unknown/oversized archives fail. Package and CLI imports are explicit.

Ruff, exact generated source/file maps, 9 TypeScript unit tests and strict
TypeScript/Vite production build passed. Existing warning policy and hosted
cross-platform/browser/security gates remain. Exact approved Office/hash/ZIP/source
and local-link validation are separate from the dated functional observations;
this integration does not assert future PR/main, new installation or release results.
