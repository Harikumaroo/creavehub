import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
import django
django.setup()

from accounts.services import RegistrationService, TokenService, DeviceSessionService
from accounts.models import OTP, User


def run():
    try:
        mobile = "+919999999999"
        # Clean up any previous test user
        User.objects.filter(mobile_number=mobile).delete()

        print('1) Registration initiate')
        success, message, data = RegistrationService.initiate(mobile)
        print('   initiate ->', success, message, data)
        if not success:
            raise Exception('Registration initiation failed')

        # Mark OTP as verified directly (since SMS gateway is not available in tests)
        otp_qs = OTP.objects.filter(mobile_number=mobile, purpose=OTP.PURPOSE_REGISTER, is_used=False)
        otp = otp_qs.latest('created_at')
        otp.is_verified = True
        otp.save(update_fields=['is_verified'])
        print('   marked OTP verified:', otp.id)

        print('2) Registration complete')
        success, message, result = RegistrationService.complete(
            mobile_number=mobile,
            full_name='Smoke Tester',
            email='smoke@example.com',
            device_id='smoke-device-1',
            device_type='web',
            device_name='smoke-client',
            ip_address='127.0.0.1',
            user_agent='smoke-agent',
        )
        print('   complete ->', success, message)
        if not success:
            raise Exception('Registration complete failed')

        access = result.get('access_token')
        refresh = result.get('refresh_token')
        jti = result.get('jti') or None
        print('   tokens present:', bool(access), bool(refresh))

        print('3) Create additional tokens via TokenService')
        user = User.objects.get(mobile_number=mobile)
        tokens2 = TokenService.generate_tokens(user)
        print('   generated tokens ok:', 'access_token' in tokens2)

        print('4) Create device session via DeviceSessionService')
        session = DeviceSessionService.create_session(
            user=user,
            device_id='smoke-device-2',
            device_type='web',
            device_name='smoke-2',
            ip_address='127.0.0.1',
            user_agent='smoke-agent',
            refresh_token_id=tokens2.get('jti')
        )
        print('   session created:', session.id)

        print('5) Blacklist refresh token')
        ok = TokenService.blacklist_token(refresh)
        print('   blacklist result:', ok)

        print('SMOKE TESTS: SUCCESS')
    except Exception:
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    run()
