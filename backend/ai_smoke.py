import os
import django
import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from accounts.models import User
from ai_engine.recommendation import RecommendationEngine

def run():
    mobile = "+919999999999"
    user = User.objects.filter(mobile_number=mobile).first()
    if not user:
        print('No smoke user found; run backend/smoke_tests.py first')
        return
    print('User:', user.id, user.mobile_number)
    result = RecommendationEngine.get_recommendations(user, context='home')
    pprint.pprint(result)

if __name__ == '__main__':
    run()
