#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI STORY CREATOR PRO - Ứng dụng AI đa năng
Tác giả: Hệ thống AI
"""

import os
import sys
import json
import threading
from pathlib import Path

# Thêm thư mục hiện tại vào PATH
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from gui import MainApp
from utils.logger import setup_logger

def main():
    """Hàm chính khởi chạy ứng dụng"""
    try:
        # Kiểm tra và tạo thư mục cần thiết
        required_dirs = ['output', 'logs', 'temp', 'models']
        for dir_name in required_dirs:
            dir_path = current_dir / dir_name
            dir_path.mkdir(exist_ok=True)
        
        # Setup logger
        logger = setup_logger()
        logger.info("=" * 60)
        logger.info("Khởi động AI Story Creator Pro")
        logger.info("=" * 60)
        
        # Load cấu hình
        config_path = current_dir / 'config.json'
        if not config_path.exists():
            create_default_config(config_path)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Phiên bản: {config['version']}")
        
        # Khởi chạy ứng dụng
        app = MainApp(config)
        app.mainloop()
        
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {str(e)}")
        input("Nhấn Enter để thoát...")
        sys.exit(1)

def create_default_config(config_path):
    """Tạo file cấu hình mặc định"""
    default_config = {
        "app_name": "AI Story Creator Pro",
        "version": "1.0.0",
        "lm_studio_url": "http://localhost:1234/v1",
        "sd_api_url": "http://localhost:7860",
        "themes": {
            "light": "#FFFFFF",
            "dark": "#1E1E1E",
            "primary": "#6366F1",
            "secondary": "#8B5CF6"
        },
        "translation_styles": [
            "hiện đại",
            "cổ đại",
            "văn học",
            "giản dị",
            "trẻ trung"
        ],
        "platforms": [
            "bilibili.com",
            "v.qq.com",
            "youku.com",
            "iqiyi.com",
            "douyin.com"
        ]
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
