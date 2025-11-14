"""
Утилиты логирования для тестового сервиса
"""

import logging
import sys
from typing import Optional

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Настройка логгера для сервиса
    """
    logger = logging.getLogger(name)
    
    # Избегаем дублирования хендлеров
    if not logger.handlers:
        # Настройка уровня логирования
        logger.setLevel(getattr(logging, level.upper()))
        
        # Создаем форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный хендлер
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Файловый хендлер (опционально)
        try:
            file_handler = logging.FileHandler('test_service.log')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # Игнорируем ошибки с файловым логированием
            pass
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Получение логгера по имени
    """
    return logging.getLogger(name)