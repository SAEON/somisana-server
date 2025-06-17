from somisana.const import SOMISANAScope


def all_scopes_excluding(scope):
    return [s for s in SOMISANAScope if s != scope]


def assert_forbidden(response):
    assert response.status_code == 403
    assert response.json() == {'detail': 'Forbidden'}
