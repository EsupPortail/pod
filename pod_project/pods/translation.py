# -*- coding: utf-8 -*-
"""
Copyright (C) 2014 Nicolas Can
Ce programme est un logiciel libre : vous pouvez
le redistribuer et/ou le modifier sous les termes
de la licence GNU Public Licence telle que publiée
par la Free Software Foundation, soit dans la
version 3 de la licence, ou (selon votre choix)
toute version ultérieure. 
Ce programme est distribué avec l'espoir
qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties
implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir
la licence GNU General Public License
pour plus de détails.
Vous devriez avoir reçu une copie de la licence
GNU General Public Licence
avec ce programme. Si ce n'est pas le cas,
voir http://www.gnu.org/licenses/
"""
from modeltranslation.translator import translator, TranslationOptions
from pods.models import Type, Discipline, Channel
from django.utils.translation import ugettext_lazy as _


class TypeTranslationOptions(TranslationOptions):
    fallback_values = _('-- sorry, no translation provided --')
    fields = ('title',)
translator.register(Type, TypeTranslationOptions)


class DisciplineTranslationOptions(TranslationOptions):
    fallback_values = _('-- sorry, no translation provided --')
    fields = ('title',)
translator.register(Discipline, DisciplineTranslationOptions)


class ChannelTranslationOptions(TranslationOptions):
    fallback_values = _('-- sorry, no translation provided --')
    fields = ('title',)
translator.register(Channel, ChannelTranslationOptions)
