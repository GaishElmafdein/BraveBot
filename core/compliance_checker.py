def check_product_compliance(product):
    """
    لو الوضع mock → بيرجع بيانات اختبارية
    لو الوضع live → يربط مع APIs الحقيقية
    """
    from config.config import config

    # وضع mock
    if config["mode"] == "mock":
        # دايمًا نرجع dict حتى لو نتيجة وهمية
        return {
            "compliant": True,
            "reason": "تمت الموافقة بشكل افتراضي (وضع mock)."
        }

    # وضع live (أكواد API هنا لو فعلتها لاحقًا)
    # مثال افتراضي لفحص حقيقي
    price = product.get("price", 0)
    if price > config["max_price"]:
        return {
            "compliant": False,
            "reason": "السعر أعلى من الحد المسموح."
        }

    return {
        "compliant": True,
        "reason": ""
    }
