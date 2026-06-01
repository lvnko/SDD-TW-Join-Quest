from entities import Order, OrderItem


class OrderService:
    def __init__(self, promotions=None):
        self.promotions = promotions or []

    def checkout(self, items: list) -> Order:
        original_amount = sum(
            item.product.unit_price * item.quantity for item in items
        )
        discount = 0
        result_items = list(items)

        for promotion in self.promotions:
            discount, result_items = promotion.apply(result_items, original_amount, discount)

        total_amount = original_amount - discount
        return Order(result_items, original_amount, discount, total_amount)
