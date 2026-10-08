# Dragonlords content migration inventory

Inventory of the local `../queens-own/dragonlords.fans/` split archive, prepared October 8, 2026. This describes the supplied archive, rather than current live-site availability.

## Findings

- **1,789 files inventoried**, including **882 HTML pages and archived HTML service responses**.
- **43 pages selected for migration**: 19 Compass Rose journal pages, 11 Velgarth reference/persona/fan-activity pages, eight Vanyel Fan Club pages, three Queen’s Own chapter pages, and two shared club resources (cookbook and release form).
- **386 other relevant pages remain on Dragonlords**: 344 mailing-list archive/service pages and 42 mixed-purpose or incidental-reference pages.
- **453 pages have no identified reason to move** under this inventory’s criteria.
- **21 HTML pages mention Velgarth**. Every one is included as a migration or review candidate, including references in mailing-list archives and Dragonlords rules.
- **90 assets/downloads** are referenced by the source candidate pages. Before migration, 45 were present in `static/`; 39 were added, and six commerce images were omitted.
- **14 PDFs text-scanned**: 13 are byte-identical to files already in the Queen’s Own source archive and upload manifest. `Vita2022.pdf`, an author CV mentioning Velgarth and club work, is a review candidate rather than an automatic club-page migration.

The original split used the `qo` filename namespace. This missed dedicated club content named `dan*`, `vfc*`, and `cr*`. A simple keyword search would also miss some chapters and journal articles while including unrelated bookstore and Dragonlords pages.

## Evidence and scope

The page inventory records titles, matched terms/counts, recommendation, rationale, current Queen’s Own referring pages, page links, asset dependencies, and missing local dependencies. The spreadsheet covers every source file with its size and SHA-256 hash. PDF keyword matches and extraction results are in the JSON.

The original archive remains unchanged. The selected pages have now been imported into this repository; deployed sites change only when the new build is published. The `migrate` recommendation means the page’s subject clearly belongs with Queen’s Own. `review` means there is evidence of relevance but ownership, duplication, historical functionality, or mixed subject matter needs a decision. `retain` means no relevant evidence was identified; it is not proof that no part could ever be useful.

Only declared HTML content and PDF text are searched for topic keywords. Images and ZIP archives are inventoried through filenames, hashes, and references; their visual or packaged contents are not semantically classified. No handwritten excerpt of mailing-list messages or contact details is reproduced in this report.

## Direct Fun Stuff candidates

| Current source path | Subject | Migration rationale |
| --- | --- | --- |
| `danyagg.htm` | Golden Grove | Explicitly the California chapter of Queen’s Own. |
| `danyacc.htm` | Pacific Northwest Collegium / Collegium Chronicles | Chapter newsletter, artwork, and submission guidance. |
| `vfcindex.htm` | Vanyel Fan Club | Club homepage; move the connected eight-page group together. |
| `danc.htm` | Companions’ Choices | Herald persona guidance explaining Companion choices. |
| `dantime.htm` | Valdemar Timeline | Timeline of the Velgarth novels. |
| `danp.htm` | Proverbs from Velgarth | Attributed fan compilation. |
| `danmag1.htm` | The Magic of Velgarth | Detailed magic reference tied to Herald-Mage persona work. |

`bkstore.htm` is a general Dragonlords bookstore and should remain an external link. The Fun Stuff “Return to the Queen’s Own Home Page” link currently points at `dragonlords.fans/index.htm`; that is a link correction to make during migration, not a reason to move the Dragonlords home page.

## Complete recommended page set

### Queen’s Own chapters

| Source path | Title |
| --- | --- |
| `danyacc.htm` | Collegium Chronicles |
| `danyagg.htm` | Golden Grove |
| `danyasc.htm` | Sonoran Collegium |

### Vanyel Fan Club

| Source path | Title |
| --- | --- |
| `vfcchat.htm` | Vanyel Fan Club--Chat List |
| `vfcgate.htm` | Gate to Heralds' Haven |
| `vfcgates.htm` | Heralds' Haven |
| `vfcindex.htm` | Welcome to the Vanyel Fan Club! |
| `vfcjoin.htm` | Join the Vanyel Fan Club! |
| `vfcnews.htm` | The Valdemaran Herald |
| `vfcpres.htm` | About the Vanyel Fan Club President |
| `vfcqa.htm` | Vanyel Fan Club Q&A |

### Velgarth reference and fan activities

| Source path | Title |
| --- | --- |
| `danc.htm` | Companions' Choices |
| `danhc.htm` | Heralds and Companions |
| `danmag1.htm` | The Magic of Velgarth |
| `danp.htm` | Proverbs From Velgarth |
| `danr.htm` | Reincarnated Characters |
| `danspell.htm` | Magic Spells |
| `dantime.htm` | Valdemar Timeline |
| `danya.htm` | Danya Winterborn |
| `dcpawn.htm` | Magic's Pawn |
| `dcprice.htm` | Magic's Price |
| `dcprom.htm` | Magic's Promise |

