import pytest
import json
import boto3
import os
from moto import mock_aws
from app import app, create_tables, calculate_similarity, generate_pair_id, get_dynamodb

@pytest.fixture
def client(mock_dynamodb_tables):
    """Fixture para crear un cliente de prueba de Flask con DynamoDB mockeado"""
    app.config['TESTING'] = True
    
    # Configurar variables de entorno para el mock
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    # Reemplazar la función get_dynamodb con el mock
    import app as app_module
    app_module.get_dynamodb = lambda: mock_dynamodb_tables
    app_module.dynamodb = mock_dynamodb_tables
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_dynamodb_tables():
    """Fixture para crear tablas DynamoDB simuladas"""
    with mock_aws():
        # Configurar variables de entorno para el mock
        import os
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        # Crear cliente DynamoDB simulado
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Crear tabla de pares
        pairs_table = dynamodb.create_table(
            TableName='item_pairs',
            KeySchema=[
                {'AttributeName': 'pair_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pair_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Crear tabla de ítems
        items_table = dynamodb.create_table(
            TableName='items',
            KeySchema=[
                {'AttributeName': 'item_id', 'KeyType': 'HASH'},
                {'AttributeName': 'title', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'item_id', 'AttributeType': 'N'},
                {'AttributeName': 'title', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Esperar a que las tablas estén activas
        pairs_table.meta.client.get_waiter('table_exists').wait(TableName='item_pairs')
        items_table.meta.client.get_waiter('table_exists').wait(TableName='items')
        
        yield dynamodb

class TestHealthCheck:
    """Pruebas para el endpoint de salud"""
    
    def test_health_check(self, client, mock_dynamodb_tables):
        """Prueba que el endpoint de salud funcione correctamente"""
        response = client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert 'API de Ítems Similares funcionando correctamente' in data['message']
        assert 'timestamp' in data

class TestCompareItems:
    """Pruebas para el endpoint de comparación de ítems"""
    
    def test_compare_items_success(self, client, mock_dynamodb_tables):
        """Prueba comparación exitosa de dos ítems"""
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            },
            'item_b': {
                'item_id': 456,
                'title': 'Telefono celular'
            }
        }
        
        response = client.post('/items/compare',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert 'similarity_score' in data
        assert 'are_equal' in data
        assert 'are_similar' in data
        assert 'pair_exists' in data
        assert isinstance(data['similarity_score'], float)
        assert isinstance(data['are_equal'], bool)
        assert isinstance(data['are_similar'], bool)
    
    def test_compare_items_equal_titles(self, client, mock_dynamodb_tables):
        """Prueba comparación de títulos iguales"""
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            },
            'item_b': {
                'item_id': 456,
                'title': 'Telefono movil'
            }
        }
        
        response = client.post('/items/compare',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['are_equal'] == True
        assert data['similarity_score'] == 1.0
    
    def test_compare_items_missing_data(self, client, mock_dynamodb_tables):
        """Prueba error cuando faltan datos requeridos"""
        # Sin item_b
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            }
        }
        
        response = client.post('/items/compare',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['status'] == 'error'
        assert 'item_a e item_b' in data['message']
    
    def test_compare_items_invalid_structure(self, client, mock_dynamodb_tables):
        """Prueba error cuando la estructura de datos es inválida"""
        payload = {
            'item_a': {
                'item_id': 123
                # Falta 'title'
            },
            'item_b': {
                'item_id': 456,
                'title': 'Telefono celular'
            }
        }
        
        response = client.post('/items/compare',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['status'] == 'error'
        assert 'item_id y title' in data['message']

class TestCreateItemPair:
    """Pruebas para el endpoint de creación de pares"""
    
    def test_create_item_pair_success(self, client, mock_dynamodb_tables):
        """Prueba creación exitosa de un par de ítems"""
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            },
            'item_b': {
                'item_id': 456,
                'title': 'Telefono celular'
            }
        }
        
        response = client.post('/items/pairs',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['status'] == 'success'
        assert data['action'] == 'created'
        assert 'Par de ítems creado exitosamente' in data['message']
        assert 'pair_id' in data
    
    def test_create_item_pair_duplicate(self, client, mock_dynamodb_tables):
        """Prueba que no se duplique un par existente"""
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            },
            'item_b': {
                'item_id': 456,
                'title': 'Telefono celular'
            }
        }
        
        # Crear el par por primera vez
        response1 = client.post('/items/pairs',
                              data=json.dumps(payload),
                              content_type='application/json')
        data1 = json.loads(response1.data)
        
        assert response1.status_code == 201
        assert data1['action'] == 'created'
        
        # Intentar crear el mismo par nuevamente
        response2 = client.post('/items/pairs',
                              data=json.dumps(payload),
                              content_type='application/json')
        data2 = json.loads(response2.data)
        
        assert response2.status_code == 200
        assert data2['action'] == 'existing'
        assert 'ya existe' in data2['message']
        assert data1['pair_id'] == data2['pair_id']
    
    def test_create_item_pair_missing_data(self, client, mock_dynamodb_tables):
        """Prueba error cuando faltan datos requeridos"""
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            }
            # Falta item_b
        }
        
        response = client.post('/items/pairs',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['status'] == 'error'
        assert 'item_a e item_b' in data['message']

class TestGetAllPairs:
    """Pruebas para el endpoint de obtener todos los pares"""
    
    def test_get_all_pairs_empty(self, client, mock_dynamodb_tables):
        """Prueba obtener pares cuando la tabla está vacía"""
        response = client.get('/items/pairs')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['pairs']) == 0
        assert 'Se encontraron 0 pares' in data['message']
    
    def test_get_all_pairs_with_data(self, client, mock_dynamodb_tables):
        """Prueba obtener pares cuando hay datos"""
        # Crear un par primero
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            },
            'item_b': {
                'item_id': 456,
                'title': 'Telefono celular'
            }
        }
        
        client.post('/items/pairs',
                   data=json.dumps(payload),
                   content_type='application/json')
        
        # Obtener todos los pares
        response = client.get('/items/pairs')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['pairs']) == 1
        assert 'Se encontraron 1 pares' in data['message']

