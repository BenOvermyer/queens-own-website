#!/usr/bin/env python3
"""Move obsolete, presentation-only markup into shared stylesheet classes.

The archive relies on ``<font>`` and ``<center>`` elements and on presentational
attributes such as ``align``, ``valign``, ``border``, ``cellpadding``, ``cellspacing``,
``face``, ``size``, ``color``, ``bgcolor``, ``width`` and ``height``. This module
rewrites them to semantic elements with classes defined in ``static/css/site.css``:

* ``<font face size color>`` becomes ``<span>`` with ``ff-*``, ``fs-*`` and ``c-*``
  classes;
* ``<center>`` becomes ``<div class="center">``;
* ``align``/``valign`` become ``align-*``/``valign-*`` (or ``float-*`` on images,
  ``table-align-*`` on tables);
* table ``border``/``cellpadding``/``cellspacing`` become ``border-*``,
  ``cellpadding-*`` and ``cellspacing-*`` classes;
* ``width``/``height``/``bgcolor`` and any other residual dimensions become inline
  styles, since their values are one-off.

``<u>``, ``<s>`` and the raw-text ``<xmp>`` code-sample element are left alone.
"""
import re

from bs4 import BeautifulSoup

ALIGN_CLASSES = {'left': 'align-left', 'center': 'align-center', 'right': 'align-right', 'justify': 'align-justify'}
VALIGN_CLASSES = {'top': 'valign-top', 'middle': 'valign-middle', 'center': 'valign-middle'}
FONT_FAMILIES = {
    'bookman old style': 'ff-bookman', 'comic sans ms': 'ff-comic-sans', 'harem': 'ff-harem',
    'times new roman': 'ff-times', 'new york': 'ff-new-york', 'arial': 'ff-arial', 'helvetica': 'ff-helvetica',
}
FONT_SIZES = {
    '1': 'fs-1', '2': 'fs-2', '3': 'fs-3', '4': 'fs-4', '5': 'fs-5', '6': 'fs-6', '7': 'fs-7',
    '8': 'fs-7', '9': 'fs-7', '+1': 'fs-plus1', '+2': 'fs-plus2', '-1': 'fs-minus1', '-2': 'fs-minus2',
}
COLORS = {
    '#0000ff': 'c-blue', 'blue': 'c-blue', 'red': 'c-red', 'black': 'c-black', 'aqua': 'c-aqua', 'white': 'c-white',
}
DIMENSION_ATTRIBUTES = ('width', 'height')
INTEGER = re.compile(r'^\d+$')


def _add_class(element, class_name):
    classes = element.get('class', [])
    if class_name not in classes:
        classes.append(class_name)
    element['class'] = classes


def _add_style(element, declarations):
    if not declarations:
        return
    existing = element.get('style', '').rstrip('; ')
    merged = '; '.join(part for part in [existing, '; '.join(declarations)] if part)
    element['style'] = merged


def _dimension(value):
    value = value.strip()
    if not value:
        return None
    if INTEGER.match(value):
        return value + 'px'
    return value


def destyle_soup(soup):
    """Rewrite obsolete presentational markup to classes and inline dimensions in place."""
    for table in soup.find_all('table'):
        for attribute in ('cellpadding', 'cellspacing'):
            if not table.has_attr(attribute):
                continue
            value = str(table[attribute]).strip()
            if INTEGER.match(value):
                _add_class(table, f'{attribute}-{value}')
            del table[attribute]
    for element in soup.find_all(True):
        if element.has_attr('border'):
            value = str(element['border']).strip()
            del element['border']
            if INTEGER.match(value) and value != '0':
                _add_class(element, 'border-' + value)
        if element.has_attr('align'):
            value = str(element['align']).strip().lower()
            del element['align']
            if value in ALIGN_CLASSES:
                if element.name == 'img':
                    _add_class(element, 'float-' + value)
                elif element.name == 'table':
                    _add_class(element, 'table-' + ALIGN_CLASSES[value])
                else:
                    _add_class(element, ALIGN_CLASSES[value])
        if element.has_attr('valign'):
            value = str(element['valign']).strip().lower()
            del element['valign']
            if value in VALIGN_CLASSES:
                _add_class(element, VALIGN_CLASSES[value])
        styles = []
        for attribute in DIMENSION_ATTRIBUTES:
            if element.has_attr(attribute):
                dimension = _dimension(str(element[attribute]))
                del element[attribute]
                if dimension:
                    styles.append(f'{attribute}:{dimension}')
        if element.has_attr('bgcolor'):
            styles.append('background-color:' + str(element['bgcolor']).strip())
            del element['bgcolor']
        if element.has_attr('background'):
            styles.append('background-image:url(' + str(element['background']).strip() + ')')
            del element['background']
        _add_style(element, styles)
    for font in soup.find_all('font'):
        classes = []
        for attribute, table in (('face', FONT_FAMILIES), ('size', FONT_SIZES), ('color', COLORS)):
            if font.has_attr(attribute):
                classes.append(table.get(str(font[attribute]).strip().lower(), ''))
                del font[attribute]
        font.name = 'span'
        for class_name in classes:
            if class_name:
                _add_class(font, class_name)
    for center in soup.find_all('center'):
        center.name = 'div'
        _add_class(center, 'center')
    return soup
