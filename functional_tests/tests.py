import os
import django
import time 
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ตั้งค่า Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jplearn.settings')
django.setup()

class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        from lessons.models import Level, Question
        # สร้างด่าน
        level_n5 = Level.objects.create(level_number=1, title="N5")
        
        # สร้างคำถามตัวอย่าง
        from lessons.models import Question
        Question.objects.create(
            level=level_n5,
            question_type='word',
            jp_text="会う",
            jp_reading="あう",
            th_meaning="พบ",
            en_meaning="to meet"
        )

        chrome_options = Options()

        # 🙈 ปิดบรรทัดนี้เพื่อให้เห็นหน้าจอจริง!
        #chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # กลับมาใช้ ChromeDriverManager เพื่อความแม่นยำ
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        
        try:
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            self.browser.implicitly_wait(10)
        except Exception as e:
            print(f"❌ Error: {e}")
            raise e

    def tearDown(self):
        if hasattr(self, 'browser'):
            self.browser.quit()

    def test_can_view_home_page_and_see_title(self):
        # ขุนแผนเข้าชมหน้าเว็บ
        self.browser.get(self.live_server_url)
        
        # 🌟 เพิ่มการรอเล็กน้อยเพื่อให้มั่นใจว่าหน้าเว็บโหลดเสร็จ
        time.sleep(2) 
        
        # ตรวจสอบ Title
        self.assertIn('JP Learn', self.browser.title)
        
        # 🌟 เพิ่มการตรวจสอบ Header เพื่อความชัวร์
        header_text = self.browser.find_element("tag name", "h1").text
        self.assertIn('JP Learn', header_text) #
    
    def test_can_start_game_and_see_japanese_text(self):
        # 1. ขุนแผนเข้ามาที่หน้าแรกของ JP Learn
        self.browser.get(self.live_server_url)
        
        # 2. เขามองหาการ์ดบทเรียน N5 และคลิกปุ่ม "เริ่มเรียนเลย!"
        # (เราสร้าง Level 1 ไว้ใน setUp แล้ว)
        start_button = self.browser.find_element(By.CLASS_NAME, 'transition-link')
        start_button.click()
        
        # 3. เขารอให้ Modal เด้งขึ้นมา (รอ Animation 1 วินาที)
        time.sleep(1)
        
        # 4. เนื่องจากเกมรันอยู่ใน Iframe เขาจึงต้อง "สลับตัว" เข้าไปใน Iframe นั้น
        iframe = self.browser.find_element(By.ID, 'game-iframe')
        self.browser.switch_to.frame(iframe)
        
        # 5. ตอนนี้เขาอยู่ในหน้าเล่นเกมแล้ว เขาควรจะเห็นโจทย์ภาษาญี่ปุ่นปรากฏขึ้นมา
        # เราจะเช็คว่าตัวอักษรใน id="jp-text" ไม่ใช่ค่าว่าง
        jp_text_element = self.browser.find_element(By.ID, 'jp-text')
        self.assertNotEqual(jp_text_element.text, "...")
        self.assertNotEqual(jp_text_element.text, "")
        
        # 6. พอใจแล้ว เขาก็ปิด Browser (tearDown จะจัดการให้เอง)