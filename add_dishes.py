from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.stolovaya
dishes_collection = db.dishes

def add_dish():
    dish_type = input("Введите тип блюда: ")
    while True:
        name = input("Введите название блюда (или 'exit' для выхода): ")
        if name.lower() == 'exit':
            break
        price = int(input("Введите цену блюда: "))
        dish = {
            'name': name,
            'type': dish_type,
            'price': price
        }
        dishes_collection.insert_one(dish)
        print(f"Блюдо {name} добавлено в базу данных.")

def list_dishes():
    dish_type = input("Введите тип блюда для вывода списка: ")
    dishes = dishes_collection.find({'type': dish_type})
    for dish in dishes:
        print(f"Название: {dish['name']}, Цена: {dish['price']}")

def add_bulk_dishes():
    dish_type = input("Введите тип блюда: ")
    bulk_input = input("Введите блюда и цены в формате 'Название блюда\\nЦена\\n': ")
    lines = bulk_input.split('\n')
    for i in range(0, len(lines), 3):
        name = lines[i].strip()
        if not name:
            continue
        price = int(lines[i + 1].strip())
        dish = {
            'name': name,
            'type': dish_type,
            'price': price
        }
        dishes_collection.insert_one(dish)
        print(f"Блюдо {name} добавлено в базу данных.")

if __name__ == "__main__":
    while True:
        action = input("Введите 'add' для добавления блюда, 'list' для вывода списка блюд, 'bulk' для массового добавления блюд (или 'exit' для выхода): ")
        if action.lower() == 'add':
            add_dish()
        elif action.lower() == 'list':
            list_dishes()
        elif action.lower() == 'bulk':
            add_bulk_dishes()
        elif action.lower() == 'exit':
            break
