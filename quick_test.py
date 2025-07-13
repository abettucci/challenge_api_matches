#!/usr/bin/env python3
"""
Script de prueba rápida para el API
"""

import requests
import json

def test_api():
    """Prueba rápida del API"""
    base_url = "https://cjlqfw7vq4.execute-api.us-east-1.amazonaws.com/prod"
    
    print("🚀 Prueba Rápida del API")
    print("="*40)
    
    # 1. Health Check
    print("1️⃣ Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API funcionando")
            print(f"   Status: {health.get('status')}")
            print(f"   DynamoDB: {health.get('dynamodb_status')}")
            print(f"   Método: {health.get('similarity_method')}")
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return
    
    # 2. Comparar ítems similares
    print("\n2️⃣ Comparando ítems similares...")
    similar_items = {
        "item_a": {"item_id": 1, "title": "Telefono Samsung Galaxy"},
        "item_b": {"item_id": 2, "title": "Telefono celular Samsung Galaxy"}
    }
    
    try:
        response = requests.post(f"{base_url}/items/compare", json=similar_items)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Comparación exitosa")
            print(f"   Similitud: {result.get('similarity_score', 0):.3f}")
            print(f"   Son similares: {result.get('are_similar')}")
            print(f"   Son iguales: {result.get('are_equal')}")
        else:
            print(f"❌ Comparación falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en comparación: {e}")
    
    # 3. Comparar ítems diferentes
    print("\n3️⃣ Comparando ítems diferentes...")
    different_items = {
        "item_a": {"item_id": 3, "title": "Telefono Samsung Galaxy"},
        "item_b": {"item_id": 4, "title": "Laptop HP 15 pulgadas"}
    }
    
    try:
        response = requests.post(f"{base_url}/items/compare", json=different_items)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Comparación exitosa")
            print(f"   Similitud: {result.get('similarity_score', 0):.3f}")
            print(f"   Son similares: {result.get('are_similar')}")
            print(f"   Son iguales: {result.get('are_equal')}")
        else:
            print(f"❌ Comparación falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en comparación: {e}")
    
    # 4. Crear un par
    print("\n4️⃣ Creando un par de ítems...")
    new_pair = {
        "item_a": {"item_id": 5, "title": "Auriculares bluetooth Sony"},
        "item_b": {"item_id": 6, "title": "Audifonos bluetooth Sony"}
    }
    
    try:
        response = requests.post(f"{base_url}/items/pairs", json=new_pair)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Par creado exitosamente")
            print(f"   Pair ID: {result.get('pair_id')}")
            print(f"   Similitud: {result.get('similarity_score', 0):.3f}")
            print(f"   Son similares: {result.get('are_similar')}")
        else:
            print(f"❌ Creación falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creando par: {e}")
    
    # 5. Obtener todos los pares
    print("\n5️⃣ Obteniendo todos los pares...")
    try:
        response = requests.get(f"{base_url}/items/pairs")
        if response.status_code == 200:
            result = response.json()
            pairs = result.get('pairs', [])
            print(f"✅ Pares obtenidos: {len(pairs)}")
            if pairs:
                print("   Últimos pares:")
                for pair in pairs[-3:]:  # Mostrar solo los últimos 3
                    print(f"   • {pair.get('pair_id')}: {pair.get('item_a_title')} vs {pair.get('item_b_title')}")
            else:
                print("   No hay pares en la base de datos")
        else:
            print(f"❌ Obtención falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo pares: {e}")
    
    print("\n🎉 Prueba rápida completada!")

if __name__ == "__main__":
    test_api() 