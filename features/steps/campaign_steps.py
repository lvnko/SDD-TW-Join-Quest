from behave import given, when, then
from order_service import OrderService
from entities import Product, OrderItem
from promotions import DoubleElevenDiscount


@given('雙十一優惠活動已啟動')
def step_double_eleven_active(context):
    context.order_service = OrderService(promotions=[DoubleElevenDiscount()])


@when('顧客下訂單，內含以下商品')
def step_place_order_zh(context):
    items = []
    for row in context.table:
        product = Product(
            name=row['商品名稱'],
            unit_price=float(row['單價']),
        )
        item = OrderItem(product=product, quantity=int(row['數量']))
        items.append(item)
    context.order = context.order_service.checkout(items)


@then('訂單總金額應為 {amount:d}')
def step_check_total_zh(context, amount):
    assert context.order.total_amount == float(amount), \
        f"Expected totalAmount={amount}, got {context.order.total_amount}"
