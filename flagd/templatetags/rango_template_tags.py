from django import template

register = template.Library()

#@register.inclusion_tag('flagd/categories.html')

#def get_category_list(current_category=None):
    #return {'categories': Category.objects.all(), 'current_category': current_category}
