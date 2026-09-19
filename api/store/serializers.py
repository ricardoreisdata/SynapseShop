from rest_framework import serializers

from .models import Category, Item


class CategorySerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "item_count",
            "created_at",
            "updated_at",
        ]


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "sku",
            "category",
            "category_name",
            "price",
            "stock",
            "active",
            "created_at",
            "updated_at",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("O preco deve ser maior que zero.")
        return value