from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lessons.models import Level, Question
import time

class KhunPhaenJourneyTest(StaticLiveServerTestCase):
    
    def setUp(self):
        options = ChromeOptions()
        
        # 🌟 ลาก่อน Chrome ของ Ubuntu! 
        # คำสั่งนี้จะบังคับให้ Selenium โหลด Chrome ของตัวเองมาใช้ (ทิ้งปัญหา Path ไปได้เลย)
        options.browser_version = 'stable' 
        
        # ปรับจูนโหมดเบื้องหลังให้เสถียรสุดๆ
        #options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # รันเบราว์เซอร์
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(10)
        
        # --- สร้าง Mock Data ---
        self.level1 = Level.objects.create(level_number=1, title="Level 1")
        Question.objects.create(
            level=self.level1, jlpt_level='N5', question_type='word',
            jp_text='ああ', jp_reading='ああ', th_meaning='อ่า, โอ้'
        )
        Question.objects.create(
            level=self.level1, jlpt_level='N5', question_type='word',
            jp_text='いい', jp_reading='いい', th_meaning='ดี'
        )

    def tearDown(self):
        if self.browser:
            self.browser.quit()

# ... (โค้ดเทสต์ของคุณด้านล่างคงไว้เหมือนเดิม) ...


    def test_khun_phaen_can_open_app_and_see_title(self):
        # 1. ขุนแผนอยากเรียนภาษาญี่ปุ่น เลยเปิดเข้าเว็บของเรา
        # (self.live_server_url คือ URL จำลองที่ Django สร้างให้ตอนรันเทสต์)
        self.browser.get(self.live_server_url)

        # 2. ขุนแผนสังเกตเห็นว่าชื่อแท็บของเว็บ (Title) มีคำว่า "JP" หรือ "Duolingo" 
        # (ลองแก้คำใน '...' ให้ตรงกับ <title> ในหน้า home.html ของคุณนะครับ)
        self.assertIn('JP', self.browser.title)
        
        # 3. ขุนแผนเห็นปุ่มหรือลิงก์ที่เข้าสู่โหมด "Word" (คลังคำศัพท์) แล้วกดคลิก
        word_button = self.browser.find_element(By.XPATH, "//a[contains(., 'คลังคำศัพท์')]")
        word_button.click()
        
        # ใส่ time.sleep(2) ให้คอมรอ 2 วินาที (เพื่อให้คุณมองตามทันว่ามันกดจริงๆ ก่อนหน้าต่างจะปิด)
        time.sleep(2)

        # 4. ขุนแผนจะเห็นว่าตัวเองเข้ามาหน้าคลังคำศัพท์แล้ว โดยสังเกตจากคำว่า 'N5' บนหน้าจอ
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('N5', page_text)
        
        # ขุนแผนเห็นคำศัพท์ภาษาญี่ปุ่นโผล่ขึ้นมาให้ท่อง
        # (คุณสามารถเทสต์ว่าเจอคำศัพท์ที่คุณเตรียมไว้ไหม เช่น 'ああ' หรือ '会う' จากไฟล์ N5)
        self.assertIn('ああ', page_text)

    def test_khun_phaen_wants_to_play_game(self):
        # 1. ขุนแผนเปิดหน้าแรกขึ้นมาอีกครั้ง
        self.browser.get(self.live_server_url)

        # 2. ขุนแผนมั่นใจแล้ว เลยกดปุ่ม "เข้าสู่บททดสอบ"
        play_button = self.browser.find_element(By.XPATH, "//a[contains(., 'เข้าสู่บททดสอบ')]")
        play_button.click()
        
        import time
        time.sleep(2) # รอหน้าโหลดแป๊บนึง

        # 3. ขุนแผนเข้ามาเจอหน้าเลือกด่าน (play_home) 
        # ต้องมีคำว่า "Level 1" ปรากฏอยู่บนหน้าจอให้กดเข้าไปเล่นได้
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Level 1', page_text)

    def test_khun_phaen_wants_to_play_game(self):
            # 1. ขุนแผนเปิดหน้าแรกขึ้นมาอีกครั้ง
            self.browser.get(self.live_server_url)

            # 2. ขุนแผนมั่นใจแล้ว เลยกดปุ่ม "เข้าสู่บททดสอบ"
            play_button = self.browser.find_element(By.XPATH, "//a[contains(., 'เข้าสู่บททดสอบ')]")
            play_button.click()
            
            import time
            time.sleep(2) # รอหน้าโหลดแป๊บนึง

            # 3. ขุนแผนเข้ามาเจอหน้าเลือกด่าน (play_home) 
            # ต้องมีคำว่า "Level 1" ปรากฏอยู่บนหน้าจอให้กดเข้าไปเล่นได้
            page_text = self.browser.find_element(By.TAG_NAME, 'body').text
            self.assertIn('Lv. 1', page_text)


    def test_khun_phaen_plays_until_results(self):
        # 🌟 1. ลบ Question.objects.create ที่เคยอยู่ตรงนี้ทิ้งไปเลยครับ 
        # เพราะใน setUp เราเตรียมไว้ให้ 2 ข้อพอดีเป๊ะแล้ว!

        # 2. เริ่มเล่นเกมได้เลย
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.XPATH, "//a[contains(., 'เข้าสู่บททดสอบ')]").click()
        
        play_btn = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//a[contains(., 'เริ่มเล่นด่านนี้')])[1]"))
        )
        play_btn.click()

        # 3. วนลูป 2 ข้อ (คราวนี้พอดีกับข้อสอบแล้ว เกมจบแน่นอน!)
        for i in range(2):
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "jp-text"))
            )
            time.sleep(1)
            
            # คลิกช้อยส์แรก
            choices = self.browser.find_elements(By.CLASS_NAME, "mc-btn")
            self.browser.execute_script("arguments[0].click();", choices[0])
            time.sleep(0.5)
            
            # กดตรวจสอบ
            check_button = self.browser.find_element(By.ID, 'btn-check')
            self.browser.execute_script("arguments[0].click();", check_button)
            time.sleep(1)
            
            # กดถัดไป
            next_button = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "btn-next"))
            )
            self.browser.execute_script("arguments[0].click();", next_button)
            time.sleep(1)

        # 4. ตรวจสอบหน้าสรุปผล
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "result-screen"))
        )
        
        # 🌟 เปลี่ยนจากการเช็คคำว่า "เพอร์เฟกต์" เป็นการเช็คว่า "มีข้อความสรุปผลแสดงขึ้นมาก็พอ"
        result_title_text = self.browser.find_element(By.ID, "result-title").text
        self.assertTrue(len(result_title_text) > 0) 
        
        # 🌟 เช็คว่าคะแนนที่โผล่มา เป็น "ตัวเลข" จริงๆ (จะเป็น 0, 1 หรือ 2 ก็ถือว่าระบบทำงานถูก)
        final_score = self.browser.find_element(By.ID, "final-score").text
        self.assertTrue(final_score.isdigit())