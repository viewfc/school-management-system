# School Management System (Login / Register / Dashboard)

โปรเจกต์ตัวอย่างระบบ School Management System ที่มีฟีเจอร์หลักดังนี้:

- Login
- Register
- Dashboard ตามบทบาทผู้ใช้
- SQLite database พร้อม seed ข้อมูลตัวอย่าง
- บทบาทผู้ใช้: `admin`, `teacher`, `student`

## เทคโนโลยีที่ใช้

- Python 3
- Flask
- SQLite
- HTML + CSS

## โครงสร้างโปรเจกต์

```bash
school_management_system/
├── app.py
├── requirements.txt
├── school.db              # สร้างอัตโนมัติเมื่อรันครั้งแรก
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    └── dashboard.html
```

## วิธีรัน

### 1) สร้าง virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

### 3) รันโปรเจกต์

```bash
python app.py
```

จากนั้นเปิดเบราว์เซอร์ที่:

```bash
http://127.0.0.1:5000
```

## บัญชีทดสอบ

- Admin: `admin@school.local` / `admin123`
- Teacher: `teacher@school.local` / `teacher123`
- Student: `student@school.local` / `student123`

## ฟีเจอร์ของ Dashboard

### Admin
- ดูจำนวนครู นักเรียน และห้องเรียนทั้งหมด
- ดูรายชื่อผู้ใช้ล่าสุด

### Teacher
- ดูจำนวนวิชาที่สอน
- ดูจำนวนนักเรียนที่ดูแล
- ดูจำนวนการเช็กชื่อวันนี้
- ดูตารางสอนของตนเอง

### Student
- ดูจำนวนวิชาที่ลงทะเบียน
- ดูจำนวนการเข้าเรียน
- ดูอัตราการเข้าเรียน
- ดูวิชาที่ลงทะเบียน

## หมายเหตุ

- หน้า Register เปิดให้สมัครได้เฉพาะ `student` และ `teacher`
- Admin ถูก seed ไว้สำหรับการทดสอบระบบ
- ควรเปลี่ยน `SECRET_KEY` และย้ายไปใช้ฐานข้อมูลที่เหมาะสมกว่าเดิมเมื่อนำขึ้น production