### The Compass Rose journal

| Source path | Title |
| --- | --- |
| `cr2ddl.htm` | The Compass Rose:  The Death of Diversity in our Nation's Libraries |
| `cr2ddl1.htm` | The Compass Rose:  The Death of Diversity in our Nation's Libraries |
| `cr2le.htm` | The Compass Rose:  Letter from the Editor |
| `cr2rev.htm` | The Compass Rose:  Reviews |
| `cr2sim.htm` | The Compass Rose:  Sources of Information on Music in Medieval Ireland |
| `cr2sim1.htm` | The Compass Rose:  Sources of Information on Music in Medieval Ireland--Notes and References |
| `cr2tat.htm` | The Compass Rose:  The Arthurian Tales |
| `cr2tat1.htm` | The Compass Rose:  The Arthurian Tales |
| `cr2toc.htm` | The Compass Rose:  Volume 2/Issue 1 |
| `crbi.htm` | The Compass Rose:  Either Or |
| `crbi1.htm` | The Compass Rose:  Either Or--References |
| `crc.htm` | The Compass Rose:  In the Name of God |
| `crc1.htm` | The Compass Rose:  In the Name of God--Notes and References |
| `crfrm.htm` | The Compass Rose:  From Reptile to Mammal |
| `crfrm1.htm` | The Compass Rose:  From Reptile to Mammal--References |
| `crle.htm` | The Compass Rose:  Letter from the Editor |
| `crrev.htm` | The Compass Rose:  Reviews |
| `crsos.htm` | The Compass Rose:  Excerpts from Sink or Swim |
| `crtoc.htm` | The Compass Rose:  Vol. 1, No. 1 |

The Sonoran Collegium (`danyasc.htm`) is another clear chapter candidate beyond the Fun Stuff examples. The full Compass Rose articles and reference pages belong with the journal even when they discuss science, libraries, music, or Arthurian literature rather than Velgarth.

Vanyel chat/join/gate pages are historical information. They reference legacy mailing-list services and an explicitly inactive gate; moving the static pages does not restore those services. `danya.htm` is a club persona hub with art and related activities, distinct from the general author biography at `author.htm`.

## Pages requiring a decision

### Mailing-list archives and services

**334 Pipermail pages and 10 Mailman responses** are related to Queen’s Own, QOPending, or the Vanyel Fan Club. These include messages, monthly/thread/author indexes, list information, subscription/options pages, and captured administration responses. Treat these as an archive group; decide which static content to preserve and how to replace historical service links. Do not copy archived service responses as working forms.

The complete path list is in the JSON and CSV. All 14 mailing-list pages explicitly mentioning Velgarth are included in this group, and the other related pages are included so the archive is not split by individual keyword hits.

### Mixed-purpose and incidental-reference pages (pre-migration review)

