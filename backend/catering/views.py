from rest_framework import generics, permissions
from .models import CateringMenu, CateringInquiry
from .serializers import CateringMenuSerializer, CateringInquirySerializer

class CateringMenuListView(generics.ListAPIView):
    queryset = CateringMenu.objects.filter(is_active=True).select_related("restaurant")
    serializer_class = CateringMenuSerializer
    permission_classes = [permissions.AllowAny]

class CateringInquiryCreateView(generics.CreateAPIView):
    serializer_class = CateringInquirySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
