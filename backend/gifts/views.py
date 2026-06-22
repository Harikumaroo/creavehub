from rest_framework import generics, permissions
from .models import GiftCard, GiftOrder
from .serializers import GiftCardSerializer, GiftOrderSerializer

class GiftCardListView(generics.ListAPIView):
    queryset = GiftCard.objects.filter(is_active=True)
    serializer_class = GiftCardSerializer
    permission_classes = [permissions.AllowAny]

class GiftOrderCreateView(generics.CreateAPIView):
    serializer_class = GiftOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
