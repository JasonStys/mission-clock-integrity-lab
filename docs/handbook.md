# Mission Clock Integrity Lab handbook

By Jason Stys.

Compare synthetic clock histories and qualified timestamp order, inspect uncertainty frontiers and export evidence from 1.1 portable apps.

Packages the native model, independent auditor and review interface together while keeping application/native product versions coherent and checking actual extracted execution.

## Read the documentation

| Edition                                                      | Audience and contents                                                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [project-guide.docx](reports/project-guide.docx)             | User and developer guide: purpose, current usage, design, boundaries and source references.                        |
| [validation-review.docx](reports/validation-review.docx)     | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits.             |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [ORDER REVIEW](ORDER_REVIEW.md)
- [RELEASE](RELEASE.md)
- [USER GUIDE](USER_GUIDE.md)

### Design and contracts

- [API](API.md)
- [ARCHITECTURE](ARCHITECTURE.md)
- [MODEL](MODEL.md)

### Security and validation

- [VALIDATION](VALIDATION.md)

## Historical results and reproduction

The reviewed source is [`1af9738149716f944cc74a3c577746bea35194db`](https://github.com/JasonStys/mission-clock-integrity-lab/tree/1af9738149716f944cc74a3c577746bea35194db). The observed functional workflow baseline is `1af9738149716f944cc74a3c577746bea35194db`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/PORTABLE_RELEASE_20261109.md)
- [Current Actions](https://github.com/JasonStys/mission-clock-integrity-lab/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Synthetic integer intervals and logical time do not establish real UTC accuracy, timing certification or host-clock control.
- Readiness frontiers are not total-order ranks; timestamp separation is not causality, and unqualified intervals remain unknown.
- Unsigned desktop portable files for specific OS/CPU targets; no system installer, public hosting or physical timing integration.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
