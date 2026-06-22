from django.test import TestCase

from accounts.models import User
from restaurants.models import Restaurant, RestaurantAddress
from menu.models import MenuItem, MenuCategory
from ai_engine.recommendation import RecommendationEngine
from ai_engine.services import AIService


class AIEngineTests(TestCase):

	def setUp(self):
		# create a smoke user
		self.user, _ = User.objects.get_or_create(mobile_number='+919999999999', defaults={'full_name': 'Smoke User'})

		# create a restaurant and address
		self.rest = Restaurant.objects.create(
			name='AI Test Restaurant',
			rating=4.5,
			is_active=True,
			is_open=True,
			delivery_fee=30.00,
		)
		RestaurantAddress.objects.create(
			restaurant=self.rest,
			address='1 Test St', city='TestCity', state='TS', pincode='560001'
		)

		# menu category + item
		cat = MenuCategory.objects.create(restaurant=self.rest, name='Main')
		MenuItem.objects.create(
			restaurant=self.rest,
			category=cat,
			name='Test Dish',
			price=100.00,
			is_available=True,
			is_veg=True,
		)

	def test_rule_based_recommendations(self):
		result = RecommendationEngine.get_recommendations(self.user, context='home')
		self.assertIsInstance(result, dict)
		self.assertIn('restaurants', result)
		self.assertIn('menu_items', result)

	def test_food_chat_fallback(self):
		reply = AIService.food_chat(self.user, 'hello', history=[])
		self.assertIsInstance(reply, str)
		self.assertTrue('Hey' in reply or 'help' in reply)

