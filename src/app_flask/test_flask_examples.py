import requests

API_URL = "http://localhost:5000/items/compare"

def create_sample_data():
    return [
        {"item_a": {"item_id": 1, "title": "Telefono Samsung Galaxy"}, "item_b": {"item_id": 2, "title": "Telefono celular Samsung Galaxy"}},
        {"item_a": {"item_id": 3, "title": "Laptop HP 15 pulgadas"}, "item_b": {"item_id": 4, "title": "Notebook HP 15 inch"}},
        {"item_a": {"item_id": 5, "title": "Auriculares bluetooth Sony"}, "item_b": {"item_id": 6, "title": "Audifonos bluetooth Sony"}},
        {"item_a": {"item_id": 7, "title": "Telefono Samsung Galaxy"}, "item_b": {"item_id": 8, "title": "Laptop HP 15 pulgadas"}},
        {"item_a": {"item_id": 9, "title": "Camara digital Canon"}, "item_b": {"item_id": 10, "title": "Camara fotografica Canon"}},
    ]

def main():
    ejemplos = create_sample_data()
    print("\n=== Ejemplos de comparación de ítems (Flask) ===\n")
    for i, pair in enumerate(ejemplos, 1):
        resp = requests.post(API_URL, json=pair)
        data = resp.json()
        print(f"Ejemplo {i}:")
        print(f"  A: {pair['item_a']['title']}")
        print(f"  B: {pair['item_b']['title']}")
        print(f"  Similarity: {data.get('similarity_score')}")
        print(f"  Are similar: {data.get('are_similar')}")
        print(f"  Are equal: {data.get('are_equal')}")
        print(f"  Status: {data.get('status')}")
        print(f"  Mensaje: {data.get('message')}")
        print()

if __name__ == "__main__":
    main() 