class TestGetPair:
    """Pruebas para el endpoint de obtener un par específico"""
    
    def test_get_pair_success(self, client, mock_dynamodb_tables):
        """Prueba obtener un par específico exitosamente"""
        # Crear un par primero
        payload = {
            'item_a': {
                'item_id': 123,
                'title': 'Telefono movil'
            },
            'item_b': {
                'item_id': 456,
                'title': 'Telefono celular'
            }
        }
        
        create_response = client.post('/items/pairs',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        create_data = json.loads(create_response.data)
        pair_id = create_data['pair_id']
        
        # Obtener el par específico
        response = client.get(f'/items/pairs/{pair_id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert 'pair' in data
        assert data['pair']['pair_id'] == pair_id
        assert str(data['pair']['item_a_id']) == str(123)
        assert str(data['pair']['item_b_id']) == str(456)
    
    def test_get_pair_not_found(self, client, mock_dynamodb_tables):
        """Prueba obtener un par que no existe"""
        response = client.get('/items/pairs/nonexistent_pair')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['status'] == 'error'
        assert 'no encontrado' in data['message']

class TestUtilityFunctions:
    """Pruebas para funciones utilitarias"""
    
    def test_calculate_similarity(self):
        """Prueba el cálculo de similitud"""
        # Títulos iguales
        similarity = calculate_similarity('Telefono movil', 'Telefono movil')
        assert similarity == 1.0
        
        # Títulos similares
        similarity = calculate_similarity('Telefono movil', 'Telefono celular')
        assert 0.0 <= similarity <= 1.0
        
        # Títulos diferentes
        similarity = calculate_similarity('Telefono movil', 'Libro de cocina')
        assert similarity < 0.5
    
    def test_generate_pair_id(self):
        """Prueba la generación de IDs de pares"""
        # Debe ser consistente independientemente del orden
        pair_id1 = generate_pair_id(123, 456)
        pair_id2 = generate_pair_id(456, 123)
        
        assert pair_id1 == pair_id2
        assert pair_id1 == "123_456"
        
        # Con números diferentes
        pair_id3 = generate_pair_id(789, 101)
        assert pair_id3 == "101_789"

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 