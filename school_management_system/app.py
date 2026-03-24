from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from functools import wraps
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "school.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-this")

LANGUAGES: dict[str, str] = {
    "th": "ไทย",
    "en": "English",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "ar": "العربية",
    "hi": "हिन्दी",
}
DEFAULT_LANG = "th"
RTL_LANGS = {"ar"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "brand": {
        "th": "School Management System",
        "en": "School Management System",
        "zh": "学校管理系统",
        "ja": "学校管理システム",
        "ko": "학교 관리 시스템",
        "es": "Sistema de Gestión Escolar",
        "fr": "Système de gestion scolaire",
        "de": "Schulverwaltungssystem",
        "ar": "نظام إدارة المدرسة",
        "hi": "स्कूल प्रबंधन प्रणाली",
    },
    "login": {
        "th": "เข้าสู่ระบบ",
        "en": "Login",
        "zh": "登录",
        "ja": "ログイン",
        "ko": "로그인",
        "es": "Iniciar sesión",
        "fr": "Connexion",
        "de": "Anmelden",
        "ar": "تسجيل الدخول",
        "hi": "लॉगिन",
    },
    "register": {
        "th": "สมัครสมาชิก",
        "en": "Register",
        "zh": "注册",
        "ja": "登録",
        "ko": "회원가입",
        "es": "Registrarse",
        "fr": "S'inscrire",
        "de": "Registrieren",
        "ar": "إنشاء حساب",
        "hi": "रजिस्टर",
    },
    "logout": {
        "th": "ออกจากระบบ",
        "en": "Logout",
        "zh": "退出登录",
        "ja": "ログアウト",
        "ko": "로그아웃",
        "es": "Cerrar sesión",
        "fr": "Déconnexion",
        "de": "Abmelden",
        "ar": "تسجيل الخروج",
        "hi": "लॉगआउट",
    },
    "dashboard": {
        "th": "แดชบอร์ด",
        "en": "Dashboard",
        "zh": "仪表板",
        "ja": "ダッシュボード",
        "ko": "대시보드",
        "es": "Panel",
        "fr": "Tableau de bord",
        "de": "Dashboard",
        "ar": "لوحة التحكم",
        "hi": "डैशबोर्ड",
    },
    "language": {
        "th": "ภาษา",
        "en": "Language",
        "zh": "语言",
        "ja": "言語",
        "ko": "언어",
        "es": "Idioma",
        "fr": "Langue",
        "de": "Sprache",
        "ar": "اللغة",
        "hi": "भाषा",
    },
    "starter_project": {
        "th": "โปรเจกต์เริ่มต้น",
        "en": "Starter Project",
        "zh": "入门项目",
        "ja": "スタータープロジェクト",
        "ko": "스타터 프로젝트",
        "es": "Proyecto inicial",
        "fr": "Projet de démarrage",
        "de": "Starter-Projekt",
        "ar": "مشروع مبدئي",
        "hi": "स्टार्टर प्रोजेक्ट",
    },
    "hero_title": {
        "th": "ระบบจัดการโรงเรียน",
        "en": "School Management System",
        "zh": "学校管理系统",
        "ja": "学校管理システム",
        "ko": "학교 관리 시스템",
        "es": "Sistema de Gestión Escolar",
        "fr": "Système de gestion scolaire",
        "de": "Schulverwaltungssystem",
        "ar": "نظام إدارة المدرسة",
        "hi": "स्कूल प्रबंधन प्रणाली",
    },
    "hero_desc": {
        "th": "ระบบตัวอย่างนี้ประกอบด้วย Login, Register และ Dashboard สำหรับบทบาท Admin, Teacher และ Student",
        "en": "This starter app includes Login, Register, and a Dashboard for Admin, Teacher, and Student roles.",
        "zh": "此示例应用包含管理员、教师和学生角色的登录、注册和仪表板。",
        "ja": "このサンプルアプリには、管理者・教師・学生向けのログイン、登録、ダッシュボードが含まれています。",
        "ko": "이 예제 앱에는 관리자, 교사, 학생 역할용 로그인, 회원가입, 대시보드가 포함되어 있습니다.",
        "es": "Esta aplicación inicial incluye inicio de sesión, registro y panel para los roles de administrador, profesor y estudiante.",
        "fr": "Cette application de démarrage inclut la connexion, l'inscription et un tableau de bord pour les rôles administrateur, enseignant et étudiant.",
        "de": "Diese Starter-App enthält Login, Registrierung und ein Dashboard für Administrator-, Lehrer- und Schülerrollen.",
        "ar": "يتضمن هذا التطبيق المبدئي تسجيل الدخول والتسجيل ولوحة تحكم لأدوار المسؤول والمعلم والطالب.",
        "hi": "इस स्टार्टर ऐप में एडमिन, टीचर और स्टूडेंट भूमिकाओं के लिए लॉगिन, रजिस्टर और डैशबोर्ड शामिल हैं।",
    },
    "demo_accounts": {
        "th": "บัญชีสำหรับทดสอบ",
        "en": "Demo accounts",
        "zh": "演示账号",
        "ja": "デモアカウント",
        "ko": "데모 계정",
        "es": "Cuentas de demostración",
        "fr": "Comptes de démonstration",
        "de": "Demo-Konten",
        "ar": "حسابات تجريبية",
        "hi": "डेमो खाते",
    },
    "email": {
        "th": "อีเมล",
        "en": "Email",
        "zh": "邮箱",
        "ja": "メール",
        "ko": "이메일",
        "es": "Correo electrónico",
        "fr": "E-mail",
        "de": "E-Mail",
        "ar": "البريد الإلكتروني",
        "hi": "ईमेल",
    },
    "password": {
        "th": "รหัสผ่าน",
        "en": "Password",
        "zh": "密码",
        "ja": "パスワード",
        "ko": "비밀번호",
        "es": "Contraseña",
        "fr": "Mot de passe",
        "de": "Passwort",
        "ar": "كلمة المرور",
        "hi": "पासवर्ड",
    },
    "full_name": {
        "th": "ชื่อ - นามสกุล",
        "en": "Full name",
        "zh": "姓名",
        "ja": "氏名",
        "ko": "성명",
        "es": "Nombre completo",
        "fr": "Nom complet",
        "de": "Vollständiger Name",
        "ar": "الاسم الكامل",
        "hi": "पूरा नाम",
    },
    "role": {
        "th": "บทบาท",
        "en": "Role",
        "zh": "角色",
        "ja": "役割",
        "ko": "역할",
        "es": "Rol",
        "fr": "Rôle",
        "de": "Rolle",
        "ar": "الدور",
        "hi": "भूमिका",
    },
    "confirm_password": {
        "th": "ยืนยันรหัสผ่าน",
        "en": "Confirm password",
        "zh": "确认密码",
        "ja": "パスワード確認",
        "ko": "비밀번호 확인",
        "es": "Confirmar contraseña",
        "fr": "Confirmer le mot de passe",
        "de": "Passwort bestätigen",
        "ar": "تأكيد كلمة المرور",
        "hi": "पासवर्ड की पुष्टि करें",
    },
    "go_to_login": {
        "th": "กลับไปหน้า Login",
        "en": "Back to Login",
        "zh": "返回登录",
        "ja": "ログインに戻る",
        "ko": "로그인으로 돌아가기",
        "es": "Volver al inicio de sesión",
        "fr": "Retour à la connexion",
        "de": "Zurück zum Login",
        "ar": "العودة إلى تسجيل الدخول",
        "hi": "लॉगिन पर वापस जाएँ",
    },
    "no_account": {
        "th": "ยังไม่มีบัญชี?",
        "en": "Don't have an account?",
        "zh": "还没有账号？",
        "ja": "アカウントをお持ちでないですか？",
        "ko": "계정이 없으신가요?",
        "es": "¿No tienes una cuenta?",
        "fr": "Vous n'avez pas de compte ?",
        "de": "Noch kein Konto?",
        "ar": "ليس لديك حساب؟",
        "hi": "क्या आपके पास खाता नहीं है?",
    },
    "register_desc": {
        "th": "เปิดสมัครสำหรับบทบาท Student และ Teacher ส่วน Admin ให้สร้างจากฐานข้อมูลหรือระบบหลังบ้าน",
        "en": "Registration is open for Student and Teacher roles. Admin accounts should be created from the database or admin backend.",
        "zh": "开放学生和教师角色注册。管理员账号应通过数据库或后台创建。",
        "ja": "登録は学生と教師の役割に対応しています。管理者アカウントはデータベースまたは管理画面から作成してください。",
        "ko": "학생과 교사 역할만 회원가입할 수 있습니다. 관리자 계정은 데이터베이스 또는 관리자 백엔드에서 생성해야 합니다.",
        "es": "El registro está abierto para los roles Estudiante y Profesor. Las cuentas de administrador deben crearse desde la base de datos o el panel administrativo.",
        "fr": "L'inscription est ouverte aux rôles Étudiant et Enseignant. Les comptes administrateur doivent être créés depuis la base de données ou le back-office.",
        "de": "Die Registrierung ist für Schüler- und Lehrerrollen geöffnet. Admin-Konten sollten über die Datenbank oder das Backend erstellt werden.",
        "ar": "التسجيل متاح لأدوار الطالب والمعلم فقط. يجب إنشاء حسابات المسؤول من قاعدة البيانات أو الواجهة الخلفية.",
        "hi": "रजिस्ट्रेशन केवल स्टूडेंट और टीचर भूमिकाओं के लिए खुला है। एडमिन खाते डेटाबेस या एडमिन बैकएंड से बनाए जाने चाहिए।",
    },
    "users": {"th": "ผู้ใช้", "en": "Users", "zh": "用户", "ja": "ユーザー", "ko": "사용자", "es": "Usuarios", "fr": "Utilisateurs", "de": "Benutzer", "ar": "المستخدمون", "hi": "उपयोगकर्ता"},
    "classes": {"th": "ห้องเรียน", "en": "Classes", "zh": "班级", "ja": "授業", "ko": "수업", "es": "Clases", "fr": "Classes", "de": "Klassen", "ar": "الفصول", "hi": "कक्षाएँ"},
    "announcements": {"th": "ประกาศ", "en": "Announcements", "zh": "公告", "ja": "お知らせ", "ko": "공지사항", "es": "Anuncios", "fr": "Annonces", "de": "Ankündigungen", "ar": "الإعلانات", "hi": "घोषणाएँ"},
    "welcome": {"th": "สวัสดี", "en": "Welcome", "zh": "欢迎", "ja": "ようこそ", "ko": "환영합니다", "es": "Bienvenido", "fr": "Bienvenue", "de": "Willkommen", "ar": "مرحباً", "hi": "स्वागत है"},
    "your_role": {"th": "บทบาทของคุณคือ", "en": "Your role is", "zh": "您的角色是", "ja": "あなたの役割は", "ko": "당신의 역할은", "es": "Tu rol es", "fr": "Votre rôle est", "de": "Ihre Rolle ist", "ar": "دورك هو", "hi": "आपकी भूमिका है"},
    "system_overview": {"th": "ภาพรวมข้อมูลสำคัญของระบบโรงเรียนอยู่ด้านล่าง", "en": "An overview of the key school system information is shown below.", "zh": "下面显示学校系统关键信息概览。", "ja": "学校システムの重要な情報の概要が以下に表示されます。", "ko": "학교 시스템의 주요 정보 개요가 아래에 표시됩니다.", "es": "A continuación se muestra una visión general de la información clave del sistema escolar.", "fr": "Un aperçu des principales informations du système scolaire est affiché ci-dessous.", "de": "Unten finden Sie einen Überblick über die wichtigsten Informationen des Schulsystems.", "ar": "يظهر أدناه ملخص لأهم معلومات نظام المدرسة.", "hi": "नीचे स्कूल सिस्टम की मुख्य जानकारी का अवलोकन दिखाया गया है।"},
    "secure_login": {"th": "ล็อกอินปลอดภัย", "en": "Secure Login", "zh": "安全登录", "ja": "安全なログイン", "ko": "보안 로그인", "es": "Inicio seguro", "fr": "Connexion sécurisée", "de": "Sicherer Login", "ar": "تسجيل دخول آمن", "hi": "सुरक्षित लॉगिन"},
    "role_based_dashboard": {"th": "แดชบอร์ดตามบทบาท", "en": "Role-Based Dashboard", "zh": "基于角色的仪表板", "ja": "役割別ダッシュボード", "ko": "역할 기반 대시보드", "es": "Panel por roles", "fr": "Tableau de bord par rôle", "de": "Rollenbasiertes Dashboard", "ar": "لوحة حسب الدور", "hi": "भूमिका आधारित डैशबोर्ड"},
    "sqlite_ready": {"th": "พร้อมใช้กับ SQLite", "en": "SQLite Ready", "zh": "支持 SQLite", "ja": "SQLite 対応", "ko": "SQLite 지원", "es": "Compatible con SQLite", "fr": "Prêt pour SQLite", "de": "SQLite bereit", "ar": "جاهز لـ SQLite", "hi": "SQLite समर्थित"},
    "latest_data": {"th": "ข้อมูลล่าสุด", "en": "Latest data", "zh": "最新数据", "ja": "最新データ", "ko": "최신 데이터", "es": "Datos más recientes", "fr": "Données récentes", "de": "Neueste Daten", "ar": "أحدث البيانات", "hi": "नवीनतम डेटा"},
    "latest_announcements": {"th": "ประกาศล่าสุด", "en": "Latest announcements", "zh": "最新公告", "ja": "最新のお知らせ", "ko": "최신 공지", "es": "Últimos anuncios", "fr": "Dernières annonces", "de": "Neueste Ankündigungen", "ar": "أحدث الإعلانات", "hi": "नवीनतम घोषणाएँ"},
    "user_permissions": {"th": "ตามสิทธิ์ของผู้ใช้", "en": "Based on user permissions", "zh": "基于用户权限", "ja": "ユーザー権限に基づく", "ko": "사용자 권한 기준", "es": "Según permisos del usuario", "fr": "Selon les autorisations utilisateur", "de": "Basierend auf Benutzerrechten", "ar": "بحسب صلاحيات المستخدم", "hi": "उपयोगकर्ता अनुमतियों के आधार पर"},
    "no_data": {"th": "ยังไม่มีข้อมูล", "en": "No data yet", "zh": "暂无数据", "ja": "データはまだありません", "ko": "아직 데이터가 없습니다", "es": "Aún no hay datos", "fr": "Pas encore de données", "de": "Noch keine Daten", "ar": "لا توجد بيانات بعد", "hi": "अभी कोई डेटा नहीं है"},
    "footer_note": {"th": "Starter project by ChatGPT", "en": "Starter project by ChatGPT", "zh": "由 ChatGPT 提供的入门项目", "ja": "ChatGPT によるスタータープロジェクト", "ko": "ChatGPT 제공 스타터 프로젝트", "es": "Proyecto inicial por ChatGPT", "fr": "Projet de démarrage par ChatGPT", "de": "Starter-Projekt von ChatGPT", "ar": "مشروع مبدئي من ChatGPT", "hi": "ChatGPT द्वारा स्टार्टर प्रोजेक्ट"},
    "admin": {"th": "ผู้ดูแลระบบ", "en": "Administrator", "zh": "管理员", "ja": "管理者", "ko": "관리자", "es": "Administrador", "fr": "Administrateur", "de": "Administrator", "ar": "المسؤول", "hi": "प्रशासक"},
    "teacher": {"th": "ครู", "en": "Teacher", "zh": "教师", "ja": "教師", "ko": "교사", "es": "Profesor", "fr": "Enseignant", "de": "Lehrer", "ar": "المعلم", "hi": "शिक्षक"},
    "student": {"th": "นักเรียน", "en": "Student", "zh": "学生", "ja": "学生", "ko": "학생", "es": "Estudiante", "fr": "Étudiant", "de": "Schüler", "ar": "الطالب", "hi": "विद्यार्थी"},
    "label_students": {"th": "นักเรียน", "en": "Students", "zh": "学生", "ja": "学生", "ko": "학생", "es": "Estudiantes", "fr": "Étudiants", "de": "Schüler", "ar": "الطلاب", "hi": "छात्र"},
    "label_teachers": {"th": "ครู", "en": "Teachers", "zh": "教师", "ja": "教師", "ko": "교사", "es": "Profesores", "fr": "Enseignants", "de": "Lehrer", "ar": "المعلمون", "hi": "शिक्षक"},
    "label_classes": {"th": "ห้องเรียน", "en": "Classes", "zh": "班级", "ja": "授業", "ko": "수업", "es": "Clases", "fr": "Classes", "de": "Klassen", "ar": "الفصول", "hi": "कक्षाएँ"},
    "label_subjects_taught": {"th": "วิชาที่สอน", "en": "Subjects taught", "zh": "授课科目", "ja": "担当科目", "ko": "담당 과목", "es": "Asignaturas impartidas", "fr": "Matières enseignées", "de": "Unterrichtete Fächer", "ar": "المواد التي يتم تدريسها", "hi": "पढ़ाए जाने वाले विषय"},
    "label_managed_students": {"th": "นักเรียนที่ดูแล", "en": "Managed students", "zh": "管理的学生", "ja": "担当学生数", "ko": "담당 학생", "es": "Estudiantes a cargo", "fr": "Étudiants suivis", "de": "Betreute Schüler", "ar": "الطلاب المشرف عليهم", "hi": "देखरेख वाले छात्र"},
    "label_today_attendance": {"th": "เช็กชื่อวันนี้", "en": "Today's attendance", "zh": "今日考勤", "ja": "本日の出席", "ko": "오늘의 출석", "es": "Asistencia de hoy", "fr": "Présences du jour", "de": "Heutige Anwesenheit", "ar": "حضور اليوم", "hi": "आज की उपस्थिति"},
    "label_registered_subjects": {"th": "วิชาที่ลงทะเบียน", "en": "Registered subjects", "zh": "已注册科目", "ja": "登録科目", "ko": "등록 과목", "es": "Asignaturas inscritas", "fr": "Matières inscrites", "de": "Registrierte Fächer", "ar": "المواد المسجلة", "hi": "पंजीकृत विषय"},
    "label_attendance_records": {"th": "บันทึกการเข้าเรียน", "en": "Attendance records", "zh": "考勤记录", "ja": "出席記録", "ko": "출석 기록", "es": "Registros de asistencia", "fr": "Présences enregistrées", "de": "Anwesenheitsdaten", "ar": "سجلات الحضور", "hi": "उपस्थिति अभिलेख"},
    "label_attendance_rate": {"th": "อัตราการเข้าเรียน", "en": "Attendance rate", "zh": "出勤率", "ja": "出席率", "ko": "출석률", "es": "Tasa de asistencia", "fr": "Taux de présence", "de": "Anwesenheitsquote", "ar": "نسبة الحضور", "hi": "उपस्थिति दर"},
    "table_recent_users": {"th": "ผู้ใช้งานล่าสุด", "en": "Recent users", "zh": "最近用户", "ja": "最近のユーザー", "ko": "최근 사용자", "es": "Usuarios recientes", "fr": "Utilisateurs récents", "de": "Neueste Benutzer", "ar": "المستخدمون الجدد", "hi": "हाल के उपयोगकर्ता"},
    "table_my_schedule": {"th": "ตารางสอนของฉัน", "en": "My teaching schedule", "zh": "我的课表", "ja": "私の授業スケジュール", "ko": "내 수업 일정", "es": "Mi horario de clases", "fr": "Mon emploi du temps", "de": "Mein Stundenplan", "ar": "جدول تدريسي", "hi": "मेरा शिक्षण कार्यक्रम"},
    "table_my_subjects": {"th": "วิชาที่ลงทะเบียน", "en": "My registered subjects", "zh": "我注册的科目", "ja": "登録済み科目", "ko": "내 등록 과목", "es": "Mis asignaturas inscritas", "fr": "Mes matières inscrites", "de": "Meine registrierten Fächer", "ar": "المواد المسجلة", "hi": "मेरे पंजीकृत विषय"},
    "col_name": {"th": "ชื่อ", "en": "Name", "zh": "姓名", "ja": "名前", "ko": "이름", "es": "Nombre", "fr": "Nom", "de": "Name", "ar": "الاسم", "hi": "नाम"},
    "col_email": {"th": "อีเมล", "en": "Email", "zh": "邮箱", "ja": "メール", "ko": "이메일", "es": "Correo", "fr": "E-mail", "de": "E-Mail", "ar": "البريد الإلكتروني", "hi": "ईमेल"},
    "col_role": {"th": "บทบาท", "en": "Role", "zh": "角色", "ja": "役割", "ko": "역할", "es": "Rol", "fr": "Rôle", "de": "Rolle", "ar": "الدور", "hi": "भूमिका"},
    "col_created_at": {"th": "วันที่สมัคร", "en": "Created at", "zh": "创建日期", "ja": "作成日", "ko": "생성일", "es": "Fecha de creación", "fr": "Créé le", "de": "Erstellt am", "ar": "تاريخ الإنشاء", "hi": "निर्माण तिथि"},
    "col_class": {"th": "ห้อง", "en": "Class", "zh": "班级", "ja": "クラス", "ko": "반", "es": "Clase", "fr": "Classe", "de": "Klasse", "ar": "الفصل", "hi": "कक्षा"},
    "col_subject": {"th": "วิชา", "en": "Subject", "zh": "科目", "ja": "科目", "ko": "과목", "es": "Asignatura", "fr": "Matière", "de": "Fach", "ar": "المادة", "hi": "विषय"},
    "col_room": {"th": "ห้องเรียน", "en": "Room", "zh": "教室", "ja": "教室", "ko": "교실", "es": "Aula", "fr": "Salle", "de": "Raum", "ar": "القاعة", "hi": "कक्ष"},
    "please_login_first": {"th": "กรุณาเข้าสู่ระบบก่อน", "en": "Please log in first", "zh": "请先登录", "ja": "先にログインしてください", "ko": "먼저 로그인해 주세요", "es": "Por favor, inicia sesión primero", "fr": "Veuillez vous connecter d'abord", "de": "Bitte melden Sie sich zuerst an", "ar": "يرجى تسجيل الدخول أولاً", "hi": "कृपया पहले लॉगिन करें"},
    "invalid_credentials": {"th": "อีเมลหรือรหัสผ่านไม่ถูกต้อง", "en": "Invalid email or password", "zh": "邮箱或密码不正确", "ja": "メールまたはパスワードが正しくありません", "ko": "이메일 또는 비밀번호가 올바르지 않습니다", "es": "Correo o contraseña no válidos", "fr": "E-mail ou mot de passe invalide", "de": "Ungültige E-Mail oder ungültiges Passwort", "ar": "البريد الإلكتروني أو كلمة المرور غير صحيحة", "hi": "ईमेल या पासवर्ड गलत है"},
    "welcome_user": {"th": "ยินดีต้อนรับ {name}", "en": "Welcome {name}", "zh": "欢迎，{name}", "ja": "ようこそ {name}", "ko": "환영합니다, {name}", "es": "Bienvenido, {name}", "fr": "Bienvenue {name}", "de": "Willkommen {name}", "ar": "مرحباً {name}", "hi": "स्वागत है, {name}"},
    "fill_all_fields": {"th": "กรุณากรอกข้อมูลให้ครบถ้วน", "en": "Please fill in all required fields", "zh": "请填写所有必填字段", "ja": "必須項目をすべて入力してください", "ko": "필수 항목을 모두 입력해 주세요", "es": "Por favor, complete todos los campos obligatorios", "fr": "Veuillez remplir tous les champs requis", "de": "Bitte füllen Sie alle Pflichtfelder aus", "ar": "يرجى تعبئة جميع الحقول المطلوبة", "hi": "कृपया सभी आवश्यक फ़ील्ड भरें"},
    "invalid_role": {"th": "บทบาทที่เลือกไม่ถูกต้อง", "en": "Selected role is invalid", "zh": "所选角色无效", "ja": "選択した役割は無効です", "ko": "선택한 역할이 올바르지 않습니다", "es": "El rol seleccionado no es válido", "fr": "Le rôle sélectionné n'est pas valide", "de": "Die ausgewählte Rolle ist ungültig", "ar": "الدور المحدد غير صالح", "hi": "चयनित भूमिका अमान्य है"},
    "password_mismatch": {"th": "ยืนยันรหัสผ่านไม่ตรงกัน", "en": "Passwords do not match", "zh": "两次输入的密码不一致", "ja": "パスワードが一致しません", "ko": "비밀번호가 일치하지 않습니다", "es": "Las contraseñas no coinciden", "fr": "Les mots de passe ne correspondent pas", "de": "Passwörter stimmen nicht überein", "ar": "كلمتا المرور غير متطابقتين", "hi": "पासवर्ड मेल नहीं खाते"},
    "password_too_short": {"th": "รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร", "en": "Password must be at least 6 characters", "zh": "密码至少需要 6 个字符", "ja": "パスワードは6文字以上にしてください", "ko": "비밀번호는 6자 이상이어야 합니다", "es": "La contraseña debe tener al menos 6 caracteres", "fr": "Le mot de passe doit contenir au moins 6 caractères", "de": "Das Passwort muss mindestens 6 Zeichen lang sein", "ar": "يجب أن تتكون كلمة المرور من 6 أحرف على الأقل", "hi": "पासवर्ड कम से कम 6 अक्षरों का होना चाहिए"},
    "email_in_use": {"th": "อีเมลนี้ถูกใช้งานแล้ว", "en": "This email is already in use", "zh": "该邮箱已被使用", "ja": "このメールアドレスは既に使用されています", "ko": "이미 사용 중인 이메일입니다", "es": "Este correo ya está en uso", "fr": "Cet e-mail est déjà utilisé", "de": "Diese E-Mail wird bereits verwendet", "ar": "هذا البريد الإلكتروني مستخدم بالفعل", "hi": "यह ईमेल पहले से उपयोग में है"},
    "register_success": {"th": "สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ", "en": "Registration successful. Please log in.", "zh": "注册成功，请登录。", "ja": "登録に成功しました。ログインしてください。", "ko": "회원가입이 완료되었습니다. 로그인해 주세요.", "es": "Registro exitoso. Por favor, inicia sesión.", "fr": "Inscription réussie. Veuillez vous connecter.", "de": "Registrierung erfolgreich. Bitte melden Sie sich an.", "ar": "تم التسجيل بنجاح. يرجى تسجيل الدخول.", "hi": "पंजीकरण सफल हुआ। कृपया लॉगिन करें।"},
    "logout_success": {"th": "ออกจากระบบเรียบร้อยแล้ว", "en": "Logged out successfully", "zh": "已成功退出登录", "ja": "ログアウトしました", "ko": "로그아웃되었습니다", "es": "Sesión cerrada correctamente", "fr": "Déconnexion réussie", "de": "Erfolgreich abgemeldet", "ar": "تم تسجيل الخروج بنجاح", "hi": "सफलतापूर्वक लॉगआउट हो गया"},
    "lang_changed": {"th": "เปลี่ยนภาษาเรียบร้อยแล้ว", "en": "Language changed successfully", "zh": "语言切换成功", "ja": "言語を変更しました", "ko": "언어가 변경되었습니다", "es": "Idioma cambiado correctamente", "fr": "Langue modifiée avec succès", "de": "Sprache erfolgreich geändert", "ar": "تم تغيير اللغة بنجاح", "hi": "भाषा सफलतापूर्वक बदल दी गई"},
}


