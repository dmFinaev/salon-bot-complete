"""
EXCEPTIONS: Исключения для домена Клиента
"""

class ClientException(Exception):
    """Базовое исключение для клиентов"""
    pass

class InvalidClientDataException(ClientException):
    """Некорректные данные клиента"""
    pass

class ClientNotFoundException(ClientException):
    """Клиент не найден"""
    pass

class DuplicateClientException(ClientException):
    """Дубликат клиента"""
    pass
