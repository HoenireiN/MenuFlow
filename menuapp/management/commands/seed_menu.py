from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from restaurants.models import Restaurant
from menuapp.models import Allergen, Category, Ingredient, MenuItem


ALLERGEN_NAMES = [
    "Gluten", "Dairy", "Nuts", "Peanuts", "Soy", "Egg", "Seafood",
    "Shellfish", "Sesame", "Mustard", "Celery", "Sulphites", "Vegan",
    "Vegetarian", "Halal", "Spicy", "Extra Spicy", "Sugar Free",
    "Lactose Free", "Keto Friendly", "High Protein",
]


CATEGORY_IMAGE = "default.webp"


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


IMAGE_NAME_OVERRIDES = {
    "Kavaklıdere Yakut Glass": "red",
    "Kavaklıdere Cankaya Glass": "white",
    "Kayra Rose Glass": "rose",
    "Doluca Cabernet Sauvignon Bottle": "cabernet_bottle",
    "Suvla Sauvignon Blanc Bottle": "sauvignon_blanc_bottle",
    "Prosecco Valdobbiadene Bottle": "prosecco_bottle",
    "Kayra Shiraz Glass": "shiraz_glass",
}


INGREDIENTS = {
    "Sourdough Bread": "Ekşi maya ekmek",
    "Egg": "Yumurta",
    "Butter": "Tereyağı",
    "Avocado": "Avokado",
    "Tomato": "Domates",
    "Feta Cheese": "Beyaz peynir",
    "Cheddar Cheese": "Cheddar peyniri",
    "Mozzarella": "Mozzarella",
    "Beef Patty": "Dana köfte",
    "Beef Tenderloin": "Dana bonfile",
    "Chicken": "Tavuk",
    "Salmon": "Somon",
    "Shrimp": "Karides",
    "Tuna": "Ton balığı",
    "Pasta": "Makarna",
    "Pizza Dough": "Pizza hamuru",
    "Tomato Sauce": "Domates sosu",
    "Basil": "Fesleğen",
    "Parmesan": "Parmesan",
    "Lettuce": "Marul",
    "Rocket": "Roka",
    "Quinoa": "Kinoa",
    "Rice": "Pirinç",
    "Noodles": "Noodle",
    "Soy Sauce": "Soya sosu",
    "Sesame": "Susam",
    "Tortilla": "Tortilla",
    "Guacamole": "Guacamole",
    "Jalapeno": "Jalapeno",
    "Chocolate": "Çikolata",
    "Cream": "Krema",
    "Coffee": "Kahve",
    "Milk": "Süt",
    "Lemon": "Limon",
    "Mint": "Nane",
    "Ice": "Buz",
    "Berries": "Orman meyveleri",
    "Brioche Bun": "Brioche ekmeği",
    "Pickles": "Turşu",
    "Special Sauce": "Özel sos",
}


MENU = [
    {
        "name_en": "Breakfast",
        "name_tr": "Kahvaltı",
        "description_en": "All-day brunch plates, eggs, toasts and fresh morning bowls.",
        "description_tr": "Gün boyu servis edilen brunch tabakları, yumurtalar, tostlar ve taze kaseler.",
        "items": [
            ("Serpme Kahvaltı", "Turkish Breakfast Spread", 1850), ("Menemen", "Menemen", 420),
            ("Avokado Tost", "Avocado Toast", 580), ("Pancake Kulesi", "Pancake Stack", 540),
            ("Kruvasan Sandviç", "Croissant Sandwich", 520), ("Eggs Benedict", "Eggs Benedict", 690),
            ("Granola Kasesi", "Granola Bowl", 430), ("French Toast", "French Toast", 560),
            ("Bagel Tabağı", "Bagel Plate", 620), ("Protein Kahvaltı", "Protein Breakfast", 720),
        ],
    },
    {
        "name_en": "Bakery & Pastries",
        "name_tr": "Fırın & Kruvasan",
        "description_en": "Fresh bakery signatures, croissants and sweet pastry classics.",
        "description_tr": "Taze fırın lezzetleri, kruvasanlar ve tatlı pastane klasikleri.",
        "items": [
            ("Tereyağlı Kruvasan", "Butter Croissant", 260), ("Bademli Kruvasan", "Almond Croissant", 340),
            ("Çikolatalı Kruvasan", "Chocolate Croissant", 320), ("Peynirli Poğaça", "Cheese Pogaca", 190),
            ("Zeytinli Açma", "Olive Achma", 210), ("Tarçınlı Roll", "Cinnamon Roll", 310),
            ("Mini Danish Tabağı", "Mini Danish Plate", 390), ("Muzlu Fit Muffin", "Banana Fit Muffin", 280),
        ],
    },
    {
        "name_en": "Starters & Appetizers",
        "name_tr": "Başlangıçlar",
        "description_en": "Shareable starters, crispy bites and gastro pub favorites.",
        "description_tr": "Paylaşımlık başlangıçlar, çıtır atıştırmalıklar ve gastro pub favorileri.",
        "items": [
            ("Trüflü Patates", "Truffle Fries", 480), ("Çıtır Tavuk Sepeti", "Crispy Chicken Basket", 690),
            ("Mozzarella Sticks", "Mozzarella Sticks", 520), ("Nachos Supreme", "Nachos Supreme", 720),
            ("Humus & Pita", "Hummus & Pita", 420), ("Buffalo Wings", "Buffalo Wings", 740),
            ("Mini Taco Trio", "Mini Taco Trio", 690), ("Kalamar Tava", "Fried Calamari", 850),
        ],
    },
    {
        "name_en": "Salads",
        "name_tr": "Salatalar",
        "description_en": "Fresh, filling bowls with premium greens, grains and proteins.",
        "description_tr": "Premium yeşillikler, tahıllar ve proteinlerle doyurucu taze kaseler.",
        "items": [
            ("Sezar Salata", "Caesar Salad", 540), ("Izgara Tavuklu Sezar", "Grilled Chicken Caesar", 720),
            ("Avokadolu Kinoa Salata", "Avocado Quinoa Salad", 760), ("Somonlu Roka Salata", "Salmon Rocket Salad", 1050),
            ("Burrata Salata", "Burrata Salad", 890), ("Vegan Bowl", "Vegan Bowl", 690),
            ("Protein Bowl", "Protein Bowl", 850), ("Akdeniz Salata", "Mediterranean Salad", 590),
        ],
    },
    {
        "name_en": "Burgers",
        "name_tr": "Burgerler",
        "description_en": "Juicy brioche burgers with premium sauces and loaded sides.",
        "description_tr": "Brioche ekmekte premium soslar ve doyurucu yan lezzetlerle burgerler.",
        "items": [
            ("Smash Burger", "Smash Burger", 690), ("Double Bacon Burger", "Double Bacon Burger", 850),
            ("BBQ Cowboy Burger", "BBQ Cowboy Burger", 790), ("Trüf Burger", "Truffle Burger", 940),
            ("Classic Cheeseburger", "Classic Cheeseburger", 650), ("Volcano Burger", "Volcano Burger", 760),
            ("Mushroom Swiss Burger", "Mushroom Swiss Burger", 780), ("Crispy Chicken Burger", "Crispy Chicken Burger", 670),
            ("Avocado Ranch Burger", "Avocado Ranch Burger", 820), ("Monster Burger", "Monster Burger", 980),
        ],
    },
    {
        "name_en": "Pastas",
        "name_tr": "Makarnalar",
        "description_en": "Creamy, tomato and seafood pastas with Italian cafe character.",
        "description_tr": "İtalyan cafe karakterinde kremalı, domatesli ve deniz mahsullü makarnalar.",
        "items": [
            ("Alfredo", "Alfredo", 620), ("Carbonara", "Carbonara", 690),
            ("Spaghetti Bolognese", "Spaghetti Bolognese", 720), ("Pesto Chicken Pasta", "Pesto Chicken Pasta", 760),
            ("Mac and Cheese", "Mac and Cheese", 590), ("Seafood Linguine", "Seafood Linguine", 1150),
            ("Lasagna", "Lasagna", 790), ("Arrabbiata", "Arrabbiata", 580),
            ("Truffle Alfredo", "Truffle Alfredo", 890),
        ],
    },
    {
        "name_en": "Pizzas",
        "name_tr": "Pizzalar",
        "description_en": "Stone-baked pizzas with classic and modern gastro toppings.",
        "description_tr": "Klasik ve modern gastro malzemelerle taş fırın pizzalar.",
        "items": [
            ("Margherita", "Margherita", 650), ("Pepperoni", "Pepperoni", 780),
            ("Four Cheese", "Four Cheese", 820), ("BBQ Chicken Pizza", "BBQ Chicken Pizza", 850),
            ("Mexican Pizza", "Mexican Pizza", 820), ("Truffle Pizza", "Truffle Pizza", 980),
            ("Veggie Pizza", "Veggie Pizza", 690), ("Meat Lovers Pizza", "Meat Lovers Pizza", 1050),
        ],
    },
    {
        "name_en": "Mexican Cuisine",
        "name_tr": "Meksika Mutfağı",
        "description_en": "Spicy, colorful Mexican plates with tortillas, rice bowls and guacamole.",
        "description_tr": "Tortilla, bowl ve guacamole dokunuşlu renkli ve baharatlı Meksika lezzetleri.",
        "items": [
            ("Chicken Quesadilla", "Chicken Quesadilla", 760), ("Beef Burrito", "Beef Burrito", 840),
            ("Nachos Supreme Mex", "Mexican Nachos Supreme", 790), ("Tacos Al Pastor", "Tacos Al Pastor", 820),
            ("Loaded Fajitas", "Loaded Fajitas", 1250), ("Chili Con Carne", "Chili Con Carne", 790),
            ("Guacamole Bowl", "Guacamole Bowl", 690), ("Mexican Rice Bowl", "Mexican Rice Bowl", 760),
        ],
    },
    {
        "name_en": "Asian Cuisine",
        "name_tr": "Asya Mutfağı",
        "description_en": "Noodles, bowls, sushi and crispy Asian comfort plates.",
        "description_tr": "Noodle, bowl, sushi ve çıtır Asya comfort tabakları.",
        "items": [
            ("Chicken Teriyaki Bowl", "Chicken Teriyaki Bowl", 820), ("Beef Noodles", "Beef Noodles", 890),
            ("Sushi Platter", "Sushi Platter", 1450), ("Ramen", "Ramen", 850),
            ("Dumplings", "Dumplings", 620), ("Sweet Chili Chicken", "Sweet Chili Chicken", 790),
            ("Pad Thai", "Pad Thai", 880), ("Korean Fried Chicken", "Korean Fried Chicken", 840),
            ("Fried Rice Bowl", "Fried Rice Bowl", 690),
        ],
    },
    {
        "name_en": "Steaks & Grill",
        "name_tr": "Steak & Izgara",
        "description_en": "Premium grilled meats, steaks and high-protein signature plates.",
        "description_tr": "Premium ızgara etler, steakler ve yüksek proteinli imza tabaklar.",
        "items": [
            ("Lokum Bonfile", "Tenderloin Steak", 2450), ("Ribeye Steak", "Ribeye Steak", 2850),
            ("New York Steak", "New York Steak", 2700), ("Izgara Köfte", "Grilled Meatballs", 880),
            ("Tavuk Şiş", "Chicken Skewers", 760), ("Kuzu Pirzola", "Lamb Chops", 2250),
            ("Antrikot Burger Plate", "Entrecote Burger Plate", 1350), ("Mixed Grill", "Mixed Grill", 3200),
        ],
    },
    {
        "name_en": "Seafood",
        "name_tr": "Deniz Ürünleri",
        "description_en": "Fresh seafood plates, salmon, shrimp and coastal cafe classics.",
        "description_tr": "Taze deniz ürünleri, somon, karides ve sahil cafe klasikleri.",
        "items": [
            ("Izgara Somon", "Grilled Salmon", 1350), ("Karides Güveç", "Shrimp Casserole", 1250),
            ("Fish & Chips", "Fish & Chips", 950), ("Levrek Izgara", "Grilled Sea Bass", 1650),
            ("Deniz Mahsullü Risotto", "Seafood Risotto", 1280), ("Somon Teriyaki", "Salmon Teriyaki", 1450),
            ("Tuna Steak", "Tuna Steak", 1750), ("Seafood Tacos", "Seafood Tacos", 980),
        ],
    },
    {
        "name_en": "Main Courses",
        "name_tr": "Ana Yemekler",
        "description_en": "Cafe restaurant favorites with satisfying plates and balanced sides.",
        "description_tr": "Doyurucu tabaklar ve dengeli garnitürlerle cafe restoran favorileri.",
        "items": [
            ("Chicken Schnitzel", "Chicken Schnitzel", 790), ("Cafe de Paris Chicken", "Cafe de Paris Chicken", 890),
            ("Beef Stroganoff", "Beef Stroganoff", 1450), ("Thai Curry Chicken", "Thai Curry Chicken", 850),
            ("Mushroom Risotto", "Mushroom Risotto", 760), ("Chicken Fajita Plate", "Chicken Fajita Plate", 980),
            ("Mediterranean Chicken", "Mediterranean Chicken", 860), ("Vegan Curry Bowl", "Vegan Curry Bowl", 740),
        ],
    },
    {
        "name_en": "Desserts",
        "name_tr": "Tatlılar",
        "description_en": "House desserts, cakes and indulgent cafe classics.",
        "description_tr": "Ev yapımı tatlılar, pastalar ve zengin cafe klasikleri.",
        "items": [
            ("Brownie", "Brownie", 390), ("San Sebastian Cheesecake", "San Sebastian Cheesecake", 520),
            ("Tiramisu", "Tiramisu", 460), ("Chocolate Lava Cake", "Chocolate Lava Cake", 540),
            ("Lotus Cheesecake", "Lotus Cheesecake", 520), ("Apple Crumble", "Apple Crumble", 430),
            ("Waffle", "Waffle", 580), ("Profiterole", "Profiterole", 450),
        ],
    },
    {
        "name_en": "Hot Drinks",
        "name_tr": "Sıcak İçecekler",
        "description_en": "Specialty coffee, tea and warm signature drinks.",
        "description_tr": "Nitelikli kahveler, çaylar ve sıcak imza içecekler.",
        "items": [
            ("Espresso", "Espresso", 160), ("Americano", "Americano", 180), ("Cappuccino", "Cappuccino", 220),
            ("Latte", "Latte", 230), ("Flat White", "Flat White", 240), ("Mocha", "Mocha", 260),
            ("Turkish Coffee", "Turkish Coffee", 180), ("Hot Chocolate", "Hot Chocolate", 280),
        ],
    },
    {
        "name_en": "Soft Drinks",
        "name_tr": "Soğuk İçecekler",
        "description_en": "Refreshing sodas, lemonades and iced coffee classics.",
        "description_tr": "Ferahlatıcı gazlı içecekler, limonatalar ve soğuk kahve klasikleri.",
        "items": [
            ("Coca Cola", "Coca Cola", 150), ("Sprite", "Sprite", 150), ("Fanta", "Fanta", 150),
            ("Homemade Lemonade", "Homemade Lemonade", 240), ("Berry Iced Tea", "Berry Iced Tea", 250),
            ("Iced Latte", "Iced Latte", 270), ("Cold Brew", "Cold Brew", 260), ("Ayran", "Ayran", 120),
            ("Su", "Water", 80),
        ],
    },
    {
        "name_en": "Mocktails",
        "name_tr": "Alkolsüz Kokteyller",
        "description_en": "Alcohol-free signature mixes with fresh fruit, herbs and ice.",
        "description_tr": "Taze meyve, otlar ve buzla hazırlanan alkolsüz imza karışımlar.",
        "items": [
            ("Virgin Mojito", "Virgin Mojito", 340), ("Berry Cooler", "Berry Cooler", 380),
            ("Passion Spritz", "Passion Spritz", 390), ("Cucember Mint Fizz", "Cucember Mint Fizz", 330),
            ("Tropical Punch", "Tropical Punch", 380), ("Apple Ginger Mule", "Apple Ginger Mule", 360),
            ("Mango Iced Tea", "Mango Iced Tea", 320), ("Strawberry Basil Lemonade", "Strawberry Basil Lemonade", 390),
        ],
    },
    {
        "name_en": "Cocktails",
        "name_tr": "Kokteyller",
        "description_en": "Modern bar classics and signature evening cocktails.",
        "description_tr": "Modern bar klasikleri ve akşam imza kokteylleri.",
        "items": [
            ("Mojito", "Mojito", 560), ("Margarita", "Margarita", 620), ("Whiskey Sour", "Whiskey Sour", 650),
            ("Negroni", "Negroni", 680), ("Espresso Martini", "Espresso Martini", 720),
            ("Long Island", "Long Island", 760), ("Piña Colada", "Piña Colada", 640), ("Old Fashioned", "Old Fashioned", 740),
        ],
    },
    {
        "name_en": "Beers",
        "name_tr": "Biralar",
        "description_en": "Local and imported bottles for relaxed cafe evenings.",
        "description_tr": "Keyifli cafe akşamları için yerli ve ithal şişeler.",
        "items": [
            ("Efes Pilsen", "Efes Pilsen", 320), ("Bomonti Filtresiz", "Bomonti Filtresiz", 350),
            ("Miller", "Miller", 390), ("Corona", "Corona", 450), ("Heineken", "Heineken", 430),
            ("Guinness", "Guinness", 520), ("Craft IPA", "Craft IPA", 490),
        ],
    },
    {
        "name_en": "Wines",
        "name_tr": "Şaraplar",
        "description_en": "Selected red, white and rose wines by the glass or bottle.",
        "description_tr": "Kadeh veya şişe seçkin kırmızı, beyaz ve roze şaraplar.",
        "items": [
            ("Kavaklıdere Yakut Kadeh", "Kavaklıdere Yakut Glass", 460),
            ("Kavaklıdere Çankaya Kadeh", "Kavaklıdere Cankaya Glass", 460),
            ("Kayra Rosé Kadeh", "Kayra Rose Glass", 480),
            ("Doluca Cabernet Sauvignon Şişe", "Doluca Cabernet Sauvignon Bottle", 3200),
            ("Suvla Sauvignon Blanc Şişe", "Suvla Sauvignon Blanc Bottle", 2950),
            ("Prosecco Valdobbiadene Şişe", "Prosecco Valdobbiadene Bottle", 3800),
            ("Kayra Shiraz Kadeh", "Kayra Shiraz Glass", 520),
        ],
    },
]