# -----------------------------
# Translation helpers
# -----------------------------
def get_locale() -> str:
    lang = session.get("lang", DEFAULT_LANG)
    if lang not in LANGUAGES:
        return DEFAULT_LANG
    return lang


def tr(key: str, **kwargs: Any) -> str:
    lang = get_locale()
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        return text.format(**kwargs)
    return text


def role_label(role: str) -> str:
    return tr(role)


@app.before_request
def apply_language_choice() -> None:
    lang = request.args.get("lang") or request.form.get("lang")
    if lang in LANGUAGES:
        session["lang"] = lang


# -----------------------------
# Database helpers
# -----------------------------
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(query: str, args: tuple[Any, ...] = (), one: bool = False):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query: str, args: tuple[Any, ...] = ()) -> None:
    db = get_db()
    db.execute(query, args)
    db.commit()


# -----------------------------
# Auth helpers
# -----------------------------
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash(tr("please_login_first"), "warning")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def current_user() -> sqlite3.Row | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    return query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)


@app.context_processor
def inject_globals() -> dict[str, Any]:
    return {
        "current_user": current_user(),
        "current_year": datetime.now().year,
        "current_lang": get_locale(),
        "languages": LANGUAGES,
        "is_rtl": get_locale() in RTL_LANGS,
        "t": tr,
        "role_label": role_label,
    }


