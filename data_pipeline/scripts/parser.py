import os
import logging
from bs4 import BeautifulSoup
import re

# --- CƠ CHẾ ĐƯỜNG DẪN ĐỘNG CHUẨN DATA ENGINEER ---
# Lấy đường dẫn tuyệt đối của thư mục chứa file code này (thư mục scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Lùi lại 1 cấp để lấy thư mục gốc data_pipeline
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LegalHTMLParser:
    def __init__(self):
        # Tự động map đúng vào thư mục raw_data và processed_data
        self.input_dir = os.path.join(BASE_DIR, "raw_data")
        self.output_dir = os.path.join(BASE_DIR, "processed_data", "text_only")
        
        # Đảm bảo thư mục đầu ra tồn tại
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.content_selectors = [
            {"id": "toanvancontent"}, 
            {"class_": "content1"},
            {"class_": "chi-tiet-toan-van"}
        ]
        
        self.trash_tags = ['script', 'style', 'header', 'footer', 'nav', 'aside', 'noscript', 'iframe', 'button']

    def _clean_soup(self, soup):
        for tag in self.trash_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        for element in soup.find_all(['div', 'ul'], class_=['menu', 'sidebar', 'footer', 'banner', 'ads']):
            element.decompose()
            
        return soup

    def extract_text(self, filename):
        input_path = os.path.join(self.input_dir, filename)
        
        if not os.path.exists(input_path):
            logging.error(f"Không tìm thấy file: {input_path}")
            return False
            
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            soup = BeautifulSoup(html_content, 'lxml')
            
            main_content = None
            for selector in self.content_selectors:
                main_content = soup.find('div', **selector)
                if main_content:
                    logging.info(f"Đã tìm thấy nội dung chính bằng selector: {selector} trong file {filename}")
                    break
            
            if not main_content:
                main_content = soup.find('body')
                
            if not main_content:
                logging.error(f"File {filename} hoàn toàn trống.")
                return False
                
            clean_content = self._clean_soup(main_content)
            raw_text = clean_content.get_text(separator='\n', strip=True)
            clean_text = re.sub(r'\n\s*\n', '\n\n', raw_text)
            
            output_filename = filename.replace('.html', '.txt')
            output_path = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(clean_text)
                
            logging.info(f"Đã bóc tách và lưu text thành công: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Lỗi khi xử lý file {filename}: {e}")
            return False

if __name__ == "__main__":
    parser = LegalHTMLParser()
    raw_dir = parser.input_dir
    
    if os.path.exists(raw_dir):
        html_files = [f for f in os.listdir(raw_dir) if f.endswith('.html')]
        if not html_files:
            logging.info("Chưa có file HTML nào trong thư mục raw_data.")
        else:
            for file in html_files:
                parser.extract_text(file)
    else:
        logging.error(f"Thư mục {raw_dir} không tồn tại!")