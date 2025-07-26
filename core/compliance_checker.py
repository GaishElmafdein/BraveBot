from core.database_manager import add_log

# قائمة بسياسات وهمية كبداية (هنحدثها لاحقاً)
BANNED_KEYWORDS = ["replica", "fake", "counterfeit"]
MIN_PRICE = 5.0  # أقل سعر مقبول
MAX_PRICE = 5000.0  # أعلى سعر مقبول

def check_product_compliance(product):
    """
    بيتأكد إن المنتج compliant:
    - ما فيهوش كلمات محظورة
    - سعره في النطاق
    """
    name = product.get("name", "").lower()
    price = product.get("price", 0.0)

    # فحص الكلمات المحظورة
    for word in BANNED_KEYWORDS:
        if word in name:
            add_log(f"Product '{product['name']}' flagged for banned keyword: {word}", "WARNING")
            return False

    # فحص السعر
    if not (MIN_PRICE <= price <= MAX_PRICE):
        add_log(f"Product '{product['name']}' flagged for price out of range: {price}", "WARNING")
        return False

    # لو compliant
    add_log(f"Product '{product['name']}' passed compliance check.", "INFO")
    return True