# -----------------------------
# Database initialization + seed
# -----------------------------
def init_db() -> None:
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")

    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student')),
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            room TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            UNIQUE(user_id, class_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (class_id) REFERENCES classes(id)
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            audience TEXT NOT NULL CHECK(audience IN ('all', 'teacher', 'student')),
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('present', 'late', 'absent')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (class_id) REFERENCES classes(id)
        );
        """
    )
    db.commit()

    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        now = datetime.now().isoformat(timespec="seconds")
        admin_pw = generate_password_hash("admin123")
        teacher_pw = generate_password_hash("teacher123")
        student_pw = generate_password_hash("student123")

        db.execute(
            "INSERT INTO users (full_name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("System Admin", "admin@school.local", admin_pw, "admin", now),
        )
        db.execute(
            "INSERT INTO users (full_name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Narin Teacher", "teacher@school.local", teacher_pw, "teacher", now),
        )
        db.execute(
            "INSERT INTO users (full_name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Mali Student", "student@school.local", student_pw, "student", now),
        )
        db.commit()

        teacher_id = db.execute("SELECT id FROM users WHERE email = 'teacher@school.local'").fetchone()[0]
        student_id = db.execute("SELECT id FROM users WHERE email = 'student@school.local'").fetchone()[0]

        classes = [
            ("M.1/1", "Mathematics", "A-101", teacher_id),
            ("M.1/1", "Science", "B-204", teacher_id),
            ("M.1/2", "English", "C-305", teacher_id),
        ]
        db.executemany(
            "INSERT INTO classes (class_name, subject_name, room, teacher_id) VALUES (?, ?, ?, ?)",
            classes,
        )
        db.commit()

        class_rows = db.execute("SELECT id FROM classes ORDER BY id").fetchall()
        db.executemany(
            "INSERT INTO enrollments (user_id, class_id) VALUES (?, ?)",
            [(student_id, class_rows[0][0]), (student_id, class_rows[1][0])],
        )

        announcements = [
            (
                "เปิดภาคเรียนใหม่",
                "ยินดีต้อนรับสู่ภาคเรียนใหม่ กรุณาตรวจสอบตารางเรียนและชำระค่าธรรมเนียมภายในสัปดาห์แรก",
                "all",
                now,
            ),
            (
                "ประชุมครูประจำเดือน",
                "ประชุมครูทุกวันศุกร์ เวลา 15:30 น. ที่ห้องประชุมใหญ่",
                "teacher",
                now,
            ),
            (
                "ส่งการบ้านออนไลน์",
                "นักเรียนทุกคนต้องส่งการบ้านผ่านระบบก่อนเวลา 22:00 น.",
                "student",
                now,
            ),
        ]
        db.executemany(
            "INSERT INTO announcements (title, content, audience, created_at) VALUES (?, ?, ?, ?)",
            announcements,
        )

        today = date.today().isoformat()
        attendance_rows = [
            (student_id, class_rows[0][0], today, "present"),
            (student_id, class_rows[1][0], today, "late"),
            (student_id, class_rows[0][0], "2026-03-20", "present"),
            (student_id, class_rows[1][0], "2026-03-21", "absent"),
        ]
        db.executemany(
            "INSERT INTO attendance (user_id, class_id, attendance_date, status) VALUES (?, ?, ?, ?)",
            attendance_rows,
        )

    db.commit()
    db.close()


# -----------------------------
# View helpers
# -----------------------------
def get_dashboard_data(user: sqlite3.Row) -> dict[str, Any]:
    role = user["role"]

    announcements = query_db(
        """
        SELECT * FROM announcements
        WHERE audience = 'all' OR audience = ?
        ORDER BY datetime(created_at) DESC
        LIMIT 5
        """,
        (role,),
    )

    if role == "admin":
        total_students = query_db("SELECT COUNT(*) AS total FROM users WHERE role = 'student'", one=True)["total"]
        total_teachers = query_db("SELECT COUNT(*) AS total FROM users WHERE role = 'teacher'", one=True)["total"]
        total_classes = query_db("SELECT COUNT(*) AS total FROM classes", one=True)["total"]
        latest_users = query_db(
            "SELECT full_name, email, role, created_at FROM users ORDER BY datetime(created_at) DESC LIMIT 5"
        )
        return {
            "stats": [
                {"label": tr("label_students"), "value": total_students},
                {"label": tr("label_teachers"), "value": total_teachers},
                {"label": tr("label_classes"), "value": total_classes},
            ],
            "announcements": announcements,
            "table_title": tr("table_recent_users"),
            "table_headers": [tr("col_name"), tr("col_email"), tr("col_role"), tr("col_created_at")],
            "table_rows": [
                [row["full_name"], row["email"], role_label(row["role"]), row["created_at"][:10]] for row in latest_users
            ],
        }

    if role == "teacher":
        my_classes = query_db(
            "SELECT class_name, subject_name, room FROM classes WHERE teacher_id = ? ORDER BY subject_name",
            (user["id"],),
        )
        total_classes = len(my_classes)
        total_students = query_db(
            """
            SELECT COUNT(DISTINCT e.user_id) AS total
            FROM enrollments e
            JOIN classes c ON c.id = e.class_id
            WHERE c.teacher_id = ?
            """,
            (user["id"],),
            one=True,
        )["total"]
        today_attendance = query_db(
            """
            SELECT COUNT(*) AS total
            FROM attendance a
            JOIN classes c ON c.id = a.class_id
            WHERE c.teacher_id = ? AND attendance_date = ?
            """,
            (user["id"], date.today().isoformat()),
            one=True,
        )["total"]
        return {
            "stats": [
                {"label": tr("label_subjects_taught"), "value": total_classes},
                {"label": tr("label_managed_students"), "value": total_students},
                {"label": tr("label_today_attendance"), "value": today_attendance},
            ],
            "announcements": announcements,
            "table_title": tr("table_my_schedule"),
            "table_headers": [tr("col_class"), tr("col_subject"), tr("col_room")],
            "table_rows": [[row["class_name"], row["subject_name"], row["room"]] for row in my_classes],
        }

    enrolled_classes = query_db(
        """
        SELECT c.class_name, c.subject_name, c.room
        FROM enrollments e
        JOIN classes c ON c.id = e.class_id
        WHERE e.user_id = ?
        ORDER BY c.subject_name
        """,
        (user["id"],),
    )
    total_classes = len(enrolled_classes)
    attendance_summary = query_db(
        "SELECT COUNT(*) AS total FROM attendance WHERE user_id = ?",
        (user["id"],),
        one=True,
    )["total"]
    present_summary = query_db(
        "SELECT COUNT(*) AS total FROM attendance WHERE user_id = ? AND status IN ('present', 'late')",
        (user["id"],),
        one=True,
    )["total"]
    attendance_rate = f"{(present_summary / attendance_summary * 100):.0f}%" if attendance_summary else "0%"

    return {
        "stats": [
            {"label": tr("label_registered_subjects"), "value": total_classes},
            {"label": tr("label_attendance_records"), "value": attendance_summary},
            {"label": tr("label_attendance_rate"), "value": attendance_rate},
        ],
        "announcements": announcements,
        "table_title": tr("table_my_subjects"),
        "table_headers": [tr("col_class"), tr("col_subject"), tr("col_room")],
        "table_rows": [[row["class_name"], row["subject_name"], row["room"]] for row in enrolled_classes],
    }


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/set-language", methods=["POST"])
def set_language():
    lang = request.form.get("lang", DEFAULT_LANG)
    if lang in LANGUAGES:
        session["lang"] = lang
        flash(tr("lang_changed"), "success")
    next_url = request.form.get("next") or request.referrer or url_for("index")
    return redirect(next_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if user is None or not check_password_hash(user["password_hash"], password):
            flash(tr("invalid_credentials"), "danger")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user["id"]
        session.setdefault("lang", DEFAULT_LANG)
        flash(tr("welcome_user", name=user["full_name"]), "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "student")

        allowed_roles = {"student", "teacher"}

        if not full_name or not email or not password:
            flash(tr("fill_all_fields"), "warning")
            return render_template("register.html")
        if role not in allowed_roles:
            flash(tr("invalid_role"), "danger")
            return render_template("register.html")
        if password != confirm_password:
            flash(tr("password_mismatch"), "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash(tr("password_too_short"), "warning")
            return render_template("register.html")

        existing_user = query_db("SELECT id FROM users WHERE email = ?", (email,), one=True)
        if existing_user:
            flash(tr("email_in_use"), "danger")
            return render_template("register.html")

        execute_db(
            "INSERT INTO users (full_name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (full_name, email, generate_password_hash(password), role, datetime.now().isoformat(timespec="seconds")),
        )
        flash(tr("register_success"), "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user is None:
        return redirect(url_for("login"))
    data = get_dashboard_data(user)
    return render_template("dashboard.html", dashboard=data)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash(tr("logout_success"), "info")
    return redirect(url_for("login"))


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
