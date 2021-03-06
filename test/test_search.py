"""
Test the search interface.
"""
from test.fixtures import make_test_env, make_fake_space

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from tiddlyweb.model.user import User
from tiddlyweb.model.tiddler import Tiddler


def setup_module(module):
    make_test_env(module)
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 8080, app_fn)
    wsgi_intercept.add_wsgi_intercept('cdent.0.0.0.0', 8080, app_fn)
    wsgi_intercept.add_wsgi_intercept('fnd.0.0.0.0', 8080, app_fn)
    make_fake_space(module.store, 'cdent')
    make_fake_space(module.store, 'fnd')
    user = User('cdent')
    user.set_password('cow')
    module.store.put(user)
    module.http = httplib2.Http()


def teardown_module(module):
    import os
    os.chdir('..')

def test_basic_search():
    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=title:TiddlyWebAdaptor')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert info[0]['title'] == 'TiddlyWebAdaptor'

def test_wildcard_search():
    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:TiddlyWebA*')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert info[0]['title'] == 'TiddlyWebAdaptor'

def test_multiword_phrase_search():
    tiddler = Tiddler('one', 'cdent_public')
    tiddler.text = 'monkeys are fun!'
    store.put(tiddler)
    tiddler = Tiddler('one two', 'cdent_public')
    tiddler.text = 'monkeys are fun!'
    store.put(tiddler)
    tiddler = Tiddler('one two three', 'cdent_public')
    tiddler.text = 'monkeys are fun!'
    store.put(tiddler)
    tiddler = Tiddler('three two one', 'cdent_public')
    tiddler.text = 'monkeys are fun!'
    store.put(tiddler)

    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:one')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert len(info) == 1, info

    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:one%20two')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert len(info) == 0, info

    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:one%20two%20three')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert len(info) == 0, info

    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:%22one%20two%20three%22')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert len(info) == 1, info

def test_multibag_search():
    tiddler = Tiddler('one two', 'fnd_public')
    tiddler.text = 'monkeys are not fun!'
    store.put(tiddler)

    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:%22one%20two%22%20fbag:cdent_public')
    info = simplejson.loads(content)
    assert len(info) == 1, info
    assert info[0]['bag'] == 'cdent_public', info

    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:%22one%20two%22%20(fbag:cdent_public%20OR%20fbag:fnd_public)')
    info = simplejson.loads(content)
    assert len(info) == 2, info

def test_cased_search():
    tiddler = Tiddler('One Two', 'fnd_public')
    tiddler.text = 'monkeys are not fun!'
    store.put(tiddler)

    response, content = http.request(
            'http://0.0.0.0:8080/search.json?q=ftitle:%22one%20two%22%20fbag:fnd_public')
    info = simplejson.loads(content)
    assert len(info) == 1, info # don't get the new tiddler because of case
