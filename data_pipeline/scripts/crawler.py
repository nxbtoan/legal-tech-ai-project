import os
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

# Cấu hình logging để dễ debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VBPLCrawler:
    def __init__(self, output_dir="../raw_data"):
        self.output_dir = output_dir
        self.ua = UserAgent()
        
        # Đảm bảo thư mục lưu trữ tồn tại
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def fetch_html(self, url, filename):
        """Tải mã nguồn HTML của trang luật và lưu trữ cục bộ."""
        headers = {
            "User-Agent": self.ua.random,
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        try:
            logging.info(f"Đang cào dữ liệu từ: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status() # Báo lỗi ngay nếu HTTP status code != 200
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Lưu file HTML thô
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            logging.info(f"Đã lưu thành công: {filepath}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Lỗi khi cào {url}: {e}")
            return None

if __name__ == "__main__":
    crawler = VBPLCrawler(output_dir="raw_data")
    
    # Danh sách các link Bộ luật cần cào (Ví dụ từ vbpl.vn hoặc thuvienphapluat)
    # Lưu ý: Cậu cần thay link này bằng link URL "Toàn văn" chính xác trên trang vbpl.vn
    target_laws = [
        {
            "name": "bo_luat_lao_dong_2019.html",
            # Đây là link ví dụ, cậu hãy vào vbpl.vn search Luật Lao động 2019, 
            # bấm vào tab "Toàn văn" rồi copy URL dán vào đây
            "url": "https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=139264" 
        },
        {
            "name": "luat_viec_lam_2013.html",
            "url": "https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=32801"
        }
    ]
    
    for law in target_laws:
        crawler.fetch_html(law['url'], law['name'])
        # Ngủ 3 giây giữa các request để lịch sự, không làm sập server của nhà nước
        time.sleep(3)