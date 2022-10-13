from django.core.exceptions import ValidationError


def validate_empty(value):
    data = value.strip()
    if data == '':
        raise ValidationError('Поле текста не может быть пустым')
    return data
