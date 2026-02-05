import requests
import json
from typing import Dict, Any, Optional, List
import logging

class LMStudioClient:
    """Client để kết nối với LM Studio local server"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def check_connection(self) -> bool:
        """Kiểm tra kết nối đến LM Studio"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text từ prompt"""
        try:
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "stop": kwargs.get("stop", []),
                "stream": False
            }
            
            response = self.session.post(
                f"{self.base_url}/completions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("text", "").strip()
            else:
                self.logger.error(f"LM Studio error: {response.text}")
                return f"Error: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return f"Connection error: {str(e)}"
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion với LM Studio"""
        try:
            payload = {
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "stream": False
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            else:
                self.logger.error(f"LM Studio error: {response.text}")
                return f"Error: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return f"Connection error: {str(e)}"
    
    def edit_story_text(self, text: str, instruction: str) -> str:
        """Chỉnh sửa văn bản theo instruction"""
        prompt = f"""Hãy chỉnh sửa văn bản sau theo yêu cầu:

VĂN BẢN GỐC:
{text}

YÊU CẦU CHỈNH SỬA:
{instruction}

VĂN BẢN ĐÃ CHỈNH SỬA:"""
        
        return self.generate_text(prompt, max_tokens=2000)
    
    def translate_text(self, text: str, source_lang: str, target_lang: str, style: str = "modern") -> str:
        """Dịch văn bản với văn phong chỉ định"""
        style_map = {
            "hiện đại": "văn phong hiện đại, tự nhiên",
            "cổ đại": "văn phong cổ điển, trang trọng",
            "văn học": "văn phong văn học, trau chuốt",
            "giản dị": "văn phong giản dị, dễ hiểu",
            "trẻ trung": "văn phong trẻ trung, năng động"
        }
        
        style_desc = style_map.get(style, "văn phong tự nhiên")
        
        prompt = f"""Hãy dịch văn bản sau từ {source_lang} sang {target_lang} với {style_desc}:

{text}

Bản dịch:"""
        
        return self.generate_text(prompt)
    
    def generate_image_script(self, story: str, num_scenes: int, style: str, detail_level: str) -> str:
        """Tạo kịch bản ảnh từ truyện"""
        detail_map = {
            "cơ bản": "mô tả ngắn gọn",
            "chi tiết": "mô tả chi tiết",
            "rất chi tiết": "mô tả rất chi tiết với đầy đủ yếu tố"
        }
        
        detail_desc = detail_map.get(detail_level, "mô tả chi tiết")
        
        prompt = f"""Hãy tạo kịch bản ảnh từ câu chuyện sau:

CÂU CHUYỆN:
{story}

YÊU CẦU:
- Tạo {num_scenes} cảnh quan trọng
- Phong cách: {style}
- Mức độ: {detail_desc}
- Mỗi cảnh bao gồm:
  1. Tên cảnh
  2. Mô tả cảnh
  3. Các nhân vật
  4. Bối cảnh
  5. Prompt cho AI tạo ảnh

KỊCH BẢN ẢNH:"""
        
        return self.generate_text(prompt, max_tokens=3000)
