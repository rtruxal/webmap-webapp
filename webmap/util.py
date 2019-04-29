class ValidationError(BaseException):
    pass

def raise_validation_err(text=''):
    raise ValidationError(text)