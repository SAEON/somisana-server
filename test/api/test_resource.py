import pytest

from somisana.const import SOMISANAScope
from somisana.db.models import Resource
from test import TestSession
from test.api import assert_forbidden
from test.api.lib import compare_resources
from test.factories import ResourceFactory


@pytest.mark.require_scope(SOMISANAScope.RESOURCE_READ)
def test_get_resource(api, scopes):
    authorized = SOMISANAScope.RESOURCE_READ in scopes

    resource = ResourceFactory.create()

    r = api(scopes).get(f'/resource/{resource.id}/')

    if not authorized:
        assert_forbidden(r)
    else:
        compare_resources(resource, r.json())


@pytest.mark.require_scope(SOMISANAScope.RESOURCE_ADMIN)
def test_delete_resource(api, scopes):
    authorized = SOMISANAScope.RESOURCE_ADMIN in scopes

    resource = ResourceFactory.create()

    r = api(scopes).delete(f'/resource/{resource.id}/')

    if not authorized:
        assert_forbidden(r)
    else:
        assert TestSession.get(Resource, resource.id) is None