| Source path | Title | Terms found |
| --- | --- | --- |
| `author.htm` | About the Author | Queen's Own |
| `basic.htm` | Basic Rules | Velgarth, Valdemar |
| `bkfanml.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Valdemar, Queen's Own |
| `bkmlbc.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlbs.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlbt.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlbv.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmldt.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlem.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlft.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlha.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlhc.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlj.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlobs.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlot.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlse.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlsk.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `bkmlvs.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Valdemar, Queen's Own, Herald-Mage |
| `bkmlwc.htm` | Dragonlords' Bookstore--Fantasy--Mercedes Lackey | Queen's Own |
| `dstips.htm` | Tips | Valdemar |
| `funstuff.htm` | Fun Stuff | Queen's Own |
| `index.htm` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_00.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=12.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=14.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=22.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=23.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=32.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=4.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=40.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=44.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=5.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=6.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `index__q_id=7.html` | Dragonlords of Dumnonia's Home Page | Queen's Own |
| `mapr00.htm` | April 2000 | Queen's Own |
| `mlrelease.htm` | Release Form for Mercedes Lackey | Valdemar |
| `napr98.htm` | April Newsletter | Valdemar |
| `naug00.htm` | August 2000 Newsletter | Queen's Own |
| `njul00.htm` | July 2000 Newsletter | Queen's Own |
| `njun00.htm` | June 2000 Newsletter | Queen's Own |
| `nmay00.htm` | May 2000 Newsletter | Queen's Own |
| `pcpak.htm` | Persona Pak | Vanyel |
| `recipes.htm` | Herald Danya's Cookbook | Queen's Own |

Likely dispositions after review:

- Keep the Dragonlords home pages, general author biography, generic writing tips, bookstore catalog, and Dragonlords persona/rules pages on that site; extract or link useful Queen’s Own portions if needed. `basic.htm` discusses Velgarth as a comparison but defines Centuria/Dragonlords rules.
- Migrate `mlrelease.htm` as a shared Mercedes Lackey resource and preserve its historical date/status; it is linked by the chapter and Vanyel publication pages.
- Migrate `recipes.htm` and its linked `recipes.zip` as Danya-associated fan activity. The ZIP is preserved as an original download; its contents have not been rewritten.
- Review the old Dragonlords newsletters and `mapr00.htm` for relevant sections rather than moving complete issues based on a single club reference.
- Keep duplicate query-string captures of the Dragonlords homepage out of the new site’s page tree.
- Review the author CV `Vita2022.pdf` separately; its Velgarth mentions are bibliography/biographical material.

## Assets and downloads

The 90 dependencies comprise 72 GIFs, 16 JPEGs, one PNG, and one ZIP. The original inventory found 45 assets already in `static/` and the following 45 absent. Migration added 39 of those, including `recipes.zip`; six commerce images were omitted.

| Asset/download absent before migration | Referenced by candidate pages |
| --- | --- |
| `Aerolyn.jpg` | `crle.htm` |
| `GGlogo.png` | `danyagg.htm` |
| `amzn1.gif` | `crtoc.htm` |
| `barflow.gif` | `danya.htm` |
| `barlinks.gif` | `danya.htm` |
| `bk1.gif` | `crrev.htm` |
| `bk2.jpg` | `crrev.htm` |
| `butback.gif` | `danyacc.htm`, `danyagg.htm`, `danyasc.htm` |
| `cc1.gif` | `danyacc.htm` |
| `cc10.gif` | `danyacc.htm` |
| `cc10a.gif` | `danya.htm`, `danyacc.htm` |
| `cc11.gif` | `danyacc.htm` |
| `cc13.gif` | `danyacc.htm` |
| `cc14.gif` | `danyacc.htm` |
| `cc15.gif` | `danyacc.htm` |
| `cc16.gif` | `danyacc.htm` |
| `cc17.gif` | `danyacc.htm` |
| `cc20.gif` | `danyacc.htm` |
| `cc21.gif` | `danyacc.htm` |
| `cc22.gif` | `danyacc.htm` |
| `cc22a.gif` | `danyacc.htm` |
| `cc23.gif` | `danyacc.htm` |
| `cc24.gif` | `danyacc.htm` |
| `cc25.gif` | `danyacc.htm` |
| `cc26.gif` | `danyacc.htm` |
| `cc28.gif` | `danyacc.htm` |
| `cc29.gif` | `danyacc.htm` |
| `cc2a.gif` | `danya.htm`, `danyacc.htm` |
| `cc3.gif` | `danyacc.htm` |
| `cc4.gif` | `danyacc.htm` |
| `cc6.gif` | `danyacc.htm` |
| `cc8a.gif` | `danya.htm`, `danyacc.htm` |
| `compassrose.jpg` | `cr2le.htm` |
| `crlogo.jpg` | `cr2ddl.htm`, `cr2ddl1.htm`, `cr2le.htm`, `cr2rev.htm`, `cr2sim.htm`, `cr2sim1.htm`, `cr2tat.htm`, `cr2tat1.htm`, `crbi.htm`, `crbi1.htm`, `crc.htm`, `crc1.htm`, `crfrm.htm`, `crfrm1.htm`, `crle.htm`, `crrev.htm`, `crsos.htm` |
| `ml58.jpg` | `cr2rev.htm` |
| `rainbar.gif` | `danspell.htm`, `danya.htm`, `vfcchat.htm`, `vfcgate.htm`, `vfcgates.htm`, `vfcindex.htm`, `vfcjoin.htm`, `vfcnews.htm`, `vfcpres.htm`, `vfcqa.htm` |
| `recipes.zip` | `danya.htm` |
| `tile11.gif` | `danyacc.htm` |
| `vfcfronta.jpg` | `vfcindex.htm` |
| `vfcgate.jpg` | `vfcgate.htm` |
| `vfchgn.jpg` | `vfcgates.htm` |
| `vfcmail.jpg` | `vfcchat.htm` |
| `vfcp.jpg` | `vfcpres.htm` |
| `vfcqa.jpg` | `vfcqa.htm` |
| `vid1.jpg` | `crrev.htm` |

The 13 duplicate PDFs have matching source names and SHA-256 hashes in the existing PDF manifest; keep using `files.queensown.org` for them. No extra PDF upload is indicated by those duplicates. `Vita2022.pdf` is the only PDF in this archive absent from the existing manifest.

## Missing or malformed candidate dependencies

| Referring candidate | Target | Migration follow-up |
| --- | --- | --- |
| `cr2sim1.htm` | `sim1.htm` with bibliography fragments | References appear intended for the article’s bibliography; check the existing reference anchors and correct the target during import. |
| `danspell.htm` | `danyahm.htm` | Missing Herald-Mage sheet; compare existing Queen’s Own handouts and determine whether this referred to a personal worksheet. |
| `vfcindex.htm` | Malformed VFC Chat List link spanning HTML tags | Repair the anchor markup and point at the existing `vfcchat.htm` page. |
| `vfcjoin.htm` | `vfcjoin.jpg` | Missing image/button; locate the original or provide an accurately labeled text link. |
| `vfcqa.htm` | `president.html` | The link identifies Herald Bastian; `vfcpres.htm` is the existing president page and is a strong replacement candidate. |

These are additional migration findings, separate from the issue #4 inventory of the already-imported site. Golden Grove’s California chapter page supplies the content expected by the missing `qogg.htm` link; that reference now points to `/golden-grove/`, and its unavailable notice and unresolved disposition were removed.

## Proposed migration sequence

1. Move the three chapter pages, eight Vanyel pages, and eleven reference/fan-activity pages with their required assets and original credits.
2. Move both Compass Rose issue contents and their article/reference pages as complete publication groups.
3. Resolve the five dependency problems above and replace relevant Queen’s Own cross-domain links with links to the migrated pages.
4. Use descriptive, extensionless paths under issue #2 (for example, `/golden-grove/`, `/vanyel-fan-club/`, and `/companions-choices/`) and document old-path mappings. Arrange redirects for the old `dragonlords.fans` URLs when that site can be updated.
5. Decide the mailing-list archive, shared release form, cookbook, author CV, and mixed-page excerpts separately; retain the surrounding Dragonlords material.
6. Run the site’s local link/anchor audit, confirm PDF destinations, and check new pages for publication dates, artwork attribution, and original notices.

## Regenerate the inventory

```sh
python3 scripts/inventory_dragonlords.py ../queens-own/dragonlords.fans
```

Requires the migration Python dependencies and Poppler’s `pdftotext` for PDF keyword extraction. This regenerates the machine-readable data files. Update this review report if the source or recommendations change.

- `data/dragonlords-file-inventory.csv`: complete file inventory for spreadsheet review.
- `data/dragonlords-content-inventory.json`: all page classifications, evidence, incoming links, dependencies, and PDF findings.
- `scripts/inventory_dragonlords.py`: repeatable scan and explicit candidate-group definitions.

## Completed migration

The clarified boundary keeps substantive Dragonlords content and the bookstore on
that site. Shared hosting footers and bookstore promotions do not disqualify
otherwise dedicated club pages; those references were removed from imported copies.

Imported 43 pages under descriptive, extensionless paths, listed in
`data/dragonlords-route-map.json`. Added 39 previously absent assets/downloads,
reused existing assets, updated over 600 cross-domain references in this site's
content, and added the new pages to the archive index. All bookstore/catalog pages,
general author material (including the CV), Dragonlords-world content, and old
mailing-list/service snapshots remain in the source archive. The static migration
does not restore old mailing-list services; their club information is preserved as
historical material with publication/contact notices.

The original author/artwork credits and copyright notices were retained. Shared
hosting return links, bookstore promotions, commerce links and their book-cover
images were omitted from imported copies. The Vanyel dues answer retains the club's
free-membership information without the store promotion; Compass Rose design
credit remains after removal of its affiliate-sales wording.

Repaired the malformed Vanyel chat/FAQ navigation, replaced the missing join image
with its descriptive text, mapped the old president link to the actual president
page, linked the Herald-Mage sheet to the existing handout, and corrected music
bibliography paths. Added aliases for misspelled citation anchors and the cookbook's
persona link; fixed a Renaissance Faires link that used the wrong fragment. Original
bibliographic prose, including its historical date inconsistencies, was retained.

`static/_redirects` provides permanent old-filename redirects on this Netlify site.
The old `dragonlords.fans` host has not been changed; when updating its deployment,
use the route map to redirect moved pages to the intended Queen's Own deployment
URL while leaving the bookstore and other retained material in place.

To repeat the import:

```sh
python3 scripts/migrate_dragonlords.py ../queens-own/dragonlords.fans
python3 scripts/build.py
python3 scripts/verify.py
```

Reimport overwrites the imported pages from the archive. Edit the migration script
for repeatable changes. The original Queen's Own importer also uses the route map
and restores the imported archive listing, so it does not reinstate old cross-domain
links when reimporting the original site's content.
