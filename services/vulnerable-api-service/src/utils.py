"""
Уязвимые утилиты для Vulnerable API Service
Содержит функции с намеренными уязвимостями безопасности

Уязвимости в этом файле:
1. Небезопасная работа с паролями
2. Слабое шифрование
3. Небезопасная сериализация
4. Information disclosure через логи
5. Path traversal
6. Небезопасная обработка файлов
7. SQL injection helper functions
8. Небезопасная аутентификация
"""

import os
import sqlite3
import hashlib
import secrets
import json
import base64
import pickle
import subprocess
import time
import re
from typing import Any, Dict, List, Optional
import logging


# Уязвимость: Слабая настройка логирования - может привести к information disclosure
logging.basicConfig(
    level=logging.DEBUG,  # Уязвимость: DEBUG логи в production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s:%(lineno)d',
    handlers=[
        logging.FileHandler('/tmp/vulnerable_app.log'),  # Уязвимость: Логи в /tmp
        logging.StreamHandler()  # Уязвимость: Вывод логов в stdout
    ]
)

logger = logging.getLogger("vulnerable_utils")


# Уязвимость: Небезопасное хеширование паролей
def hash_password_vulnerable(password: str) -> str:
    """
    Уязвимость: Использует MD5 вместо bcrypt/Argon2
    Также не использует соль
    """
    # Уязвимость: MD5 небезопасен для хеширования паролей
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    # Уязвимость: Логируем пароль в DEBUG режиме
    logger.debug(f"Password hash for '{password}': {password_hash}")
    
    return password_hash


def verify_password_vulnerable(password: str, password_hash: str) -> bool:
    """
    Уязвимость: Слабая проверка пароля
    """
    computed_hash = hash_password_vulnerable(password)
    is_valid = computed_hash == password_hash
    
    # Уязвимость: Логируем информацию о неудачной аутентификации
    if not is_valid:
        logger.warning(f"Failed login attempt - password: '{password}', hash: {password_hash}")
    else:
        logger.info(f"Successful login - password: '{password}'")  # Уязвимость: логируем пароль
    
    return is_valid


# Уязвимость: Небезопасная "криптография"
def encrypt_data_vulnerable(data: str, key: str = "default_key_123") -> str:
    """
    Уязвимость: Наивное "шифрование" с base64
    """
    try:
        # Уязвимость: Простое XOR "шифрование" (небезопасно)
        key_bytes = key.encode()
        data_bytes = data.encode()
        
        encrypted_bytes = bytes([data_byte ^ key_bytes[i % len(key_bytes)] 
                                for i, data_byte in enumerate(data_bytes)])
        
        # Уязвимость: Base64 не является шифрованием
        encrypted_base64 = base64.b64encode(encrypted_bytes).decode()
        
        logger.debug(f"Encrypted data '{data}' with key '{key}': {encrypted_base64}")
        
        return encrypted_base64
    except Exception as e:
        logger.error(f"Encryption error for data '{data}': {str(e)}")
        return data  # Уязвимость: возвращаем исходные данные при ошибке


def decrypt_data_vulnerable(encrypted_data: str, key: str = "default_key_123") -> str:
    """
    Уязвимость: Небезопасное "дешифрование"
    """
    try:
        # Уязвимость: Base64 не является шифрованием
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        key_bytes = key.encode()
        
        decrypted_bytes = bytes([encrypted_byte ^ key_bytes[i % len(key_bytes)] 
                                for i, encrypted_byte in enumerate(encrypted_bytes)])
        
        decrypted_data = decrypted_bytes.decode()
        
        logger.debug(f"Decrypted data '{encrypted_data}': {decrypted_data}")
        
        return decrypted_data
    except Exception as e:
        logger.error(f"Decryption error for data '{encrypted_data}': {str(e)}")
        return encrypted_data  # Уязвимость: возвращаем зашифрованные данные при ошибке


# Уязвимость: Небезопасная сериализация
def serialize_data_vulnerable(data: Any) -> str:
    """
    Уязвимость: Использует pickle для сериализации (небезопасно)
    """
    try:
        # Уязвимость: pickle может выполнять произвольный код
        serialized_data = pickle.dumps(data)
        serialized_base64 = base64.b64encode(serialized_data).decode()
        
        logger.debug(f"Serialized data: {serialized_base64}")
        
        return serialized_base64
    except Exception as e:
        logger.error(f"Serialization error: {str(e)}")
        raise


def deserialize_data_vulnerable(serialized_data: str) -> Any:
    """
    Уязвимость: Небезопасная десериализация с pickle
    """
    try:
        # Уязвимость: pickle может выполнять произвольный код при десериализации
        serialized_bytes = base64.b64decode(serialized_data.encode())
        deserialized_data = pickle.loads(serialized_bytes)
        
        logger.debug(f"Deserialized data: {type(deserialized_data)}")
        
        return deserialized_data
    except Exception as e:
        logger.error(f"Deserialization error: {str(e)}")
        raise


