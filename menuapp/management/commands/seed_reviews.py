import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from menuapp.models import MenuItem
from restaurants.models import Restaurant
from reviews.models import Review


DEMO_USERS = [
    ("demo_aylin", "Aylin K.", "aylin.demo@example.com"),
    ("demo_mert", "Mert A.", "mert.demo@example.com"),
    ("demo_zeynep", "Zeynep T.", "zeynep.demo@example.com"),
    ("demo_can", "Can B.", "can.demo@example.com"),
    ("demo_deniz", "Deniz S.", "deniz.demo@example.com"),
    ("demo_eda", "Eda Y.", "eda.demo@example.com"),
    ("demo_burak", "Burak N.", "burak.demo@example.com"),
    ("demo_selin", "Selin D.", "selin.demo@example.com"),
    ("demo_kaan", "Kaan R.", "kaan.demo@example.com"),
    ("demo_naz", "Naz C.", "naz.demo@example.com"),
    ("demo_emir", "Emir P.", "emir.demo@example.com"),
    ("demo_melis", "Melis G.", "melis.demo@example.com"),
    ("demo_arda", "Arda F.", "arda.demo@example.com"),
    ("demo_yagmur", "Yağmur E.", "yagmur.demo@example.com"),
    ("demo_kerem", "Kerem O.", "kerem.demo@example.com"),
    ("demo_lara", "Lara M.", "lara.demo@example.com"),
    ("demo_onur", "Onur V.", "onur.demo@example.com"),
    ("demo_asli", "Aslı H.", "asli.demo@example.com"),
    ("demo_efe", "Efe L.", "efe.demo@example.com"),
    ("demo_duru", "Duru I.", "duru.demo@example.com"),
    ("demo_tolga", "Tolga U.", "tolga.demo@example.com"),
    ("demo_mina", "Mina Ş.", "mina.demo@example.com"),
]


COMMENT_POOL = {
    5: [
        "Gerçekten beklediğimden iyiydi. Servis hızlı, ürün sıcak ve lezzetli geldi.",
        "Bir otel menüsü için şaşırtıcı derecede özenli. Tekrar söylerim.",
        "Lezzet çok dengeliydi, porsiyon da gayet tatmin edici.",
        "Sunum güzel, tadı daha güzel. Masada herkes çatal uzattı.",
        "Kısa yorum: efsane. Uzun yorum: gerçekten efsane.",
        "Kahve/yiyecek kalitesi stabil, bu benim için büyük artı.",
        "Tatilde kalori saymayı bıraktıran ürünlerden. Pişman değilim.",
    ],
    4: [
        "Gayet başarılıydı. Bir tık daha sıcak gelse 5 verirdim.",
        "Lezzet iyi, servis de hızlıydı. Fiyat biraz yüksek ama mekan standardına göre normal.",
        "Beklentimi karşıladı. Sosu özellikle güzeldi.",
        "Güzel ürün, sadece porsiyon biraz daha büyük olabilir.",
        "Fotoğraftakine yakın geldi, bu bile başlı başına başarı.",
        "Genel olarak memnun kaldım, tekrar denenir.",
    ],
    3: [
        "Fena değil ama akılda kalıcı da değildi. Ortalama bir deneyim.",
        "Lezzet iyi başladı ama sonlara doğru biraz ağır geldi.",
        "Ne kötü ne mükemmel. Açken mutlu eder, tokken düşündürür.",
        "Servis hızlıydı ama tat biraz daha güçlü olabilirdi.",
        "Benim damak tadıma tam uymadı, yine de kötü diyemem.",
    ],
    2: [
        "Malzemeler taze gibiydi ama lezzet beklentimin altında kaldı.",
        "Biraz kuru geldi. Yanındaki sos olmasa zorlanırdım.",
        "Fiyatına göre daha iyi olmasını beklerdim.",
        "Bugün mutfak biraz formsuzdu sanırım. Olur öyle.",
    ],
    1: [
        "Benim için olmadı. Belki yanlış seçim yaptım ama tekrar sipariş etmem.",
        "Çok bekledim ve geldiğinde de beklediğime değmedi.",
        "Lezzet bana hitap etmedi. Masadaki arkadaşım sevdi, ben sevemedim.",
    ],
}


RESTAURANT_REVIEW_TARGETS = {
    "The Grand Atrium Restaurant": 38,
    "Azure Beach Bar": 18,
    "Luna Lobby Cafe": 16,
}


class Command(BaseCommand):
    help = "Seeds demo customer accounts and natural-looking restaurant reviews."

    def handle(self, *args, **kwargs):
        random.seed(42)
        User = get_user_model()

        display_names = [display_name for _, display_name, _ in DEMO_USERS]
        Review.objects.filter(customer_name__in=display_names).delete()

        for username, display_name, email in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": display_name.split()[0],
                    "role": "CUSTOMER",
                },
            )

            if created:
                user.set_password("DemoPass123!")
                user.save()
            elif user.role != "CUSTOMER":
                user.role = "CUSTOMER"
                user.save(update_fields=["role"])

        created_reviews = 0

        for restaurant_name, target_count in RESTAURANT_REVIEW_TARGETS.items():
            restaurant = Restaurant.objects.filter(name=restaurant_name).first()

            if not restaurant:
                self.stdout.write(self.style.WARNING(f"Restaurant not found: {restaurant_name}"))
                continue

            items = list(
                MenuItem.objects.filter(
                    restaurant=restaurant,
                    is_available=True,
                ).select_related("category")
            )

            if not items:
                self.stdout.write(self.style.WARNING(f"No items found for: {restaurant_name}"))
                continue

            for _ in range(target_count):
                username, display_name, _ = random.choice(DEMO_USERS)
                rating = random.choices(
                    population=[1, 2, 3, 4, 5],
                    weights=[4, 8, 18, 34, 36],
                    k=1,
                )[0]
                item = random.choice(items)
                comment = random.choice(COMMENT_POOL[rating])

                if random.random() < 0.35:
                    comment = f"{item.title} için yazıyorum: {comment}"

                review = Review.objects.create(
                    restaurant=restaurant,
                    menu_item=item if random.random() < 0.85 else None,
                    customer_name=display_name,
                    rating=rating,
                    comment=comment,
                )
                review.created_at = timezone.now() - timedelta(
                    days=random.randint(0, 75),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )
                review.save(update_fields=["created_at"])
                created_reviews += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(DEMO_USERS)} demo accounts and {created_reviews} reviews."
            )
        )
