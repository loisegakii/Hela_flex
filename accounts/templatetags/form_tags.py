from django import template
register = template.Library()

@register.filter(name='add_input_classes')
def add_input_classes(field):
    return field.as_widget(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
    })