VENUE_MENUS = [
    {
        "name": "Azure Beach Bar",
        "name_tr": "Azure Plaj Barı",
        "name_en": "Azure Beach Bar",
        "venue_type": "beach_club",
        "description_tr": "Gün batımı kokteylleri, hafif plaj tabakları ve havuz kenarı servis.",
        "description_en": "Sunset cocktails, light beach plates and poolside service.",
        "opening_hours": "10:00 - 01:00",
        "table_count": 65,
        "categories": [
            {
                "name_en": "Beach Plates",
                "name_tr": "Plaj Tabakları",
                "description_en": "Fresh, easy plates for pool and beach dining.",
                "description_tr": "Havuz ve plaj için taze, pratik tabaklar.",
                "items": [
                    ("Watermelon Feta Salad", "Karpuz Beyaz Peynir Salatası", 520, ["Vegetarian"], ["Watermelon", "Feta Cheese", "Mint"]),
                    ("Shrimp Tacos", "Karides Taco", 920, ["Shellfish", "Spicy"], ["Shrimp", "Tortilla", "Guacamole"]),
                    ("Beach Club Sandwich", "Beach Club Sandviç", 690, ["Gluten", "Egg"], ["Sourdough Bread", "Chicken", "Lettuce"]),
                    ("Poke Bowl", "Poke Bowl", 880, ["Seafood", "Soy"], ["Tuna", "Rice", "Sesame"]),
                ],
            },
            {
                "name_en": "Signature Cocktails",
                "name_tr": "İmza Kokteyller",
                "description_en": "Refreshing cocktails designed for long summer evenings.",
                "description_tr": "Uzun yaz akşamları için ferah imza kokteyller.",
                "items": [
                    ("Azure Spritz", "Azure Spritz", 640, ["Vegan"], ["Prosecco", "Citrus", "Ice"]),
                    ("Passion Mojito", "Passion Mojito", 590, ["Vegan"], ["Mint", "Lime", "Ice"]),
                    ("Frozen Margarita", "Frozen Margarita", 620, ["Vegan"], ["Lime", "Ice", "Salt"]),
                ],
            },
            {
                "name_en": "Alcoholic Drinks",
                "name_tr": "Alkollü İçecekler",
                "description_en": "Beach-ready beers, wines and long drinks served chilled.",
                "description_tr": "Plaja uygun soğuk bira, şarap ve long drink seçenekleri.",
                "items": [
                    ("Corona Extra", "Corona Extra", 420, ["Gluten", "Vegan", "Sulphites"], ["Lager Beer", "Lime", "Ice"]),
                    ("Efes Draft", "Efes Fıçı", 360, ["Gluten", "Vegan", "Sulphites"], ["Draft Beer", "Ice"]),
                    ("Aperol Spritz", "Aperol Spritz", 640, ["Vegan", "Sulphites"], ["Aperol", "Prosecco", "Soda", "Orange"]),
                    ("Gin Tonic", "Gin Tonik", 590, ["Vegan", "Sulphites"], ["Gin", "Tonic", "Lime", "Ice"]),
                    ("Rose Wine Glass", "Roze Şarap Kadeh", 520, ["Vegan", "Sulphites"], ["Rose Wine", "Ice"]),
                    ("White Wine Glass", "Beyaz Şarap Kadeh", 500, ["Vegan", "Sulphites"], ["White Wine", "Ice"]),
                    ("Sangria Pitcher", "Sangria Sürahi", 1450, ["Vegan", "Sulphites"], ["Red Wine", "Orange", "Apple", "Soda"]),
                ],
            },
            {
                "name_en": "Non-Alcoholic Drinks",
                "name_tr": "Alkolsüz İçecekler",
                "description_en": "Fresh mocktails, lemonades and hydrating beach drinks.",
                "description_tr": "Taze mocktail, limonata ve ferahlatıcı plaj içecekleri.",
                "items": [
                    ("Virgin Mojito", "Virgin Mojito", 340, ["Vegan", "Sugar Free"], ["Mint", "Lime", "Soda", "Ice"]),
                    ("Watermelon Cooler", "Karpuz Cooler", 360, ["Vegan"], ["Watermelon", "Mint", "Lime", "Ice"]),
                    ("Pineapple Iced Tea", "Ananaslı Soğuk Çay", 330, ["Vegan"], ["Iced Tea", "Pineapple", "Lemon", "Ice"]),
                    ("Cucumber Mint Lemonade", "Salatalık Naneli Limonata", 320, ["Vegan"], ["Cucumber", "Mint", "Lemon", "Ice"]),
                    ("Mango Smoothie", "Mango Smoothie", 390, ["Dairy", "Vegetarian"], ["Mango", "Yogurt", "Honey", "Ice"]),
                    ("Coconut Water", "Hindistan Cevizi Suyu", 300, ["Vegan", "Sugar Free"], ["Coconut Water", "Ice"]),
                    ("Sparkling Water", "Soda", 180, ["Vegan", "Sugar Free"], ["Sparkling Water", "Ice"]),
                ],
            },
        ],
    },
    {
        "name": "Luna Lobby Cafe",
        "name_tr": "Luna Lobi Kafe",
        "name_en": "Luna Lobby Cafe",
        "venue_type": "cafe",
        "description_tr": "Specialty kahve, pastane ürünleri ve gün boyu hafif atıştırmalıklar.",
        "description_en": "Specialty coffee, patisserie and all-day light bites.",
        "opening_hours": "07:00 - 23:00",
        "table_count": 32,
        "categories": [
            {
                "name_en": "Coffee Bar",
                "name_tr": "Kahve Barı",
                "description_en": "Espresso classics and iced specialty coffee.",
                "description_tr": "Espresso klasikleri ve soğuk specialty kahveler.",
                "items": [
                    ("Espresso", "Espresso", 160, ["Vegan", "Sugar Free"], ["Coffee"]),
                    ("Americano", "Americano", 180, ["Vegan", "Sugar Free"], ["Coffee", "Hot Water"]),
                    ("Cappuccino", "Cappuccino", 220, ["Dairy", "Vegetarian"], ["Coffee", "Milk", "Milk Foam"]),
                    ("Latte", "Latte", 230, ["Dairy", "Vegetarian"], ["Coffee", "Milk"]),
                    ("Flat White", "Flat White", 240, ["Dairy"], ["Coffee", "Milk"]),
                    ("Mocha", "Mocha", 260, ["Dairy", "Vegetarian"], ["Coffee", "Milk", "Chocolate Sauce"]),
                    ("Hot Chocolate", "Sıcak Çikolata", 280, ["Dairy", "Vegetarian"], ["Milk", "Cocoa", "Chocolate"]),
                    ("Iced Spanish Latte", "Soğuk Spanish Latte", 310, ["Dairy"], ["Coffee", "Milk", "Ice"]),
                    ("Iced Latte", "Soğuk Latte", 270, ["Dairy", "Vegetarian"], ["Coffee", "Milk", "Ice"]),
                    ("Cold Brew", "Cold Brew", 260, ["Vegan", "Sugar Free"], ["Cold Brew Coffee", "Ice"]),
                    ("Turkish Coffee", "Türk Kahvesi", 220, ["Vegan"], ["Coffee"]),
                ],
            },
            {
                "name_en": "Cafe Refreshers",
                "name_tr": "Cafe Ferahlatıcıları",
                "description_en": "Fresh lemonades, iced teas and easy non-alcoholic cafe drinks.",
                "description_tr": "Taze limonatalar, soğuk çaylar ve alkolsüz cafe içecekleri.",
                "items": [
                    ("Homemade Lemonade", "Ev Yapımı Limonata", 240, ["Vegan", "Vegetarian"], ["Lemon", "Mint", "Sugar Syrup", "Ice"]),
                    ("Berry Iced Tea", "Orman Meyveli Soğuk Çay", 250, ["Vegan", "Vegetarian"], ["Black Tea", "Berries", "Lemon", "Ice"]),
                    ("Coca Cola", "Coca Cola", 150, ["Vegan"], ["Cola", "Ice"]),
                    ("Sprite", "Sprite", 150, ["Vegan"], ["Lemon Lime Soda", "Ice"]),
                    ("Fanta", "Fanta", 150, ["Vegan"], ["Orange Soda", "Ice"]),
                    ("Water", "Su", 80, ["Vegan", "Sugar Free"], ["Water"]),
                ],
            },
            {
                "name_en": "Lobby Patisserie",
                "name_tr": "Lobi Pastanesi",
                "description_en": "Elegant pastries and afternoon sweets.",
                "description_tr": "Zarif pastane ürünleri ve beş çayı tatlıları.",
                "items": [
                    ("Butter Croissant", "Tereyağlı Kruvasan", 260, ["Gluten", "Dairy", "Egg", "Vegetarian"], ["Croissant Dough", "Butter"]),
                    ("Almond Croissant", "Bademli Kruvasan", 320, ["Gluten", "Dairy", "Nuts", "Egg", "Vegetarian"], ["Croissant", "Almond Cream", "Sliced Almond", "Butter"]),
                    ("Chocolate Croissant", "Çikolatalı Kruvasan", 300, ["Gluten", "Dairy", "Egg", "Vegetarian"], ["Croissant Dough", "Dark Chocolate", "Butter"]),
                    ("Cinnamon Roll", "Tarçınlı Roll", 290, ["Gluten", "Dairy", "Egg", "Vegetarian"], ["Sweet Dough", "Cinnamon", "Cream Cheese Glaze", "Butter"]),
                    ("Mini Danish Plate", "Mini Danish Tabağı", 380, ["Gluten", "Dairy", "Egg", "Vegetarian"], ["Danish Pastry", "Custard", "Berries", "Chocolate"]),
                    ("Pistachio Eclair", "Fıstıklı Ekler", 360, ["Gluten", "Dairy", "Nuts", "Egg"], ["Cream", "Pistachio", "Chocolate"]),
                    ("Lemon Tart", "Limon Tart", 340, ["Gluten", "Dairy", "Egg"], ["Lemon", "Butter", "Cream"]),
                    ("Mini Macaron Plate", "Mini Makaron Tabağı", 420, ["Nuts", "Egg"], ["Almond", "Sugar", "Cream"]),
                ],
            },
        ],
    },
]


def detail(description_tr, description_en, ingredients, allergens, prep_time, calories):
    return {
        "description_tr": description_tr,
        "description_en": description_en,
        "ingredients": ingredients,
        "allergens": allergens,
        "prep_time": prep_time,
        "calories": calories,
    }


