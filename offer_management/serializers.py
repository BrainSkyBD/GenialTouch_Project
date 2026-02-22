from rest_framework import serializers
from .models import PromoCode

class PromoCodeApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    
    def validate_code(self, value):
        try:
            promo_code = PromoCode.objects.get(code=value, is_active=True)
            if not promo_code.is_valid:
                raise serializers.ValidationError("Promo code is expired or invalid")
            return value
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("Promo code does not exist")