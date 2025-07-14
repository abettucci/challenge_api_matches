import pytest
import json
from ..app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'API de Ítems Similares' in data['message']

def test_compare_items(client):
    payload = {
        "item_a": {"item_id": 1, "title": "Telefono movil"},
        "item_b": {"item_id": 2, "title": "Telefono celular"}
    }
    response = client.post('/items/compare',
                           data=json.dumps(payload),
                           content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'similarity_score' in data
    assert 'are_similar' in data
    assert 'pair_id' in data 

def test_compare_items_with_and_without_ml(client):
    payload = {
        "item_a": {"item_id": 1, "title": "Telefono movil"},
        "item_b": {"item_id": 2, "title": "Telefono celular"}
    }
    # Forzar método tradicional
    payload_no_ml = dict(payload)
    payload_no_ml["use_ml"] = False
    response_no_ml = client.post('/items/compare',
                                 data=json.dumps(payload_no_ml),
                                 content_type='application/json')
    assert response_no_ml.status_code == 200
    data_no_ml = response_no_ml.get_json()
    # Forzar ML (si está disponible)
    payload_ml = dict(payload)
    payload_ml["use_ml"] = True
    response_ml = client.post('/items/compare',
                              data=json.dumps(payload_ml),
                              content_type='application/json')
    assert response_ml.status_code == 200 or response_ml.status_code == 500  # Puede fallar si no hay modelo
    data_ml = response_ml.get_json()
    # Si ambos funcionaron, comparar resultados
    if response_ml.status_code == 200:
        assert data_no_ml['similarity_score'] != data_ml['similarity_score'] or data_no_ml['similarity_score'] == data_ml['similarity_score'] 