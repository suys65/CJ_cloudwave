import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "ecommerce_sales.csv"

categories = ["전자기기", "도서", "패션", "생활용품", "식품", "스포츠"]
regions = ["서울", "경기", "부산", "대구", "광주", "대전", "인천"]
channels = ["web", "mobile", "store"]
payment_methods = ["card", "bank_transfer", "point", "coupon"]

start_date = date(2026, 1, 1)
days = 90

random.seed(42)

with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "order_id",
        "order_date",
        "customer_id",
        "region",
        "category",
        "product_name",
        "channel",
        "quantity",
        "unit_price",
        "discount_amount",
        "payment_method",
        "is_returned"
    ])

    order_no = 1

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        daily_orders = random.randint(20, 45)

        for _ in range(daily_orders):
            category = random.choice(categories)

            if category == "전자기기":
                product = random.choice(["무선이어폰", "키보드", "마우스", "모니터", "USB허브"])
                price = random.choice([25000, 45000, 79000, 150000, 320000])
            elif category == "도서":
                product = random.choice(["클라우드입문", "파이썬기초", "보안개론", "네트워크실습"])
                price = random.choice([15000, 22000, 28000, 35000])
            elif category == "패션":
                product = random.choice(["티셔츠", "운동화", "자켓", "가방"])
                price = random.choice([19000, 49000, 89000, 129000])
            elif category == "생활용품":
                product = random.choice(["수납박스", "텀블러", "책상조명", "청소도구"])
                price = random.choice([9000, 15000, 23000, 37000])
            elif category == "식품":
                product = random.choice(["커피", "간편식", "견과류", "비타민음료"])
                price = random.choice([6000, 11000, 18000, 26000])
            else:
                product = random.choice(["요가매트", "덤벨", "운동밴드", "러닝벨트"])
                price = random.choice([12000, 24000, 39000, 59000])

            quantity = random.randint(1, 5)
            discount = random.choice([0, 0, 0, 1000, 2000, 5000])
            is_returned = random.choice([False, False, False, False, True])

            writer.writerow([
                f"ORD-{order_no:06d}",
                current_date.isoformat(),
                f"CUST-{random.randint(1, 500):04d}",
                random.choice(regions),
                category,
                product,
                random.choice(channels),
                quantity,
                price,
                discount,
                random.choice(payment_methods),
                str(is_returned).lower()
            ])

            order_no += 1

print(f"샘플 데이터 생성 완료: {OUTPUT_FILE}")
