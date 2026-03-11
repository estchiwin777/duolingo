from django.test import TestCase, Client
from django.urls import reverse
from lessons.models import Level, Question

class PlayLevelViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # --- สร้าง Mock Data สำหรับทดสอบ ---
        # สร้าง Level 1 ถึง 5
        self.levels = {}
        for i in range(1, 6):
            self.levels[i] = Level.objects.create(level_number=i, title=f"Level {i}")

        # สร้างข้อสอบแบบคำศัพท์ (Word) ให้ด่าน 1, 2, 3
        for i in range(1, 4):
            for j in range(5):
                Question.objects.create(
                    level=self.levels[i],
                    question_type='word',
                    jp_text=f'Word{i}_{j}',
                    jp_reading=f'Reading{i}_{j}',
                    th_meaning=f'Meaning{i}_{j}, ความหมายที่สอง'
                )

        # สร้างข้อสอบแบบประโยค (Sentence) ให้ด่าน 3, 4, 5
        for i in range(3, 6):
            for j in range(5):
                Question.objects.create(
                    level=self.levels[i],
                    question_type='sentence',
                    jp_text=f'Word{i}_{j}',
                    jp_reading=f'Reading{i}_{j}',
                    th_meaning=f'Meaning{i}_{j}',
                    jp_sentence=f'Jp Sentence {i} {j}',
                    th_sentence=f'ฉัน กิน ข้าว {i} {j}'
                )

    def test_level_1_and_2_mode(self):
        """Level 1 และ 2 ต้องเป็นโหมด multiple_choice ทั้งหมด"""
        for level_id in [1, 2]:
            response = self.client.get(reverse('play_level', args=[level_id]))
            self.assertEqual(response.status_code, 200)
            
            # ดึงตัวแปร questions_data (ตามที่อยู่ใน views.py ของคุณ)
            questions_data = response.context['questions_data']
            self.assertTrue(len(questions_data) > 0)
            
            # ตรวจสอบว่าทุกข้อเป็น multiple_choice
            for q in questions_data:
                self.assertEqual(q['mode'], 'multiple_choice')

    def test_level_3_mixed_mode(self):
        """Level 3 ต้องผสมระหว่าง type_answer (3 ข้อแรก) และ fill_blank/mc (2 ข้อหลัง)"""
        response = self.client.get(reverse('play_level', args=[3]))
        self.assertEqual(response.status_code, 200)
        
        questions_data = response.context['questions_data']
        self.assertEqual(len(questions_data), 5) # ดึงมา 5 ข้อ
        
        # 3 ข้อแรกควรเป็น type_answer
        for i in range(3):
            self.assertEqual(questions_data[i]['mode'], 'type_answer')
            
        # 2 ข้อหลังควรเป็น fill_blank (เพราะเราใส่ jp_sentence ไว้)
        for i in range(3, 5):
            self.assertEqual(questions_data[i]['mode'], 'fill_blank')

    def test_level_4_mode(self):
        """Level 4 ต้องเป็นโหมด fill_blank ทั้งหมด"""
        response = self.client.get(reverse('play_level', args=[4]))
        self.assertEqual(response.status_code, 200)
        
        questions_data = response.context['questions_data']
        self.assertTrue(len(questions_data) > 0)
        
        for q in questions_data:
            self.assertEqual(q['mode'], 'fill_blank')

    def test_level_5_mode(self):
        """Level 5 ต้องเป็นโหมด sort_sentence ทั้งหมด"""
        response = self.client.get(reverse('play_level', args=[5]))
        self.assertEqual(response.status_code, 200)
        
        questions_data = response.context['questions_data']
        self.assertTrue(len(questions_data) > 0)
        
        for q in questions_data:
            self.assertEqual(q['mode'], 'sort_sentence')

    def test_vocab_bank_view(self):
        """ทดสอบว่าขุนแผนสามารถเข้าหน้า 'Word' (Vocab Bank) เพื่อดูคำศัพท์เบื้องต้นได้"""
        # ลองเข้าหน้า vocab_bank โดยขอดูคำศัพท์ระดับ N5
        response = self.client.get(reverse('vocab_bank') + '?level=N5')
        
        # ต้องเข้าได้สำเร็จ (200)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessons/vocab_bank.html')
        
        # ต้องมีคำศัพท์ถูกส่งมาที่หน้าเว็บ และต้องเป็นระดับ N5
        self.assertIn('questions', response.context)
        self.assertEqual(response.context['current_level'], 'N5')