# Уязвимость: Небезопасная работа с файлами
def read_file_vulnerable(file_path: str) -> str:
    """
    Уязвимость: Не проверяет path traversal
    """
    try:
        # Уязвимость: Не проверяем path traversal атаки
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Уязвимость: Логируем путь к файлу
        logger.debug(f"Read file '{file_path}' successfully")
        
        # Уязвимость: Логируем содержимое файла в DEBUG режиме
        logger.debug(f"File content: {content[:100]}...")
        
        return content
    except Exception as e:
        logger.error(f"Error reading file '{file_path}': {str(e)}")
        raise


def write_file_vulnerable(file_path: str, content: str) -> bool:
    """
    Уязвимость: Не проверяет path traversal и права доступа
    """
    try:
        # Уязвимость: Не проверяем path traversal
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)  # Уязвимость: создаем директории без проверки
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.debug(f"Wrote file '{file_path}' successfully")
        
        # Уязвимость: Логируем содержимое записываемого файла
        logger.debug(f"File content written: {content[:100]}...")
        
        return True
    except Exception as e:
        logger.error(f"Error writing file '{file_path}': {str(e)}")
        return False


# Уязвимость: Небезопасные SQL helper functions
def execute_sql_vulnerable(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Уязвимость: Позволяет прямое выполнение SQL без проверки
    """
    try:
        conn = sqlite3.connect("vulnerable.db")
        cursor = conn.cursor()
        
        # Уязвимость: Не проверяем содержимое SQL запроса
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Уязвимость: Возвращаем результат как dict
        columns = [description[0] for description in cursor.description] if cursor.description else []
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        logger.debug(f"SQL executed successfully: {query}")
        logger.debug(f"SQL results: {results}")
        
        return results
    except Exception as e:
        logger.error(f"SQL execution error: {str(e)}")
        logger.error(f"Failed query: {query}")
        raise


def build_sql_query_vulnerable(table: str, conditions: Dict[str, Any]) -> str:
    """
    Уязвимость: Строит SQL запрос без экранирования
    """
    try:
        # Уязвимость: Не экранируем названия таблиц и полей
        where_clauses = []
        for key, value in conditions.items():
            # Уязвимость: Не экранируем значения
            if isinstance(value, str):
                where_clauses.append(f"{key} = '{value}'")
            else:
                where_clauses.append(f"{key} = {value}")
        
        where_clause = " AND ".join(where_clauses)
        query = f"SELECT * FROM {table} WHERE {where_clause}"
        
        logger.debug(f"Built SQL query: {query}")
        
        return query
    except Exception as e:
        logger.error(f"Error building SQL query: {str(e)}")
        raise


# Уязвимость: Небезопасная аутентификация
class VulnerableAuth:
    """Класс с небезопасной аутентификацией"""
    
    def __init__(self):
        self.admin_password = "admin123"  # Уязвимость: hardcoded password
        self.session_tokens = {}  # Уязвимость: храним токены в памяти
        self.users_db_path = "vulnerable.db"
    
    def authenticate_vulnerable(self, username: str, password: str) -> Optional[str]:
        """
        Уязвимость: Небезопасная аутентификация
        """
        try:
            # Уязвимость: SQL injection в запросе аутентификации
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            
            conn = sqlite3.connect(self.users_db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # Уязвимость: Слабое генерирование токена
                token = hashlib.md5(f"{username}{time.time()}".encode()).hexdigest()
                self.session_tokens[token] = {
                    "user_id": user[0],
                    "username": username,
                    "role": user[4],
                    "created_at": time.time()
                }
                
                logger.info(f"User '{username}' authenticated successfully")
                
                # Уязвимость: Возвращаем информацию о пользователе в токене
                return token
            else:
                logger.warning(f"Failed authentication attempt for user '{username}'")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    def verify_token_vulnerable(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Уязвимость: Небезопасная проверка токена
        """
        if token in self.session_tokens:
            session_info = self.session_tokens[token]
            
            # Уязвимость: Не проверяем срок действия токена
            return session_info
        else:
            logger.warning(f"Invalid token used: {token}")
            return None
    
    def get_user_info_vulnerable(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Уязвимость: Information disclosure через user info
        """
        try:
            # Уязвимость: Небезопасный SQL запрос
            query = f"SELECT id, username, password, email, role FROM users WHERE id = {user_id}"
            
            conn = sqlite3.connect(self.users_db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # Уязвимость: Возвращаем пароль пользователя
                return {
                    "id": user[0],
                    "username": user[1],
                    "password": user[2],  # НЕБЕЗОПАСНО!
                    "email": user[3],
                    "role": user[4]
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info for ID {user_id}: {str(e)}")
            return None


# Уязвимость: Небезопасная обработка пользовательского ввода
def sanitize_input_vulnerable(user_input: str) -> str:
    """
    Уязвимость: Неэффективная санитизация
    """
    # Уязвимость: Неполная санитизация
    sanitized = user_input.strip()
    
    # Уязвимость: Не удаляем все потенциально опасные символы
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'union\s+select',             # SQL injection
        r'[\'";]',                     # Quote characters
        r'--',                         # SQL comments
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            logger.warning(f"Potentially dangerous input detected: '{sanitized}'")
            # Уязвимость: Не блокируем запрос, а только логируем
            break
    
    return sanitized


def validate_email_vulnerable(email: str) -> bool:
    """
    Уязвимость: Слабая валидация email
    """
    # Уязвимость: Простая regex validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    is_valid = re.match(email_pattern, email) is not None
    
    if not is_valid:
        logger.warning(f"Invalid email format: '{email}'")
    else:
        logger.debug(f"Valid email: '{email}'")
    
    return is_valid


# Уязвимость: Небезопасное выполнение команд
def execute_command_vulnerable(command: str, args: List[str] = None) -> Dict[str, Any]:
    """
    Уязвимость: Небезопасное выполнение shell команд
    """
    try:
        if args:
            # Уязвимость: Не проверяем аргументы
            full_command = [command] + args
        else:
            full_command = command
        
        logger.info(f"Executing command: {' '.join(full_command)}")
        
        # Уязвимость: shell=True позволяет command injection
        result = subprocess.run(full_command, shell=isinstance(full_command, str), 
                              capture_output=True, text=True, timeout=30)
        
        return {
            "status": "success",
            "command": ' '.join(full_command),
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"Command timeout: {' '.join(full_command)}")
        return {
            "status": "error",
            "message": "Command timeout"
        }
    except Exception as e:
        logger.error(f"Command execution error: {str(e)}")
        return {
            "status": "error",
            "message": f"Command execution failed: {str(e)}"
        }


# Уязвимость: Небезопасная работа с конфигурацией
class VulnerableConfig:
    """Класс с небезопасной конфигурацией"""
    
    def __init__(self):
        self.config = {
            "debug_mode": True,        # Уязвимость: debug в production
            "log_level": "DEBUG",      # Уязвимость: DEBUG логи
            "secret_key": "super_secret_key_123",
            "database_url": "sqlite:///vulnerable.db",
            "admin_password": "admin123",
            "allow_origins": ["*"],    # Уязвимость: CORS без ограничений
            "rate_limit": None,        # Уязвимость: нет rate limiting
            "ssl_verify": False,       # Уязвимость: не проверяем SSL
        }
    
    def get_config(self, key: str) -> Any:
        """
        Уязвимость: Позволяет получить любую конфигурацию
        """
        logger.debug(f"Getting config key: {key}")
        
        if key in self.config:
            value = self.config[key]
            logger.debug(f"Config value for '{key}': {value}")
            return value
        else:
            logger.warning(f"Config key '{key}' not found")
            return None
    
    def set_config(self, key: str, value: Any) -> bool:
        """
        Уязвимость: Позволяет изменять конфигурацию без проверки
        """
        logger.info(f"Setting config '{key}' to '{value}'")
        self.config[key] = value
        return True
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Возвращает всю конфигурацию включая секреты
        """
        logger.warning("Getting all configuration - SECRET EXPOSURE!")
        
        return self.config.copy()


# Уязвимость: Небезопасная работа с сессиями
class VulnerableSessionManager:
    """Менеджер сессий с уязвимостями"""
    
    def __init__(self):
        self.sessions = {}  # Уязвимость: храним сессии в памяти
        self.session_timeout = 3600  # 1 час
    
    def create_session_vulnerable(self, user_id: int, username: str) -> str:
        """
        Уязвимость: Слабое генерирование сессий
        """
        session_token = hashlib.md5(f"{user_id}{username}{time.time()}".encode()).hexdigest()
        
        self.sessions[session_token] = {
            "user_id": user_id,
            "username": username,
            "created_at": time.time(),
            "last_access": time.time()
        }
        
        logger.info(f"Created session for user '{username}': {session_token}")
        
        # Уязвимость: возвращаем токен с информацией о пользователе
        return session_token
    
    def validate_session_vulnerable(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Уязвимость: Не проверяем timeout сессии
        """
        if session_token in self.sessions:
            session_info = self.sessions[session_token]
            session_info["last_access"] = time.time()
            
            logger.debug(f"Session validated: {session_token}")
            return session_info
        else:
            logger.warning(f"Invalid session token: {session_token}")
            return None
    
    def get_all_sessions_vulnerable(self) -> Dict[str, Dict[str, Any]]:
        """
        КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Возвращает все активные сессии
        """
        logger.warning("Getting all sessions - SECURITY BREACH!")
        return self.sessions.copy()


# Экспортируем экземпляры уязвимых классов
vulnerable_auth = VulnerableAuth()
vulnerable_config = VulnerableConfig()
vulnerable_session_manager = VulnerableSessionManager()