# فحص المنتج (محاكاة)
def check_product_compliance(product_data):
    name = product_data["name"]
    price = product_data["price"]

    # هنا تقدر تحط أي منطق تحقق حقيقي لاحقاً
    # دلوقتي نعتبر أي منتج أقل من 5000 "مطابق"
    if price <= 5000:
        return {"compliant": True, "reason": "السعر في النطاق المسموح ✅"}
    else:
        return {"compliant": False, "reason": "السعر مرتفع جداً ❌"}
