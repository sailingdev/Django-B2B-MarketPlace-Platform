from django import template

register = template.Library()

@register.filter(name='getByKey')
def getByKey(d, key):
    return d.get(key)

#func from https://stackoverflow.com/questions/401025/define-css-class-in-django-forms/41129192#41129192
@register.filter(name='addclass')
def addclass(field, given_class):
    existing_classes = field.field.widget.attrs.get('class', None)
    if existing_classes:
        if existing_classes.find(given_class) == -1:
            # if the given class doesn't exist in the existing classes
            classes = existing_classes + ' ' + given_class
        else:
            classes = existing_classes
    else:
        classes = given_class
    return field.as_widget(attrs={"class": classes})
