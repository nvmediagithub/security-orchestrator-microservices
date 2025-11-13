"""
Модели данных для Vulnerable API Service
Содержит Pydantic модели с намеренными уязвимостями
"""

from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import re


class UserBase(BaseModel):
    """Базовая модель пользователя с уязвимостями валидации"""
    username: str
    email: EmailStr
    role: str = "user"
    
    # Уязвимость: Слабая валидация пароля
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username should be at least 3 characters')
        return v
    
    # Уязвимость: Нет валидации на специальные символы (potential XSS)
    @validator('email')
    def validate_email(cls, v):
        # Уязвимость: Не проверяем на потенциально опасные символы в email
        return v


class UserCreate(UserBase):
    """Модель для создания пользователя с уязвимостями"""
    password: str
    
    # Уязвимость: Слабая валидация пароля
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 4:  # Очень слабый пароль
            raise ValueError('Password should be at least 4 characters')
        return v


class UserLogin(BaseModel):
    """Модель для входа в систему"""
    username: str
    password: str


class User(UserBase):
    """Модель пользователя с дополнительными полями"""
    id: int
    created_at: str
    
    class Config:
        # Уязвимость: orm_mode может привести к information disclosure
        orm_mode = True


class UserWithPassword(User):
    """Уязвимость: Модель, которая раскрывает пароли пользователей"""
    password: str  # НЕБЕЗОПАСНО!


class OrderBase(BaseModel):
    """Базовая модель заказа"""
    product_name: str
    amount: float
    status: str = "pending"
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class OrderCreate(OrderBase):
    """Модель для создания заказа"""
    user_id: int


class Order(OrderBase):
    """Модель заказа"""
    id: int
    user_id: int
    created_at: str
    
    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    """Базовая модель платежа с критическими уязвимостями"""
    user_id: int
    order_id: int
    amount: float
    card_number: str
    cvv: str
    cardholder_name: str
    
    # Уязвимость: Слабая валидация номера карты
    @validator('card_number')
    def validate_card_number(cls, v):
        # Уязвимость: Не проверяем формат и не маскируем номер
        if len(v) < 13 or len(v) > 19:
            raise ValueError('Invalid card number length')
        return v
    
    # Уязвимость: CVV не шифруется и хранится как есть
    @validator('cvv')
    def validate_cvv(cls, v):
        if len(v) not in [3, 4]:
            raise ValueError('Invalid CVV length')
        return v


class PaymentCreate(PaymentBase):
    """Модель для создания платежа"""
    pass


class Payment(PaymentBase):
    """Модель платежа - раскрывает все данные карты!"""
    id: int
    created_at: str
    
    class Config:
        orm_mode = True


class PaymentWithFullCardData(Payment):
    """КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Раскрытие полных данных карты"""
    full_card_data: Dict[str, Any]  # НЕБЕЗОПАСНО!
    encryption_key: str  # НЕБЕЗОПАСНО!


class AdminConfig(BaseModel):
    """Модель административной конфигурации с секретами"""
    admin_password: str
    secret_key: str
    database_path: str
    debug_mode: bool
    allow_origins: List[str]
    api_keys: List[str]
    internal_ips: List[str]
    
    class Config:
        # Уязвимость: Не скрываем секретные поля в логах
        schema_extra = {
            "example": {
                "admin_password": "admin123",
                "secret_key": "super_secret_key_123",
                "database_path": "vulnerable.db",
                "debug_mode": True,
                "allow_origins": ["*"],
                "api_keys": ["sk-1234567890abcdef"],
                "internal_ips": ["192.168.1.100", "10.0.0.5"]
            }
        }


class SearchRequest(BaseModel):
    """Модель поискового запроса с SQL injection уязвимостью"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    
    # Уязвимость: Нет санитизации пользовательского ввода
    @validator('query')
    def validate_query(cls, v):
        # Уязвимость: Не проверяем на SQL injection
        return v


class FileUpload(BaseModel):
    """Модель для загрузки файлов с уязвимостями"""
    filename: str
    content_type: str
    size: int
    
    @validator('filename')
    def validate_filename(cls, v):
        # Уязвимость: Не проверяем на path traversal
        return v
    
    @validator('size')
    def validate_size(cls, v):
        # Уязвимость: Нет проверки на максимальный размер
        if v < 0:
            raise ValueError('Size must be positive')
        return v


class APIKey(BaseModel):
    """Модель API ключа"""
    key_id: str
    key_value: str
    permissions: List[str]
    created_at: str
    expires_at: Optional[str] = None
    
    class Config:
        # Уязвимость: Ключи могут быть раскрыты
        schema_extra = {
            "example": {
                "key_id": "key_001",
                "key_value": "sk-1234567890abcdef1234567890abcdef",
                "permissions": ["read", "write", "admin"],
                "created_at": "2023-01-01T00:00:00Z",
                "expires_at": "2024-01-01T00:00:00Z"
            }
        }


class DebugInfo(BaseModel):
    """Модель отладочной информации (НЕБЕЗОПАСНО для production)"""
    system_info: Dict[str, Any]
    environment_variables: Dict[str, str]  # КРИТИЧЕСКАЯ УЯЗВИМОСТЬ!
    database_queries: List[str]  # Уязвимость: раскрытие SQL
    internal_paths: List[str]  # Уязвимость: information disclosure
    memory_usage: Dict[str, Any]
    active_connections: List[Dict[str, Any]]
    
    class Config:
        # Уязвимость: Вся отладочная информация доступна
        schema_extra = {
            "example": {
                "system_info": {
                    "os": "Linux 5.4.0",
                    "python_version": "3.9.7",
                    "hostname": "vulnerable-server"
                },
                "environment_variables": {
                    "DATABASE_URL": "sqlite:///vulnerable.db",
                    "SECRET_KEY": "super_secret_key_123",
                    "ADMIN_PASSWORD": "admin123"
                },
                "database_queries": [
                    "SELECT * FROM users WHERE id = 1",
                    "SELECT password FROM users WHERE username = 'admin'"
                ],
                "internal_paths": ["/var/log/app.log", "/etc/passwd"],
                "memory_usage": {"used": "256MB", "total": "512MB"},
                "active_connections": [{"ip": "192.168.1.100", "user": "admin"}]
            }
        }


class SecurityAudit(BaseModel):
    """Модель для результатов аудита безопасности"""
    vulnerability_count: int
    critical_issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    scan_timestamp: str
    scan_duration: float
    
    class Config:
        schema_extra = {
            "example": {
                "vulnerability_count": 15,
                "critical_issues": [
                    "Отсутствие аутентификации на admin endpoints",
                    "SQL injection в /api/v1/users",
                    "Раскрытие данных кредитных карт",
                    "Отсутствие HTTPS"
                ],
                "warnings": [
                    "Слабая валидация входных данных",
                    "Отсутствие rate limiting",
                    "CORS политика слишком мягкая"
                ],
                "recommendations": [
                    "Реализовать аутентификацию",
                    "Использовать HTTPS",
                    "Добавить валидацию и санитизацию",
                    "Настроить proper CORS"
                ],
                "scan_timestamp": "2023-01-01T12:00:00Z",
                "scan_duration": 2.34
            }
        }


class ErrorResponse(BaseModel):
    """Модель ответа с ошибкой"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "error": "AuthenticationError",
                "message": "Invalid credentials",
                "details": {"attempts": 3, "last_attempt": "2023-01-01T12:00:00Z"},
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }