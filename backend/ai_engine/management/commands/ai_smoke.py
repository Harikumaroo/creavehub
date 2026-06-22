from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run AI smoke test for RecommendationEngine using the smoke user'

    def handle(self, *args, **options):
        try:
            from accounts.models import User
            from ai_engine.recommendation import RecommendationEngine
            import pprint

            mobile = "+919999999999"
            user = User.objects.filter(mobile_number=mobile).first()
            if not user:
                self.stdout.write(self.style.ERROR('No smoke user found; run backend/smoke_tests.py first'))
                return
            self.stdout.write(f'User: {user.id} {user.mobile_number}')
            result = RecommendationEngine.get_recommendations(user, context='home')
            pprint.pprint(result)
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'AI smoke failed: {exc}'))
