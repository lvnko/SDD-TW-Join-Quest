from entities import OrderItem


class DoubleElevenDiscount:
    def apply(self, items: list, original_amount: float, current_discount: float):
        added_discount = 0.0
        for item in items:
            complete_groups = item.quantity // 10
            added_discount += complete_groups * 10 * item.product.unit_price * 0.2
        return current_discount + added_discount, items


class ThresholdDiscount:
    def __init__(self, threshold: float, discount_amount: float):
        self.threshold = threshold
        self.discount_amount = discount_amount

    def apply(self, items: list, original_amount: float, current_discount: float):
        if original_amount >= self.threshold:
            return current_discount + self.discount_amount, items
        return current_discount, items


class BuyOneGetOnePromotion:
    def apply(self, items: list, original_amount: float, current_discount: float):
        new_items = []
        for item in items:
            if item.product.category == 'cosmetics':
                new_items.append(OrderItem(product=item.product, quantity=item.quantity + 1))
            else:
                new_items.append(item)
        return current_discount, new_items
