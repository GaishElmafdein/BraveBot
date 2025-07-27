import yaml
import os

# تحميل config.yaml من مجلد config
try:
    with open(os.path.join("config", "config.yaml"), "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    config = {
        "max_price": 10000,
        "min_price": 0.01,
        "admin_ids": [],
        "rate_limit": {"checks_per_hour": 50, "checks_per_day": 200}
    }

def check_product_compliance(product):
    """
    التحقق من توافق المنتج مع المعايير
    """
    price = product.get("price", 0)
    name = product.get("name", "").lower()

    # تحقق من السعر
    if price < config["min_price"] or price > config["max_price"]:
        return {
            "compliant": False,
            "reason": f"السعر خارج النطاق المسموح: {config['min_price']} - {config['max_price']}"
        }

    # تحقق من الكلمات المحظورة
    forbidden_keywords = ["fake", "counterfeit", "replica"]
    if any(keyword in name for keyword in forbidden_keywords):
        return {
            "compliant": False,
            "reason": "اسم المنتج يحتوي على كلمات محظورة."
        }

    # لو كل حاجة تمام
    return {
        "compliant": True,
        "reason": "المنتج مطابق للشروط."
    }
