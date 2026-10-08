# Content inventory and recovery dispositions

Issue: https://github.com/BenOvermyer/queens-own-website/issues/4

## Findings

The audit checks every internal page, asset, PDF, and fragment reference in the
built site. Filenames remain case-sensitive; percent-encoded paths and fragments
are decoded for local lookup. External community/bookstore sites are outside the
internal-link audit, except for verifying the repaired Vanyel newsletter destination.

- All 120 PDFs in the source manifest return HTTP 200 with `application/pdf`.
- There are now 147 distinct linked PDF filenames. The original 146 excluded the
  extensionless `qoApr-May2019` reference; correcting it to `.pdf` reveals a 27th
  missing PDF rather than recovering a file.
- All 27 missing PDFs return 404 on both `files.queensown.org` and the original
  `queensown.org` host. None is present in the supplied local archive.
- Six non-PDF targets remain unresolved: two pages, two named image references,
  an image placeholder, and a malformed email link with no recoverable address.
- All six originally unresolved anchors now resolve. Original working anchor IDs
  are retained; aliases were added for the broken incoming names.
- Every manifest PDF is linked; no source PDFs are orphaned.

Full referring-page lists, resource types, local presence, HTTP status, content type,
redirect destinations, and UTC check times are in `data/link-inventory.json` and
`data/link-http-evidence.json`. `data/migration-report.json` is the unmodified
migration snapshot; it is not a list of current failures.

Golden Grove’s formerly missing `qogg.htm` reference was resolved during the later
Dragonlords content migration: the recovered California chapter page is now at
`/golden-grove/`, and its unavailable notice has been removed.

## Corrections and recovered destinations

| Original reference | Resolution and evidence |
| --- | --- |
| `qomar.htm` in the persona list | `qomar90.htm`; visible label identifies March 1990 and that newsletter exists. |
| `qofeb.htm` in the persona list | `qofeb91.htm`; visible label identifies February 1991 and that newsletter exists. |
| `mlrel2.htm` | `qomlrel2.htm`; the existing Queen's Own release form matches the reference. |
| `qojournal.htm"` | Remove the stray quote; the Compass Rose page exists. |
| Windows `file:///F:/Docs2/club/WEBSITE/qo.htm` | Link to the existing home page (`index.html`); the local restored `qo.htm` is the original Queen's Own home page. |
| Windows `file:///F:/Docs2/club/WEBSITE/vfcnews.htm` | Link to `https://dragonlords.fans/vfcnews.htm`; the local split archive contains the Vanyel Fan Club newsletter and the live destination returned HTTP 200. |
| `mailto` with `lois@dendarii.com` as visible text | Restore `mailto:lois@dendarii.com` in six newsletters. |
| `:mailto:info@hollywoodexpo.com"` | Restore the email scheme and remove extraneous punctuation. |
| Duplicate `mailto:mailto:` | Normalize to a single email scheme. |
| `qoApr-May2019` | Append the PDF extension, based on its newsletter-list context; availability remains unresolved. |
| `qob.htm#teach` | Add an alias beside existing `#teacher`. |
| `qohe.htm#low`, `#high` | Add aliases at the corresponding low-strength and normal/high-strength specialty headings. |
| `qorel.htm#formal` | Add alias at Advanced Rank, which contains the priest/priestess training requirements. |
| `qoww.htm#formal` | Add alias at Formal Training. |
| `qom.htm#advance` | Add alias at Advanced Rank. |

These corrections are applied by the importer as well as the standalone repair
script. No new prose, contact addresses, or missing artwork were invented.

## Recovery evidence and limitations

The supplied backup contains a restored copy of the original `dragonlordsnet.com`
site and the CDX index used to recover it. The index covers 2,424 resources with a
July 1, 2026 cutoff. A case-insensitive exact-filename comparison finds none of the
33 unresolved targets in that index. The restored, browsable, and split-site trees
also contain no files matching the missing targets, except the two Windows-path
references corrected above. This establishes absence from this recovery snapshot,
not absence from every historical snapshot or private club collection.

The live original-host candidates returned 404. Outstanding resources therefore
remain `pending_recovery` with a documented request/recovery action. The placeholder
`***.jpg` and unnamed email destination remain `historical_gap` because guessing
would create inaccurate content. `qo267.htm` was used as an image URL, so it is
classified as an incorrect resource type; a replacement filename is not assumed.

Pages display “unavailable in archive” beside unresolved links. Missing images
have an unavailable alt description instead of requesting nonexistent files. The
unknown email link is plain text with a gap notice. The intended targets remain in
the inventory, including when an image `src` or invalid email `href` is removed.

## Outstanding resource inventory

Every listed resource remains unresolved. For PDFs, recovery includes adding the
file to the files host using the original case-sensitive filename; for pages and
images, recover the content with its original credits and record provenance.

| Target | Classification | Referring pages | Disposition / recovery action |
| --- | --- | --- | --- |
| `***.jpg` | placeholder_image | `qoaug89.htm`, `qojan89.htm`, `qojun89.htm`, `qojun90.htm`, `qomay89.htm`, `qonov88.htm`, `qooct89.htm` | Preserve as a historical gap; no reliable replacement can be inferred. |
| `mailto` | malformed_email | `qolist.htm` | Preserve as a historical gap; no reliable replacement can be inferred. |
| `qo231.jpg` | asset | `qodec04.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qo267.htm` | incorrect_resource_type | `qosep96.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qodec98.htm` | page | `qolist.htm`, `qonews.htm`, `qonpc.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qonov98.htm` | page | `qolist.htm`, `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `Pirate.pdf` | pdf | `qofanfic.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoApr-May2019.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoAug-Sep2019.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoFall2022.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoJan2021.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoSep2021.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoSpring2022.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoapr2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoaug2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qoaug2015.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qodec2005.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qofeb2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qofeb2011.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qohac.pdf` | pdf | `qofun.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qojan2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qojan2022.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qojul2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qojul2016.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qojul2018.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qojun2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qojun2016.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qomar2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qomay2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qonov2005.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qonov2015.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qooct2018.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |
| `qosep2008.pdf` | pdf | `qonews.htm` | Request original from club editors or locate another archive snapshot; preserve filename and credits. |

## Repeatable validation

```sh
python3 scripts/build.py
python3 scripts/verify.py
python3 scripts/audit_links.py --online
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The offline audit uses saved HTTP evidence and does not make network requests.
The online audit refreshes all linked PDFs and original-host recovery candidates.
Dispositions acknowledge specific targets and referring pages; they do not change
missing statuses to available. A new missing target, new missing anchor, or new
page linking to an acknowledged gap fails validation. A formerly available PDF
returning an error or HTML also fails the online audit.

When a resource is recovered, remove its disposition and unavailable markup,
record where it came from, rebuild, and rerun the online audit. Do not suppress a
new audit failure by marking the resource recovered without checking it.
