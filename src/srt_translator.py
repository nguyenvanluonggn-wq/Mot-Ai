import pysrt
from typing import List, Tuple, Optional, Callable
import os
import re
from datetime import timedelta
import logging

class SRTTranslator:
    """Dịch file SRT sử dụng AI"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)
    
    def translate_file(self, file_path: str, src_lang: str, tgt_lang: str, 
                       style: str = "modern", batch_size: int = 10,
                       progress_callback: Optional[Callable] = None) -> str:
        """Dịch toàn bộ file SRT"""
        
        # Đọc file SRT
        subs = pysrt.open(file_path, encoding='utf-8')
        
        if not subs:
            raise ValueError("File SRT trống hoặc không đọc được")
        
        # Chia thành các batch
        batches = self._create_batches(subs, batch_size)
        
        translated_subs = []
        
        # Dịch từng batch
        total_batches = len(batches)
        for i, batch in enumerate(batches, 1):
            if progress_callback:
                progress_callback(i, total_batches)
            
            # Tạo text batch
            batch_text = self._batch_to_text(batch)
            
            # Dịch batch
            translated_text = self.ai_client.translate_text(
                text=batch_text,
                source_lang=src_lang,
                target_lang=tgt_lang,
                style=style
            )
            
            # Chuyển về các subtitle
            translated_batch = self._text_to_subtitles(translated_text, batch)
            
            # Thêm vào kết quả
            translated_subs.extend(translated_batch)
            
            self.logger.info(f"Translated batch {i}/{total_batches}")
        
        # Tạo file SRT mới
        output_srt = self._create_srt_content(translated_subs)
        
        return output_srt
    
    def _create_batches(self, subs: pysrt.SubRipFile, batch_size: int) -> List[List[pysrt.SubRipItem]]:
        """Chia subtitles thành các batch"""
        batches = []
        current_batch = []
        
        for sub in subs:
            current_batch.append(sub)
            
            if len(current_batch) >= batch_size:
                batches.append(current_batch)
                current_batch = []
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _batch_to_text(self, batch: List[pysrt.SubRipItem]) -> str:
        """Chuyển batch subtitles thành text"""
        texts = []
        
        for i, sub in enumerate(batch, 1):
            # Làm sạch text (loại bỏ tags HTML)
            clean_text = re.sub(r'<[^>]+>', '', sub.text)
            clean_text = clean_text.replace('\n', ' ')
            
            texts.append(f"{i}. {clean_text}")
        
        return "\n".join(texts)
    
    def _text_to_subtitles(self, translated_text: str, 
                          original_batch: List[pysrt.SubRipItem]) -> List[Tuple[str, timedelta, timedelta]]:
        """Chuyển text đã dịch về subtitles"""
        
        lines = translated_text.strip().split('\n')
        translated_items = []
        
        for i, line in enumerate(lines):
            if i < len(original_batch):
                original = original_batch[i]
                
                # Lấy số thứ tự và text từ dòng đã dịch
                match = re.match(r'^\d+\.\s*(.+)', line)
                if match:
                    translated_text = match.group(1)
                else:
                    translated_text = line
                
                # Giữ nguyên timing
                translated_items.append((translated_text, original.start, original.end))
        
        return translated_items
    
    def _create_srt_content(self, subs: List[Tuple[str, timedelta, timedelta]]) -> str:
        """Tạo nội dung SRT từ subtitles đã dịch"""
        lines = []
        
        for i, (text, start, end) in enumerate(subs, 1):
            # Format thời gian
            start_str = self._timedelta_to_srt(start)
            end_str = self._timedelta_to_srt(end)
            
            lines.append(str(i))
            lines.append(f"{start_str} --> {end_str}")
            lines.append(text)
            lines.append("")  # Dòng trống
            
        return "\n".join(lines)
    
    def _timedelta_to_srt(self, td: timedelta) -> str:
        """Chuyển timedelta thành định dạng SRT"""
        total_seconds = int(td.total_seconds())
        milliseconds = int((td.total_seconds() - total_seconds) * 1000)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
