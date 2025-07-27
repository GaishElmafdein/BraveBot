from core.database_manager import add_log

# الكلمات المحظورة
BANNED_KEYWORDS = ["replica", "fake", "counterfeit"]

# الحد الأدنى والأقصى للسعر
MIN_PRICE = 5.0
MAX_PRICE = 5000.0

def check_product_compliance(product: dict) -> bool:
    """
    دالة لفحص المنتج والتأكد من مطابقته للشروط
    """
    is_compliant = True

    # التحقق من الكلمات المحظورة
    name = product.get("name", "").lower()
    price = product.get("price", 0.0)

    for word in BANNED_KEYWORDS:
        if word in name:
            add_log(f"Product '{product['name']}' flagged for banned keyword: {word}")
            is_compliant = False

    # التحقق من السعر
    if not (MIN_PRICE <= price <= MAX_PRICE):
        add_log(f"Product '{product['name']}' flagged for price out of range: {price}")
        is_compliant = False

    # لو المنتج مطابق
    if is_compliant:
        add_log(f"Product '{product['name']}' passed compliance check")

    return is_compliant
