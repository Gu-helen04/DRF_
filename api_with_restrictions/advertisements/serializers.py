from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement, AdvertisementStatusChoices


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at',)
        # read_onli_filds = ['user']

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # TODO: добавьте требуемую валидацию
        request = self.context["request"]
        status_new_ads = request.data.get('status')
        total_ads = Advertisement.objects.filter(creator=request.user, status=AdvertisementStatusChoices.OPEN)
        if request.method in ['POST', 'PATCH', 'PUT']:
            if len(total_ads) >= 10 and status_new_ads != AdvertisementStatusChoices.CLOSED:
                raise ValidationError('Ошибка: Количество объявлений в статусе:ОТКРЫТО, не может привешать 10-ти')
        return data
