class Product:
    def __init__(self, name: str, unit_price: float, category: str = ""):
        self.name = name
        self.unit_price = unit_price
        self.category = category


class OrderItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity


class Order:
    def __init__(self, items: list, original_amount: float, discount: float, total_amount: float):
        self.items = items
        self.original_amount = original_amount
        self.discount = discount
        self.total_amount = total_amount
