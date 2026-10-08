# Site organization and canonical URLs

Implements https://github.com/BenOvermyer/queens-own-website/issues/2.

## Sitemap and browsing structure

| Landing page | Purpose and principal resources |
| --- | --- |
| `/` | A directory into membership, personas, reference material, community, publications, and archives. |
| `/membership/` | Joining instructions, club FAQ, mentors, seal, and legal/privacy information. |
| `/personas/` | Persona handouts, submission instructions, and historical persona/NPC directories. |
| `/world/` | Velgarth FAQs, magic, peoples, travel, proverbs, and other reference articles. |
| `/community/` | Published social links, chapters, historical services, and fan activities. |
| `/vanyel-fan-club/` | The preserved Vanyel club pages and newsletter guidance. |
| `/dream-casts/` | The historical Last Herald-Mage dream-cast activity. |
| `/publications/` | Entry point to newsletters, The Compass Rose, and fan fiction. |
| `/newsletters/` | Years from 1988 through 2024 for which the source links an issue. Years without linked material are not invented. |
| `/newsletters/YEAR/` | Calendar-ordered HTML and PDF issues, with missing material explicitly identified. |
| `/compass-rose/` | Nonfiction journal overview and preserved issues. |
| `/compass-rose/summer-2000/` | Volume 1, Number 1; original issue contents, articles, references, and notices. |
| `/compass-rose/spring-2002/` | Volume 2, Number 1; original issue contents, articles, references, and notices. |
| `/fan-fiction/` | Story downloads, Children of Velgarth, original directory/credits, and historical release guidance. |
| `/archive/` | A topic-organized index of every preserved source page and the two unavailable newsletter notices. |

Pages live in native Zola sections. Their public paths can be customized independently
of the physical section: for example, `content/world/bards-faq.md` is published at
`/bards-faq/`. Breadcrumbs connect it back to World reference. The navbar links the
main topic hubs, and the home page provides direct publication-archive entry points.
Zola's section model and sorting are documented in the [official section documentation](https://www.getzola.org/documentation/content/section/).

## Navigation and source context

The home page and navigation hubs provide directories into the preserved articles,
club resources, and publications. Publication dates and original content remain
intact. Historical-material banners and “(historical)” qualifiers were removed at
the site owner's request; source-context metadata remains internal to the tooling.
Original prose, artwork credits, copyright text, and fragment anchors are retained.
Source contents inside disclosure elements are open by default so direct fragment
destinations remain visible.

The editorial homepage contains the current club introduction and contacts. Legal
and privacy notices live at `/legal-notices/` and `/privacy-policy/`, linked in the
footer. The superseded source homepage is no longer published or imported. Legacy
home URLs redirect to `/`. Draft adoption checks are in `docs/legal-notices-review.md`
and `docs/privacy-policy-review.md`.

## Publication organization

- **155 preserved HTML newsletters** are titled by month and year and placed in
  year sections. Month-only dates are represented as the first day for Zola sorting,
  with `date_precision = "month"`; the interface displays no invented day.
- **132 linked PDF newsletter editions** are grouped by year and their original
  period labels, including multi-month and seasonal issues. File names and case on
  `files.queensown.org` remain unchanged.
- **Two unavailable HTML newsletters**, November and December 1998, have canonical
  notice pages. They contain no fabricated newsletter text and remain
  `unavailable_content` in the audit.
- **14 fan-fiction PDF references** are listed by title. Availability uses the saved
  HTTP evidence; unavailable downloads are labeled and are not offered as working links.
- **Two Compass Rose issues** are native sections containing the original contents
  and article/reference pages. Their issue labels are the original seasons and years.

There are 35 newsletter year indexes. Years are newest-first;
issues within a year are in calendar order. The JSON publication index includes the
known missing editions, not just files that happen to be available. The old newsletter
publication/submission page is retained at `/newsletter-guidance/`, separate from
the primary chronological archive.

`data/publication-index.json` is generated from source metadata, original PDF labels,
and saved HTTP availability evidence. After an online audit refresh, rerun the
organizer and build to publish revised availability labels.

## Redirects and link compatibility

All 248 preserved source pages have explicit canonical paths and old-to-new
mappings. The two unavailable notices are also mapped. Canonical navigation,
internal page links, and sitemap entries do not use `.htm` or `.html` extensions.
Those names remain as provenance/recovery identifiers and redirect sources.

`static/_redirects` contains forced permanent (`301!`) rules for old file paths and
trailing-slash variants. For example:

```text
/qofaqb.htm /bards-faq/ 301!
/qob.htm /bard-handout/ 301!
/qojan05.htm /newsletters/2005/january/ 301!
```

