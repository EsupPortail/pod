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

from __future__ import unicode_literals

from django_cas_gateway.backends import CASBackend
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

import sys
import logging
logger = logging.getLogger(__name__)
#FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
#logging.basicConfig(format=FORMAT)
#d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
#logger = logging.getLogger(__name__)


class PopulatedCASBackend(CASBackend):
    """CAS authentication backend with user data populated from AD"""

    def authenticate(self, ticket, service, request):
        """Authenticates CAS ticket and retrieves user data"""

        user = super(PopulatedCASBackend, self).authenticate(
            ticket, service, request)

        if user is not None:
            user.is_active = True
            user.save()
            if settings.USE_LDAP_TO_POPULATE_USER:
                import ldap
                try:
                    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
                    l.protocol_version = ldap.VERSION3
                    if settings.AUTH_LDAP_BIND_DN != '':
                        l.simple_bind_s(settings.AUTH_LDAP_BIND_DN,
                                        settings.AUTH_LDAP_BIND_PASSWORD)

                    ldap_scope = {'ONELEVEL': ldap.SCOPE_ONELEVEL,
                                  'SUBTREE': ldap.SCOPE_SUBTREE}

                    list_value = []
                    for val in settings.AUTH_USER_ATTR_MAP.values():
                        list_value.append(str(val))
                    try:
                        r = l.search_s(settings.AUTH_LDAP_USER_SEARCH[0], ldap_scope[
                                       settings.AUTH_LDAP_SCOPE], settings.AUTH_LDAP_USER_SEARCH[1] % {"uid": user.username}, list_value)
                        (dn, attrs) = r[0]  # une seule entree par uid
                        if settings.AUTH_USER_ATTR_MAP.get('first_name') and attrs.get(settings.AUTH_USER_ATTR_MAP['first_name']):
                            user.first_name = attrs[settings.AUTH_USER_ATTR_MAP[
                                'first_name']][0]  # get first value
                        if settings.AUTH_USER_ATTR_MAP.get('last_name') and attrs.get(settings.AUTH_USER_ATTR_MAP['last_name']):
                            user.last_name = attrs[settings.AUTH_USER_ATTR_MAP[
                                'last_name']][0]  # get first value
                        if settings.AUTH_USER_ATTR_MAP.get('email') and attrs.get(settings.AUTH_USER_ATTR_MAP['email']):
                            user.email = attrs[settings.AUTH_USER_ATTR_MAP[
                                'email']][0]  # get first value
                        if settings.AUTH_USER_ATTR_MAP.get('affiliation') and attrs.get(settings.AUTH_USER_ATTR_MAP['affiliation']):
                            try:
                                user.userprofile.affiliation = attrs[
                                    settings.AUTH_USER_ATTR_MAP['affiliation']][0]  # get first value
                                user.userprofile.save()

                                if user.userprofile.affiliation in settings.AFFILIATION_STAFF:
                                    user.is_staff = True

                            except:
                                # print u'\n*****Unexpected error link :%s -
                                # %s' % (sys.exc_info()[0], sys.exc_info()[1])
                                msg = u'\n*****Unexpected error link :%s - %s' % (
                                    sys.exc_info()[0], sys.exc_info()[1])
                                logger.error(msg)
                    except:
                        user.is_active = False
                        user.save()
                        msg = u'\n*****Unexpected error link :%s - %s' % (
                            sys.exc_info()[0], sys.exc_info()[1])
                        logger.error(msg)
                except ldap.LDAPError, e:
                    logger.error(e)
            else:
                if request.session.get('attributes') and settings.AUTH_USER_ATTR_MAP != ():
                    if settings.AUTH_USER_ATTR_MAP.get('first_name') and request.session['attributes'].get(settings.AUTH_USER_ATTR_MAP['first_name']):
                        user.first_name = request.session['attributes'][
                            settings.AUTH_USER_ATTR_MAP['first_name']]
                    if settings.AUTH_USER_ATTR_MAP.get('last_name') and request.session['attributes'].get(settings.AUTH_USER_ATTR_MAP['last_name']):
                        user.last_name = request.session['attributes'][
                            settings.AUTH_USER_ATTR_MAP['last_name']]
                    if settings.AUTH_USER_ATTR_MAP.get('email') and request.session['attributes'].get(settings.AUTH_USER_ATTR_MAP['email']):
                        user.email = request.session['attributes'][
                            settings.AUTH_USER_ATTR_MAP['email']]
                    if settings.AUTH_USER_ATTR_MAP.get('affiliation') and request.session['attributes'].get(settings.AUTH_USER_ATTR_MAP['affiliation']):
                        try:
                            user.userprofile.affiliation = request.session[
                                'attributes'][settings.AUTH_USER_ATTR_MAP['affiliation']]
                            user.userprofile.save()

                            if user.userprofile.affiliation in settings.AFFILIATION_STAFF:
                                user.is_staff = True

                        except:
                            msg = u'\n*****Unexpected error link :%s - %s' % (
                                sys.exc_info()[0], sys.exc_info()[1])
                            logger.error(msg)

            # on sauvegarde l'utilisateur
            user.save()
            try:
                user.userprofile.auth_type = "cas"
                user.userprofile.save()
            except:
                msg = u'\n*****Unexpected error link :%s - %s' % (
                    sys.exc_info()[0], sys.exc_info()[1])
                logger.error(msg)

        else:
            msg = u'%s' % _(u'Unable to authenticate')
            messages.add_message(request, messages.ERROR, msg)

        return user
