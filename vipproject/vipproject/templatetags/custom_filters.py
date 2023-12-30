from django import template

register = template.Library()


@register.filter(name='exclude_order_id')
def exclude_order_id(queryset, order_id):
    return queryset.exclude(order_id=order_id)
