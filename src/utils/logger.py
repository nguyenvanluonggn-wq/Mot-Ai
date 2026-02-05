import logging
from pathlib import Path
import sys
from datetime import datetime

def setup_logger(name: str = "AI_Story_App"):
    """Setup logger cho ứng dụng"""
    
    # Tạo thư mục logs (ở thư mục gốc, cùng cấp với src)
    current_dir = Path(__file__).parent.parent.parent  # Lên 2 cấp từ src/utils/logger.py
    log_dir = current_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Tạo logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Tạo formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler
    log_file = log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Thêm handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
