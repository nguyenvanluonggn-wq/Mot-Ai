import requests
import base64
from PIL import Image
from io import BytesIO
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

class ImageGenerator:
    """Tạo ảnh AI từ text prompt"""
    
    def __init__(self, api_url: str = "http://localhost:7860"):
        self.api_url = api_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Tạo thư mục output
        self.output_dir = Path(__file__).parent.parent / 'output' / 'images'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def check_connection(self) -> bool:
        """Kiểm tra kết nối đến Stable Diffusion"""
        try:
            response = self.session.get(f"{self.api_url}/sdapi/v1/sd-models", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, model: str = "stable-diffusion", 
                 width: int = 512, height: int = 512, num_images: int = 1,
                 steps: int = 30, cfg_scale: float = 7.5, sampler: str = "Euler a") -> List[str]:
        """Tạo ảnh từ prompt"""
        
        # Map model names to actual model names
        model_map = {
            "stable-diffusion": "",
            "midjourney-style": "midjourney",
            "anime-diffusion": "anything-v4",
            "realistic-vision": "realistic-vision"
        }
        
        # Prepare payload
        payload = {
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, distorted, ugly, deformed",
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_index": sampler,
            "batch_size": num_images,
            "n_iter": 1,
            "seed": -1,  # Random seed
        }
        
        try:
            # Text2Image
            response = self.session.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                images = result.get("images", [])
                
                # Save images
                saved_paths = []
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                for i, img_data in enumerate(images):
                    # Decode base64 image
                    img_bytes = base64.b64decode(img_data.split(",", 1)[0] if "," in img_data else img_data)
                    
                    # Create filename
                    filename = f"ai_image_{timestamp}_{i+1}.png"
                    filepath = self.output_dir / filename
                    
                    # Save image
                    with open(filepath, "wb") as f:
                        f.write(img_bytes)
                    
                    saved_paths.append(str(filepath))
                
                self.logger.info(f"Generated {len(saved_paths)} images")
                return saved_paths
                
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Generation error: {str(e)}")
            
            # Fallback: Create placeholder image
            return self._create_placeholder_images(num_images, prompt)
    
    def _create_placeholder_images(self, num_images: int, prompt: str) -> List[str]:
        """Tạo ảnh placeholder khi API không hoạt động"""
        saved_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i in range(num_images):
            # Tạo ảnh placeholder đơn giản
            img = Image.new('RGB', (512, 512), color=(73, 109, 137))
            
            filename = f"placeholder_{timestamp}_{i+1}.png"
            filepath = self.output_dir / filename
            
            img.save(filepath)
            saved_paths.append(str(filepath))
        
        self.logger.warning(f"Created {num_images} placeholder images")
        return saved_paths
    
    def generate_batch(self, prompts: List[str], **kwargs) -> Dict[str, List[str]]:
        """Tạo batch ảnh từ nhiều prompt"""
        results = {}
        
        for i, prompt in enumerate(prompts):
            try:
                images = self.generate(prompt, **kwargs)
                results[prompt[:50]] = images
                self.logger.info(f"Generated images for prompt {i+1}/{len(prompts)}")
            except Exception as e:
                self.logger.error(f"Error generating for prompt {i+1}: {str(e)}")
                results[prompt[:50]] = []
        
        return results
