"""
CraveHub — Load Sample Data Script
Run with: python manage.py shell < scripts/load_sample_data.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()
from datetime import date
from decimal import Decimal

from categories.models import Category
from restaurants.models import Restaurant, RestaurantAddress, RestaurantCategory, FavoriteRestaurant
from menu.models import MenuCategory, MenuItem
from offers.models import Offer, SavedOffer
from banners.models import Banner
from accounts.models import User, UserAddress, UserSettings
from payments.models import SavedPaymentMethod

print("=" * 60)
print("  CraveHub — Loading Sample Data")
print("=" * 60)

# ──────────────────────────────────────────────
# 1. CATEGORIES
# ──────────────────────────────────────────────
print("\n[1/6] Creating Categories...")

categories_data = [
    {
        "name": "Mexican",
        "image": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600",
        "icon": "https://img.icons8.com/color/96/taco.png",
        "display_order": 5,
    },
    {
        "name": "Italian",
        "image": "https://images.unsplash.com/photo-1498579150354-977475b7ea0b?w=600",
        "icon": "https://img.icons8.com/color/96/pizza.png",
        "display_order": 6,
    },
    {
        "name": "Seafood",
        "image": "https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?w=600",
        "icon": "https://img.icons8.com/color/96/shrimp.png",
        "display_order": 7,
    },
    {
        "name": "Street Food",
        "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
        "icon": "https://img.icons8.com/color/96/street-food.png",
        "display_order": 8,
    },
]

created_categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        name=cat_data["name"],
        defaults={
            "image": cat_data["image"],
            "icon": cat_data["icon"],
            "display_order": cat_data["display_order"],
            "is_active": True,
        },
    )
    created_categories[cat_data["name"]] = cat
    status = "CREATED" if created else "EXISTS"
    print(f"  {status}: {cat.name} (slug: {cat.slug})")

# ──────────────────────────────────────────────
# 2. RESTAURANTS
# ──────────────────────────────────────────────
print("\n[2/6] Creating Restaurants...")

restaurants_data = [
    {
        "name": "El Fuego Cantina",
        "description": "Authentic Mexican street food with fiery salsas, hand-rolled burritos, and signature margaritas. Born on the streets of Oaxaca, perfected in your city.",
        "logo": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=200",
        "cover_image": "https://images.unsplash.com/photo-1552332386-f8dd00dc2f85?w=1200",
        "rating": Decimal("4.4"),
        "total_reviews": 312,
        "average_delivery_time": 35,
        "minimum_order_amount": Decimal("199.00"),
        "delivery_fee": Decimal("25.00"),
        "preparation_time": 20,
        "is_pure_veg": False,
        "is_featured": True,
        "restaurant_type": "food",
        "categories": ["Mexican"],
        "address": {
            "address": "42 MG Road, Koramangala",
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "pincode": "560034",
            "latitude": Decimal("12.935200"),
            "longitude": Decimal("77.614700"),
        },
    },
    {
        "name": "Trattoria Bella Vita",
        "description": "Rustic Italian comfort food — hand-tossed Neapolitan pizzas, creamy risottos, and fresh pastas made daily. A little piece of Tuscany on your plate.",
        "logo": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=200",
        "cover_image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200",
        "rating": Decimal("4.6"),
        "total_reviews": 487,
        "average_delivery_time": 40,
        "minimum_order_amount": Decimal("249.00"),
        "delivery_fee": Decimal("35.00"),
        "preparation_time": 25,
        "is_pure_veg": False,
        "is_featured": True,
        "restaurant_type": "food",
        "categories": ["Italian"],
        "address": {
            "address": "15 Church Street, Brigade Road",
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "pincode": "560001",
            "latitude": Decimal("12.975800"),
            "longitude": Decimal("77.607100"),
        },
    },
    {
        "name": "The Grand Fork",
        "description": "European-inspired continental dining — from golden French toast to sizzling steaks. Classic recipes with a modern, urban twist.",
        "logo": "https://images.unsplash.com/photo-1550966871-3ed3cdb51f3a?w=200",
        "cover_image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200",
        "rating": Decimal("4.2"),
        "total_reviews": 198,
        "average_delivery_time": 45,
        "minimum_order_amount": Decimal("299.00"),
        "delivery_fee": Decimal("40.00"),
        "preparation_time": 30,
        "is_pure_veg": False,
        "is_featured": False,
        "restaurant_type": "food",
        "categories": ["Italian"],
        "address": {
            "address": "88 Park Avenue, Indiranagar",
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "pincode": "560038",
            "latitude": Decimal("12.978500"),
            "longitude": Decimal("77.640600"),
        },
    },
    {
        "name": "Chaat Chowk",
        "description": "Delhi's favourite street food flavours, now at your doorstep. Tangy chaats, crispy tikkis, loaded kulhad chai, and everything that makes Indian street food legendary.",
        "logo": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=200",
        "cover_image": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=1200",
        "rating": Decimal("4.1"),
        "total_reviews": 534,
        "average_delivery_time": 25,
        "minimum_order_amount": Decimal("99.00"),
        "delivery_fee": Decimal("15.00"),
        "preparation_time": 15,
        "is_pure_veg": True,
        "is_featured": True,
        "restaurant_type": "food",
        "categories": ["Street Food"],
        "address": {
            "address": "7 Chandni Chowk, Old Delhi",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "pincode": "110006",
            "latitude": Decimal("28.656100"),
            "longitude": Decimal("77.230300"),
        },
    },
    {
        "name": "The Coastal Catch",
        "description": "Fresh-from-the-coast seafood — Mangalorean fish curries, Goan prawn masalas, and crispy fried calamari. Every dish celebrates India's stunning coastline.",
        "logo": "https://images.unsplash.com/photo-1579631542720-3a87824fff86?w=200",
        "cover_image": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=1200",
        "rating": Decimal("4.5"),
        "total_reviews": 276,
        "average_delivery_time": 40,
        "minimum_order_amount": Decimal("249.00"),
        "delivery_fee": Decimal("30.00"),
        "preparation_time": 25,
        "is_pure_veg": False,
        "is_featured": True,
        "restaurant_type": "food",
        "categories": ["Seafood"],
        "address": {
            "address": "22 Bandra Bandstand, Bandra West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "pincode": "400050",
            "latitude": Decimal("19.044500"),
            "longitude": Decimal("72.821400"),
        },
    },
    {
        "name": "MoMo Junction",
        "description": "Steaming hot momos, crunchy rolls, and fiery Tibetan-style sauces. From classic steamed to tandoori and cheese-pull momos — the ultimate momo experience.",
        "logo": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=200",
        "cover_image": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=1200",
        "rating": Decimal("4.3"),
        "total_reviews": 423,
        "average_delivery_time": 25,
        "minimum_order_amount": Decimal("129.00"),
        "delivery_fee": Decimal("20.00"),
        "preparation_time": 15,
        "is_pure_veg": False,
        "is_featured": False,
        "restaurant_type": "food",
        "categories": ["Street Food"],
        "address": {
            "address": "3 Hudson Lane, GTB Nagar",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "pincode": "110009",
            "latitude": Decimal("28.698900"),
            "longitude": Decimal("77.210200"),
        },
    },
]

created_restaurants = {}
for rest_data in restaurants_data:
    cats = rest_data.pop("categories")
    addr_data = rest_data.pop("address")

    rest, created = Restaurant.objects.get_or_create(
        name=rest_data["name"],
        defaults=rest_data,
    )
    created_restaurants[rest.name] = rest
    status = "CREATED" if created else "EXISTS"
    print(f"  {status}: {rest.name} (slug: {rest.slug})")

    if created:
        # Create address
        RestaurantAddress.objects.get_or_create(
            restaurant=rest,
            defaults=addr_data,
        )
        print(f"    + Address: {addr_data['address']}, {addr_data['city']}")

        # Link categories
        for cat_name in cats:
            if cat_name in created_categories:
                RestaurantCategory.objects.get_or_create(
                    restaurant=rest,
                    category=created_categories[cat_name],
                )
                print(f"    + Category: {cat_name}")

# ──────────────────────────────────────────────
# 3. MENU CATEGORIES & ITEMS
# ──────────────────────────────────────────────
print("\n[3/6] Creating Menu Categories...")
print("[4/6] Creating Menu Items...")

menu_data = {
    "El Fuego Cantina": {
        "Starters": {
            "order": 1,
            "items": [
                {"name": "Loaded Nachos Supreme", "description": "Crispy tortilla chips topped with melted cheese, jalapeños, sour cream, and guacamole", "image": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?w=400", "price": Decimal("249.00"), "discounted_price": Decimal("199.00"), "is_veg": True, "calories": 520},
                {"name": "Chicken Quesadilla", "description": "Grilled flour tortilla stuffed with shredded chicken, bell peppers, and mozzarella", "image": "https://images.unsplash.com/photo-1618040996337-56904b7850b9?w=400", "price": Decimal("279.00"), "discounted_price": None, "is_veg": False, "calories": 480},
                {"name": "Spicy Chicken Wings (8 pcs)", "description": "Deep-fried wings tossed in chipotle-habanero sauce with ranch dip", "image": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=400", "price": Decimal("349.00"), "discounted_price": Decimal("299.00"), "is_veg": False, "calories": 640},
            ],
        },
        "Tacos & Burritos": {
            "order": 2,
            "items": [
                {"name": "Classic Beef Tacos (3 pcs)", "description": "Seasoned ground beef, shredded lettuce, diced tomatoes, and cheddar on corn tortillas", "image": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=400", "price": Decimal("329.00"), "discounted_price": Decimal("289.00"), "is_veg": False, "calories": 580},
                {"name": "Paneer Tikka Burrito", "description": "Smoky paneer, cilantro rice, rajma, pico de gallo, wrapped in a jumbo flour tortilla", "image": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400", "price": Decimal("299.00"), "discounted_price": None, "is_veg": True, "calories": 620},
            ],
        },
        "Bowls": {
            "order": 3,
            "items": [
                {"name": "Chicken Burrito Bowl", "description": "Seasoned chicken, cilantro lime rice, black beans, corn salsa, and chipotle mayo", "image": "https://images.unsplash.com/photo-1543339308-d595c3a7650d?w=400", "price": Decimal("319.00"), "discounted_price": Decimal("269.00"), "is_veg": False, "calories": 550},
            ],
        },
        "Sides & Extras": {
            "order": 4,
            "items": [
                {"name": "Churros with Chocolate Sauce", "description": "Crispy cinnamon-sugar churros served with warm Belgian chocolate dipping sauce", "image": "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400", "price": Decimal("179.00"), "discounted_price": None, "is_veg": True, "calories": 380},
                {"name": "Mexican Street Corn (Elote)", "description": "Grilled corn on the cob with mayo, cotija cheese, chili powder, and lime", "image": "https://images.unsplash.com/photo-1470119693884-47d3a1d1f180?w=400", "price": Decimal("149.00"), "discounted_price": None, "is_veg": True, "calories": 220},
            ],
        },
        "Beverages": {
            "order": 5,
            "items": [
                {"name": "Horchata (Iced Rice Drink)", "description": "Traditional Mexican cinnamon-vanilla rice milk, served ice-cold", "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400", "price": Decimal("129.00"), "discounted_price": None, "is_veg": True, "calories": 180},
                {"name": "Mango Jalapeño Cooler", "description": "Fresh mango purée with a hint of jalapeño and lime, shaken with ice", "image": "https://images.unsplash.com/photo-1546173159-315724a31696?w=400", "price": Decimal("149.00"), "discounted_price": None, "is_veg": True, "calories": 150},
            ],
        },
    },
    "Trattoria Bella Vita": {
        "Antipasti": {
            "order": 1,
            "items": [
                {"name": "Bruschetta al Pomodoro", "description": "Toasted ciabatta topped with diced Roma tomatoes, fresh basil, garlic, and extra virgin olive oil", "image": "https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?w=400", "price": Decimal("199.00"), "discounted_price": None, "is_veg": True, "calories": 280},
                {"name": "Garlic Bread with Cheese", "description": "Toasted baguette with garlic butter and melted mozzarella (4 pcs)", "image": "https://images.unsplash.com/photo-1619535860434-ba1f915b0d12?w=400", "price": Decimal("179.00"), "discounted_price": Decimal("149.00"), "is_veg": True, "calories": 340},
            ],
        },
        "Pizzas": {
            "order": 2,
            "items": [
                {"name": "Margherita Pizza (12\")", "description": "San Marzano tomato sauce, fresh mozzarella di bufala, basil, on hand-tossed dough", "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400", "price": Decimal("349.00"), "discounted_price": Decimal("299.00"), "is_veg": True, "calories": 720},
                {"name": "Pepperoni Pizza (12\")", "description": "Spicy pepperoni, mozzarella, tomato sauce, and a drizzle of chili oil", "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400", "price": Decimal("399.00"), "discounted_price": None, "is_veg": False, "calories": 850},
            ],
        },
        "Pasta": {
            "order": 3,
            "items": [
                {"name": "Spaghetti Aglio e Olio", "description": "Spaghetti sautéed in olive oil with garlic, red chili flakes, and parsley", "image": "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=400", "price": Decimal("279.00"), "discounted_price": None, "is_veg": True, "calories": 480},
                {"name": "Penne Arrabbiata", "description": "Penne in a fiery tomato sauce with garlic, red chilies, and fresh parsley", "image": "https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=400", "price": Decimal("269.00"), "discounted_price": Decimal("229.00"), "is_veg": True, "calories": 460},
                {"name": "Chicken Alfredo Fettuccine", "description": "Fettuccine in a rich, creamy Parmesan sauce with grilled chicken strips", "image": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=400", "price": Decimal("379.00"), "discounted_price": None, "is_veg": False, "calories": 680},
            ],
        },
        "Risotto & Mains": {
            "order": 4,
            "items": [
                {"name": "Mushroom Risotto", "description": "Arborio rice slow-cooked with porcini mushrooms, white wine, butter, and Parmesan", "image": "https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=400", "price": Decimal("329.00"), "discounted_price": Decimal("289.00"), "is_veg": True, "calories": 520},
            ],
        },
        "Dolci (Desserts)": {
            "order": 5,
            "items": [
                {"name": "Tiramisu", "description": "Layers of espresso-soaked ladyfingers, mascarpone cream, and cocoa dusting", "image": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400", "price": Decimal("229.00"), "discounted_price": None, "is_veg": True, "calories": 420},
                {"name": "Classic Lemonade (Italian Style)", "description": "Fresh-squeezed lemons, sparkling water, and a hint of rosemary", "image": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400", "price": Decimal("129.00"), "discounted_price": None, "is_veg": True, "calories": 120},
            ],
        },
    },
    "The Grand Fork": {
        "Soups & Salads": {
            "order": 1,
            "items": [
                {"name": "Classic Caesar Salad", "description": "Crisp romaine lettuce, Parmesan shavings, croutons, and house-made Caesar dressing", "image": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400", "price": Decimal("229.00"), "discounted_price": None, "is_veg": True, "calories": 320},
                {"name": "Cream of Mushroom Soup", "description": "Velvety smooth mushroom soup with a swirl of cream and toasted bread", "image": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400", "price": Decimal("179.00"), "discounted_price": Decimal("149.00"), "is_veg": True, "calories": 260},
                {"name": "French Onion Soup", "description": "Caramelized onion soup topped with a crusty bread slice and melted Gruyère", "image": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?w=400", "price": Decimal("199.00"), "discounted_price": None, "is_veg": True, "calories": 290},
            ],
        },
        "Starters": {
            "order": 2,
            "items": [
                {"name": "Fish & Chips", "description": "Beer-battered cod fillet with golden fries, mushy peas, and tartar sauce", "image": "https://images.unsplash.com/photo-1579208030886-b1f5b6bae22d?w=400", "price": Decimal("399.00"), "discounted_price": None, "is_veg": False, "calories": 650},
            ],
        },
        "Mains & Steaks": {
            "order": 3,
            "items": [
                {"name": "Grilled Chicken Steak", "description": "Herb-marinated chicken breast grilled to perfection, served with mashed potatoes and sautéed veggies", "image": "https://images.unsplash.com/photo-1558030006-450675393462?w=400", "price": Decimal("429.00"), "discounted_price": Decimal("379.00"), "is_veg": False, "calories": 580},
                {"name": "Chicken Cordon Bleu", "description": "Breaded chicken breast stuffed with ham and Swiss cheese, served with gravy", "image": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400", "price": Decimal("449.00"), "discounted_price": Decimal("399.00"), "is_veg": False, "calories": 620},
                {"name": "Spaghetti Bolognese", "description": "Al dente spaghetti in a rich, slow-cooked minced lamb ragù with Parmesan", "image": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400", "price": Decimal("349.00"), "discounted_price": None, "is_veg": False, "calories": 560},
            ],
        },
        "Sandwiches & Wraps": {
            "order": 4,
            "items": [
                {"name": "Veg Club Sandwich", "description": "Triple-decker with grilled veggies, lettuce, tomato, cheese, and herb mayo on sourdough", "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400", "price": Decimal("259.00"), "discounted_price": None, "is_veg": True, "calories": 420},
            ],
        },
        "Desserts": {
            "order": 5,
            "items": [
                {"name": "Chocolate Lava Cake", "description": "Warm, gooey chocolate cake with a molten center, served with vanilla ice cream", "image": "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400", "price": Decimal("249.00"), "discounted_price": None, "is_veg": True, "calories": 480},
                {"name": "Iced Americano", "description": "Double-shot espresso poured over ice with chilled water", "image": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=400", "price": Decimal("149.00"), "discounted_price": None, "is_veg": True, "calories": 15},
            ],
        },
    },
    "Chaat Chowk": {
        "Chaats": {
            "order": 1,
            "items": [
                {"name": "Raj Kachori", "description": "Crispy kachori filled with boiled potato, sprouts, curd, and tamarind-mint chutneys", "image": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400", "price": Decimal("129.00"), "discounted_price": Decimal("99.00"), "is_veg": True, "calories": 320},
                {"name": "Pani Puri (12 pcs)", "description": "Crispy puris with spiced potato filling, served with tangy mint water and sweet chutney", "image": "https://images.unsplash.com/photo-1625398407796-82650a8c135f?w=400", "price": Decimal("99.00"), "discounted_price": None, "is_veg": True, "calories": 240},
                {"name": "Aloo Tikki Chaat", "description": "Golden-fried potato patties topped with curd, chutneys, sev, and pomegranate seeds", "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400", "price": Decimal("119.00"), "discounted_price": None, "is_veg": True, "calories": 350},
                {"name": "Dahi Bhalla", "description": "Soft lentil dumplings soaked in sweetened curd, topped with tamarind chutney and cumin powder", "image": "https://images.unsplash.com/photo-1589733955941-5eeaf752f6dd?w=400", "price": Decimal("109.00"), "discounted_price": None, "is_veg": True, "calories": 280},
                {"name": "Papdi Chaat", "description": "Crispy papdis topped with boiled potatoes, chickpeas, yogurt, and chutneys", "image": "https://images.unsplash.com/photo-1567337710282-00832b415979?w=400", "price": Decimal("99.00"), "discounted_price": None, "is_veg": True, "calories": 260},
            ],
        },
        "Tikkis & Cutlets": {
            "order": 2,
            "items": [
                {"name": "Chole Bhature (2 pcs)", "description": "Fluffy deep-fried bhature with spicy Amritsari chole and pickled onions", "image": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=400", "price": Decimal("149.00"), "discounted_price": Decimal("129.00"), "is_veg": True, "calories": 580},
            ],
        },
        "Parathas & Rolls": {
            "order": 3,
            "items": [
                {"name": "Paneer Roll", "description": "Smoky tandoori paneer wrapped in a roomali roti with onions, mint chutney, and lemon", "image": "https://images.unsplash.com/photo-1628294895950-9805252327bc?w=400", "price": Decimal("159.00"), "discounted_price": None, "is_veg": True, "calories": 380},
                {"name": "Masala Dosa (Regular)", "description": "Crispy golden dosa stuffed with spiced potato filling, served with sambar and coconut chutney", "image": "https://images.unsplash.com/photo-1630383249896-424e482df921?w=400", "price": Decimal("139.00"), "discounted_price": Decimal("119.00"), "is_veg": True, "calories": 360},
            ],
        },
        "Snacks": {
            "order": 4,
            "items": [],
        },
        "Drinks": {
            "order": 5,
            "items": [
                {"name": "Kulhad Chai", "description": "Authentic clay-pot chai brewed with ginger, cardamom, and whole milk", "image": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=400", "price": Decimal("49.00"), "discounted_price": None, "is_veg": True, "calories": 90},
                {"name": "Fresh Sugarcane Juice", "description": "Cold-pressed sugarcane with ginger and lemon", "image": "https://images.unsplash.com/photo-1622597467836-f3285f2131b8?w=400", "price": Decimal("69.00"), "discounted_price": None, "is_veg": True, "calories": 120},
            ],
        },
    },
    "The Coastal Catch": {
        "Starters": {
            "order": 1,
            "items": [
                {"name": "Crispy Calamari Rings", "description": "Golden-fried squid rings with spicy aioli and lemon wedge", "image": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400", "price": Decimal("299.00"), "discounted_price": Decimal("249.00"), "is_veg": False, "calories": 380},
            ],
        },
        "Curries": {
            "order": 2,
            "items": [
                {"name": "Goan Prawn Curry", "description": "Juicy prawns simmered in a tangy coconut and kokum curry", "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400", "price": Decimal("379.00"), "discounted_price": None, "is_veg": False, "calories": 420},
                {"name": "Crab Masala", "description": "Whole crab cooked in a fiery Chettinad-style masala", "image": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400", "price": Decimal("499.00"), "discounted_price": Decimal("449.00"), "is_veg": False, "calories": 520},
            ],
        },
        "Grilled & Fried": {
            "order": 3,
            "items": [
                {"name": "Mangalorean Fish Fry", "description": "Surmai fillet marinated in red masala, shallow-fried to a crispy golden crust", "image": "https://images.unsplash.com/photo-1580476262798-bddd9f4b7369?w=400", "price": Decimal("349.00"), "discounted_price": Decimal("299.00"), "is_veg": False, "calories": 380},
                {"name": "Butter Garlic Prawns", "description": "Tiger prawns tossed in a rich butter-garlic sauce with herbs", "image": "https://images.unsplash.com/photo-1625943553852-781c6dd46faa?w=400", "price": Decimal("429.00"), "discounted_price": None, "is_veg": False, "calories": 450},
                {"name": "Fish & Chips (Coastal Style)", "description": "Beer-battered pomfret with crispy sweet potato fries and wasabi mayo", "image": "https://images.unsplash.com/photo-1579208030886-b1f5b6bae22d?w=400", "price": Decimal("379.00"), "discounted_price": None, "is_veg": False, "calories": 580},
                {"name": "Grilled Lobster Tail", "description": "Half lobster tail grilled with herb butter, served with garlic bread and salad", "image": "https://images.unsplash.com/photo-1553247407-23251ce81f59?w=400", "price": Decimal("699.00"), "discounted_price": Decimal("599.00"), "is_veg": False, "calories": 360},
            ],
        },
        "Rice & Breads": {
            "order": 4,
            "items": [
                {"name": "Seafood Fried Rice", "description": "Wok-tossed basmati rice with prawns, squid, mussels, and Asian sauces", "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400", "price": Decimal("329.00"), "discounted_price": None, "is_veg": False, "calories": 520},
            ],
        },
        "Beverages": {
            "order": 5,
            "items": [
                {"name": "Kokum Soda", "description": "Refreshing Goan kokum concentrate with soda water and cumin", "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400", "price": Decimal("89.00"), "discounted_price": None, "is_veg": True, "calories": 60},
                {"name": "Sol Kadhi", "description": "Traditional Goan digestif made with kokum and coconut milk", "image": "https://images.unsplash.com/photo-1541658016709-82535e94bc69?w=400", "price": Decimal("79.00"), "discounted_price": None, "is_veg": True, "calories": 80},
            ],
        },
    },
    "MoMo Junction": {
        "Steamed Momos": {
            "order": 1,
            "items": [
                {"name": "Classic Steamed Veg Momos (8 pcs)", "description": "Cabbage, carrot, and onion filling steamed in thin wrappers, with spicy red chutney", "image": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400", "price": Decimal("129.00"), "discounted_price": Decimal("99.00"), "is_veg": True, "calories": 280},
                {"name": "Chicken Steamed Momos (8 pcs)", "description": "Minced chicken with ginger, garlic, and spring onion filling, steamed to perfection", "image": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=400", "price": Decimal("159.00"), "discounted_price": None, "is_veg": False, "calories": 320},
            ],
        },
        "Fried & Tandoori Momos": {
            "order": 2,
            "items": [
                {"name": "Tandoori Momos (8 pcs)", "description": "Steamed momos charred on a tandoor with tikka masala, served with mint chutney", "image": "https://images.unsplash.com/photo-1626776876729-bab4369a5a5a?w=400", "price": Decimal("189.00"), "discounted_price": Decimal("159.00"), "is_veg": False, "calories": 360},
                {"name": "Fried Momos with Schezwan (8 pcs)", "description": "Crispy fried momos tossed in a fiery Schezwan sauce with sesame seeds", "image": "https://images.unsplash.com/photo-1625220194771-7ebdea0b70b9?w=400", "price": Decimal("179.00"), "discounted_price": None, "is_veg": False, "calories": 420},
                {"name": "Cheese Pull Momos (6 pcs)", "description": "Mozzarella-stuffed momos with a gooey cheese pull, served with dynamite sauce", "image": "https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=400", "price": Decimal("219.00"), "discounted_price": Decimal("189.00"), "is_veg": True, "calories": 480},
                {"name": "Afghani Momos (8 pcs)", "description": "Creamy, mildly spiced cashew-cream gravy momos topped with crushed almonds", "image": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400", "price": Decimal("209.00"), "discounted_price": Decimal("179.00"), "is_veg": False, "calories": 440},
                {"name": "Kurkure Momos (8 pcs)", "description": "Triple-coated crunchy momos deep-fried to golden perfection with dynamite mayo", "image": "https://images.unsplash.com/photo-1625220194771-7ebdea0b70b9?w=400", "price": Decimal("199.00"), "discounted_price": None, "is_veg": True, "calories": 460},
            ],
        },
        "Rolls & Wraps": {
            "order": 3,
            "items": [
                {"name": "Paneer Tikka Roll", "description": "Chargrilled paneer tikka wrapped in a laccha paratha with onion and green chutney", "image": "https://images.unsplash.com/photo-1628294895950-9805252327bc?w=400", "price": Decimal("169.00"), "discounted_price": None, "is_veg": True, "calories": 380},
                {"name": "Chicken Seekh Roll", "description": "Smoky chicken seekh kebab wrapped in a rumali roti with salad and chutney", "image": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400", "price": Decimal("189.00"), "discounted_price": None, "is_veg": False, "calories": 400},
            ],
        },
        "Specials": {
            "order": 4,
            "items": [],
        },
        "Drinks": {
            "order": 5,
            "items": [
                {"name": "Iced Lemon Tea", "description": "Freshly brewed black tea with lemon and honey, served over ice", "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400", "price": Decimal("79.00"), "discounted_price": None, "is_veg": True, "calories": 80},
            ],
        },
    },
}

total_categories_created = 0
total_items_created = 0

for rest_name, categories in menu_data.items():
    if rest_name not in created_restaurants:
        # Try to fetch from DB
        try:
            rest = Restaurant.objects.get(name=rest_name)
            created_restaurants[rest_name] = rest
        except Restaurant.DoesNotExist:
            print(f"  SKIPPED: Restaurant '{rest_name}' not found")
            continue

    rest = created_restaurants[rest_name]
    print(f"\n  📍 {rest_name}:")

    for cat_name, cat_data in categories.items():
        menu_cat, created = MenuCategory.objects.get_or_create(
            restaurant=rest,
            name=cat_name,
            defaults={"display_order": cat_data["order"]},
        )
        if created:
            total_categories_created += 1
        status = "+" if created else "="
        print(f"    {status} Menu Category: {cat_name}")

        for item_data in cat_data["items"]:
            item, created = MenuItem.objects.get_or_create(
                restaurant=rest,
                name=item_data["name"],
                defaults={
                    "category": menu_cat,
                    "description": item_data["description"],
                    "image": item_data["image"],
                    "price": item_data["price"],
                    "discounted_price": item_data["discounted_price"],
                    "is_veg": item_data["is_veg"],
                    "is_available": True,
                    "calories": item_data["calories"],
                },
            )
            if created:
                total_items_created += 1
            status = "+" if created else "="
            veg_icon = "🟢" if item_data["is_veg"] else "🔴"
            print(f"      {status} {veg_icon} {item_data['name']} — ₹{item_data['price']}")

print(f"\n  Menu Categories created: {total_categories_created}")
print(f"  Menu Items created: {total_items_created}")

# ──────────────────────────────────────────────
# 5. OFFERS
# ──────────────────────────────────────────────
print("\n[5/6] Creating Offers...")

offers_data = [
    {
        "title": "Flat ₹120 Off on Your First Order",
        "coupon_code": "FIRSTBITE120",
        "discount_type": "FLAT",
        "discount_value": Decimal("120.00"),
        "minimum_order_amount": Decimal("249.00"),
        "maximum_discount": None,
        "expiry_date": date(2026, 12, 31),
    },
    {
        "title": "25% Off on All Italian Orders",
        "coupon_code": "ITALIA25",
        "discount_type": "PERCENTAGE",
        "discount_value": Decimal("25.00"),
        "minimum_order_amount": Decimal("399.00"),
        "maximum_discount": Decimal("200.00"),
        "expiry_date": date(2026, 9, 30),
    },
    {
        "title": "Free Delivery Weekend Blast",
        "coupon_code": "FREEDEL",
        "discount_type": "FREE_DELIVERY",
        "discount_value": Decimal("50.00"),
        "minimum_order_amount": Decimal("199.00"),
        "maximum_discount": None,
        "expiry_date": date(2026, 8, 31),
    },
    {
        "title": "Mega Monsoon: ₹150 Off",
        "coupon_code": "MONSOON150",
        "discount_type": "FLAT",
        "discount_value": Decimal("150.00"),
        "minimum_order_amount": Decimal("499.00"),
        "maximum_discount": None,
        "expiry_date": date(2026, 7, 31),
    },
]

for offer_data in offers_data:
    offer, created = Offer.objects.get_or_create(
        coupon_code=offer_data["coupon_code"],
        defaults={
            "title": offer_data["title"],
            "discount_type": offer_data["discount_type"],
            "discount_value": offer_data["discount_value"],
            "minimum_order_amount": offer_data["minimum_order_amount"],
            "maximum_discount": offer_data["maximum_discount"],
            "expiry_date": offer_data["expiry_date"],
            "is_active": True,
        },
    )
    status = "CREATED" if created else "EXISTS"
    print(f"  {status}: {offer.coupon_code} — {offer.title}")

# ──────────────────────────────────────────────
# 6. BANNERS
# ──────────────────────────────────────────────
print("\n[6/6] Creating Banners...")

banners_data = [
    {
        "title": "🌧️ Monsoon Food Fest",
        "subtitle": "Flat 40% off on orders above ₹199 — use code MONSOON150",
        "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1200",
        "redirect_url": "/offers/",
        "priority": 1,
        "start_date": date(2026, 6, 14),
        "end_date": date(2026, 8, 31),
    },
    {
        "title": "🌮 New Cuisines Alert!",
        "subtitle": "Explore Mexican, Seafood & Continental — freshly added to CraveHub",
        "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1200",
        "redirect_url": "/restaurants/",
        "priority": 2,
        "start_date": date(2026, 6, 14),
        "end_date": date(2026, 7, 31),
    },
]

for banner_data in banners_data:
    banner, created = Banner.objects.get_or_create(
        title=banner_data["title"],
        defaults={
            "subtitle": banner_data["subtitle"],
            "image": banner_data["image"],
            "redirect_url": banner_data["redirect_url"],
            "priority": banner_data["priority"],
            "is_active": True,
            "start_date": banner_data["start_date"],
            "end_date": banner_data["end_date"],
        },
    )
    status = "CREATED" if created else "EXISTS"
    print(f"  {status}: {banner.title}")

# ──────────────────────────────────────────────
# 7. USER PROFILE SECTORS (TEST DATA)
# ──────────────────────────────────────────────
print("\n[7/7] Creating Test User Profile Data...")

user, created = User.objects.get_or_create(
    mobile_number="+919999999999",
    defaults={
        "full_name": "Test User",
        "email": "test@cravehub.com",
        "is_verified": True,
        "is_active": True,
        "is_staff": True,
        "is_superuser": True
    }
)
if created:
    user.set_password("cravehub123")
    user.save()
    print("  CREATED: Test User (+919999999999)")
else:
    print("  EXISTS: Test User (+919999999999)")

# Ensure UserSettings
UserSettings.objects.get_or_create(user=user)

# Add Addresses
addresses_data = [
    {
        "label": "Home",
        "flat_no": "Flat 404",
        "building_name": "Maple Woods",
        "street": "Outer Ring Road",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560103",
        "is_default": True
    },
    {
        "label": "Work",
        "flat_no": "Floor 5",
        "building_name": "Tech Park",
        "street": "Indiranagar",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560038",
        "is_default": False
    }
]

for addr_data in addresses_data:
    addr, addr_created = UserAddress.objects.get_or_create(
        user=user,
        label=addr_data["label"],
        defaults=addr_data
    )
    status = "CREATED" if addr_created else "EXISTS"
    print(f"  {status}: Address ({addr.label})")

# Add Payment Methods
payments_data = [
    {
        "provider": "HDFC Bank",
        "card_type": "Credit Card",
        "last_four": "4242",
        "is_default": True
    },
    {
        "provider": "Paytm Wallet",
        "card_type": "Wallet",
        "last_four": "9999",
        "is_default": False
    }
]

for pay_data in payments_data:
    pay, pay_created = SavedPaymentMethod.objects.get_or_create(
        user=user,
        provider=pay_data["provider"],
        card_type=pay_data["card_type"],
        defaults=pay_data
    )
    status = "CREATED" if pay_created else "EXISTS"
    print(f"  {status}: Payment Method ({pay.provider})")

# Add Favorite Restaurants (using a couple of restaurants we just created)
if created_restaurants:
    for name in ["El Fuego Cantina", "Trattoria Bella Vita"]:
        if name in created_restaurants:
            fav, fav_created = FavoriteRestaurant.objects.get_or_create(
                user=user,
                restaurant=created_restaurants[name]
            )
            status = "CREATED" if fav_created else "EXISTS"
            print(f"  {status}: Favorite Restaurant ({name})")

# Add Saved Offers
first_offer = Offer.objects.filter(coupon_code="FIRSTBITE120").first()
monsoon_offer = Offer.objects.filter(coupon_code="MONSOON150").first()

for offer in [first_offer, monsoon_offer]:
    if offer:
        saved_offer, so_created = SavedOffer.objects.get_or_create(
            user=user,
            offer=offer
        )
        status = "CREATED" if so_created else "EXISTS"
        print(f"  {status}: Saved Offer ({offer.coupon_code})")

# ──────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("  ✅ Sample Data Loading Complete!")
print("=" * 60)
print(f"  Categories:      {Category.objects.count()}")
print(f"  Restaurants:     {Restaurant.objects.count()}")
print(f"  Menu Categories: {MenuCategory.objects.count()}")
print(f"  Menu Items:      {MenuItem.objects.count()}")
print(f"  Offers:          {Offer.objects.count()}")
print(f"  Banners:         {Banner.objects.count()}")
print("=" * 60)
