# School Management System

Starter project สำหรับระบบโรงเรียนที่มี:
- Login
- Register
- Role-based Dashboard
- Admin management for Users, Classes, Announcements
- SQLite database

## Stack
- Flask
- SQLite
- Bootstrap 5

## Roles
- **Admin**: จัดการ users, classes, announcements
- **Teacher**: ดูคลาสที่ตัวเองสอน และประกาศของโรงเรียน
- **Student**: ดูโปรไฟล์, ตารางคลาส, และประกาศของโรงเรียน

## Demo Admin
- Email: `admin@school.local`
- Password: `admin123`

## วิธีรัน
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

จากนั้นเปิดเบราว์เซอร์ที่:
```bash
http://127.0.0.1:5000
```

## หมายเหตุ
- ฐานข้อมูล `school.db` จะถูกสร้างให้อัตโนมัติเมื่อรันครั้งแรก
- เหมาะสำหรับใช้เป็น starter template และต่อยอดเป็นระบบจริง เช่น attendance, grades, fees, parent portal
