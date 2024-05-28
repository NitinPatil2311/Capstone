import pytest
from application import app
from flask import session

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert b'Welcome to the Effort Estimation Tool' in response.data

def test_register(client):
    response = client.post('/register', data=dict(
        email='test@example.com',
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'' in response.data


def test_login(client):
    response = client.post('/login', data=dict(
        email='test@example.com',
        password='testpassword'
    ), follow_redirects=True)
    assert b'' in response.data

def test_estimation_submission(client):
    with client.session_transaction() as sess:
        sess['email'] = 'admin@gmail.com'  # Simulate logged in user

    response = client.get('/estimation_submission')
    assert response.status_code == 200
    assert b'' in response.data

def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data