from behave import given, when, then
from order_service import OrderService
from entities import Product, OrderItem
from promotions import ThresholdDiscount, BuyOneGetOnePromotion


@given('no promotions are applied')
def step_no_promotions(context):
    context.order_service = OrderService()


@given('the threshold discount promotion is configured:')
def step_threshold_discount(context):
    row = context.table[0]
    promotion = ThresholdDiscount(
        threshold=float(row['threshold']),
        discount_amount=float(row['discount']),
    )
    context.promotions.append(promotion)
    context.order_service = OrderService(promotions=context.promotions)


@given('the buy one get one promotion for cosmetics is active')
def step_bogo_cosmetics(context):
    context.promotions.append(BuyOneGetOnePromotion())
    context.order_service = OrderService(promotions=context.promotions)


@when('a customer places an order with:')
def step_place_order(context):
    items = []
    for row in context.table:
        category = row.get('category', '')
        product = Product(
            name=row['productName'],
            unit_price=float(row['unitPrice']),
            category=category,
        )
        item = OrderItem(product=product, quantity=int(row['quantity']))
        items.append(item)
    context.order = context.order_service.checkout(items)


@then('the order summary should be:')
def step_check_summary(context):
    row = context.table[0]
    if 'totalAmount' in row.headings:
        assert context.order.total_amount == float(row['totalAmount']), \
            f"Expected totalAmount={row['totalAmount']}, got {context.order.total_amount}"
    if 'originalAmount' in row.headings:
        assert context.order.original_amount == float(row['originalAmount']), \
            f"Expected originalAmount={row['originalAmount']}, got {context.order.original_amount}"
    if 'discount' in row.headings:
        assert context.order.discount == float(row['discount']), \
            f"Expected discount={row['discount']}, got {context.order.discount}"


@then('the customer should receive:')
def step_check_received(context):
    received = {item.product.name: item.quantity for item in context.order.items}
    for row in context.table:
        name = row['productName']
        expected_qty = int(row['quantity'])
        actual_qty = received.get(name, 0)
        assert actual_qty == expected_qty, \
            f"Expected {name} quantity={expected_qty}, got {actual_qty}"
