#!/usr/bin/env python3
"""Repair malformed legacy markup in raw archive HTML before it is parsed.

The original hand-authored pages contain attributes whose quotes are mismatched or
missing, for example ``href='page.htm">`` or ``href="mailto:a@b.com>a@b.com</a>``.
A lenient parser then reads the attribute value as everything up to the *next* quote,
swallowing the link text and following markup; on serialization the swallowed tags
come back as escaped ``&lt;``/``&gt;`` text. Normalizing the quotes first lets the
parser recover the intended structure.

Operates on raw bytes so the archive's original encoding is preserved unchanged.
The rules are deliberately conservative: they only touch attribute values that are
unterminated or closed with the wrong quote, and a few exact broken fragments.
"""
import re

# Each rule fixes an attribute value that cannot be parsed as written:
#   "value'   double quote opened, single quote used to close
#   "value    double quote opened, never closed before the tag ends
#   'value"   single quote opened, double quote used to close
#   'value    single quote opened, never closed before the tag ends
# The value pattern excludes quotes and angle brackets, so well-formed attributes,
# which always close with the matching quote, never match.
QUOTE_RULES = [
    # An anchor whose opening "<" was followed by spaces, so it parsed as text: "< a href=".
    # A malformed font element: source "<font="Bookman Old Style" face=4>" or the
    # parser-mangled "<font="bookman face="4">" both meant face + size.
    (re.compile(rb'<font="([^"]*)"\s+face="(\w+)">'), rb'<font face="\1" size="\2">'),
    (re.compile(rb'<font="([^"]*)"\s+face=(\w+)>'), rb'<font face="\1" size="\2">'),
    (re.compile(rb'<font="(\w+)\s+face="(\w+)">'), rb'<font face="\1" size="\2">'),
    (re.compile(rb'</font="[^"]*>"?'), rb'</font>'),
    (re.compile(rb'<\s+a\s+href=', re.I), rb'<a href='),
    (re.compile(rb'=\s*"([^"\'<>]*)\'>'), rb'="\1">'),
    (re.compile(rb'=\s*"([^"\'<>]*)>'), rb'="\1">'),
    (re.compile(rb'=\s*\'([^"\'<>]*)\">'), rb'="\1">'),
    (re.compile(rb'=\s*\'([^"\'<>]*)>'), rb'="\1">'),
    # A duplicated opening fragment: href="mailto:<a href="user@host
    (re.compile(rb'href="mailto:<a href="'), rb'href="mailto:'),
    # A mailto href that swallowed its own closing </a> and link text.
    (re.compile(rb'href="mailto:([^"\'<>]*)</a>'), rb'href="mailto:\1">\1</a>'),
]
# Exact broken fragments that no general rule should touch.
TARGETED_RULES = [
    (b'<a href="mailto:Sacree Noir <sn.keeper@yahoo.com>">Sacree Noir <sn.keeper@yahoo.com></a>',
     b'<a href="mailto:sn.keeper@yahoo.com">Sacree Noir &lt;sn.keeper@yahoo.com&gt;</a>'),
]


def repair_markup(data):
    """Return archive HTML/Markdown bytes with malformed attribute quoting repaired."""
    for pattern, replacement in QUOTE_RULES:
        data = pattern.sub(replacement, data)
    for broken, fixed in TARGETED_RULES:
        data = data.replace(broken, fixed)
    return data
