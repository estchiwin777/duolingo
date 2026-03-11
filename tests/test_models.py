from django.test import TestCase
from lessons.models import Level, Question

class LevelModelTest(TestCase):
    def setUp(self):
        # สร้างข้อมูลจำลอง (Mock Data) สำหรับการทดสอบ
        self.level1 = Level.objects.create(level_number=1, title="Easy Words")
        self.level5 = Level.objects.create(level_number=5, title="Sentences")

        # สร้างข้อสอบแบบคำศัพท์สำหรับ Level 1
        Question.objects.create(
            level=self.level1,
            question_type='word',
            jp_text='犬',
            jp_reading='いぬ',
            th_meaning='หมา,สุนัข'
        )

        # สร้างข้อสอบแบบประโยคสำหรับ Level 5
        Question.objects.create(
            level=self.level5,
            question_type='sentence',
            jp_text='こんにちは、世界',
            jp_reading='こんにちは、せかい',
            th_meaning='สวัสดี,โลก'
        )

    def test_level_creation(self):
        """ทดสอบว่าสร้าง Level ได้ถูกต้อง"""
        self.assertEqual(self.level1.level_number, 1)
        self.assertEqual(Level.objects.count(), 2)

    def test_question_assignment(self):
        """ทดสอบว่าข้อสอบถูกผูกเข้ากับ Level ที่ถูกต้อง"""
        q_lv1 = Question.objects.filter(level=self.level1).first()
        self.assertEqual(q_lv1.jp_text, '犬')
        self.assertEqual(q_lv1.question_type, 'word')