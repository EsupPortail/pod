# -*- coding: utf-8 -*-
"""
Ce programme est un logiciel libre : vous pouvez le redistribuer
et/ou le modifier sous les termes de la licence GNU Public Licence
telle que publiée par la Free Software Foundation, soit dans la version 3
de la licence, ou (selon votre choix) toute version ultérieure.
Ce programme est distribué avec l'espoir qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir la licence GNU General Public License
pour plus de détails. Vous devriez avoir reçu une copie de la licence
GNU General Public Licence avec ce programme. Si ce n'est pas le cas, voir
http://www.gnu.org/licenses/
"""
from __future__ import unicode_literals

import re
from django import template
from HTMLParser import HTMLParser

register = template.Library()
parser = HTMLParser()


@register.filter(name='metaformat')
def metaformat(content):
    """
        Meta tag content text formatter

    Tries to make meta tag content more usable, by removing HTML entities and
    control chars. Works in conjunction with [striptags] and maybe [safe]
    this way:
        someHTMLContent|metaformat|safe|striptags

    Args:
        content (str):  the string to process

    Returns:
        content (str):  the cleaned string

    """
    content = re.sub('\s\s+', " ", parser.unescape(content))
    toReplace = {
        '&#39;': "'",
        '"': "'",
    }
    for bad, good in toReplace.iteritems():
        content = content.replace(bad, good)
    return content
