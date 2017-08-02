import pytest

from apistar import App, Include, Route, TestClient, exceptions, typesystem
from apistar.interfaces import URLArgs
from apistar.routing import PathWildcard


class MaxLength(typesystem.String):
    max_length = 5


def found():
    return {
        'message': 'Found'
    }


def path_params(args: URLArgs, var: int):
    return {
        'args': args
    }


def path_param(var):
    return {
        'var': var
    }


def path_param_with_int(var: int):
    return {
        'var': var
    }


def path_param_with_full_path(var: PathWildcard):
    return {
        'var': var
    }


def path_param_with_max_length(var: MaxLength):
    return {
        'var': var
    }


def path_param_with_number(var: typesystem.Number):
    return {
        'var': var
    }


def path_param_with_integer(var: typesystem.Integer):
    return {
        'var': var
    }


def path_param_with_string(var: typesystem.String):
    return {
        'var': var
    }


def subpath(var: typesystem.Integer):
    return {
        'var': var
    }


app = App(routes=[
    Route('/found/', 'GET', found),
    Route('/path_params/{var}/', 'GET', path_params),
    Route('/path_param/{var}/', 'GET', path_param),
    Route('/int/{var}/', 'GET', path_param_with_int),
    Route('/full_path/{var}', 'GET', path_param_with_full_path),
    Route('/max_length/{var}/', 'GET', path_param_with_max_length),
    Route('/number/{var}/', 'GET', path_param_with_number),
    Route('/integer/{var}/', 'GET', path_param_with_integer),
    Route('/string/{var}/', 'GET', path_param_with_string),
    Include('/subpath', [
        Route('/{var}/', 'GET', subpath),
    ], namespace='included'),
])


client = TestClient(app)


def test_200():
    response = client.get('/found/')
    assert response.status_code == 200
    assert response.json() == {
        'message': 'Found'
    }


def test_404():
    response = client.get('/404/')
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Not found'
    }


def test_405():
    response = client.post('/found/')
    assert response.status_code == 405
    assert response.json() == {
        'message': 'Method not allowed'
    }


def test_found_no_slash():
    response = client.get('/found', allow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://testserver/found/'

    response = client.get('/found')
    assert response.status_code == 200
    assert response.url == 'http://testserver/found/'


def test_path_params():
    response = client.get('/path_params/1/')
    assert response.json() == {
        'args': {'var': 1}
    }


def test_path_param():
    response = client.get('/path_param/abc/')
    assert response.json() == {
        'var': 'abc'
    }


def test_int_path_param():
    response = client.get('/int/1/')
    assert response.json() == {
        'var': 1
    }


def test_subpath():
    response = client.get('/subpath/123/')
    assert response.json() == {
        'var': 123
    }


def test_full_path_param():
    response = client.get('/full_path/abc/def/ghi/')
    assert response.json() == {
        'var': 'abc/def/ghi/'
    }


def test_valid_max_length():
    response = client.get('/max_length/abcde/')
    assert response.status_code == 200
    assert response.json() == {
        'var': 'abcde'
    }


def test_invalid_max_length():
    response = client.get('/max_length/abcdef/')
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Not found'
    }


def test_valid_number():
    response = client.get('/number/1.23/')
    assert response.status_code == 200
    assert response.json() == {
        'var': 1.23
    }


def test_invalid_number():
    response = client.get('/number/abc/')
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Not found'
    }


def test_valid_integer():
    response = client.get('/integer/123/')
    assert response.status_code == 200
    assert response.json() == {
        'var': 123
    }


def test_invalid_integer():
    response = client.get('/integer/abc/')
    assert response.status_code == 404
    assert response.json() == {
        'message': 'Not found'
    }


def test_valid_string():
    response = client.get('/string/hello world/')
    assert response.status_code == 200
    assert response.json() == {
        'var': 'hello world'  # makes sure we don't return hello%20world
    }


def test_misconfigured_omission_on_route():
    def missing_type():
        raise NotImplementedError

    with pytest.raises(exceptions.ConfigurationError):
        App(routes=[Route('/{var}/', 'GET', missing_type)])


def test_misconfigured_type_on_route():
    def set_type(var: set):
        raise NotImplementedError

    with pytest.raises(exceptions.ConfigurationError):
        App(routes=[Route('/{var}/', 'GET', set_type)])


def test_routing_reversal_on_path_without_url_params():
    url = app.router.reverse_url('found')
    assert url == '/found/'


def test_routing_reversal_on_path_non_existent_path():
    with pytest.raises(exceptions.NoReverseMatch):
        app.router.reverse_url('missing', {'var': 'not_here'})


def test_routing_reversal_on_path_with_url_params():
    url = app.router.reverse_url('path_params', {'var': '100'})
    assert url == '/path_params/100/'


def test_routing_reversal_on_subpath():
    url = app.router.reverse_url('included:subpath', {'var': '100'})
    assert url == '/subpath/100/'