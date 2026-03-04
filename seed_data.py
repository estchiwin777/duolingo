import os
import django

# ตั้งค่าให้สคริปต์รู้จัก Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jplearn.settings')
django.setup()

from lessons.models import Level, Question

print("กำลังล้างข้อมูลเก่าเพื่อให้เริ่มต้นใหม่แบบคลีนๆ...")
Level.objects.all().delete()

print("🌟 กำลังสร้าง Level 1: คำศัพท์ทักทาย...")
lv1 = Level.objects.create(level_number=1, title="คำศัพท์ทักทาย")
Question.objects.create(level=lv1, question_type='word', jp_text="こんにちは", jp_reading="konnichiwa", th_meaning="สวัสดี", en_meaning="hello")
Question.objects.create(level=lv1, question_type='word', jp_text="ありがとう", jp_reading="arigatou", th_meaning="ขอบคุณ", en_meaning="thank you")
Question.objects.create(level=lv1, question_type='word', jp_text="さようなら", jp_reading="sayounara", th_meaning="ลาก่อน", en_meaning="goodbye")

print("🌟 กำลังสร้าง Level 2: สัตว์และสิ่งของ...")
lv2 = Level.objects.create(level_number=2, title="สัตว์และสิ่งของ")
Question.objects.create(level=lv2, question_type='word', jp_text="猫", jp_reading="ねこ", th_meaning="แมว", en_meaning="cat")
Question.objects.create(level=lv2, question_type='word', jp_text="犬", jp_reading="いぬ", th_meaning="หมา,สุนัข", en_meaning="dog")
Question.objects.create(level=lv2, question_type='word', jp_text="水", jp_reading="みず", th_meaning="น้ำ", en_meaning="water")

print("🌟 กำลังสร้าง Level 3: ประโยคเบื้องต้น...")
lv3 = Level.objects.create(level_number=3, title="ประโยคเบื้องต้น")
# หมายเหตุ: โหมด sentence จะมีเว้นวรรคใน jp_reading เพื่อให้ตัวตัดคำทำงานง่ายขึ้น
Question.objects.create(level=lv3, question_type='sentence', jp_text="私は猫が好きです", jp_reading="わたし は ねこ が すき です", th_meaning="ฉันชอบแมว", en_meaning="I like cats")
Question.objects.create(level=lv3, question_type='sentence', jp_text="これは水です", jp_reading="これ は みず です", th_meaning="นี่คือน้ำ", en_meaning="This is water")

print("🎉 สร้างข้อมูลเสร็จเรียบร้อย! ตอนนี้มี 3 ด่านพร้อมเล่นแล้วครับ!")