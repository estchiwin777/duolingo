// ดึงปุ่มทั้งหมดมา
const choices = document.querySelectorAll('.mc-btn');
const checkBtn = document.getElementById('btn-check');

// เมื่อคลิกที่ช้อยส์ใดๆ
choices.forEach(btn => {
    btn.addEventListener('click', () => {
        // 1. ลบ class 'selected' ออกจากทุกปุ่มก่อน
        choices.forEach(c => c.classList.remove('selected'));
        
        // 2. เติม class 'selected' ให้กับปุ่มที่เพิ่งถูกคลิก (ปุ่มจะกลายเป็นสีฟ้าเด้งๆ)
        btn.classList.add('selected');
        
        // 3. ปลดล็อกปุ่ม "ตรวจ" ให้กลายเป็นสีเขียวและกดได้
        checkBtn.disabled = false;
        checkBtn.classList.add('active');
    });
});