Forced rules ensure the legacy homepage filename redirects even though its generated
HTML file exists. Netlify passes query parameters through ordinary 301 redirects;
see [Netlify's redirect options](https://docs.netlify.com/manage/routing/redirects/redirect-options/).
Fragments remain in their links, and the destination pages retain their named
anchors. Verification checks canonical destinations, every registered redirect,
absence of redirect chains, local anchors, and absence of legacy internal/sitemap URLs.

The build now uses standard Zola directory indexes. The former `.htm` directory
flattening is removed. `zola serve` previews canonical content; Netlify implements
the redirects. No domain was switched to production: Netlify still supplies the
deployment URL through `DEPLOY_PRIME_URL`. Redirects on the separate Dragonlords
host require a separate deployment there; its bookstore and other retained content
remain external links.

## Reimports and maintenance

Both importers look up canonical content-file locations before writing source
pages, then rerun `scripts/organize_site.py`. This keeps the organized structure and
prevents source reimports from replacing the curated home page. Existing hub body
edits are preserved. The organizer is idempotent and does not rewrite source archives.

Source reimports overwrite the preserved source copies, as before; maintain
repeatable source corrections in the import/organization scripts. Edit the hub
Markdown directly for editorial navigation changes. Ordinary new editorial pages
can be created in the relevant section without inventing a legacy source identifier.

```sh
python3 scripts/organize_site.py
python3 scripts/build.py
python3 scripts/verify.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The verifier uses saved HTTP evidence during offline checks. Online evidence can be
refreshed with `python3 scripts/audit_links.py --online`; rebuild after regenerating
the publication index. A notice page does not count as recovered content, and new
unaccounted gaps or new referring pages still fail the audit.

## Complete source-to-content mapping

The same mapping is available in `data/site-map.csv` for spreadsheet review and in
`data/site-routes.json` for tooling. The JSON includes permanent-redirect aliases,
canonical destinations, page/section type, source-presence status, and publication periods.

| Legacy source | Topic | Canonical path | Content file | Status |
| --- | --- | --- | --- | --- |
| `qochap.htm` | community | `/chapters/` | `community/chapters.md` | Preserved |
| `qochat.htm` | community | `/club-chat/` | `community/club-chat.md` | Preserved |
| `qoring.htm` | community | `/club-webring/` | `community/club-webring.md` | Preserved |
| `danya.htm` | community | `/danya-winterborn/` | `community/danya-winterborn.md` | Preserved |
| `recipes.htm` | community | `/danyas-cookbook/` | `community/danyas-cookbook.md` | Preserved |
| `qodelphi.htm` | community | `/delphi-forum/` | `community/delphi-forum.md` | Preserved |
| `dcpawn.htm` | community | `/dream-casts/magics-pawn/` | `dream-casts/magics-pawn.md` | Preserved |
| `dcprice.htm` | community | `/dream-casts/magics-price/` | `dream-casts/magics-price.md` | Preserved |
| `dcprom.htm` | community | `/dream-casts/magics-promise/` | `dream-casts/magics-promise.md` | Preserved |
| `qofun.htm` | community | `/fun-stuff/` | `community/fun-stuff.md` | Preserved |
| `danyagg.htm` | community | `/golden-grove/` | `community/golden-grove.md` | Preserved |
| `qolinks.htm` | community | `/mercedes-lackey-links/` | `community/mercedes-lackey-links.md` | Preserved |
| `danyacc.htm` | community | `/pacific-northwest-collegium/` | `community/pacific-northwest-collegium.md` | Preserved |
| `qorpg.htm` | community | `/role-playing/` | `community/role-playing.md` | Preserved |
| `danspell.htm` | community | `/science-and-magic-tricks/` | `community/science-and-magic-tricks.md` | Preserved |
| `danyasc.htm` | community | `/sonoran-collegium/` | `community/sonoran-collegium.md` | Preserved |
| `vfcindex.htm` | community | `/vanyel-fan-club/` | `vanyel-fan-club/_index.md` | Preserved |
| `vfcchat.htm` | community | `/vanyel-fan-club/chat/` | `vanyel-fan-club/chat.md` | Preserved |
| `vfcqa.htm` | community | `/vanyel-fan-club/faq/` | `vanyel-fan-club/faq.md` | Preserved |
| `vfcgate.htm` | community | `/vanyel-fan-club/heralds-haven-gate/` | `vanyel-fan-club/heralds-haven-gate.md` | Preserved |
| `vfcgates.htm` | community | `/vanyel-fan-club/heralds-haven/` | `vanyel-fan-club/heralds-haven.md` | Preserved |
| `vfcjoin.htm` | community | `/vanyel-fan-club/join/` | `vanyel-fan-club/join.md` | Preserved |
| `vfcnews.htm` | community | `/vanyel-fan-club/newsletter/` | `vanyel-fan-club/newsletter.md` | Preserved |
| `vfcpres.htm` | community | `/vanyel-fan-club/president/` | `vanyel-fan-club/president.md` | Preserved |
| `qoring1.htm` | community | `/webring-code/` | `community/webring-code.md` | Preserved |
| `qofaqqo.htm` | membership | `/club-faq/` | `membership/club-faq.md` | Preserved |
| `qoseal.htm` | membership | `/club-seal/` | `membership/club-seal.md` | Preserved |
| `qojoin.htm` | membership | `/how-to-join/` | `membership/how-to-join.md` | Preserved |
| `qomentor.htm` | membership | `/mentors/` | `membership/mentors.md` | Preserved |
| `qob.htm` | personas | `/bard-handout/` | `personas/bard-handout.md` | Preserved |
| `qobl.htm` | personas | `/blues-handout/` | `personas/blues-handout.md` | Preserved |
| `qog.htm` | personas | `/guild-handout/` | `personas/guild-handout.md` | Preserved |
| `qohe.htm` | personas | `/healer-handout/` | `personas/healer-handout.md` | Preserved |
| `qohh.htm` | personas | `/herald-handout/` | `personas/herald-handout.md` | Preserved |
| `qohm.htm` | personas | `/herald-mage-handout/` | `personas/herald-mage-handout.md` | Preserved |
| `qok.htm` | personas | `/kalen-edral-handout/` | `personas/kalen-edral-handout.md` | Preserved |
| `qom.htm` | personas | `/military-handout/` | `personas/military-handout.md` | Preserved |
| `qoba.htm` | personas | `/northern-barbarian-handout/` | `personas/northern-barbarian-handout.md` | Preserved |
| `qonpc.htm` | personas | `/npc-directory/` | `personas/npc-directory.md` | Preserved |
| `qolist.htm` | personas | `/persona-directory/` | `personas/persona-directory.md` | Preserved |
| `qohandouts.htm` | personas | `/persona-handouts/` | `personas/persona-handouts.md` | Preserved |
| `qorel.htm` | personas | `/priest-and-priestess-handout/` | `personas/priest-and-priestess-handout.md` | Preserved |
| `qos.htm` | personas | `/shina-in-handout/` | `personas/shina-in-handout.md` | Preserved |
| `qoww.htm` | personas | `/sorcerer-handout/` | `personas/sorcerer-handout.md` | Preserved |
| `qot.htm` | personas | `/tayledras-handout/` | `personas/tayledras-handout.md` | Preserved |
| `qozine.htm` | publications | `/children-of-velgarth/` | `fan-fiction/children-of-velgarth.md` | Preserved |
| `qojournal.htm` | publications | `/compass-rose/about/` | `compass-rose/about.md` | Preserved |
| `cr2toc.htm` | publications | `/compass-rose/spring-2002/` | `compass-rose/spring-2002/_index.md` | Preserved |
| `cr2tat.htm` | publications | `/compass-rose/spring-2002/arthurian-tales/` | `compass-rose/spring-2002/arthurian-tales.md` | Preserved |
| `cr2tat1.htm` | publications | `/compass-rose/spring-2002/arthurian-tales/references/` | `compass-rose/spring-2002/arthurian-tales--references.md` | Preserved |
| `cr2ddl.htm` | publications | `/compass-rose/spring-2002/diversity-in-libraries/` | `compass-rose/spring-2002/diversity-in-libraries.md` | Preserved |
| `cr2ddl1.htm` | publications | `/compass-rose/spring-2002/diversity-in-libraries/references/` | `compass-rose/spring-2002/diversity-in-libraries--references.md` | Preserved |
| `cr2le.htm` | publications | `/compass-rose/spring-2002/editorial/` | `compass-rose/spring-2002/editorial.md` | Preserved |
| `cr2sim.htm` | publications | `/compass-rose/spring-2002/music-in-medieval-ireland/` | `compass-rose/spring-2002/music-in-medieval-ireland.md` | Preserved |
| `cr2sim1.htm` | publications | `/compass-rose/spring-2002/music-in-medieval-ireland/references/` | `compass-rose/spring-2002/music-in-medieval-ireland--references.md` | Preserved |
| `cr2rev.htm` | publications | `/compass-rose/spring-2002/reviews/` | `compass-rose/spring-2002/reviews.md` | Preserved |
| `crtoc.htm` | publications | `/compass-rose/summer-2000/` | `compass-rose/summer-2000/_index.md` | Preserved |
| `crle.htm` | publications | `/compass-rose/summer-2000/editorial/` | `compass-rose/summer-2000/editorial.md` | Preserved |
| `crbi.htm` | publications | `/compass-rose/summer-2000/either-or/` | `compass-rose/summer-2000/either-or.md` | Preserved |
| `crbi1.htm` | publications | `/compass-rose/summer-2000/either-or/references/` | `compass-rose/summer-2000/either-or--references.md` | Preserved |
| `crfrm.htm` | publications | `/compass-rose/summer-2000/from-reptile-to-mammal/` | `compass-rose/summer-2000/from-reptile-to-mammal.md` | Preserved |
| `crfrm1.htm` | publications | `/compass-rose/summer-2000/from-reptile-to-mammal/references/` | `compass-rose/summer-2000/from-reptile-to-mammal--references.md` | Preserved |
| `crc.htm` | publications | `/compass-rose/summer-2000/in-the-name-of-god/` | `compass-rose/summer-2000/in-the-name-of-god.md` | Preserved |
| `crc1.htm` | publications | `/compass-rose/summer-2000/in-the-name-of-god/references/` | `compass-rose/summer-2000/in-the-name-of-god--references.md` | Preserved |
| `crrev.htm` | publications | `/compass-rose/summer-2000/reviews/` | `compass-rose/summer-2000/reviews.md` | Preserved |
| `crsos.htm` | publications | `/compass-rose/summer-2000/sink-or-swim/` | `compass-rose/summer-2000/sink-or-swim.md` | Preserved |
| `qofanfic.htm` | publications | `/fan-fiction/` | `fan-fiction/_index.md` | Preserved |
| `mlrelease.htm` | publications | `/mercedes-lackey-release-form/` | `fan-fiction/mercedes-lackey-release-form.md` | Preserved |
| `qonews.htm` | publications | `/newsletter-guidance/` | `newsletters/newsletter-guidance.md` | Preserved |
| `qoapr88.htm` | publications | `/newsletters/1988/april/` | `newsletters/1988/april.md` | Preserved |
| `qojul88.htm` | publications | `/newsletters/1988/july/` | `newsletters/1988/july.md` | Preserved |
| `qojun88.htm` | publications | `/newsletters/1988/june/` | `newsletters/1988/june.md` | Preserved |
| `qomay88.htm` | publications | `/newsletters/1988/may/` | `newsletters/1988/may.md` | Preserved |
| `qonov88.htm` | publications | `/newsletters/1988/november/` | `newsletters/1988/november.md` | Preserved |
| `qooct88.htm` | publications | `/newsletters/1988/october/` | `newsletters/1988/october.md` | Preserved |
| `qosep88.htm` | publications | `/newsletters/1988/september/` | `newsletters/1988/september.md` | Preserved |
| `qoapr89.htm` | publications | `/newsletters/1989/april/` | `newsletters/1989/april.md` | Preserved |
| `qoaug89.htm` | publications | `/newsletters/1989/august/` | `newsletters/1989/august.md` | Preserved |
| `qofeb89.htm` | publications | `/newsletters/1989/february/` | `newsletters/1989/february.md` | Preserved |
| `qojan89.htm` | publications | `/newsletters/1989/january/` | `newsletters/1989/january.md` | Preserved |
| `qojun89.htm` | publications | `/newsletters/1989/june/` | `newsletters/1989/june.md` | Preserved |
| `qomar89.htm` | publications | `/newsletters/1989/march/` | `newsletters/1989/march.md` | Preserved |
| `qomay89.htm` | publications | `/newsletters/1989/may/` | `newsletters/1989/may.md` | Preserved |
| `qonov89.htm` | publications | `/newsletters/1989/november/` | `newsletters/1989/november.md` | Preserved |
| `qooct89.htm` | publications | `/newsletters/1989/october/` | `newsletters/1989/october.md` | Preserved |
| `qoapr90.htm` | publications | `/newsletters/1990/april/` | `newsletters/1990/april.md` | Preserved |
| `qodec90.htm` | publications | `/newsletters/1990/december/` | `newsletters/1990/december.md` | Preserved |
| `qofeb90.htm` | publications | `/newsletters/1990/february/` | `newsletters/1990/february.md` | Preserved |
| `qojan90.htm` | publications | `/newsletters/1990/january/` | `newsletters/1990/january.md` | Preserved |
| `qojul90.htm` | publications | `/newsletters/1990/july/` | `newsletters/1990/july.md` | Preserved |
| `qojun90.htm` | publications | `/newsletters/1990/june/` | `newsletters/1990/june.md` | Preserved |
| `qomar90.htm` | publications | `/newsletters/1990/march/` | `newsletters/1990/march.md` | Preserved |
| `qooct90.htm` | publications | `/newsletters/1990/october/` | `newsletters/1990/october.md` | Preserved |
| `qosep90.htm` | publications | `/newsletters/1990/september/` | `newsletters/1990/september.md` | Preserved |
| `qoapr91.htm` | publications | `/newsletters/1991/april/` | `newsletters/1991/april.md` | Preserved |
| `qodec91.htm` | publications | `/newsletters/1991/december/` | `newsletters/1991/december.md` | Preserved |
| `qofeb91.htm` | publications | `/newsletters/1991/february/` | `newsletters/1991/february.md` | Preserved |
| `qojan91.htm` | publications | `/newsletters/1991/january/` | `newsletters/1991/january.md` | Preserved |
| `qojul91.htm` | publications | `/newsletters/1991/july/` | `newsletters/1991/july.md` | Preserved |
| `qojun91.htm` | publications | `/newsletters/1991/june/` | `newsletters/1991/june.md` | Preserved |
| `qomar91.htm` | publications | `/newsletters/1991/march/` | `newsletters/1991/march.md` | Preserved |
| `qomay91.htm` | publications | `/newsletters/1991/may/` | `newsletters/1991/may.md` | Preserved |
| `qonov91.htm` | publications | `/newsletters/1991/november/` | `newsletters/1991/november.md` | Preserved |
| `qooct91.htm` | publications | `/newsletters/1991/october/` | `newsletters/1991/october.md` | Preserved |
| `qosep91.htm` | publications | `/newsletters/1991/september/` | `newsletters/1991/september.md` | Preserved |
| `qoapr92.htm` | publications | `/newsletters/1992/april/` | `newsletters/1992/april.md` | Preserved |
| `qodec92.htm` | publications | `/newsletters/1992/december/` | `newsletters/1992/december.md` | Preserved |
| `qofeb92.htm` | publications | `/newsletters/1992/february/` | `newsletters/1992/february.md` | Preserved |
| `qojan92.htm` | publications | `/newsletters/1992/january/` | `newsletters/1992/january.md` | Preserved |
| `qojul92.htm` | publications | `/newsletters/1992/july/` | `newsletters/1992/july.md` | Preserved |
| `qojun92.htm` | publications | `/newsletters/1992/june/` | `newsletters/1992/june.md` | Preserved |
| `qomay92.htm` | publications | `/newsletters/1992/may/` | `newsletters/1992/may.md` | Preserved |
| `qooct92.htm` | publications | `/newsletters/1992/october/` | `newsletters/1992/october.md` | Preserved |
| `qosep92.htm` | publications | `/newsletters/1992/september/` | `newsletters/1992/september.md` | Preserved |
| `qofeb93.htm` | publications | `/newsletters/1993/february/` | `newsletters/1993/february.md` | Preserved |
| `qojan93.htm` | publications | `/newsletters/1993/january/` | `newsletters/1993/january.md` | Preserved |
| `qofeb94.htm` | publications | `/newsletters/1994/february/` | `newsletters/1994/february.md` | Preserved |
| `qojan94.htm` | publications | `/newsletters/1994/january/` | `newsletters/1994/january.md` | Preserved |
| `qojul94.htm` | publications | `/newsletters/1994/july/` | `newsletters/1994/july.md` | Preserved |
| `qomar94.htm` | publications | `/newsletters/1994/march/` | `newsletters/1994/march.md` | Preserved |
| `qomay94.htm` | publications | `/newsletters/1994/may/` | `newsletters/1994/may.md` | Preserved |
| `qonov94.htm` | publications | `/newsletters/1994/november/` | `newsletters/1994/november.md` | Preserved |
| `qooct94.htm` | publications | `/newsletters/1994/october/` | `newsletters/1994/october.md` | Preserved |
| `qofeb95.htm` | publications | `/newsletters/1995/february/` | `newsletters/1995/february.md` | Preserved |
| `qojan95.htm` | publications | `/newsletters/1995/january/` | `newsletters/1995/january.md` | Preserved |
| `qomar95.htm` | publications | `/newsletters/1995/march/` | `newsletters/1995/march.md` | Preserved |
| `qomay95.htm` | publications | `/newsletters/1995/may/` | `newsletters/1995/may.md` | Preserved |
| `qoapr96.htm` | publications | `/newsletters/1996/april/` | `newsletters/1996/april.md` | Preserved |
| `qoaug96.htm` | publications | `/newsletters/1996/august/` | `newsletters/1996/august.md` | Preserved |
| `qodec96.htm` | publications | `/newsletters/1996/december/` | `newsletters/1996/december.md` | Preserved |
| `qojan96.htm` | publications | `/newsletters/1996/january/` | `newsletters/1996/january.md` | Preserved |
| `qojul96.htm` | publications | `/newsletters/1996/july/` | `newsletters/1996/july.md` | Preserved |
| `qojun96.htm` | publications | `/newsletters/1996/june/` | `newsletters/1996/june.md` | Preserved |
| `qomar96.htm` | publications | `/newsletters/1996/march/` | `newsletters/1996/march.md` | Preserved |
| `qonov96.htm` | publications | `/newsletters/1996/november/` | `newsletters/1996/november.md` | Preserved |
| `qosep96.htm` | publications | `/newsletters/1996/september/` | `newsletters/1996/september.md` | Preserved |
| `qoapr97.htm` | publications | `/newsletters/1997/april/` | `newsletters/1997/april.md` | Preserved |
| `qoaug97.htm` | publications | `/newsletters/1997/august/` | `newsletters/1997/august.md` | Preserved |
| `qodec97.htm` | publications | `/newsletters/1997/december/` | `newsletters/1997/december.md` | Preserved |
| `qofeb97.htm` | publications | `/newsletters/1997/february/` | `newsletters/1997/february.md` | Preserved |
| `qojan97.htm` | publications | `/newsletters/1997/january/` | `newsletters/1997/january.md` | Preserved |
| `qojun97.htm` | publications | `/newsletters/1997/june/` | `newsletters/1997/june.md` | Preserved |
| `qomay97.htm` | publications | `/newsletters/1997/may/` | `newsletters/1997/may.md` | Preserved |
| `qooct97.htm` | publications | `/newsletters/1997/october/` | `newsletters/1997/october.md` | Preserved |
| `qosep97.htm` | publications | `/newsletters/1997/september/` | `newsletters/1997/september.md` | Preserved |
| `qoapr98.htm` | publications | `/newsletters/1998/april/` | `newsletters/1998/april.md` | Preserved |
| `qoaug98.htm` | publications | `/newsletters/1998/august/` | `newsletters/1998/august.md` | Preserved |
| `qodec98.htm` | publications | `/newsletters/1998/december/` | `newsletters/1998/december.md` | Unavailable notice |
| `qofeb98.htm` | publications | `/newsletters/1998/february/` | `newsletters/1998/february.md` | Preserved |
| `qojan98.htm` | publications | `/newsletters/1998/january/` | `newsletters/1998/january.md` | Preserved |
| `qojun98.htm` | publications | `/newsletters/1998/june/` | `newsletters/1998/june.md` | Preserved |
| `qomay98.htm` | publications | `/newsletters/1998/may/` | `newsletters/1998/may.md` | Preserved |
| `qonov98.htm` | publications | `/newsletters/1998/november/` | `newsletters/1998/november.md` | Unavailable notice |
| `qosep98.htm` | publications | `/newsletters/1998/september/` | `newsletters/1998/september.md` | Preserved |
| `qodec99.htm` | publications | `/newsletters/1999/december/` | `newsletters/1999/december.md` | Preserved |
| `qojan99.htm` | publications | `/newsletters/1999/january/` | `newsletters/1999/january.md` | Preserved |
| `qojul99.htm` | publications | `/newsletters/1999/july/` | `newsletters/1999/july.md` | Preserved |
| `qojun99.htm` | publications | `/newsletters/1999/june/` | `newsletters/1999/june.md` | Preserved |
| `qomar99.htm` | publications | `/newsletters/1999/march/` | `newsletters/1999/march.md` | Preserved |
| `qomay99.htm` | publications | `/newsletters/1999/may/` | `newsletters/1999/may.md` | Preserved |
| `qosep99.htm` | publications | `/newsletters/1999/september/` | `newsletters/1999/september.md` | Preserved |
| `qoaug00.htm` | publications | `/newsletters/2000/august/` | `newsletters/2000/august.md` | Preserved |
| `qodec00.htm` | publications | `/newsletters/2000/december/` | `newsletters/2000/december.md` | Preserved |
| `qojul00.htm` | publications | `/newsletters/2000/july/` | `newsletters/2000/july.md` | Preserved |
| `qojun00.htm` | publications | `/newsletters/2000/june/` | `newsletters/2000/june.md` | Preserved |
| `qomay00.htm` | publications | `/newsletters/2000/may/` | `newsletters/2000/may.md` | Preserved |
| `qonov00.htm` | publications | `/newsletters/2000/november/` | `newsletters/2000/november.md` | Preserved |
| `qooct00.htm` | publications | `/newsletters/2000/october/` | `newsletters/2000/october.md` | Preserved |
| `qosep00.htm` | publications | `/newsletters/2000/september/` | `newsletters/2000/september.md` | Preserved |
| `qoapr01.htm` | publications | `/newsletters/2001/april/` | `newsletters/2001/april.md` | Preserved |
| `qoaug01.htm` | publications | `/newsletters/2001/august/` | `newsletters/2001/august.md` | Preserved |
| `qodec01.htm` | publications | `/newsletters/2001/december/` | `newsletters/2001/december.md` | Preserved |
| `qofeb01.htm` | publications | `/newsletters/2001/february/` | `newsletters/2001/february.md` | Preserved |
| `qojan01.htm` | publications | `/newsletters/2001/january/` | `newsletters/2001/january.md` | Preserved |
| `qojul01.htm` | publications | `/newsletters/2001/july/` | `newsletters/2001/july.md` | Preserved |
| `qojun01.htm` | publications | `/newsletters/2001/june/` | `newsletters/2001/june.md` | Preserved |
| `qomar01.htm` | publications | `/newsletters/2001/march/` | `newsletters/2001/march.md` | Preserved |
| `qomay01.htm` | publications | `/newsletters/2001/may/` | `newsletters/2001/may.md` | Preserved |
| `qonov01.htm` | publications | `/newsletters/2001/november/` | `newsletters/2001/november.md` | Preserved |
| `qooct01.htm` | publications | `/newsletters/2001/october/` | `newsletters/2001/october.md` | Preserved |
| `qosep01.htm` | publications | `/newsletters/2001/september/` | `newsletters/2001/september.md` | Preserved |
| `qoapr02.htm` | publications | `/newsletters/2002/april/` | `newsletters/2002/april.md` | Preserved |
| `qoaug02.htm` | publications | `/newsletters/2002/august/` | `newsletters/2002/august.md` | Preserved |
| `qodec02.htm` | publications | `/newsletters/2002/december/` | `newsletters/2002/december.md` | Preserved |
| `qofeb02.htm` | publications | `/newsletters/2002/february/` | `newsletters/2002/february.md` | Preserved |
| `qojan02.htm` | publications | `/newsletters/2002/january/` | `newsletters/2002/january.md` | Preserved |
| `qojul02.htm` | publications | `/newsletters/2002/july/` | `newsletters/2002/july.md` | Preserved |
| `qojun02.htm` | publications | `/newsletters/2002/june/` | `newsletters/2002/june.md` | Preserved |
| `qomar02.htm` | publications | `/newsletters/2002/march/` | `newsletters/2002/march.md` | Preserved |
| `qomay02.htm` | publications | `/newsletters/2002/may/` | `newsletters/2002/may.md` | Preserved |
| `qonov02.htm` | publications | `/newsletters/2002/november/` | `newsletters/2002/november.md` | Preserved |
| `qooct02.htm` | publications | `/newsletters/2002/october/` | `newsletters/2002/october.md` | Preserved |
| `qosep02.htm` | publications | `/newsletters/2002/september/` | `newsletters/2002/september.md` | Preserved |
| `qoapr03.htm` | publications | `/newsletters/2003/april/` | `newsletters/2003/april.md` | Preserved |
| `qoaug03.htm` | publications | `/newsletters/2003/august/` | `newsletters/2003/august.md` | Preserved |
| `qodec03.htm` | publications | `/newsletters/2003/december/` | `newsletters/2003/december.md` | Preserved |
| `qofeb03.htm` | publications | `/newsletters/2003/february/` | `newsletters/2003/february.md` | Preserved |
| `qojan03.htm` | publications | `/newsletters/2003/january/` | `newsletters/2003/january.md` | Preserved |
| `qojul03.htm` | publications | `/newsletters/2003/july/` | `newsletters/2003/july.md` | Preserved |
| `qojun03.htm` | publications | `/newsletters/2003/june/` | `newsletters/2003/june.md` | Preserved |
| `qomar03.htm` | publications | `/newsletters/2003/march/` | `newsletters/2003/march.md` | Preserved |
| `qomay03.htm` | publications | `/newsletters/2003/may/` | `newsletters/2003/may.md` | Preserved |
| `qonov03.htm` | publications | `/newsletters/2003/november/` | `newsletters/2003/november.md` | Preserved |
| `qooct03.htm` | publications | `/newsletters/2003/october/` | `newsletters/2003/october.md` | Preserved |
| `qosep03.htm` | publications | `/newsletters/2003/september/` | `newsletters/2003/september.md` | Preserved |
| `qoapr04.htm` | publications | `/newsletters/2004/april/` | `newsletters/2004/april.md` | Preserved |
| `qoaug04.htm` | publications | `/newsletters/2004/august/` | `newsletters/2004/august.md` | Preserved |
| `qodec04.htm` | publications | `/newsletters/2004/december/` | `newsletters/2004/december.md` | Preserved |
| `qofeb04.htm` | publications | `/newsletters/2004/february/` | `newsletters/2004/february.md` | Preserved |
| `qojan04.htm` | publications | `/newsletters/2004/january/` | `newsletters/2004/january.md` | Preserved |
| `qojul04.htm` | publications | `/newsletters/2004/july/` | `newsletters/2004/july.md` | Preserved |
| `qojun04.htm` | publications | `/newsletters/2004/june/` | `newsletters/2004/june.md` | Preserved |
| `qomar04.htm` | publications | `/newsletters/2004/march/` | `newsletters/2004/march.md` | Preserved |
| `qomay04.htm` | publications | `/newsletters/2004/may/` | `newsletters/2004/may.md` | Preserved |
| `qonov04.htm` | publications | `/newsletters/2004/november/` | `newsletters/2004/november.md` | Preserved |
| `qooct04.htm` | publications | `/newsletters/2004/october/` | `newsletters/2004/october.md` | Preserved |
| `qosep04.htm` | publications | `/newsletters/2004/september/` | `newsletters/2004/september.md` | Preserved |
| `qoapr05.htm` | publications | `/newsletters/2005/april/` | `newsletters/2005/april.md` | Preserved |
| `qoaug05.htm` | publications | `/newsletters/2005/august/` | `newsletters/2005/august.md` | Preserved |
| `qofeb05.htm` | publications | `/newsletters/2005/february/` | `newsletters/2005/february.md` | Preserved |
| `qojan05.htm` | publications | `/newsletters/2005/january/` | `newsletters/2005/january.md` | Preserved |
| `qojul05.htm` | publications | `/newsletters/2005/july/` | `newsletters/2005/july.md` | Preserved |
| `qojun05.htm` | publications | `/newsletters/2005/june/` | `newsletters/2005/june.md` | Preserved |
| `qomar05.htm` | publications | `/newsletters/2005/march/` | `newsletters/2005/march.md` | Preserved |
| `qomay05.htm` | publications | `/newsletters/2005/may/` | `newsletters/2005/may.md` | Preserved |
| `qosep05.htm` | publications | `/newsletters/2005/september/` | `newsletters/2005/september.md` | Preserved |
| `qomlrel2.htm` | publications | `/release-form-instructions/` | `fan-fiction/release-form-instructions.md` | Preserved |
| `qofaqb.htm` | world | `/bards-faq/` | `world/bards-faq.md` | Preserved |
| `qofaqbl.htm` | world | `/blues-and-blue-bloods-faq/` | `world/blues-and-blue-bloods-faq.md` | Preserved |
| `danc.htm` | world | `/companions-choices/` | `world/companions-choices.md` | Preserved |
| `qofaqc.htm` | world | `/cooking-velgarth-style/` | `world/cooking-velgarth-style.md` | Preserved |
| `qofaqa.htm` | world | `/fauna-faq/` | `world/fauna-faq.md` | Preserved |
| `qofaqgarb.htm` | world | `/garb-faq/` | `world/garb-faq.md` | Preserved |
| `qofaqgifts.htm` | world | `/gifts-faq/` | `world/gifts-faq.md` | Preserved |
| `qofaqg.htm` | world | `/guilds-faq/` | `world/guilds-faq.md` | Preserved |
| `qofaqhe.htm` | world | `/healers-faq/` | `world/healers-faq.md` | Preserved |
| `danhc.htm` | world | `/heralds-and-companions/` | `world/heralds-and-companions.md` | Preserved |
| `qofaqh.htm` | world | `/heralds-faq/` | `world/heralds-faq.md` | Preserved |
| `danmag1.htm` | world | `/magic-of-velgarth/` | `world/magic-of-velgarth.md` | Preserved |
| `qofaqm.htm` | world | `/military-faq/` | `world/military-faq.md` | Preserved |
| `qofaqba.htm` | world | `/northern-barbarians-faq/` | `world/northern-barbarians-faq.md` | Preserved |
| `qofaqp.htm` | world | `/plants-faq/` | `world/plants-faq.md` | Preserved |
| `danp.htm` | world | `/proverbs-of-velgarth/` | `world/proverbs-of-velgarth.md` | Preserved |
| `danr.htm` | world | `/reincarnated-characters/` | `world/reincarnated-characters.md` | Preserved |
| `qofaqrel.htm` | world | `/religions-faq/` | `world/religions-faq.md` | Preserved |
| `qofaqs.htm` | world | `/shina-in-faq/` | `world/shina-in-faq.md` | Preserved |
| `qofaqt.htm` | world | `/tayledras-faq/` | `world/tayledras-faq.md` | Preserved |
| `qofaqtr.htm` | world | `/travel-guide/` | `world/travel-guide.md` | Preserved |
| `dantime.htm` | world | `/valdemar-timeline/` | `world/valdemar-timeline.md` | Preserved |
| `qojust.htm` | world | `/world-reference-guide/` | `world/world-reference-guide.md` | Preserved |

## Validation performed

- Deployment build: 247 pages, 48 native sections, no orphaned content.
- All 250 source/notice mappings and 508 permanent redirects have real destinations;
  redirects have no chains, and internal links and sitemap entries use canonical paths.
- Named anchors in the retained source pages resolve; the superseded homepage is excluded.
- Newsletter year and period ordering, HTML/PDF issue counts, and preserved title labels
  were checked against the catalog.
- Eighteen regression tests pass, covering routing, redirect failures, source preservation,
  curated-hub preservation, repeatability, and unavailable-content accounting.
- Both original imports were run in a fresh directory, then built with a simulated Netlify
  deployment URL and checked with the link and redirect validators.
- A second organization pass leaves the content, curated hubs, indexes, and redirects
  byte-for-byte unchanged.