VENUE_ITEM_DETAILS = {
    "Watermelon Feta Salad": detail("Soğuk karpuz dilimleri, beyaz peynir, taze nane, roka ve lime-zeytinyağı sosuyla hafif plaj salatası.", "Chilled watermelon with feta cheese, fresh mint, rocket and lime olive oil dressing for a light beach salad.", [("Watermelon", "Karpuz"), ("Feta Cheese", "Beyaz peynir"), ("Mint", "Nane"), ("Rocket", "Roka"), ("Lime", "Lime")], ["Dairy", "Vegetarian", "Sugar Free"], 7, 310),
    "Shrimp Tacos": detail("Izgara karides, guacamole, lahana salatası, acı mayo ve lime ile üç yumuşak tortilla taco.", "Three soft tortilla tacos with grilled shrimp, guacamole, cabbage slaw, spicy mayo and lime.", [("Shrimp", "Karides"), ("Tortilla", "Tortilla"), ("Guacamole", "Guacamole"), ("Cabbage Slaw", "Lahana salatası"), ("Spicy Mayo", "Acı mayo")], ["Gluten", "Egg", "Shellfish", "Spicy", "High Protein"], 12, 620),
    "Beach Club Sandwich": detail("Ekşi maya ekmekte ızgara tavuk, yumurta, marul, domates, cheddar ve ev yapımı aioli ile doyurucu club sandviç.", "A filling club sandwich on sourdough with grilled chicken, egg, lettuce, tomato, cheddar and house aioli.", [("Sourdough Bread", "Ekşi maya ekmek"), ("Chicken", "Tavuk"), ("Egg", "Yumurta"), ("Lettuce", "Marul"), ("Cheddar Cheese", "Cheddar peyniri")], ["Gluten", "Dairy", "Egg", "Halal", "High Protein"], 11, 720),
    "Poke Bowl": detail("Ton balığı, sushi pirinci, edamame, avokado, salatalık, susam ve soya-lime soslu ferah bowl.", "A fresh bowl with tuna, sushi rice, edamame, avocado, cucumber, sesame and soy-lime dressing.", [("Tuna", "Ton balığı"), ("Rice", "Pirinç"), ("Avocado", "Avokado"), ("Cucumber", "Salatalık"), ("Sesame", "Susam")], ["Soy", "Seafood", "Sesame", "High Protein"], 10, 610),
    "Azure Spritz": detail("Prosecco, turunçgil bitter, soda, portakal ve bol buzla hazırlanan ferah sahil spritz'i.", "A bright beach spritz with prosecco, citrus bitter, soda, orange and plenty of ice.", [("Prosecco", "Prosecco"), ("Citrus", "Turunçgil"), ("Soda", "Soda"), ("Orange", "Portakal"), ("Ice", "Buz")], ["Vegan", "Sulphites"], 5, 210),
    "Passion Mojito": detail("Rom, passion fruit püresi, taze nane, lime, soda ve kırık buzla tropik mojito yorumu.", "A tropical mojito with rum, passion fruit puree, fresh mint, lime, soda and crushed ice.", [("Rum", "Rom"), ("Passion Fruit", "Passion fruit"), ("Mint", "Nane"), ("Lime", "Lime"), ("Soda", "Soda")], ["Vegan", "Sulphites"], 5, 230),
    "Frozen Margarita": detail("Tekila, lime, portakal likörü ve tuz kenarlı bardakta servis edilen buzlu margarita.", "Frozen margarita with tequila, lime, orange liqueur and a salted rim.", [("Tequila", "Tekila"), ("Lime", "Lime"), ("Orange Liqueur", "Portakal likörü"), ("Salt", "Tuz"), ("Ice", "Buz")], ["Vegan", "Sulphites"], 6, 240),
    "Corona Extra": detail("Lime dilimiyle servis edilen hafif ve ferah Meksika lager birası.", "Light and crisp Mexican lager served chilled with a lime wedge.", [("Lager Beer", "Lager bira"), ("Lime", "Lime"), ("Ice", "Buz")], ["Gluten", "Vegan", "Sulphites"], 2, 148),
    "Efes Draft": detail("Soğuk servis edilen taze fıçı lager; plaj atıştırmalıklarıyla dengeli bir eşleşme.", "Fresh chilled draft lager with a clean finish, ideal with beach snacks.", [("Draft Beer", "Fıçı bira"), ("Ice", "Buz")], ["Gluten", "Vegan", "Sulphites"], 2, 170),
    "Aperol Spritz": detail("Aperol, prosecco, soda ve portakal dilimiyle gün batımı için klasik İtalyan spritz.", "Classic Italian sunset spritz with Aperol, prosecco, soda and orange.", [("Aperol", "Aperol"), ("Prosecco", "Prosecco"), ("Soda", "Soda"), ("Orange", "Portakal")], ["Vegan", "Sulphites"], 5, 220),
    "Gin Tonic": detail("Cin, premium tonik, lime ve bol buzla hazırlanan sade ve serinletici long drink.", "A clean long drink with gin, premium tonic, lime and plenty of ice.", [("Gin", "Cin"), ("Tonic", "Tonik"), ("Lime", "Lime"), ("Ice", "Buz")], ["Vegan", "Sulphites"], 4, 190),
    "Rose Wine Glass": detail("Soğuk servis edilen meyvemsi roze şarap; salatalar ve deniz ürünleriyle uyumludur.", "Chilled fruity rose wine by the glass, pairing well with salads and seafood.", [("Rose Wine", "Roze şarap"), ("Ice", "Buz")], ["Vegan", "Sulphites"], 2, 125),
    "White Wine Glass": detail("Narenciye notalı soğuk beyaz şarap; hafif plaj tabakları için ferah seçenek.", "Chilled white wine with citrus notes, a refreshing option for light beach plates.", [("White Wine", "Beyaz şarap"), ("Ice", "Buz")], ["Vegan", "Sulphites"], 2, 120),
    "Sangria Pitcher": detail("Kırmızı şarap, portakal, elma, soda ve buzla paylaşımlık yaz sangria sürahisi.", "Shareable summer sangria pitcher with red wine, orange, apple, soda and ice.", [("Red Wine", "Kırmızı şarap"), ("Orange", "Portakal"), ("Apple", "Elma"), ("Soda", "Soda")], ["Vegan", "Sulphites"], 6, 520),
    "Virgin Mojito": detail("Alkolsüz mojito; taze nane, lime, soda ve kırık buzla ferah ve hafif içimlidir.", "Alcohol-free mojito with fresh mint, lime, soda and crushed ice.", [("Mint", "Nane"), ("Lime", "Lime"), ("Soda", "Soda"), ("Ice", "Buz")], ["Vegan", "Sugar Free"], 5, 65),
    "Watermelon Cooler": detail("Taze karpuz suyu, nane, lime ve buzla plaj için serinletici alkolsüz içecek.", "Refreshing alcohol-free beach cooler with fresh watermelon juice, mint, lime and ice.", [("Watermelon", "Karpuz"), ("Mint", "Nane"), ("Lime", "Lime"), ("Ice", "Buz")], ["Vegan"], 5, 120),
    "Pineapple Iced Tea": detail("Demlenmiş soğuk çay, ananas, limon ve buzla tropik aromalı alkolsüz içecek.", "Tropical alcohol-free iced tea with brewed tea, pineapple, lemon and ice.", [("Iced Tea", "Soğuk çay"), ("Pineapple", "Ananas"), ("Lemon", "Limon"), ("Ice", "Buz")], ["Vegan"], 4, 140),
    "Cucumber Mint Lemonade": detail("Salatalık, nane, limon suyu ve buzla hazırlanan hafif ev yapımı limonata.", "Light house lemonade with cucumber, mint, lemon juice and ice.", [("Cucumber", "Salatalık"), ("Mint", "Nane"), ("Lemon", "Limon"), ("Ice", "Buz")], ["Vegan"], 5, 135),
    "Mango Smoothie": detail("Mango, yoğurt, bal ve buzla hazırlanan kremamsı tropik smoothie.", "Creamy tropical smoothie with mango, yogurt, honey and ice.", [("Mango", "Mango"), ("Yogurt", "Yoğurt"), ("Honey", "Bal"), ("Ice", "Buz")], ["Dairy", "Vegetarian"], 6, 280),
    "Coconut Water": detail("Soğuk servis edilen doğal hindistan cevizi suyu; hafif ve şekersiz ferahlık.", "Natural coconut water served chilled for light, sugar-free hydration.", [("Coconut Water", "Hindistan cevizi suyu"), ("Ice", "Buz")], ["Vegan", "Sugar Free"], 2, 45),
    "Sparkling Water": detail("Buz ve limonla servis edilen sade maden suyu.", "Plain sparkling water served with ice and lemon.", [("Sparkling Water", "Soda"), ("Ice", "Buz")], ["Vegan", "Sugar Free"], 2, 0),
    "Flat White": detail("Çift shot espresso ve ince mikro köpüklü sütle dengeli, yoğun kahve.", "A balanced, rich coffee with double espresso and silky microfoam milk.", [("Coffee", "Kahve"), ("Milk", "Süt")], ["Dairy", "Vegetarian"], 4, 120),
    "Iced Spanish Latte": detail("Espresso, süt, yoğunlaştırılmış süt ve buzla tatlı, kremamsı soğuk kahve.", "Sweet creamy iced coffee with espresso, milk, condensed milk and ice.", [("Coffee", "Kahve"), ("Milk", "Süt"), ("Ice", "Buz"), ("Condensed Milk", "Yoğunlaştırılmış süt")], ["Dairy", "Vegetarian"], 5, 260),
    "Turkish Coffee": detail("Bakır cezvede ağır ateşte pişirilen yoğun gövdeli geleneksel Türk kahvesi.", "Traditional full-bodied Turkish coffee slowly brewed in a copper cezve.", [("Coffee", "Kahve")], ["Vegan", "Sugar Free"], 6, 15),
    "Pistachio Eclair": detail("Pastacı kreması dolgulu ekler, Antep fıstığı kreması ve bitter çikolata ile tamamlanır.", "Eclair filled with pastry cream, finished with pistachio cream and dark chocolate.", [("Cream", "Krema"), ("Pistachio", "Antep fıstığı"), ("Chocolate", "Çikolata"), ("Choux Pastry", "Şu hamuru")], ["Gluten", "Dairy", "Nuts", "Egg", "Vegetarian"], 5, 430),
    "Lemon Tart": detail("Tereyağlı tart tabanı üzerinde limon kreması, hafif mereng ve taze limon kabuğu.", "Butter tart shell with lemon cream, light meringue and fresh lemon zest.", [("Lemon", "Limon"), ("Butter", "Tereyağı"), ("Cream", "Krema"), ("Tart Shell", "Tart tabanı")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 5, 390),
    "Mini Macaron Plate": detail("Badem bazlı mini makaronlardan oluşan paylaşım tabağı; vanilya, çikolata ve orman meyvesi çeşitleri.", "A sharing plate of almond-based mini macarons in vanilla, chocolate and berry flavors.", [("Almond", "Badem"), ("Sugar", "Şeker"), ("Cream", "Krema"), ("Chocolate", "Çikolata")], ["Nuts", "Egg", "Dairy", "Vegetarian"], 4, 460),
}


ITEM_DETAILS = {
    "Turkish Breakfast Spread": detail("Ezine peyniri, zeytin, bal-kaymak, yumurta, domates, salatalık ve sıcak ekmeklerle paylaşımlık klasik serpme kahvaltı.", "A generous Turkish breakfast spread with Ezine cheese, olives, honey cream, eggs, tomatoes, cucumber and warm bread.", [("Ezine Cheese", "Ezine peyniri"), ("Olives", "Zeytin"), ("Honey Cream", "Bal kaymak"), ("Egg", "Yumurta"), ("Sourdough Bread", "Ekşi maya ekmek")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 18, 920),
    "Menemen": detail("Tereyağında pişen domates, yeşil biber ve yumurtayla hazırlanan bol soslu geleneksel kahvaltı lezzeti.", "A traditional Turkish egg dish cooked with tomatoes, green peppers and butter, served rich and saucy.", [("Egg", "Yumurta"), ("Tomato", "Domates"), ("Green Pepper", "Yeşil biber"), ("Butter", "Tereyağı"), ("Sourdough Bread", "Ekşi maya ekmek")], ["Egg", "Dairy", "Vegetarian"], 12, 430),
    "Avocado Toast": detail("Ekşi maya ekmek üzerinde ezilmiş avokado, poşe yumurta, roka, cherry domates ve limonlu zeytinyağı.", "Smashed avocado on sourdough with poached egg, rocket, cherry tomatoes and lemon olive oil.", [("Sourdough Bread", "Ekşi maya ekmek"), ("Avocado", "Avokado"), ("Egg", "Yumurta"), ("Rocket", "Roka"), ("Cherry Tomato", "Cherry domates")], ["Gluten", "Egg", "Vegetarian"], 10, 510),
    "Pancake Stack": detail("Üst üste dizilmiş yumuşak pancake, orman meyveleri, tereyağı ve akçaağaç şurubuyla servis edilir.", "Fluffy stacked pancakes served with berries, butter and maple syrup.", [("Pancake Batter", "Pancake hamuru"), ("Berries", "Orman meyveleri"), ("Butter", "Tereyağı"), ("Maple Syrup", "Akçaağaç şurubu")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 12, 680),
    "Croissant Sandwich": detail("Tereyağlı kruvasan içinde füme hindi, cheddar, roka, domates ve hafif hardallı sos.", "A buttery croissant filled with smoked turkey, cheddar, rocket, tomato and a light mustard sauce.", [("Croissant", "Kruvasan"), ("Smoked Turkey", "Füme hindi"), ("Cheddar Cheese", "Cheddar peyniri"), ("Rocket", "Roka"), ("Mustard Sauce", "Hardallı sos")], ["Gluten", "Dairy", "Egg", "Mustard", "High Protein"], 9, 620),
    "Eggs Benedict": detail("English muffin üzerinde füme et, poşe yumurta ve ipeksi hollandez sosla hazırlanan brunch klasiği.", "A brunch classic with English muffin, smoked beef, poached eggs and silky hollandaise sauce.", [("English Muffin", "English muffin"), ("Smoked Beef", "Füme et"), ("Egg", "Yumurta"), ("Hollandaise Sauce", "Hollandez sos"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Egg", "High Protein"], 14, 720),
    "Granola Bowl": detail("Yoğurt, ev yapımı granola, muz, orman meyveleri, bal ve chia ile ferah kahvaltı kasesi.", "A fresh breakfast bowl with yogurt, homemade granola, banana, berries, honey and chia.", [("Greek Yogurt", "Süzme yoğurt"), ("Granola", "Granola"), ("Banana", "Muz"), ("Berries", "Orman meyveleri"), ("Chia", "Chia")], ["Dairy", "Nuts", "Vegetarian"], 6, 480),
    "French Toast": detail("Brioche ekmek, tarçınlı yumurtalı karışımda kızartılıp berry sos ve mascarpone kremayla servis edilir.", "Brioche soaked in cinnamon egg custard, griddled and served with berry sauce and mascarpone cream.", [("Brioche", "Brioche"), ("Egg", "Yumurta"), ("Cinnamon", "Tarçın"), ("Berry Sauce", "Orman meyveli sos"), ("Mascarpone", "Mascarpone")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 12, 650),
    "Bagel Plate": detail("Susamlı bagel, krem peynir, füme somon, kapari, kırmızı soğan ve roka ile dengeli brunch tabağı.", "Sesame bagel with cream cheese, smoked salmon, capers, red onion and rocket.", [("Sesame Bagel", "Susamlı bagel"), ("Cream Cheese", "Krem peynir"), ("Smoked Salmon", "Füme somon"), ("Capers", "Kapari"), ("Red Onion", "Kırmızı soğan")], ["Gluten", "Dairy", "Seafood", "Sesame", "High Protein"], 8, 610),
    "Protein Breakfast": detail("Izgara tavuk, yumurta, avokado, kinoa, lor peyniri ve yeşilliklerle yüksek proteinli kahvaltı tabağı.", "A high-protein plate with grilled chicken, eggs, avocado, quinoa, curd cheese and greens.", [("Chicken", "Tavuk"), ("Egg", "Yumurta"), ("Avocado", "Avokado"), ("Quinoa", "Kinoa"), ("Curd Cheese", "Lor peyniri")], ["Egg", "Dairy", "High Protein", "Keto Friendly", "Halal"], 14, 740),

    "Butter Croissant": detail("Kat kat açılmış tereyağlı kruvasan; dışı çıtır, içi yumuşak ve yoğun tereyağı aromalı.", "A flaky butter croissant with a crisp shell, soft center and rich buttery aroma.", [("Croissant Dough", "Kruvasan hamuru"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 4, 360),
    "Almond Croissant": detail("Badem kremasıyla doldurulmuş, üstü file badem ve pudra şekeriyle tamamlanan kruvasan.", "A croissant filled with almond cream and finished with sliced almonds and powdered sugar.", [("Croissant", "Kruvasan"), ("Almond Cream", "Badem kreması"), ("Sliced Almond", "File badem"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Egg", "Nuts", "Vegetarian"], 5, 470),
    "Chocolate Croissant": detail("Tereyağlı kruvasan hamuru içinde bitter çikolata çubuklarıyla hazırlanan klasik pastane lezzeti.", "Buttery croissant pastry baked with dark chocolate batons inside.", [("Croissant Dough", "Kruvasan hamuru"), ("Dark Chocolate", "Bitter çikolata"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 5, 440),
    "Cheese Pogaca": detail("Yumuşak poğaça hamuru içinde beyaz peynir ve maydanozla hazırlanan sıcak fırın ürünü.", "Soft Turkish pastry filled with white cheese and parsley.", [("Pogaca Dough", "Poğaça hamuru"), ("Feta Cheese", "Beyaz peynir"), ("Parsley", "Maydanoz"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 4, 330),
    "Olive Achma": detail("Açma hamuru, siyah zeytin ezmesi ve tereyağıyla hazırlanan tuzlu fırın klasiği.", "A soft Turkish achma pastry rolled with black olive paste and butter.", [("Achma Dough", "Açma hamuru"), ("Black Olive Paste", "Siyah zeytin ezmesi"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Vegetarian"], 4, 360),
    "Cinnamon Roll": detail("Tarçınlı şeker dolgulu yumuşak roll, krem peynir glazür ve hafif vanilya aromasıyla servis edilir.", "A soft cinnamon sugar roll topped with cream cheese glaze and vanilla notes.", [("Sweet Dough", "Tatlı hamur"), ("Cinnamon", "Tarçın"), ("Cream Cheese Glaze", "Krem peynir glazür"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 6, 520),
    "Mini Danish Plate": detail("Meyveli, kremalı ve çikolatalı mini danish çeşitlerinden oluşan paylaşımlık pastane tabağı.", "A shareable plate of mini Danish pastries with fruit, custard and chocolate varieties.", [("Danish Pastry", "Danish hamuru"), ("Custard", "Pastacı kreması"), ("Berries", "Orman meyveleri"), ("Chocolate", "Çikolata")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 7, 560),
    "Banana Fit Muffin": detail("Muz, yulaf, ceviz ve az şekerle hazırlanan hafif ve doyurucu muffin.", "A lighter muffin made with banana, oats, walnuts and reduced sugar.", [("Banana", "Muz"), ("Oats", "Yulaf"), ("Walnut", "Ceviz"), ("Egg", "Yumurta")], ["Gluten", "Egg", "Nuts", "Vegetarian"], 4, 340),

    "Truffle Fries": detail("İnce çıtır patatesler, trüf yağı, parmesan ve frenk soğanıyla servis edilir.", "Crispy thin fries tossed with truffle oil, parmesan and chives.", [("Potato", "Patates"), ("Truffle Oil", "Trüf yağı"), ("Parmesan", "Parmesan"), ("Chives", "Frenk soğanı")], ["Dairy", "Vegetarian"], 9, 520),
    "Crispy Chicken Basket": detail("Baharatlı pane kaplı tavuk parçaları, patates kızartması ve ballı hardal sosla servis edilir.", "Spiced crispy chicken pieces served with fries and honey mustard sauce.", [("Chicken", "Tavuk"), ("Breadcrumb", "Pane harcı"), ("Potato", "Patates"), ("Honey Mustard", "Ballı hardal")], ["Gluten", "Egg", "Mustard", "High Protein", "Halal"], 14, 780),
    "Mozzarella Sticks": detail("Eriyik mozzarella çubukları, çıtır pane ve marinara sos ile sıcak servis edilir.", "Melting mozzarella sticks in a crisp coating, served hot with marinara sauce.", [("Mozzarella", "Mozzarella"), ("Breadcrumb", "Pane harcı"), ("Egg", "Yumurta"), ("Marinara Sauce", "Marinara sos")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 10, 610),
    "Nachos Supreme": detail("Tortilla cipsleri üzerinde cheddar sos, jalapeno, salsa, ekşi krema ve guacamole.", "Tortilla chips layered with cheddar sauce, jalapeno, salsa, sour cream and guacamole.", [("Tortilla Chips", "Tortilla cips"), ("Cheddar Sauce", "Cheddar sos"), ("Jalapeno", "Jalapeno"), ("Salsa", "Salsa"), ("Guacamole", "Guacamole")], ["Dairy", "Spicy", "Vegetarian"], 10, 740),
    "Hummus & Pita": detail("Zeytinyağlı humus, sumak, nohut ve sıcak pita ekmeğiyle paylaşımlık başlangıç.", "Olive-oil hummus with sumac, chickpeas and warm pita bread.", [("Chickpea", "Nohut"), ("Tahini", "Tahin"), ("Olive Oil", "Zeytinyağı"), ("Pita Bread", "Pita ekmeği")], ["Gluten", "Sesame", "Vegan", "Vegetarian"], 7, 430),
    "Buffalo Wings": detail("Acı buffalo sosla kaplanan tavuk kanatları, ranch dip ve kereviz çubuklarıyla servis edilir.", "Chicken wings tossed in spicy buffalo sauce with ranch dip and celery sticks.", [("Chicken Wings", "Tavuk kanat"), ("Buffalo Sauce", "Buffalo sos"), ("Ranch Sauce", "Ranch sos"), ("Celery", "Kereviz")], ["Dairy", "Celery", "Spicy", "High Protein", "Halal"], 16, 820),
    "Mini Taco Trio": detail("Üç mini taco; baharatlı tavuk, salsa, marul ve lime ile servis edilir.", "Three mini tacos with spiced chicken, salsa, lettuce and lime.", [("Tortilla", "Tortilla"), ("Chicken", "Tavuk"), ("Salsa", "Salsa"), ("Lettuce", "Marul"), ("Lime", "Lime")], ["Gluten", "Spicy", "High Protein", "Halal"], 12, 560),
    "Fried Calamari": detail("Hafif pane kalamar halkaları, limon ve sarımsaklı aioli sosla servis edilir.", "Lightly breaded calamari rings served with lemon and garlic aioli.", [("Calamari", "Kalamar"), ("Breadcrumb", "Pane harcı"), ("Lemon", "Limon"), ("Garlic Aioli", "Sarımsaklı aioli")], ["Gluten", "Egg", "Seafood", "Shellfish"], 12, 540),

    "Caesar Salad": detail("Romaine marul, parmesan, kruton ve ev yapımı sezar sosla hazırlanan klasik salata.", "Classic Caesar salad with romaine lettuce, parmesan, croutons and house Caesar dressing.", [("Romaine Lettuce", "Romaine marul"), ("Parmesan", "Parmesan"), ("Croutons", "Kruton"), ("Caesar Dressing", "Sezar sos")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 8, 390),
    "Grilled Chicken Caesar": detail("Izgara tavuk göğsü, romaine marul, parmesan, kruton ve yoğun sezar sosla doyurucu salata.", "A filling Caesar salad with grilled chicken breast, romaine, parmesan, croutons and rich dressing.", [("Chicken", "Tavuk"), ("Romaine Lettuce", "Romaine marul"), ("Parmesan", "Parmesan"), ("Croutons", "Kruton"), ("Caesar Dressing", "Sezar sos")], ["Gluten", "Dairy", "Egg", "High Protein", "Halal"], 12, 560),
    "Avocado Quinoa Salad": detail("Kinoa, avokado, roka, cherry domates, salatalık ve limonlu zeytinyağıyla hafif bowl.", "A light bowl with quinoa, avocado, rocket, cherry tomato, cucumber and lemon olive oil.", [("Quinoa", "Kinoa"), ("Avocado", "Avokado"), ("Rocket", "Roka"), ("Cherry Tomato", "Cherry domates"), ("Cucumber", "Salatalık")], ["Vegan", "Vegetarian", "Sugar Free"], 9, 430),
    "Salmon Rocket Salad": detail("Izgara somon, roka, avokado, kapari, cherry domates ve hardallı limon sosla servis edilir.", "Grilled salmon with rocket, avocado, capers, cherry tomato and mustard lemon dressing.", [("Salmon", "Somon"), ("Rocket", "Roka"), ("Avocado", "Avokado"), ("Capers", "Kapari"), ("Mustard Lemon Dressing", "Hardallı limon sos")], ["Seafood", "Mustard", "High Protein", "Keto Friendly"], 14, 620),
    "Burrata Salad": detail("Kremamsı burrata, domates, fesleğen pesto, roka ve balzamik glaze ile premium salata.", "Creamy burrata with tomatoes, basil pesto, rocket and balsamic glaze.", [("Burrata", "Burrata"), ("Tomato", "Domates"), ("Basil Pesto", "Fesleğen pesto"), ("Rocket", "Roka"), ("Balsamic Glaze", "Balzamik glaze")], ["Dairy", "Nuts", "Vegetarian"], 8, 540),
    "Vegan Bowl": detail("Nohut, kinoa, avokado, köz sebzeler, roka ve tahin-limon soslu bitkisel bowl.", "A plant-based bowl with chickpeas, quinoa, avocado, roasted vegetables, rocket and tahini lemon dressing.", [("Chickpea", "Nohut"), ("Quinoa", "Kinoa"), ("Avocado", "Avokado"), ("Roasted Vegetables", "Köz sebzeler"), ("Tahini Lemon Sauce", "Tahin limon sos")], ["Vegan", "Vegetarian", "Sesame", "Sugar Free"], 11, 510),
    "Protein Bowl": detail("Izgara tavuk, kinoa, yumurta, avokado, yeşillikler ve yoğurtlu sosla yüksek proteinli bowl.", "High-protein bowl with grilled chicken, quinoa, egg, avocado, greens and yogurt dressing.", [("Chicken", "Tavuk"), ("Quinoa", "Kinoa"), ("Egg", "Yumurta"), ("Avocado", "Avokado"), ("Yogurt Dressing", "Yoğurtlu sos")], ["Egg", "Dairy", "High Protein", "Halal"], 13, 650),
    "Mediterranean Salad": detail("Beyaz peynir, zeytin, salatalık, domates, kırmızı soğan ve kekikli zeytinyağıyla Akdeniz salatası.", "Mediterranean salad with feta, olives, cucumber, tomato, red onion and oregano olive oil.", [("Feta Cheese", "Beyaz peynir"), ("Olives", "Zeytin"), ("Cucumber", "Salatalık"), ("Tomato", "Domates"), ("Red Onion", "Kırmızı soğan")], ["Dairy", "Vegetarian", "Sugar Free"], 7, 360),

    "Smash Burger": detail("Çift yüzü mühürlenmiş dana köfte, cheddar, turşu, karamelize soğan ve özel burger sosla brioche içinde.", "Smashed beef patty in brioche with cheddar, pickles, caramelized onion and house burger sauce.", [("Beef Patty", "Dana köfte"), ("Cheddar Cheese", "Cheddar peyniri"), ("Pickles", "Turşu"), ("Caramelized Onion", "Karamelize soğan"), ("Brioche Bun", "Brioche ekmeği")], ["Gluten", "Dairy", "Egg", "High Protein"], 14, 760),
    "Double Bacon Burger": detail("İki dana köfte, çıtır bacon, cheddar, turşu ve dumanlı mayo sosla yoğun burger.", "A rich burger with two beef patties, crispy bacon, cheddar, pickles and smoky mayo.", [("Beef Patty", "Dana köfte"), ("Beef Bacon", "Dana bacon"), ("Cheddar Cheese", "Cheddar peyniri"), ("Pickles", "Turşu"), ("Smoky Mayo", "Dumanlı mayo")], ["Gluten", "Dairy", "Egg", "High Protein"], 16, 980),
    "BBQ Cowboy Burger": detail("Dana köfte, cheddar, soğan halkası, BBQ sos ve turşuyla tatlı-isli cowboy burger.", "Beef patty with cheddar, onion ring, BBQ sauce and pickles for a smoky-sweet cowboy burger.", [("Beef Patty", "Dana köfte"), ("Cheddar Cheese", "Cheddar peyniri"), ("Onion Ring", "Soğan halkası"), ("BBQ Sauce", "BBQ sos"), ("Brioche Bun", "Brioche ekmeği")], ["Gluten", "Dairy", "Mustard", "High Protein"], 15, 850),
    "Truffle Burger": detail("Dana köfte, mantar sote, trüf mayo, cheddar ve roka ile aromatik premium burger.", "Premium burger with beef patty, sautéed mushrooms, truffle mayo, cheddar and rocket.", [("Beef Patty", "Dana köfte"), ("Mushroom", "Mantar"), ("Truffle Mayo", "Trüf mayo"), ("Cheddar Cheese", "Cheddar peyniri"), ("Rocket", "Roka")], ["Gluten", "Dairy", "Egg", "High Protein"], 15, 820),
    "Classic Cheeseburger": detail("Dana köfte, cheddar, marul, domates, turşu ve klasik burger sosla sade ve güçlü lezzet.", "A clean classic with beef patty, cheddar, lettuce, tomato, pickles and burger sauce.", [("Beef Patty", "Dana köfte"), ("Cheddar Cheese", "Cheddar peyniri"), ("Lettuce", "Marul"), ("Tomato", "Domates"), ("Burger Sauce", "Burger sos")], ["Gluten", "Dairy", "Egg", "High Protein"], 13, 720),
    "Volcano Burger": detail("Acı soslu dana köfte, jalapeno, cheddar, çıtır soğan ve chili mayo ile yüksek acılı burger.", "Spicy beef burger with jalapeno, cheddar, crispy onion and chili mayo.", [("Beef Patty", "Dana köfte"), ("Jalapeno", "Jalapeno"), ("Cheddar Cheese", "Cheddar peyniri"), ("Crispy Onion", "Çıtır soğan"), ("Chili Mayo", "Chili mayo")], ["Gluten", "Dairy", "Egg", "Extra Spicy", "High Protein"], 15, 830),
    "Mushroom Swiss Burger": detail("Dana köfte, sote mantar, Swiss peyniri, karamelize soğan ve sarımsaklı mayo ile servis edilir.", "Beef patty with sautéed mushrooms, Swiss cheese, caramelized onion and garlic mayo.", [("Beef Patty", "Dana köfte"), ("Mushroom", "Mantar"), ("Swiss Cheese", "Swiss peyniri"), ("Caramelized Onion", "Karamelize soğan"), ("Garlic Mayo", "Sarımsaklı mayo")], ["Gluten", "Dairy", "Egg", "High Protein"], 15, 800),
    "Crispy Chicken Burger": detail("Çıtır pane tavuk, ranch sos, marul, turşu ve cheddar ile yumuşak brioche ekmekte.", "Crispy breaded chicken in brioche with ranch, lettuce, pickles and cheddar.", [("Chicken", "Tavuk"), ("Breadcrumb", "Pane harcı"), ("Ranch Sauce", "Ranch sos"), ("Lettuce", "Marul"), ("Brioche Bun", "Brioche ekmeği")], ["Gluten", "Dairy", "Egg", "High Protein", "Halal"], 14, 760),
    "Avocado Ranch Burger": detail("Dana köfte, avokado dilimleri, ranch sos, cheddar, roka ve domatesle ferah burger.", "Fresh burger with beef patty, avocado slices, ranch, cheddar, rocket and tomato.", [("Beef Patty", "Dana köfte"), ("Avocado", "Avokado"), ("Ranch Sauce", "Ranch sos"), ("Cheddar Cheese", "Cheddar peyniri"), ("Rocket", "Roka")], ["Gluten", "Dairy", "Egg", "High Protein"], 15, 790),
    "Monster Burger": detail("Çift dana köfte, çift cheddar, çıtır soğan, turşu ve özel sosla büyük porsiyon imza burger.", "A large signature burger with double beef, double cheddar, crispy onion, pickles and house sauce.", [("Beef Patty", "Dana köfte"), ("Cheddar Cheese", "Cheddar peyniri"), ("Crispy Onion", "Çıtır soğan"), ("Pickles", "Turşu"), ("Special Sauce", "Özel sos")], ["Gluten", "Dairy", "Egg", "High Protein"], 18, 1100),

    "Alfredo": detail("Fettuccine makarna, krema, parmesan, tereyağı ve karabiberle yoğun kıvamlı klasik Alfredo.", "Fettuccine tossed with cream, parmesan, butter and black pepper for a rich Alfredo.", [("Fettuccine", "Fettuccine"), ("Cream", "Krema"), ("Parmesan", "Parmesan"), ("Butter", "Tereyağı")], ["Gluten", "Dairy", "Vegetarian"], 13, 720),
    "Carbonara": detail("Spagetti, yumurta sarısı, parmesan, dana bacon ve taze karabiberle hazırlanan kremasız carbonara.", "Spaghetti with egg yolk, parmesan, beef bacon and cracked black pepper, made without cream.", [("Spaghetti", "Spagetti"), ("Egg Yolk", "Yumurta sarısı"), ("Parmesan", "Parmesan"), ("Beef Bacon", "Dana bacon")], ["Gluten", "Dairy", "Egg", "High Protein"], 14, 780),
    "Spaghetti Bolognese": detail("Yavaş pişmiş dana kıymalı bolonez sos, spagetti ve parmesanla servis edilir.", "Spaghetti served with slow-cooked beef bolognese sauce and parmesan.", [("Spaghetti", "Spagetti"), ("Beef Ragu", "Dana ragù"), ("Tomato Sauce", "Domates sosu"), ("Parmesan", "Parmesan")], ["Gluten", "Dairy", "High Protein"], 15, 760),
    "Pesto Chicken Pasta": detail("Izgara tavuk, fesleğen pesto, krema, parmesan ve penne makarnayla aromatik tabak.", "Penne with grilled chicken, basil pesto, cream and parmesan.", [("Penne", "Penne"), ("Chicken", "Tavuk"), ("Basil Pesto", "Fesleğen pesto"), ("Cream", "Krema"), ("Parmesan", "Parmesan")], ["Gluten", "Dairy", "Nuts", "High Protein", "Halal"], 15, 820),
    "Mac and Cheese": detail("Dirsek makarna, cheddar, mozzarella ve parmesan karışımıyla fırınlanmış kremalı comfort lezzet.", "Baked elbow pasta with a creamy cheddar, mozzarella and parmesan cheese blend.", [("Elbow Pasta", "Dirsek makarna"), ("Cheddar Cheese", "Cheddar peyniri"), ("Mozzarella", "Mozzarella"), ("Parmesan", "Parmesan")], ["Gluten", "Dairy", "Vegetarian"], 13, 790),
    "Seafood Linguine": detail("Linguine makarna, karides, kalamar, somon parçaları ve sarımsaklı domates sosla hazırlanır.", "Linguine with shrimp, calamari, salmon pieces and garlic tomato sauce.", [("Linguine", "Linguine"), ("Shrimp", "Karides"), ("Calamari", "Kalamar"), ("Salmon", "Somon"), ("Garlic Tomato Sauce", "Sarımsaklı domates sos")], ["Gluten", "Seafood", "Shellfish", "High Protein"], 17, 820),
    "Lasagna": detail("Kat kat makarna, dana ragù, beşamel ve mozzarella ile fırınlanmış klasik lazanya.", "Layered pasta baked with beef ragù, béchamel and mozzarella.", [("Lasagna Sheets", "Lazanya yaprağı"), ("Beef Ragu", "Dana ragù"), ("Bechamel", "Beşamel"), ("Mozzarella", "Mozzarella")], ["Gluten", "Dairy", "High Protein"], 18, 860),
    "Arrabbiata": detail("Penne makarna, acı biberli domates sos, sarımsak ve taze fesleğenle vegan uyumlu acılı seçenek.", "Penne with spicy tomato sauce, garlic and fresh basil; a vegan-friendly spicy option.", [("Penne", "Penne"), ("Tomato Sauce", "Domates sosu"), ("Chili Pepper", "Acı biber"), ("Garlic", "Sarımsak"), ("Basil", "Fesleğen")], ["Gluten", "Vegan", "Vegetarian", "Spicy"], 12, 590),
    "Truffle Alfredo": detail("Fettuccine, trüf yağı, krema, parmesan ve mantar soteyle zengin aromalı premium makarna.", "Premium fettuccine with truffle oil, cream, parmesan and sautéed mushrooms.", [("Fettuccine", "Fettuccine"), ("Truffle Oil", "Trüf yağı"), ("Cream", "Krema"), ("Parmesan", "Parmesan"), ("Mushroom", "Mantar")], ["Gluten", "Dairy", "Vegetarian"], 15, 820),

    "Margherita": detail("İnce pizza hamuru üzerinde domates sos, mozzarella, taze fesleğen ve zeytinyağıyla klasik lezzet.", "Classic thin-crust pizza with tomato sauce, mozzarella, fresh basil and olive oil.", [("Pizza Dough", "Pizza hamuru"), ("Tomato Sauce", "Domates sosu"), ("Mozzarella", "Mozzarella"), ("Basil", "Fesleğen")], ["Gluten", "Dairy", "Vegetarian"], 14, 690),
    "Pepperoni": detail("Domates sos, mozzarella ve baharatlı pepperoni dilimleriyle taş fırın pizza.", "Stone-baked pizza with tomato sauce, mozzarella and spicy pepperoni slices.", [("Pizza Dough", "Pizza hamuru"), ("Tomato Sauce", "Domates sosu"), ("Mozzarella", "Mozzarella"), ("Pepperoni", "Pepperoni")], ["Gluten", "Dairy", "Spicy", "High Protein"], 15, 820),
    "Four Cheese": detail("Mozzarella, gorgonzola, parmesan ve cheddar karışımıyla yoğun peynirli pizza.", "A rich four-cheese pizza with mozzarella, gorgonzola, parmesan and cheddar.", [("Pizza Dough", "Pizza hamuru"), ("Mozzarella", "Mozzarella"), ("Gorgonzola", "Gorgonzola"), ("Parmesan", "Parmesan"), ("Cheddar Cheese", "Cheddar peyniri")], ["Gluten", "Dairy", "Vegetarian"], 15, 860),
    "BBQ Chicken Pizza": detail("BBQ sos, mozzarella, ızgara tavuk, kırmızı soğan ve mısırla isli tatlı pizza.", "Smoky-sweet pizza with BBQ sauce, mozzarella, grilled chicken, red onion and corn.", [("Pizza Dough", "Pizza hamuru"), ("BBQ Sauce", "BBQ sos"), ("Mozzarella", "Mozzarella"), ("Chicken", "Tavuk"), ("Red Onion", "Kırmızı soğan")], ["Gluten", "Dairy", "Mustard", "High Protein", "Halal"], 16, 880),
    "Mexican Pizza": detail("Mozzarella, baharatlı kıyma, jalapeno, mısır, salsa ve acı sosla Meksika esintili pizza.", "Mexican-style pizza with mozzarella, spiced beef, jalapeno, corn, salsa and hot sauce.", [("Pizza Dough", "Pizza hamuru"), ("Spiced Beef", "Baharatlı dana"), ("Jalapeno", "Jalapeno"), ("Corn", "Mısır"), ("Salsa", "Salsa")], ["Gluten", "Dairy", "Spicy", "High Protein"], 16, 910),
    "Truffle Pizza": detail("Mozzarella, mantar, trüf yağı, parmesan ve roka ile aromatik beyaz soslu pizza.", "White-sauce pizza with mozzarella, mushrooms, truffle oil, parmesan and rocket.", [("Pizza Dough", "Pizza hamuru"), ("Mozzarella", "Mozzarella"), ("Mushroom", "Mantar"), ("Truffle Oil", "Trüf yağı"), ("Rocket", "Roka")], ["Gluten", "Dairy", "Vegetarian"], 16, 840),
    "Veggie Pizza": detail("Domates sos, mozzarella, biber, mantar, zeytin, mısır ve roka ile sebzeli pizza.", "Vegetable pizza with tomato sauce, mozzarella, peppers, mushrooms, olives, corn and rocket.", [("Pizza Dough", "Pizza hamuru"), ("Mozzarella", "Mozzarella"), ("Pepper", "Biber"), ("Mushroom", "Mantar"), ("Olives", "Zeytin")], ["Gluten", "Dairy", "Vegetarian"], 15, 720),
    "Meat Lovers Pizza": detail("Dana sucuk, pepperoni, dana füme, mozzarella ve domates sosla bol etli pizza.", "Loaded meat pizza with beef sucuk, pepperoni, smoked beef, mozzarella and tomato sauce.", [("Pizza Dough", "Pizza hamuru"), ("Beef Sucuk", "Dana sucuk"), ("Pepperoni", "Pepperoni"), ("Smoked Beef", "Füme dana"), ("Mozzarella", "Mozzarella")], ["Gluten", "Dairy", "Spicy", "High Protein"], 17, 980),

    "Chicken Quesadilla": detail("Tortilla içinde baharatlı tavuk, cheddar, biber ve soğan; yanında salsa ve ekşi krema.", "Tortilla filled with spiced chicken, cheddar, peppers and onion, served with salsa and sour cream.", [("Tortilla", "Tortilla"), ("Chicken", "Tavuk"), ("Cheddar Cheese", "Cheddar peyniri"), ("Pepper", "Biber"), ("Sour Cream", "Ekşi krema")], ["Gluten", "Dairy", "Spicy", "High Protein", "Halal"], 14, 760),
    "Beef Burrito": detail("Baharatlı dana, Meksika pirinci, fasulye, cheddar, salsa ve guacamole ile sarılmış doyurucu burrito.", "A filling burrito with spiced beef, Mexican rice, beans, cheddar, salsa and guacamole.", [("Tortilla", "Tortilla"), ("Spiced Beef", "Baharatlı dana"), ("Mexican Rice", "Meksika pirinci"), ("Beans", "Fasulye"), ("Guacamole", "Guacamole")], ["Gluten", "Dairy", "Spicy", "High Protein"], 15, 820),
    "Mexican Nachos Supreme": detail("Tortilla cipsleri, baharatlı dana, cheddar sos, jalapeno, salsa, ekşi krema ve guacamole ile kat kat servis edilir.", "Layered tortilla chips with spiced beef, cheddar sauce, jalapeno, salsa, sour cream and guacamole.", [("Tortilla Chips", "Tortilla cips"), ("Spiced Beef", "Baharatlı dana"), ("Cheddar Sauce", "Cheddar sos"), ("Jalapeno", "Jalapeno"), ("Guacamole", "Guacamole")], ["Dairy", "Spicy", "High Protein"], 12, 790),
    "Tacos Al Pastor": detail("Üç tortilla taco; marine et, ananas salsa, kişniş, soğan ve lime ile servis edilir.", "Three tacos with marinated beef, pineapple salsa, cilantro, onion and lime.", [("Tortilla", "Tortilla"), ("Marinated Beef", "Marine dana"), ("Pineapple Salsa", "Ananas salsa"), ("Cilantro", "Kişniş"), ("Lime", "Lime")], ["Gluten", "Spicy", "High Protein"], 13, 650),
    "Loaded Fajitas": detail("Döküm tavada tavuk ve dana, renkli biberler, soğan, tortilla, salsa ve guacamole ile gelir.", "Sizzling chicken and beef fajitas with peppers, onions, tortillas, salsa and guacamole.", [("Chicken", "Tavuk"), ("Beef", "Dana"), ("Pepper", "Biber"), ("Onion", "Soğan"), ("Tortilla", "Tortilla")], ["Gluten", "Spicy", "High Protein", "Halal"], 18, 980),
    "Chili Con Carne": detail("Yavaş pişmiş dana kıyma, fasulye, domates, chili biber ve cheddar ile baharatlı kase.", "Slow-cooked spicy bowl with beef mince, beans, tomato, chili peppers and cheddar.", [("Beef Mince", "Dana kıyma"), ("Beans", "Fasulye"), ("Tomato", "Domates"), ("Chili Pepper", "Chili biber"), ("Cheddar Cheese", "Cheddar peyniri")], ["Dairy", "Spicy", "High Protein"], 16, 720),
    "Guacamole Bowl": detail("Avokado, lime, kişniş, domates, kırmızı soğan ve tortilla cipsleriyle taze guacamole kasesi.", "Fresh guacamole bowl with avocado, lime, cilantro, tomato, red onion and tortilla chips.", [("Avocado", "Avokado"), ("Lime", "Lime"), ("Cilantro", "Kişniş"), ("Tomato", "Domates"), ("Tortilla Chips", "Tortilla cips")], ["Vegan", "Vegetarian", "Sugar Free"], 8, 420),
    "Mexican Rice Bowl": detail("Meksika pirinci, siyah fasulye, mısır, salsa, guacamole ve baharatlı tavukla renkli bowl.", "Colorful bowl with Mexican rice, black beans, corn, salsa, guacamole and spiced chicken.", [("Mexican Rice", "Meksika pirinci"), ("Black Beans", "Siyah fasulye"), ("Corn", "Mısır"), ("Salsa", "Salsa"), ("Chicken", "Tavuk")], ["Spicy", "High Protein", "Halal"], 13, 690),

    "Chicken Teriyaki Bowl": detail("Teriyaki soslu tavuk, jasmin pirinç, brokoli, havuç, susam ve taze soğanla servis edilir.", "Teriyaki chicken served with jasmine rice, broccoli, carrot, sesame and spring onion.", [("Chicken", "Tavuk"), ("Teriyaki Sauce", "Teriyaki sos"), ("Jasmine Rice", "Jasmin pirinç"), ("Broccoli", "Brokoli"), ("Sesame", "Susam")], ["Soy", "Sesame", "High Protein", "Halal"], 14, 710),
    "Beef Noodles": detail("Dana şeritleri, yumurtalı noodle, soya sos, sebzeler ve susamla wok tavada hazırlanır.", "Wok-fried beef strips with egg noodles, soy sauce, vegetables and sesame.", [("Beef", "Dana"), ("Egg Noodles", "Yumurtalı noodle"), ("Soy Sauce", "Soya sosu"), ("Mixed Vegetables", "Karışık sebze"), ("Sesame", "Susam")], ["Gluten", "Soy", "Egg", "Sesame", "High Protein"], 15, 780),
    "Sushi Platter": detail("Somon, ton balığı, karides ve avokadolu roll çeşitlerinden oluşan paylaşımlık sushi tabağı.", "Shareable sushi platter with salmon, tuna, shrimp and avocado rolls.", [("Sushi Rice", "Sushi pirinci"), ("Salmon", "Somon"), ("Tuna", "Ton balığı"), ("Shrimp", "Karides"), ("Nori", "Nori")], ["Seafood", "Shellfish", "Soy", "Sesame", "High Protein"], 20, 760),
    "Ramen": detail("Tavuk suyu bazlı ramen; noodle, marine yumurta, tavuk, mantar, nori ve taze soğan içerir.", "Chicken broth ramen with noodles, marinated egg, chicken, mushrooms, nori and spring onion.", [("Ramen Noodles", "Ramen noodle"), ("Chicken Broth", "Tavuk suyu"), ("Egg", "Yumurta"), ("Chicken", "Tavuk"), ("Nori", "Nori")], ["Gluten", "Soy", "Egg", "Sesame", "High Protein"], 16, 740),
    "Dumplings": detail("Sebzeli ve tavuklu dumplingler, susamlı soya dip sosuyla buharda pişirilir.", "Steamed chicken and vegetable dumplings served with sesame soy dip.", [("Dumpling Wrapper", "Dumpling hamuru"), ("Chicken", "Tavuk"), ("Cabbage", "Lahana"), ("Soy Dip", "Soya dip"), ("Sesame", "Susam")], ["Gluten", "Soy", "Sesame", "High Protein", "Halal"], 11, 480),
    "Sweet Chili Chicken": detail("Çıtır tavuk parçaları, tatlı acı sos, biber, taze soğan ve susamla servis edilir.", "Crispy chicken pieces glazed with sweet chili sauce, peppers, spring onion and sesame.", [("Chicken", "Tavuk"), ("Sweet Chili Sauce", "Tatlı acı sos"), ("Pepper", "Biber"), ("Spring Onion", "Taze soğan"), ("Sesame", "Susam")], ["Gluten", "Soy", "Sesame", "Spicy", "High Protein", "Halal"], 14, 820),
    "Pad Thai": detail("Pirinç noodle, karides, yumurta, tofu, yer fıstığı, tamarind sos ve lime ile Tayland klasiği.", "Thai classic with rice noodles, shrimp, egg, tofu, peanuts, tamarind sauce and lime.", [("Rice Noodles", "Pirinç noodle"), ("Shrimp", "Karides"), ("Egg", "Yumurta"), ("Tofu", "Tofu"), ("Peanuts", "Yer fıstığı")], ["Seafood", "Shellfish", "Egg", "Peanuts", "Soy"], 16, 760),
    "Korean Fried Chicken": detail("Çıtır tavuk, gochujang sos, susam, taze soğan ve turşu salatalıkla Kore usulü servis edilir.", "Korean-style crispy chicken with gochujang glaze, sesame, spring onion and pickled cucumber.", [("Chicken", "Tavuk"), ("Gochujang Sauce", "Gochujang sos"), ("Sesame", "Susam"), ("Spring Onion", "Taze soğan"), ("Pickled Cucumber", "Salatalık turşusu")], ["Gluten", "Soy", "Sesame", "Spicy", "High Protein", "Halal"], 15, 860),
    "Fried Rice Bowl": detail("Yumurta, sebze, jasmin pirinç, soya sosu ve susamla wokta çevrilmiş doyurucu bowl.", "Wok-fried jasmine rice with egg, vegetables, soy sauce and sesame.", [("Jasmine Rice", "Jasmin pirinç"), ("Egg", "Yumurta"), ("Mixed Vegetables", "Karışık sebze"), ("Soy Sauce", "Soya sosu"), ("Sesame", "Susam")], ["Egg", "Soy", "Sesame", "Vegetarian"], 12, 620),

    "Tenderloin Steak": detail("Izgara bonfile dilimleri, tereyağlı patates püresi, roka ve demi-glace sosla servis edilir.", "Grilled tenderloin slices served with buttery mashed potatoes, rocket and demi-glace sauce.", [("Beef Tenderloin", "Dana bonfile"), ("Mashed Potato", "Patates püresi"), ("Butter", "Tereyağı"), ("Rocket", "Roka"), ("Demi Glace", "Demi-glace")], ["Dairy", "High Protein", "Keto Friendly"], 22, 920),
    "Ribeye Steak": detail("Mermer dokulu antrikot, ızgara sebze, deniz tuzu ve biberli et jus ile premium steak tabağı.", "Marbled ribeye with grilled vegetables, sea salt and peppery beef jus.", [("Ribeye", "Antrikot"), ("Grilled Vegetables", "Izgara sebze"), ("Sea Salt", "Deniz tuzu"), ("Beef Jus", "Et jus")], ["High Protein", "Keto Friendly"], 24, 1050),
    "New York Steak": detail("New York strip steak, çıtır patates, sarımsaklı tereyağı ve hardallı sosla servis edilir.", "New York strip steak with crispy potatoes, garlic butter and mustard sauce.", [("New York Strip", "New York strip"), ("Potato", "Patates"), ("Garlic Butter", "Sarımsaklı tereyağı"), ("Mustard Sauce", "Hardal sos")], ["Dairy", "Mustard", "High Protein"], 24, 980),
    "Grilled Meatballs": detail("Baharatlı dana köfte, köz biber, pilav, domates sos ve yoğurtla klasik ızgara tabak.", "Spiced beef meatballs with roasted pepper, rice, tomato sauce and yogurt.", [("Beef Meatball", "Dana köfte"), ("Roasted Pepper", "Köz biber"), ("Rice", "Pirinç"), ("Tomato Sauce", "Domates sos"), ("Yogurt", "Yoğurt")], ["Gluten", "Dairy", "High Protein", "Halal"], 18, 820),
    "Chicken Skewers": detail("Marine tavuk şiş, lavaş, köz sebzeler, sumaklı soğan ve yoğurtlu sosla servis edilir.", "Marinated chicken skewers with lavash, roasted vegetables, sumac onion and yogurt sauce.", [("Chicken", "Tavuk"), ("Lavash", "Lavaş"), ("Roasted Vegetables", "Köz sebzeler"), ("Sumac Onion", "Sumaklı soğan"), ("Yogurt Sauce", "Yoğurtlu sos")], ["Gluten", "Dairy", "High Protein", "Halal"], 17, 690),
    "Lamb Chops": detail("Izgara kuzu pirzola, kekikli patates, roka ve köz domatesle zengin ızgara tabağı.", "Grilled lamb chops with thyme potatoes, rocket and roasted tomato.", [("Lamb Chops", "Kuzu pirzola"), ("Thyme Potato", "Kekikli patates"), ("Rocket", "Roka"), ("Roasted Tomato", "Köz domates")], ["High Protein", "Keto Friendly", "Halal"], 24, 1040),
    "Entrecote Burger Plate": detail("Dilim antrikot, brioche ekmek, cheddar, karamelize soğan ve trüflü patatesle tabak sunum.", "Sliced entrecote served burger-style with brioche, cheddar, caramelized onion and truffle fries.", [("Entrecote", "Antrikot"), ("Brioche Bun", "Brioche ekmeği"), ("Cheddar Cheese", "Cheddar peyniri"), ("Caramelized Onion", "Karamelize soğan"), ("Truffle Fries", "Trüflü patates")], ["Gluten", "Dairy", "High Protein"], 22, 1120),
    "Mixed Grill": detail("Bonfile, köfte, tavuk şiş ve kuzu pirzoladan oluşan paylaşımlık büyük ızgara tabağı.", "A large mixed grill platter with tenderloin, meatballs, chicken skewers and lamb chops.", [("Beef Tenderloin", "Dana bonfile"), ("Beef Meatball", "Dana köfte"), ("Chicken", "Tavuk"), ("Lamb Chops", "Kuzu pirzola"), ("Grilled Vegetables", "Izgara sebze")], ["High Protein", "Halal"], 30, 1450),

    "Grilled Salmon": detail("Izgara somon fileto, limonlu roka, kinoa ve hardallı yoğurt sosla dengeli deniz ürünü tabağı.", "Grilled salmon fillet with lemon rocket, quinoa and mustard yogurt sauce.", [("Salmon", "Somon"), ("Rocket", "Roka"), ("Quinoa", "Kinoa"), ("Mustard Yogurt", "Hardallı yoğurt"), ("Lemon", "Limon")], ["Seafood", "Dairy", "Mustard", "High Protein", "Keto Friendly"], 18, 680),
    "Shrimp Casserole": detail("Karides, domates, sarımsak, biber ve tereyağıyla güveçte sıcak servis edilir.", "Shrimp baked in a casserole with tomato, garlic, peppers and butter.", [("Shrimp", "Karides"), ("Tomato", "Domates"), ("Garlic", "Sarımsak"), ("Pepper", "Biber"), ("Butter", "Tereyağı")], ["Seafood", "Shellfish", "Dairy", "High Protein"], 16, 590),
    "Fish & Chips": detail("Çıtır pane beyaz balık, kalın patates kızartması, tartar sos ve limonla İngiliz klasiği.", "Crispy battered white fish with thick-cut fries, tartar sauce and lemon.", [("White Fish", "Beyaz balık"), ("Beer Batter", "Pane hamuru"), ("Potato", "Patates"), ("Tartar Sauce", "Tartar sos"), ("Lemon", "Limon")], ["Gluten", "Egg", "Seafood"], 17, 780),
    "Grilled Sea Bass": detail("Izgara levrek, roka, köz sebze, limon ve zeytinyağlı Akdeniz sosla servis edilir.", "Grilled sea bass with rocket, roasted vegetables, lemon and Mediterranean olive oil dressing.", [("Sea Bass", "Levrek"), ("Rocket", "Roka"), ("Roasted Vegetables", "Köz sebzeler"), ("Lemon", "Limon"), ("Olive Oil", "Zeytinyağı")], ["Seafood", "High Protein", "Keto Friendly"], 20, 610),
    "Seafood Risotto": detail("Arborio pirinci, karides, kalamar, somon, parmesan ve deniz mahsullü stokla kremamsı risotto.", "Creamy risotto with arborio rice, shrimp, calamari, salmon, parmesan and seafood stock.", [("Arborio Rice", "Arborio pirinci"), ("Shrimp", "Karides"), ("Calamari", "Kalamar"), ("Salmon", "Somon"), ("Parmesan", "Parmesan")], ["Seafood", "Shellfish", "Dairy", "High Protein"], 20, 790),
    "Salmon Teriyaki": detail("Teriyaki glaze somon, jasmin pirinç, brokoli, susam ve taze soğanla Asya esintili tabak.", "Teriyaki-glazed salmon with jasmine rice, broccoli, sesame and spring onion.", [("Salmon", "Somon"), ("Teriyaki Sauce", "Teriyaki sos"), ("Jasmine Rice", "Jasmin pirinç"), ("Broccoli", "Brokoli"), ("Sesame", "Susam")], ["Seafood", "Soy", "Sesame", "High Protein"], 18, 720),
    "Tuna Steak": detail("Dışı mühürlü ton balığı steak, susam kabuğu, wasabi mayo ve soya-lime sosla servis edilir.", "Seared tuna steak with sesame crust, wasabi mayo and soy-lime sauce.", [("Tuna", "Ton balığı"), ("Sesame", "Susam"), ("Wasabi Mayo", "Wasabi mayo"), ("Soy Lime Sauce", "Soya lime sos")], ["Seafood", "Soy", "Sesame", "Egg", "High Protein"], 16, 640),
    "Seafood Tacos": detail("Karides ve beyaz balık taco, lahana slaw, chipotle mayo, salsa ve lime ile servis edilir.", "Shrimp and white fish tacos with cabbage slaw, chipotle mayo, salsa and lime.", [("Tortilla", "Tortilla"), ("Shrimp", "Karides"), ("White Fish", "Beyaz balık"), ("Cabbage Slaw", "Lahana slaw"), ("Chipotle Mayo", "Chipotle mayo")], ["Gluten", "Seafood", "Shellfish", "Egg", "Spicy"], 15, 690),

    "Chicken Schnitzel": detail("İnce dövülmüş tavuk göğsü, çıtır pane, patates salatası ve limonla servis edilir.", "Thin chicken breast in a crisp coating, served with potato salad and lemon.", [("Chicken", "Tavuk"), ("Breadcrumb", "Pane harcı"), ("Egg", "Yumurta"), ("Potato Salad", "Patates salatası"), ("Lemon", "Limon")], ["Gluten", "Egg", "High Protein", "Halal"], 16, 820),
    "Cafe de Paris Chicken": detail("Izgara tavuk göğsü, Cafe de Paris sos, patates kızartması ve yeşilliklerle servis edilir.", "Grilled chicken breast with Cafe de Paris sauce, fries and greens.", [("Chicken", "Tavuk"), ("Cafe de Paris Sauce", "Cafe de Paris sos"), ("Butter", "Tereyağı"), ("Potato", "Patates"), ("Greens", "Yeşillik")], ["Dairy", "Mustard", "High Protein", "Halal"], 17, 790),
    "Beef Stroganoff": detail("Dana şeritleri, mantar, krema ve demi-glace sos; tereyağlı pilavla servis edilir.", "Beef strips with mushrooms, cream and demi-glace sauce, served with buttered rice.", [("Beef", "Dana"), ("Mushroom", "Mantar"), ("Cream", "Krema"), ("Demi Glace", "Demi-glace"), ("Rice", "Pirinç")], ["Dairy", "High Protein"], 20, 890),
    "Thai Curry Chicken": detail("Hindistan cevizi sütlü kırmızı curry, tavuk, sebzeler, jasmin pirinç ve taze kişnişle servis edilir.", "Red coconut curry with chicken, vegetables, jasmine rice and fresh cilantro.", [("Chicken", "Tavuk"), ("Coconut Milk", "Hindistan cevizi sütü"), ("Red Curry", "Kırmızı curry"), ("Jasmine Rice", "Jasmin pirinç"), ("Cilantro", "Kişniş")], ["Spicy", "High Protein", "Halal"], 16, 760),
    "Mushroom Risotto": detail("Arborio pirinci, mantar karışımı, parmesan, tereyağı ve trüf yağıyla kremamsı risotto.", "Creamy risotto with arborio rice, mixed mushrooms, parmesan, butter and truffle oil.", [("Arborio Rice", "Arborio pirinci"), ("Mushroom", "Mantar"), ("Parmesan", "Parmesan"), ("Butter", "Tereyağı"), ("Truffle Oil", "Trüf yağı")], ["Dairy", "Vegetarian"], 18, 690),
    "Chicken Fajita Plate": detail("Döküm tavada tavuk, biber, soğan, tortilla, salsa, guacamole ve ekşi krema ile servis edilir.", "Sizzling chicken fajita with peppers, onions, tortillas, salsa, guacamole and sour cream.", [("Chicken", "Tavuk"), ("Pepper", "Biber"), ("Onion", "Soğan"), ("Tortilla", "Tortilla"), ("Guacamole", "Guacamole")], ["Gluten", "Dairy", "Spicy", "High Protein", "Halal"], 18, 850),
    "Mediterranean Chicken": detail("Izgara tavuk, köz sebzeler, zeytin, domates sos, roka ve otlu yoğurtla Akdeniz tabağı.", "Grilled chicken with roasted vegetables, olives, tomato sauce, rocket and herbed yogurt.", [("Chicken", "Tavuk"), ("Roasted Vegetables", "Köz sebzeler"), ("Olives", "Zeytin"), ("Tomato Sauce", "Domates sos"), ("Herbed Yogurt", "Otlu yoğurt")], ["Dairy", "High Protein", "Halal"], 16, 710),
    "Vegan Curry Bowl": detail("Nohut, tatlı patates, sebzeler, hindistan cevizi curry sos ve jasmin pirinçle vegan bowl.", "Vegan bowl with chickpeas, sweet potato, vegetables, coconut curry sauce and jasmine rice.", [("Chickpea", "Nohut"), ("Sweet Potato", "Tatlı patates"), ("Mixed Vegetables", "Karışık sebze"), ("Coconut Curry", "Hindistan cevizi curry"), ("Jasmine Rice", "Jasmin pirinç")], ["Vegan", "Vegetarian", "Sugar Free"], 15, 680),

    "Brownie": detail("Yoğun bitter çikolatalı brownie, üstünde ganaj ve yanında vanilyalı dondurmayla servis edilir.", "Dense dark chocolate brownie with ganache, served with vanilla ice cream.", [("Dark Chocolate", "Bitter çikolata"), ("Butter", "Tereyağı"), ("Egg", "Yumurta"), ("Flour", "Un"), ("Vanilla Ice Cream", "Vanilyalı dondurma")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 7, 620),
    "San Sebastian Cheesecake": detail("Yanık üst dokulu, krem peynirli San Sebastian cheesecake; akışkan ve yoğun kıvamlı.", "Burnt-top San Sebastian cheesecake with a creamy, rich center.", [("Cream Cheese", "Krem peynir"), ("Cream", "Krema"), ("Egg", "Yumurta"), ("Sugar", "Şeker"), ("Vanilla", "Vanilya")], ["Dairy", "Egg", "Vegetarian"], 6, 560),
    "Tiramisu": detail("Espresso ile ıslatılmış kedi dili, mascarpone kreması ve kakao ile klasik İtalyan tatlısı.", "Classic Italian dessert with espresso-soaked ladyfingers, mascarpone cream and cocoa.", [("Ladyfinger", "Kedi dili"), ("Espresso", "Espresso"), ("Mascarpone", "Mascarpone"), ("Cocoa", "Kakao"), ("Egg", "Yumurta")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 6, 480),
    "Chocolate Lava Cake": detail("Fırından sıcak çıkan akışkan çikolatalı kek, vanilyalı dondurma ve kakao crumble ile servis edilir.", "Warm molten chocolate cake with vanilla ice cream and cocoa crumble.", [("Dark Chocolate", "Bitter çikolata"), ("Butter", "Tereyağı"), ("Egg", "Yumurta"), ("Flour", "Un"), ("Vanilla Ice Cream", "Vanilyalı dondurma")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 9, 690),
    "Lotus Cheesecake": detail("Lotus bisküvi tabanı, krem peynir dolgusu ve karamelize bisküvi sosuyla zengin cheesecake.", "Rich cheesecake with Lotus biscuit base, cream cheese filling and caramelized biscuit sauce.", [("Lotus Biscuit", "Lotus bisküvi"), ("Cream Cheese", "Krem peynir"), ("Cream", "Krema"), ("Caramel Sauce", "Karamel sos")], ["Gluten", "Dairy", "Egg", "Vegetarian"], 6, 610),
    "Apple Crumble": detail("Tarçınlı elma dolgusu, tereyağlı crumble ve vanilyalı dondurmayla sıcak servis edilir.", "Warm cinnamon apple filling topped with buttery crumble and vanilla ice cream.", [("Apple", "Elma"), ("Cinnamon", "Tarçın"), ("Butter Crumble", "Tereyağlı crumble"), ("Vanilla Ice Cream", "Vanilyalı dondurma")], ["Gluten", "Dairy", "Vegetarian"], 8, 540),
    "Waffle": detail("Belçika waffle, çikolata sos, çilek, muz, fındık kırığı ve dondurmayla servis edilir.", "Belgian waffle with chocolate sauce, strawberry, banana, hazelnut crumbs and ice cream.", [("Waffle Batter", "Waffle hamuru"), ("Chocolate Sauce", "Çikolata sos"), ("Strawberry", "Çilek"), ("Banana", "Muz"), ("Hazelnut", "Fındık")], ["Gluten", "Dairy", "Egg", "Nuts", "Vegetarian"], 10, 740),
    "Profiterole": detail("Pastacı kremalı profiterol topları, yoğun çikolata sos ve Antep fıstığı ile servis edilir.", "Choux profiteroles filled with pastry cream, covered in chocolate sauce and pistachio.", [("Choux Pastry", "Şu hamuru"), ("Pastry Cream", "Pastacı kreması"), ("Chocolate Sauce", "Çikolata sos"), ("Pistachio", "Antep fıstığı")], ["Gluten", "Dairy", "Egg", "Nuts", "Vegetarian"], 7, 590),

    "Espresso": detail("Yoğun gövdeli, kısa çekim taze öğütülmüş espresso.", "A short, full-bodied shot of freshly ground espresso.", [("Coffee", "Kahve")], ["Vegan", "Sugar Free"], 3, 5),
    "Americano": detail("Espresso üzerine sıcak su eklenerek hazırlanan sade ve dengeli kahve.", "A clean balanced coffee made by adding hot water to espresso.", [("Coffee", "Kahve"), ("Hot Water", "Sıcak su")], ["Vegan", "Sugar Free"], 4, 8),
    "Cappuccino": detail("Espresso, buharda ısıtılmış süt ve yoğun süt köpüğüyle klasik cappuccino.", "Classic cappuccino with espresso, steamed milk and thick milk foam.", [("Coffee", "Kahve"), ("Milk", "Süt"), ("Milk Foam", "Süt köpüğü")], ["Dairy", "Vegetarian"], 5, 120),
    "Latte": detail("Espresso ve ipeksi süt dokusuyla yumuşak içimli latte.", "Smooth latte with espresso and silky steamed milk.", [("Coffee", "Kahve"), ("Milk", "Süt")], ["Dairy", "Vegetarian"], 5, 150),
    "Flat White": detail("Çift espresso ve ince mikro köpükle daha yoğun kahve aromalı flat white.", "Double espresso with fine microfoam for a stronger coffee-forward flat white.", [("Coffee", "Kahve"), ("Milk", "Süt")], ["Dairy", "Vegetarian"], 5, 130),
    "Mocha": detail("Espresso, süt ve bitter çikolata sosla hazırlanan tatlı kahve.", "Espresso with milk and dark chocolate sauce for a sweet coffee drink.", [("Coffee", "Kahve"), ("Milk", "Süt"), ("Chocolate Sauce", "Çikolata sos")], ["Dairy", "Vegetarian"], 6, 230),
    "Turkish Coffee": detail("Geleneksel bakır cezvede pişirilen yoğun aromalı Türk kahvesi.", "Traditional Turkish coffee brewed in a copper cezve with rich aroma.", [("Turkish Coffee", "Türk kahvesi")], ["Vegan", "Sugar Free"], 6, 20),
    "Hot Chocolate": detail("Süt, kakao ve eritilmiş çikolatayla hazırlanan yoğun sıcak çikolata.", "Rich hot chocolate made with milk, cocoa and melted chocolate.", [("Milk", "Süt"), ("Cocoa", "Kakao"), ("Chocolate", "Çikolata")], ["Dairy", "Vegetarian"], 6, 290),

    "Coca Cola": detail("Soğuk servis edilen klasik gazlı kola.", "Classic chilled carbonated cola.", [("Cola", "Kola"), ("Ice", "Buz")], ["Vegan"], 2, 140),
    "Sprite": detail("Limon-lime aromalı ferah gazlı içecek.", "Refreshing lemon-lime carbonated soft drink.", [("Lemon Lime Soda", "Limon lime soda"), ("Ice", "Buz")], ["Vegan"], 2, 130),
    "Fanta": detail("Portakal aromalı soğuk gazlı içecek.", "Chilled orange-flavored carbonated drink.", [("Orange Soda", "Portakallı gazoz"), ("Ice", "Buz")], ["Vegan"], 2, 145),
    "Homemade Lemonade": detail("Taze limon, nane ve hafif şeker şurubuyla hazırlanan ev yapımı limonata.", "House lemonade with fresh lemon, mint and light sugar syrup.", [("Lemon", "Limon"), ("Mint", "Nane"), ("Sugar Syrup", "Şeker şurubu"), ("Ice", "Buz")], ["Vegan", "Vegetarian"], 4, 170),
    "Berry Iced Tea": detail("Demlenmiş siyah çay, orman meyvesi püresi, limon ve buzla ferah içecek.", "Brewed black tea with berry puree, lemon and ice.", [("Black Tea", "Siyah çay"), ("Berries", "Orman meyveleri"), ("Lemon", "Limon"), ("Ice", "Buz")], ["Vegan", "Vegetarian"], 4, 120),
    "Iced Latte": detail("Espresso, soğuk süt ve buzla hazırlanan yumuşak içimli soğuk kahve.", "Chilled coffee with espresso, cold milk and ice.", [("Coffee", "Kahve"), ("Milk", "Süt"), ("Ice", "Buz")], ["Dairy", "Vegetarian"], 4, 150),
    "Cold Brew": detail("Uzun süre soğuk demlenmiş, düşük asiditeli sade kahve.", "Slow cold-brewed black coffee with low acidity.", [("Cold Brew Coffee", "Cold brew kahve"), ("Ice", "Buz")], ["Vegan", "Sugar Free"], 3, 15),
    "Ayran": detail("Yoğurt, su ve tuzla hazırlanan geleneksel ferah içecek.", "Traditional refreshing yogurt drink with water and salt.", [("Yogurt", "Yoğurt"), ("Water", "Su"), ("Salt", "Tuz")], ["Dairy", "Vegetarian", "Sugar Free"], 2, 90),
    "Water": detail("Soğuk servis edilen şişe su.", "Chilled bottled water.", [("Water", "Su")], ["Vegan", "Sugar Free"], 1, 0),

    "Virgin Mojito": detail("Lime, nane, soda ve kırık buzla alkolsüz ferah mojito.", "Alcohol-free mojito with lime, mint, soda and crushed ice.", [("Lime", "Lime"), ("Mint", "Nane"), ("Soda", "Soda"), ("Ice", "Buz")], ["Vegan", "Sugar Free"], 5, 110),
    "Berry Cooler": detail("Orman meyvesi püresi, limon, soda ve buzla canlı renkli alkolsüz kokteyl.", "Berry puree, lemon, soda and ice in a bright alcohol-free cooler.", [("Berries", "Orman meyveleri"), ("Lemon", "Limon"), ("Soda", "Soda"), ("Ice", "Buz")], ["Vegan"], 5, 150),
    "Passion Spritz": detail("Passion fruit, soda, limon ve buzla tropik alkolsüz spritz.", "Tropical alcohol-free spritz with passion fruit, soda, lemon and ice.", [("Passion Fruit", "Passion fruit"), ("Soda", "Soda"), ("Lemon", "Limon"), ("Ice", "Buz")], ["Vegan"], 5, 160),
    "Cucember Mint Fizz": detail("Salatalık, nane, lime, soda ve buzla hafif içimli fizz.", "Light fizz with cucumber, mint, lime, soda and ice.", [("Cucumber", "Salatalık"), ("Mint", "Nane"), ("Lime", "Lime"), ("Soda", "Soda"), ("Ice", "Buz")], ["Vegan", "Sugar Free"], 5, 80),
    "Tropical Punch": detail("Ananas, mango, portakal ve limonla tropik meyve punch.", "Tropical fruit punch with pineapple, mango, orange and lemon.", [("Pineapple", "Ananas"), ("Mango", "Mango"), ("Orange", "Portakal"), ("Lemon", "Limon")], ["Vegan"], 5, 190),
    "Apple Ginger Mule": detail("Elma suyu, zencefil, lime, soda ve buzla keskin aromalı alkolsüz mule.", "Alcohol-free mule with apple juice, ginger, lime, soda and ice.", [("Apple Juice", "Elma suyu"), ("Ginger", "Zencefil"), ("Lime", "Lime"), ("Soda", "Soda"), ("Ice", "Buz")], ["Vegan"], 5, 150),
    "Mango Iced Tea": detail("Soğuk demlenmiş çay, mango püresi, limon ve buzla aromatik içecek.", "Iced tea with mango puree, lemon and ice.", [("Black Tea", "Siyah çay"), ("Mango", "Mango"), ("Lemon", "Limon"), ("Ice", "Buz")], ["Vegan"], 4, 130),
    "Strawberry Basil Lemonade": detail("Çilek, fesleğen, limon ve buzla hazırlanan imza limonata.", "Signature lemonade with strawberry, basil, lemon and ice.", [("Strawberry", "Çilek"), ("Basil", "Fesleğen"), ("Lemon", "Limon"), ("Ice", "Buz")], ["Vegan"], 5, 155),

    "Mojito": detail("Beyaz rom, lime, nane, soda ve kırık buzla klasik mojito.", "Classic mojito with white rum, lime, mint, soda and crushed ice.", [("White Rum", "Beyaz rom"), ("Lime", "Lime"), ("Mint", "Nane"), ("Soda", "Soda"), ("Ice", "Buz")], ["Vegan", "Sulphites"], 6, 190),
    "Margarita": detail("Tekila, lime ve portakal likörüyle tuz kenarlı klasik margarita.", "Classic salt-rim margarita with tequila, lime and orange liqueur.", [("Tequila", "Tekila"), ("Lime", "Lime"), ("Orange Liqueur", "Portakal likörü"), ("Salt", "Tuz")], ["Vegan", "Sulphites"], 6, 210),
    "Whiskey Sour": detail("Viski, limon, şeker şurubu ve köpüksü dokuyla dengeli sour kokteyl.", "Balanced sour cocktail with whiskey, lemon, sugar syrup and silky foam.", [("Whiskey", "Viski"), ("Lemon", "Limon"), ("Sugar Syrup", "Şeker şurubu"), ("Egg White", "Yumurta akı")], ["Egg", "Sulphites"], 6, 220),
    "Negroni": detail("Cin, Campari ve kırmızı vermutla acı-tatlı klasik aperitif.", "Bittersweet classic aperitif with gin, Campari and red vermouth.", [("Gin", "Cin"), ("Campari", "Campari"), ("Red Vermouth", "Kırmızı vermut"), ("Orange Peel", "Portakal kabuğu")], ["Sulphites", "Vegan"], 5, 210),
    "Espresso Martini": detail("Votka, espresso, kahve likörü ve şeker şurubuyla yoğun kahve kokteyli.", "Coffee-forward cocktail with vodka, espresso, coffee liqueur and sugar syrup.", [("Vodka", "Votka"), ("Espresso", "Espresso"), ("Coffee Liqueur", "Kahve likörü"), ("Sugar Syrup", "Şeker şurubu")], ["Sulphites", "Vegan"], 6, 230),
    "Long Island": detail("Votka, rom, cin, tekila, portakal likörü, limon ve kola ile güçlü klasik.", "Strong classic with vodka, rum, gin, tequila, orange liqueur, lemon and cola.", [("Vodka", "Votka"), ("Rum", "Rom"), ("Gin", "Cin"), ("Tequila", "Tekila"), ("Cola", "Kola")], ["Sulphites", "Vegan"], 7, 290),
    "Piña Colada": detail("Rom, hindistan cevizi kreması ve ananasla tropik kremamsı kokteyl.", "Creamy tropical cocktail with rum, coconut cream and pineapple.", [("Rum", "Rom"), ("Coconut Cream", "Hindistan cevizi kreması"), ("Pineapple", "Ananas"), ("Ice", "Buz")], ["Vegan", "Sulphites"], 6, 260),
    "Old Fashioned": detail("Bourbon, bitter, şeker ve portakal kabuğuyla güçlü klasik viski kokteyli.", "Classic whiskey cocktail with bourbon, bitters, sugar and orange peel.", [("Bourbon", "Bourbon"), ("Bitters", "Bitter"), ("Sugar", "Şeker"), ("Orange Peel", "Portakal kabuğu")], ["Sulphites", "Vegan"], 5, 210),

    "Efes Pilsen": detail("Soğuk servis edilen yerli lager bira.", "Chilled local lager beer.", [("Lager Beer", "Lager bira")], ["Gluten", "Sulphites", "Vegan"], 2, 180),
    "Bomonti Filtresiz": detail("Filtresiz gövdeli yerli buğday karakterli bira.", "Unfiltered local beer with a fuller wheat character.", [("Unfiltered Beer", "Filtresiz bira")], ["Gluten", "Sulphites", "Vegan"], 2, 210),
    "Miller": detail("Hafif içimli soğuk Amerikan lager.", "Light and crisp chilled American lager.", [("Lager Beer", "Lager bira")], ["Gluten", "Sulphites", "Vegan"], 2, 170),
    "Corona": detail("Lime dilimiyle servis edilen ferah Meksika birası.", "Refreshing Mexican beer served with a lime wedge.", [("Lager Beer", "Lager bira"), ("Lime", "Lime")], ["Gluten", "Sulphites", "Vegan"], 2, 185),
    "Heineken": detail("Dengeli acılık ve malt aromalı ithal lager bira.", "Imported lager with balanced bitterness and malt aroma.", [("Lager Beer", "Lager bira")], ["Gluten", "Sulphites", "Vegan"], 2, 190),
    "Guinness": detail("Kremamsı köpüklü, kavruk malt aromalı stout bira.", "Creamy stout with roasted malt notes and dense foam.", [("Stout Beer", "Stout bira")], ["Gluten", "Sulphites", "Vegan"], 2, 230),
    "Craft IPA": detail("Narenciye ve şerbetçiotu aromaları belirgin butik IPA.", "Craft IPA with citrus and hop-forward aromas.", [("IPA Beer", "IPA bira")], ["Gluten", "Sulphites", "Vegan"], 2, 220),

    "Kavaklıdere Yakut Glass": detail("Kavaklıdere Yakut kadeh; orta gövdeli, kırmızı meyve aromalı ve yumuşak tanenli kırmızı şarap.", "Kavaklidere Yakut by the glass; medium-bodied red wine with red fruit aromas and soft tannins.", [("Yakut Red Wine", "Yakut kırmızı şarap")], ["Sulphites", "Vegan"], 2, 125),
    "Kavaklıdere Cankaya Glass": detail("Kavaklıdere Çankaya kadeh; narenciye ve yeşil elma notalı, canlı asiditeli beyaz şarap.", "Kavaklidere Cankaya by the glass; crisp white wine with citrus and green apple notes.", [("Cankaya White Wine", "Çankaya beyaz şarap")], ["Sulphites", "Vegan"], 2, 115),
    "Kayra Rose Glass": detail("Kayra Rosé kadeh; çilek ve frambuaz aromalı, ferah ve hafif içimli roze şarap.", "Kayra Rose by the glass; fresh rose wine with strawberry and raspberry aromas.", [("Rose Wine", "Roze şarap")], ["Sulphites", "Vegan"], 2, 120),
    "Doluca Cabernet Sauvignon Bottle": detail("Doluca Cabernet Sauvignon şişe; koyu meyve, baharat ve belirgin tanen karakterli premium kırmızı şarap.", "Doluca Cabernet Sauvignon bottle; premium red wine with dark fruit, spice and structured tannins.", [("Cabernet Sauvignon", "Cabernet Sauvignon")], ["Sulphites", "Vegan"], 3, 620),
    "Suvla Sauvignon Blanc Bottle": detail("Suvla Sauvignon Blanc şişe; greyfurt, lime ve mineral notalarıyla ferah beyaz şarap.", "Suvla Sauvignon Blanc bottle; refreshing white wine with grapefruit, lime and mineral notes.", [("Sauvignon Blanc", "Sauvignon Blanc")], ["Sulphites", "Vegan"], 3, 560),
    "Prosecco Valdobbiadene Bottle": detail("Valdobbiadene Prosecco şişe; ince kabarcıklı, armut ve beyaz çiçek notalı İtalyan köpüklü şarap.", "Valdobbiadene Prosecco bottle; Italian sparkling wine with fine bubbles, pear and white flower notes.", [("Prosecco", "Prosecco")], ["Sulphites", "Vegan"], 3, 610),
    "Kayra Shiraz Glass": detail("Kayra Shiraz kadeh; karabiber, olgun erik ve baharat notalarıyla gövdeli kırmızı şarap.", "Kayra Shiraz by the glass; full-bodied red wine with black pepper, ripe plum and spice notes.", [("Shiraz Wine", "Shiraz şarap")], ["Sulphites", "Vegan"], 2, 135),
}


CATEGORY_TAGS = {
    "Breakfast": ["Egg", "Dairy"], "Bakery & Pastries": ["Gluten", "Dairy", "Egg"],
    "Starters & Appetizers": ["Gluten"], "Salads": ["Vegetarian"],
    "Burgers": ["Gluten", "Dairy", "High Protein"], "Pastas": ["Gluten", "Dairy"],
    "Pizzas": ["Gluten", "Dairy"], "Mexican Cuisine": ["Gluten", "Spicy"],
    "Asian Cuisine": ["Soy", "Sesame"], "Steaks & Grill": ["High Protein", "Halal"],
    "Seafood": ["Seafood", "Shellfish", "High Protein"], "Main Courses": ["High Protein"],
    "Desserts": ["Gluten", "Dairy", "Egg"], "Hot Drinks": ["Dairy"],
    "Soft Drinks": ["Sugar Free"], "Mocktails": ["Sugar Free"], "Cocktails": ["Sulphites"],
    "Beers": ["Gluten", "Sulphites"], "Wines": ["Sulphites"],
}


KEYWORD_TAGS = {
    "vegan": ["Vegan", "Sugar Free"], "avocado": ["Vegetarian"], "chicken": ["High Protein", "Halal"],
    "beef": ["High Protein"], "steak": ["High Protein"], "salmon": ["Seafood", "High Protein"],
    "shrimp": ["Seafood", "Shellfish"], "sushi": ["Seafood", "Soy"], "spicy": ["Spicy"],
    "volcano": ["Extra Spicy"], "buffalo": ["Spicy"], "chili": ["Spicy"], "fajita": ["Spicy"],
    "burrito": ["Gluten"], "quesadilla": ["Gluten", "Dairy"], "ramen": ["Soy", "Gluten"],
    "noodles": ["Soy", "Gluten"], "pad thai": ["Soy", "Peanuts"], "protein": ["High Protein", "Keto Friendly"],
}


def get_category_image(category_name):
    media_path = settings.MEDIA_ROOT / "menu_items" / CATEGORY_IMAGE

    if media_path.exists():
        return f"menu_items/{CATEGORY_IMAGE}"

    return "menu_items/default.webp"


def normalize_image_names(title):
    slug = slugify(title)

    return (
        slug.replace('-', '_'),
        slug,
    )


def find_menu_image(filename, category_name=None, venue_name=None):
    menu_root = settings.MEDIA_ROOT / "menu_items"
    category_slug = slugify(category_name).replace('-', '_') if category_name else None
    venue_slug = slugify(venue_name).replace('-', '_') if venue_name else None

    if venue_slug and category_slug:
        for extension in IMAGE_EXTENSIONS:
            venue_category_path = menu_root / venue_slug / category_slug / f"{filename}{extension}"

            if venue_category_path.exists():
                return str(venue_category_path.relative_to(settings.MEDIA_ROOT)).replace('\\', '/')

        for extension in IMAGE_EXTENSIONS:
            venue_category_matches = list((menu_root / venue_slug / category_slug).glob(f"{filename}_*{extension}"))

            if venue_category_matches:
                return str(venue_category_matches[0].relative_to(settings.MEDIA_ROOT)).replace('\\', '/')

    if venue_slug:
        for extension in IMAGE_EXTENSIONS:
            venue_matches = list((menu_root / venue_slug).glob(f"**/{filename}{extension}"))

            if venue_matches:
                return str(venue_matches[0].relative_to(settings.MEDIA_ROOT)).replace('\\', '/')

        for extension in IMAGE_EXTENSIONS:
            venue_matches = list((menu_root / venue_slug).glob(f"**/{filename}_*{extension}"))

            if venue_matches:
                return str(venue_matches[0].relative_to(settings.MEDIA_ROOT)).replace('\\', '/')

    for extension in IMAGE_EXTENSIONS:
        direct_path = menu_root / f"{filename}{extension}"

        if direct_path.exists():
            return f"menu_items/{direct_path.name}"

    if category_slug:
        for extension in IMAGE_EXTENSIONS:
            category_matches = list(menu_root.glob(f"**/{category_slug}/{filename}{extension}"))

            if category_matches:
                return str(category_matches[0].relative_to(settings.MEDIA_ROOT)).replace('\\', '/')

    for extension in IMAGE_EXTENSIONS:
        matches = list(menu_root.glob(f"**/{filename}{extension}"))

        if matches:
            return str(matches[0].relative_to(settings.MEDIA_ROOT)).replace('\\', '/')

    return None


def get_item_image(category_name, title_en, venue_name=None):
    override = IMAGE_NAME_OVERRIDES.get(title_en)

    if override:
        image = find_menu_image(override, category_name, venue_name)

        if image:
            return image

    for filename in normalize_image_names(title_en):
        image = find_menu_image(filename, category_name, venue_name)

        if image:
            return image

    return get_category_image(category_name)


def get_tags(category_name, title_en):
    tags = set(CATEGORY_TAGS.get(category_name, []))
    normalized = title_en.lower()

    for keyword, keyword_tags in KEYWORD_TAGS.items():
        if keyword in normalized:
            tags.update(keyword_tags)

    if "Vegan" in tags:
        tags.discard("Dairy")
        tags.discard("Egg")

    return sorted(tags)


def get_ingredient_names(category_name, title_en):
    base = {
        "Breakfast": ["Sourdough Bread", "Egg", "Butter", "Tomato", "Feta Cheese"],
        "Bakery & Pastries": ["Butter", "Chocolate", "Cream"],
        "Starters & Appetizers": ["Chicken", "Cheddar Cheese", "Special Sauce"],
        "Salads": ["Lettuce", "Rocket", "Quinoa", "Avocado", "Tomato"],
        "Burgers": ["Beef Patty", "Cheddar Cheese", "Pickles", "Brioche Bun", "Special Sauce"],
        "Pastas": ["Pasta", "Parmesan", "Cream", "Tomato Sauce"],
        "Pizzas": ["Pizza Dough", "Mozzarella", "Tomato Sauce", "Basil"],
        "Mexican Cuisine": ["Tortilla", "Guacamole", "Jalapeno", "Rice"],
        "Asian Cuisine": ["Rice", "Noodles", "Soy Sauce", "Sesame"],
        "Steaks & Grill": ["Beef Tenderloin", "Butter", "Rocket"],
        "Seafood": ["Salmon", "Shrimp", "Lemon", "Rocket"],
        "Main Courses": ["Chicken", "Rice", "Cream", "Tomato"],
        "Desserts": ["Chocolate", "Cream", "Butter", "Berries"],
        "Hot Drinks": ["Coffee", "Milk"],
        "Soft Drinks": ["Lemon", "Mint", "Ice"],
        "Mocktails": ["Lemon", "Mint", "Ice", "Berries"],
        "Cocktails": ["Lemon", "Mint", "Ice"],
        "Beers": ["Ice"],
        "Wines": ["Berries"],
    }.get(category_name, ["Special Sauce"])

    names = list(base)
    lowered = title_en.lower()

    if "chicken" in lowered:
        names.append("Chicken")
    if "beef" in lowered or "steak" in lowered:
        names.append("Beef Tenderloin")
    if "salmon" in lowered or "sushi" in lowered:
        names.append("Salmon")
    if "shrimp" in lowered:
        names.append("Shrimp")
    if "avocado" in lowered:
        names.append("Avocado")

    return list(dict.fromkeys(names))


def build_description(title_tr, title_en, category_tr, category_en):
    return {
        "description_tr": f"{title_tr}, {category_tr.lower()} seçkisinin premium malzemelerle hazırlanan imza lezzetlerinden biridir.",
        "description_en": f"{title_en} is a signature {category_en.lower()} selection prepared with premium ingredients and balanced flavors.",
    }


def validate_item_details():
    menu_titles = [
        title_en
        for category in MENU
        for title_tr, title_en, price in category["items"]
    ]
    missing = sorted(set(menu_titles) - set(ITEM_DETAILS))
    extra = sorted(set(ITEM_DETAILS) - set(menu_titles))

    if missing:
        raise CommandError(
            "Missing ITEM_DETAILS entries: " + ", ".join(missing)
        )

    if extra:
        raise CommandError(
            "ITEM_DETAILS contains unknown menu items: " + ", ".join(extra)
        )


def is_featured_item(category_name, item_index, price):
    premium_thresholds = {
        "Breakfast": 900,
        "Steaks & Grill": 2200,
        "Seafood": 1450,
        "Wines": 3000,
    }

    return item_index in (1, 4) or price >= premium_thresholds.get(category_name, 950)


def seed_hotel_venues(owner, allergens):
    for venue_data in VENUE_MENUS:
        venue, created = Restaurant.objects.get_or_create(
            owner=owner,
            name=venue_data["name"],
            defaults={
                "name_tr": venue_data["name_tr"],
                "name_en": venue_data["name_en"],
                "venue_type": venue_data["venue_type"],
                "description": venue_data["description_en"],
                "description_tr": venue_data["description_tr"],
                "description_en": venue_data["description_en"],
                "address": "Hotel Resort",
                "phone": "+90 212 000 00 00",
                "email": "dining@menuflow.hotel",
                "opening_hours": venue_data["opening_hours"],
                "table_count": venue_data["table_count"],
                "is_active": True,
            }
        )

        venue.name_tr = venue_data["name_tr"]
        venue.name_en = venue_data["name_en"]
        venue.venue_type = venue_data["venue_type"]
        venue.description = venue_data["description_en"]
        venue.description_tr = venue_data["description_tr"]
        venue.description_en = venue_data["description_en"]
        venue.opening_hours = venue_data["opening_hours"]
        venue.table_count = venue_data["table_count"]
        venue.is_active = True
        venue.save()

        active_categories = [category["name_en"] for category in venue_data["categories"]]
        Category.objects.filter(restaurant=venue).exclude(name__in=active_categories).delete()

        active_titles = set()

        for index, category_data in enumerate(venue_data["categories"], start=1):
            category, created = Category.objects.get_or_create(
                restaurant=venue,
                name=category_data["name_en"]
            )
            category.name_tr = category_data["name_tr"]
            category.name_en = category_data["name_en"]
            category.description = category_data["description_en"]
            category.description_tr = category_data["description_tr"]
            category.description_en = category_data["description_en"]
            category.display_order = index
            category.save()

            for item_index, (title_en, title_tr, price, item_allergens, item_ingredients) in enumerate(category_data["items"], start=1):
                active_titles.add(title_en)
                item_detail = VENUE_ITEM_DETAILS.get(title_en) or ITEM_DETAILS.get(title_en)
                description_en = item_detail["description_en"] if item_detail else f"{title_en} is prepared for the {venue.name_en} experience with fresh hotel-grade ingredients."
                description_tr = item_detail["description_tr"] if item_detail else f"{title_tr}, {venue.name_tr} deneyimi için taze otel kalitesinde malzemelerle hazırlanır."
                detail_allergens = item_detail["allergens"] if item_detail else item_allergens
                detail_ingredients = item_detail["ingredients"] if item_detail else [
                    (ingredient_name, INGREDIENTS.get(ingredient_name, ingredient_name))
                    for ingredient_name in item_ingredients
                ]
                image = get_item_image(category.name, title_en, venue.name_en)
                menu_item, created = MenuItem.objects.get_or_create(
                    restaurant=venue,
                    title=title_en,
                    defaults={
                        "category": category,
                        "title_tr": title_tr,
                        "title_en": title_en,
                        "description": description_en,
                        "description_tr": description_tr,
                        "description_en": description_en,
                        "price": price,
                        "image": image,
                        "is_available": True,
                        "is_featured": item_index == 1,
                        "calories": item_detail["calories"] if item_detail else 240 + item_index * 45,
                        "prep_time": item_detail["prep_time"] if item_detail else 8 + item_index * 2,
                    }
                )
                menu_item.category = category
                menu_item.title_tr = title_tr
                menu_item.title_en = title_en
                menu_item.description = description_en
                menu_item.description_tr = description_tr
                menu_item.description_en = description_en
                menu_item.price = price
                menu_item.image = image
                menu_item.is_featured = item_index == 1
                menu_item.calories = item_detail["calories"] if item_detail else 240 + item_index * 45
                menu_item.prep_time = item_detail["prep_time"] if item_detail else 8 + item_index * 2
                menu_item.save()
                menu_item.allergens.set([allergens[name] for name in detail_allergens])

                ingredient_objects = []
                for ingredient_name_en, ingredient_name_tr in detail_ingredients:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name_en=ingredient_name_en,
                        defaults={"name_tr": ingredient_name_tr}
                    )
                    if ingredient.name_tr == ingredient.name_en and ingredient_name_tr != ingredient_name_en:
                        ingredient.name_tr = ingredient_name_tr
                        ingredient.save(update_fields=["name_tr"])
                    ingredient_objects.append(ingredient)

                menu_item.ingredients.set(ingredient_objects)

        MenuItem.objects.filter(restaurant=venue).exclude(title__in=active_titles).delete()


class Command(BaseCommand):

    help = 'Seeds a premium restaurant chain style menu'

    def handle(self, *args, **kwargs):
        validate_item_details()

        User = get_user_model()
        owner, created = User.objects.get_or_create(
            username='demo_owner',
            defaults={
                'email': 'owner@menuflow.demo',
                'role': 'OWNER',
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            owner.set_password('DemoOwner123!')
            owner.save()

        restaurant = Restaurant.objects.first()

        if not restaurant:
            restaurant = Restaurant.objects.create(
                owner=owner,
                name='The Grand Atrium Restaurant',
                name_tr='The Grand Atrium Restaurant',
                name_en='The Grand Atrium Restaurant',
                description='Premium all-day dining restaurant with global dishes and hotel service.',
                description_tr='Global lezzetler ve otel servisiyle premium ana restoran.',
                description_en='Premium all-day dining restaurant with global dishes and hotel service.',
                address='MenuFlow Hotel Resort',
                phone='+90 212 000 00 00',
                email='dining@menuflow.hotel',
                opening_hours='07:00 - 23:59',
                venue_type='restaurant',
                table_count=80,
                is_active=True,
            )

        restaurant.name_tr = restaurant.name_tr or restaurant.name
        restaurant.name_en = restaurant.name_en or restaurant.name
        restaurant.description_tr = restaurant.description_tr or restaurant.description
        restaurant.description_en = restaurant.description_en or restaurant.description
        restaurant.venue_type = "restaurant"
        restaurant.is_active = True
        restaurant.save(update_fields=["name_tr", "name_en", "description_tr", "description_en", "venue_type", "is_active"])

        allergens = {
            name: Allergen.objects.get_or_create(name=name)[0]
            for name in ALLERGEN_NAMES
        }

        ingredients = {}
        for name_en, name_tr in INGREDIENTS.items():
            ingredient, created = Ingredient.objects.get_or_create(
                name_en=name_en,
                defaults={"name_tr": name_tr}
            )

            if not created and ingredient.name_tr != name_tr:
                ingredient.name_tr = name_tr
                ingredient.save(update_fields=["name_tr"])

            ingredients[name_en] = ingredient

        active_category_names = [category["name_en"] for category in MENU]
        Category.objects.filter(restaurant=restaurant).exclude(name__in=active_category_names).delete()

        active_item_titles = set()

        for index, category_data in enumerate(MENU, start=1):
            category, created = Category.objects.get_or_create(
                restaurant=restaurant,
                name=category_data["name_en"]
            )
            category.name_tr = category_data["name_tr"]
            category.name_en = category_data["name_en"]
            category.description = category_data["description_en"]
            category.description_tr = category_data["description_tr"]
            category.description_en = category_data["description_en"]
            category.display_order = index
            category.save(update_fields=[
                "name_tr", "name_en", "description", "description_tr", "description_en", "display_order"
            ])

            for item_index, (title_tr, title_en, price) in enumerate(category_data["items"], start=1):
                active_item_titles.add(title_en)
                image = get_item_image(category.name, title_en, restaurant.name_en)
                item_detail = ITEM_DETAILS[title_en]
                prep_time = item_detail["prep_time"]
                calories = item_detail["calories"]

                menu_item, created = MenuItem.objects.get_or_create(
                    restaurant=restaurant,
                    title=title_en,
                    defaults={
                        "category": category,
                        "title_tr": title_tr,
                        "title_en": title_en,
                        "description": item_detail["description_en"],
                        "description_tr": item_detail["description_tr"],
                        "description_en": item_detail["description_en"],
                        "price": price,
                        "image": image,
                        "is_available": True,
                        "is_featured": is_featured_item(category.name, item_index, price),
                        "calories": calories,
                        "prep_time": prep_time,
                    }
                )

                menu_item.category = category
                menu_item.title_tr = title_tr
                menu_item.title_en = title_en
                menu_item.description = item_detail["description_en"]
                menu_item.description_tr = item_detail["description_tr"]
                menu_item.description_en = item_detail["description_en"]
                menu_item.price = price
                menu_item.image = image
                menu_item.is_featured = is_featured_item(category.name, item_index, price)
                menu_item.calories = calories
                menu_item.prep_time = prep_time
                menu_item.save()

                menu_item.allergens.set([
                    allergens[name]
                    for name in item_detail["allergens"]
                ])

                item_ingredients = []

                for name_en, name_tr in item_detail["ingredients"]:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name_en=name_en,
                        defaults={"name_tr": name_tr}
                    )

                    if not created and ingredient.name_tr != name_tr:
                        ingredient.name_tr = name_tr
                        ingredient.save(update_fields=["name_tr"])

                    item_ingredients.append(ingredient)

                menu_item.ingredients.set([
                    ingredient
                    for ingredient in item_ingredients
                ])

        MenuItem.objects.filter(restaurant=restaurant).exclude(title__in=active_item_titles).delete()

        seed_hotel_venues(restaurant.owner, allergens)

        self.stdout.write(self.style.SUCCESS('Premium hotel dining venues seeded successfully!'))
