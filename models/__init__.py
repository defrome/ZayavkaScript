# Этот файл инициализирует все модели
from models.application import Application
from models.masters import Master, MasterTime
from models.users import User

__all__ = ['Application', 'Master', 'MasterTime', 'User']