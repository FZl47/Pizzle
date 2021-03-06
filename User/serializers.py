from rest_framework.serializers import ModelSerializer
from Food import serializers as Food_Serializers
from Config import tools


class UserBasicSerializer(ModelSerializer):

    def to_representation(self, instance):
        # Base Fields
        d = {
            'name': instance.first_name,
            'family': instance.last_name,
            'full_name': instance.get_name(),
        }
        # Order
        order = instance.get_order_active()
        if order:
            d.update({
                'order_count_meal': order.get_details().count()
            })

        return d


class UserSerializer(ModelSerializer):
    def to_representation(self, instance):
        d = UserBasicSerializer(instance).data
        d.update({
            'address': AddressSerializer(instance.get_address(), many=True).data
        })
        return d


class AddressSerializer(ModelSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'address': tools.TextToShortText(instance.address, 20),
            'postal_code': instance.postal_code,
            'cost': str(instance.cost),
            'is_free':instance.is_free()
        }


def OrderDetailSerializer(orderdetails):
    results = []
    for orderdetail in orderdetails:
        meal = orderdetail.get_meal()
        meal_is_available = False if meal == None else meal.is_available()
        # Check if meal is not available delete object order detail
        if meal and meal_is_available:
            results.append(
                {
                    'id': orderdetail.id,
                    'count': orderdetail.count,
                    'meal': Food_Serializers.MealOrderDetailSerializer(meal).data,
                    'price': orderdetail.get_price()
                }
            )
        else:
            orderdetail.delete()
    return results


def OrderBasicSerializer(order):
    d = {
        'price': order.get_price_meals(),
        'price_without_discount': order.get_price_meals_without_discount()
    }
    return d

def OrderSerializer(order):
    details = OrderDetailSerializer(order.get_details())
    d = {
        'details': details,
        'is_not_empty': True if len(details) > 0 else False,
        'price': order.get_price_meals(),
        'price_without_discount': order.get_price_meals_without_discount()
    }
    return d
