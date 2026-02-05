from typing import Dict, Any, Optional
import re
import logging

class StoryEditor:
    """Chỉnh sửa truyện với AI"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)
    
    def edit_story(self, story: str, edit_type: str = "Chỉnh văn phong", 
                   length_preference: str = "giữ nguyên", **kwargs) -> str:
        """Chỉnh sửa truyện theo loại chỉ định"""
        
        # Map edit type to instructions
        instruction_map = {
            "Chỉnh văn phong": "Hãy chỉnh sửa văn phong của truyện cho hay hơn, tự nhiên hơn",
            "Tóm tắt": "Hãy tóm tắt truyện một cách ngắn gọn nhưng vẫn giữ được nội dung chính",
            "Mở rộng": "Hãy mở rộng truyện thêm chi tiết, làm phong phú hơn",
            "Sửa lỗi chính tả": "Hãy sửa tất cả lỗi chính tả và ngữ pháp trong truyện",
            "Tối ưu hóa": "Hãy tối ưu hóa cấu trúc và cách diễn đạt của truyện"
        }
        
        instruction = instruction_map.get(edit_type, "Hãy chỉnh sửa truyện")
        
        # Thêm instruction về độ dài
        if length_preference == "ngắn hơn":
            instruction += ". Hãy làm cho truyện ngắn gọn hơn"
        elif length_preference == "dài hơn":
            instruction += ". Hãy mở rộng truyện dài hơn"
        
        # Tạo prompt hoàn chỉnh
        prompt = f"""{instruction}

TRUYỆN GỐC:
{story}

TRUYỆN ĐÃ CHỈNH SỬA:"""
        
        # Gọi AI để chỉnh sửa
        edited_story = self.ai_client.generate_text(
            prompt=prompt,
            max_tokens=4000,
            temperature=0.7
        )
        
        return edited_story
    
    def generate_image_script(self, story: str, num_scenes: int = 5, 
                            style: str = "anime", detail_level: str = "chi tiết",
                            include_prompts: bool = True) -> str:
        """Tạo kịch bản ảnh từ truyện"""
        
        # Gọi AI client để tạo kịch bản
        return self.ai_client.generate_image_script(
            story=story,
            num_scenes=num_scenes,
            style=style,
            detail_level=detail_level
        )
    
    def analyze_story(self, story: str) -> Dict[str, Any]:
        """Phân tích truyện"""
        prompt = f"""Hãy phân tích truyện sau:

{story}

PHÂN TÍCH:
1. Thể loại:
2. Nhân vật chính:
3. Bối cảnh:
4. Cốt truyện chính:
5. Điểm mạnh:
6. Điểm cần cải thiện:"""
        
        analysis = self.ai_client.generate_text(prompt=prompt)
        
        # Parse analysis
        result = {}
        lines = analysis.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        
        return result
    
    def generate_continuation(self, story: str, length: int = 500) -> str:
        """Tiếp tục câu chuyện"""
        prompt = f"""Hãy tiếp tục câu chuyện sau (khoảng {length} từ):

{story}

PHẦN TIẾP THEO:"""
        
        return self.ai_client.generate_text(
            prompt=prompt,
            max_tokens=length * 2
        )
