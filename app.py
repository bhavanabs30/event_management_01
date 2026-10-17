# event_management_app.py
# Complete Event Management with QR Code, Maps & Real-time Analytics
# Run with: python event_management_app.py

from flask import Flask, request, jsonify, render_template_string, session, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import qrcode
from io import BytesIO
import base64
import json
import random
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production-2024'
CORS(app, supports_credentials=True)

# ========== EMAIL CONFIGURATION ==========
EMAIL_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "your-email@gmail.com"  # REPLACE with your Gmail
SMTP_PASSWORD = "your-app-password"  # REPLACE with your App Password

# ========== USER DATABASE ==========
users = {
    'admin': {
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'email': 'admin@eventvault.com',
        'name': 'Admin User',
        'created': datetime.now().isoformat()
    },
    'demo': {
        'password': hashlib.sha256('demo123'.encode()).hexdigest(),
        'role': 'user',
        'email': 'demo@eventvault.com',
        'name': 'Demo User',
        'created': datetime.now().isoformat()
    }
}

# ========== 20 EVENTS DATA ==========
events_data = [
    {"id": 1, "name": "Tech Summit 2026", "date": "2026-08-12", "time": "10:00 AM", "category": "Conference", "attendees": 320, "venue": "Grand Hall", "status": "upcoming", "price": 199, "capacity": 500, "organizer": "Tech Corp", "description": "Annual technology conference with industry leaders", "emoji": "💻", "lat": 40.7128, "lng": -74.0060},
    {"id": 2, "name": "Pizza Hackathon", "date": "2026-08-15", "time": "2:00 PM", "category": "Workshop", "attendees": 85, "venue": "The Loft", "status": "upcoming", "price": 49, "capacity": 150, "organizer": "Dev Community", "description": "Build apps while enjoying unlimited pizza", "emoji": "🍕", "lat": 40.7135, "lng": -74.0070},
    {"id": 3, "name": "Art Gala Night", "date": "2026-08-20", "time": "7:00 PM", "category": "Social", "attendees": 150, "venue": "Garden Plaza", "status": "upcoming", "price": 75, "capacity": 300, "organizer": "Art Collective", "description": "Evening of art, wine, and networking", "emoji": "🎨", "lat": 40.7140, "lng": -74.0080},
    {"id": 4, "name": "Startup Mixer", "date": "2026-08-25", "time": "6:30 PM", "category": "Networking", "attendees": 200, "venue": "Bayview", "status": "upcoming", "price": 45, "capacity": 250, "organizer": "Startup Hub", "description": "Connect with entrepreneurs and investors", "emoji": "🤝", "lat": 40.7150, "lng": -74.0090},
    {"id": 5, "name": "AI & ML Summit", "date": "2026-09-05", "time": "9:00 AM", "category": "Conference", "attendees": 500, "venue": "City Center", "status": "upcoming", "price": 299, "capacity": 800, "organizer": "AI Institute", "description": "Deep dive into cutting-edge AI technologies", "emoji": "🧠", "lat": 40.7160, "lng": -74.0100},
    {"id": 6, "name": "Music Festival 2026", "date": "2026-09-10", "time": "4:00 PM", "category": "Entertainment", "attendees": 1000, "venue": "Rooftop Lounge", "status": "upcoming", "price": 150, "capacity": 1200, "organizer": "Music Events", "description": "Live music, food, and fun", "emoji": "🎵", "lat": 40.7170, "lng": -74.0110},
    {"id": 7, "name": "Blockchain Conference", "date": "2026-09-15", "time": "10:00 AM", "category": "Conference", "attendees": 350, "venue": "Grand Hall", "status": "upcoming", "price": 249, "capacity": 500, "organizer": "Blockchain Corp", "description": "The future of decentralized technology", "emoji": "⛓️", "lat": 40.7128, "lng": -74.0060},
    {"id": 8, "name": "Yoga & Wellness Retreat", "date": "2026-09-20", "time": "8:00 AM", "category": "Wellness", "attendees": 120, "venue": "Beachfront Resort", "status": "upcoming", "price": 89, "capacity": 200, "organizer": "Wellness Co", "description": "Relax, recharge, and rejuvenate", "emoji": "🧘", "lat": 40.7180, "lng": -74.0120},
    {"id": 9, "name": "Food Festival 2026", "date": "2026-09-25", "time": "11:00 AM", "category": "Entertainment", "attendees": 800, "venue": "Garden Plaza", "status": "upcoming", "price": 35, "capacity": 1000, "organizer": "Food Events", "description": "Taste the best cuisines from around the world", "emoji": "🌮", "lat": 40.7140, "lng": -74.0080},
    {"id": 10, "name": "Cyber Security Summit", "date": "2026-10-01", "time": "9:30 AM", "category": "Conference", "attendees": 280, "venue": "City Center", "status": "upcoming", "price": 199, "capacity": 400, "organizer": "Security Corp", "description": "Protecting data in the digital age", "emoji": "🛡️", "lat": 40.7160, "lng": -74.0100},
    {"id": 11, "name": "Film Screening Night", "date": "2026-10-05", "time": "7:00 PM", "category": "Social", "attendees": 180, "venue": "The Loft", "status": "upcoming", "price": 25, "capacity": 200, "organizer": "Film Society", "description": "Independent films and networking", "emoji": "🎬", "lat": 40.7135, "lng": -74.0070},
    {"id": 12, "name": "Quantum Computing Workshop", "date": "2026-10-10", "time": "1:00 PM", "category": "Workshop", "attendees": 60, "venue": "Conference Room A", "status": "upcoming", "price": 149, "capacity": 80, "organizer": "Quantum Lab", "description": "Introduction to quantum computing", "emoji": "⚛️", "lat": 40.7190, "lng": -74.0130},
    {"id": 13, "name": "Fashion Show 2026", "date": "2026-10-15", "time": "6:00 PM", "category": "Entertainment", "attendees": 300, "venue": "Grand Hall", "status": "upcoming", "price": 120, "capacity": 400, "organizer": "Fashion Week", "description": "Showcasing the latest trends", "emoji": "👗", "lat": 40.7128, "lng": -74.0060},
    {"id": 14, "name": "Entrepreneurship Bootcamp", "date": "2026-10-20", "time": "9:00 AM", "category": "Workshop", "attendees": 100, "venue": "Bayview", "status": "upcoming", "price": 199, "capacity": 150, "organizer": "Startup Academy", "description": "Build your startup from scratch", "emoji": "🚀", "lat": 40.7150, "lng": -74.0090},
    {"id": 15, "name": "Gaming Tournament", "date": "2026-10-25", "time": "12:00 PM", "category": "Entertainment", "attendees": 250, "venue": "Rooftop Lounge", "status": "upcoming", "price": 55, "capacity": 300, "organizer": "Gaming League", "description": "Compete in the ultimate gaming championship", "emoji": "🎮", "lat": 40.7170, "lng": -74.0110},
    {"id": 16, "name": "Green Energy Conference", "date": "2026-11-01", "time": "10:00 AM", "category": "Conference", "attendees": 400, "venue": "City Center", "status": "upcoming", "price": 179, "capacity": 600, "organizer": "Green Future", "description": "Sustainable energy solutions", "emoji": "🌿", "lat": 40.7160, "lng": -74.0100},
    {"id": 17, "name": "Wine Tasting Evening", "date": "2026-11-05", "time": "6:30 PM", "category": "Social", "attendees": 100, "venue": "Art Gallery", "status": "upcoming", "price": 65, "capacity": 120, "organizer": "Wine Club", "description": "Experience fine wines from around the world", "emoji": "🍷", "lat": 40.7200, "lng": -74.0140},
    {"id": 18, "name": "Robotics Competition", "date": "2026-11-10", "time": "9:00 AM", "category": "Workshop", "attendees": 200, "venue": "Grand Hall", "status": "upcoming", "price": 89, "capacity": 300, "organizer": "Robotics Lab", "description": "Build and compete with robots", "emoji": "🤖", "lat": 40.7128, "lng": -74.0060},
    {"id": 19, "name": "Photography Exhibition", "date": "2026-11-15", "time": "11:00 AM", "category": "Social", "attendees": 150, "venue": "Art Gallery", "status": "upcoming", "price": 30, "capacity": 200, "organizer": "Photo Society", "description": "Incredible photography from around the world", "emoji": "📸", "lat": 40.7200, "lng": -74.0140},
    {"id": 20, "name": "New Year's Eve Gala", "date": "2026-12-31", "time": "8:00 PM", "category": "Entertainment", "attendees": 800, "venue": "Rooftop Lounge", "status": "upcoming", "price": 250, "capacity": 1000, "organizer": "Gala Events", "description": "Ring in the New Year with style", "emoji": "🎉", "lat": 40.7170, "lng": -74.0110},
]

venues_data = [
    {"id": 1, "name": "Grand Hall", "capacity": 500, "price": 2000, "available": True, "address": "123 Main St, NYC", "rating": 4.8, "emoji": "🏛️", "lat": 40.7128, "lng": -74.0060},
    {"id": 2, "name": "Garden Plaza", "capacity": 300, "price": 1500, "available": True, "address": "456 Park Ave, NYC", "rating": 4.6, "emoji": "🌺", "lat": 40.7140, "lng": -74.0080},
    {"id": 3, "name": "The Loft", "capacity": 150, "price": 800, "available": True, "address": "789 Art St, NYC", "rating": 4.9, "emoji": "🏗️", "lat": 40.7135, "lng": -74.0070},
    {"id": 4, "name": "Bayview", "capacity": 200, "price": 1200, "available": True, "address": "101 Bay St, NYC", "rating": 4.7, "emoji": "🌊", "lat": 40.7150, "lng": -74.0090},
    {"id": 5, "name": "City Center", "capacity": 800, "price": 3500, "available": True, "address": "202 Center Plaza, NYC", "rating": 4.9, "emoji": "🏙️", "lat": 40.7160, "lng": -74.0100},
    {"id": 6, "name": "Rooftop Lounge", "capacity": 1200, "price": 4000, "available": True, "address": "303 Sky Ave, NYC", "rating": 4.9, "emoji": "🌆", "lat": 40.7170, "lng": -74.0110},
    {"id": 7, "name": "Beachfront Resort", "capacity": 400, "price": 2800, "available": True, "address": "606 Ocean Dr, NYC", "rating": 4.7, "emoji": "🏖️", "lat": 40.7180, "lng": -74.0120},
    {"id": 8, "name": "Art Gallery", "capacity": 100, "price": 600, "available": True, "address": "505 Museum St, NYC", "rating": 4.8, "emoji": "🎨", "lat": 40.7200, "lng": -74.0140},
    {"id": 9, "name": "Conference Room A", "capacity": 50, "price": 400, "available": True, "address": "404 Business Ave, NYC", "rating": 4.5, "emoji": "📋", "lat": 40.7190, "lng": -74.0130},
]

food_data = [
    {"id": 1, "name": "Italian Buffet", "price": 35, "type": "buffet", "available": True, "description": "Pasta, pizza, and more", "cuisine": "Italian", "rating": 4.8, "emoji": "🍝", "color": "#e74c3c"},
    {"id": 2, "name": "Vegan Bowl", "price": 28, "type": "plated", "available": True, "description": "Healthy plant-based", "cuisine": "Vegan", "rating": 4.6, "emoji": "🥗", "color": "#27ae60"},
    {"id": 3, "name": "Seafood Platter", "price": 42, "type": "buffet", "available": True, "description": "Fresh seafood selection", "cuisine": "Seafood", "rating": 4.9, "emoji": "🦞", "color": "#2980b9"},
    {"id": 4, "name": "Bakery Spread", "price": 20, "type": "snack", "available": True, "description": "Pastries and desserts", "cuisine": "Bakery", "rating": 4.7, "emoji": "🥐", "color": "#f39c12"},
    {"id": 5, "name": "Asian Fusion", "price": 38, "type": "buffet", "available": True, "description": "Sushi, dim sum, and more", "cuisine": "Asian", "rating": 4.8, "emoji": "🍣", "color": "#e67e22"},
    {"id": 6, "name": "BBQ Grill", "price": 45, "type": "buffet", "available": True, "description": "Grilled meats and sides", "cuisine": "BBQ", "rating": 4.9, "emoji": "🥩", "color": "#c0392b"},
    {"id": 7, "name": "Mediterranean", "price": 32, "type": "plated", "available": True, "description": "Greek and Middle Eastern", "cuisine": "Mediterranean", "rating": 4.7, "emoji": "🥙", "color": "#2ecc71"},
    {"id": 8, "name": "Mexican Fiesta", "price": 30, "type": "buffet", "available": True, "description": "Tacos, burritos, and more", "cuisine": "Mexican", "rating": 4.6, "emoji": "🌮", "color": "#e67e22"},
    {"id": 9, "name": "French Cuisine", "price": 48, "type": "plated", "available": True, "description": "Elegant French dining", "cuisine": "French", "rating": 4.9, "emoji": "🥖", "color": "#8e44ad"},
    {"id": 10, "name": "Indian Feast", "price": 35, "type": "buffet", "available": True, "description": "Spices and flavors", "cuisine": "Indian", "rating": 4.8, "emoji": "🍛", "color": "#d35400"},
]

payment_data = [
    {"id": 1, "name": "Visa", "fee": 2.5, "available": True, "icon": "fa-cc-visa"},
    {"id": 2, "name": "Mastercard", "fee": 2.5, "available": True, "icon": "fa-cc-mastercard"},
    {"id": 3, "name": "PayPal", "fee": 3.0, "available": True, "icon": "fa-cc-paypal"},
    {"id": 4, "name": "GPay", "fee": 1.5, "available": True, "icon": "fa-mobile-alt"},
    {"id": 5, "name": "Apple Pay", "fee": 1.5, "available": True, "icon": "fa-apple"},
    {"id": 6, "name": "Cryptocurrency", "fee": 0.5, "available": True, "icon": "fa-bitcoin"},
    {"id": 7, "name": "Bank Transfer", "fee": 0.0, "available": True, "icon": "fa-university"},
]

feedback_storage = []
event_registrations = []
selected_options = {'venue': None, 'food': None, 'payment': None}
email_log = []
qr_codes = {}
check_ins = []
analytics_data = {
    'page_views': 0,
    'bookings_today': 0,
    'check_ins_today': 0,
    'revenue_today': 0,
    'popular_events': {},
    'hourly_activity': {str(i).zfill(2)+':00': 0 for i in range(24)}
}

# ========== QR CODE FUNCTIONS ==========
def generate_qr_code(data):
    """Generate QR code for booking"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        print(f"QR Code generation error: {e}")
        return None

# ========== EMAIL FUNCTIONS ==========
def send_booking_email(user_email, user_name, booking_details, qr_code_data):
    """Send booking confirmation email with QR code"""
    if not EMAIL_ENABLED:
        print(f"📧 [EMAIL] Booking confirmation to {user_email}")
        return True
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎫 EventVault Booking Confirmation - {booking_details['event_name']}"
        msg['From'] = SMTP_EMAIL
        msg['To'] = user_email

        # QR Code image embed
        qr_img = f'<img src="data:image/png;base64,{qr_code_data}" style="max-width:200px;border:2px solid #4f46e5;border-radius:12px;padding:10px;background:white;">' if qr_code_data else ''

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; padding: 20px; margin: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; padding: 35px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 3px solid #4f46e5; padding-bottom: 20px; margin-bottom: 25px; }}
                .header h1 {{ color: #4f46e5; margin: 0; font-size: 28px; }}
                .badge {{ background: #10b981; color: white; padding: 8px 24px; border-radius: 50px; display: inline-block; font-weight: 600; margin: 15px 0; }}
                .qr-container {{ text-align: center; margin: 20px 0; padding: 15px; background: #f9fafb; border-radius: 12px; }}
                .qr-container p {{ color: #6b7280; font-size: 14px; }}
                .details {{ margin: 20px 0; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb; }}
                .label {{ font-weight: 600; color: #374151; }}
                .value {{ color: #1f2937; }}
                .total {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0; }}
                .total .amount {{ font-size: 32px; font-weight: 700; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 14px; }}
                .info {{ background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .info p {{ margin: 5px 0; color: #4b5563; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎫 EventVault</h1>
                    <p>Your booking is confirmed!</p>
                </div>
                
                <div style="text-align:center;"><span class="badge">✓ CONFIRMED</span></div>
                
                <div class="qr-container">
                    <p><strong>🎟️ Scan this QR code at the entrance</strong></p>
                    {qr_img}
                    <p style="font-size:12px;color:#9ca3af;">Booking ID: #{booking_details['booking_id']}</p>
                </div>
                
                <div class="details">
                    <div class="detail-row"><span class="label">Event</span><span class="value"><strong>{booking_details['event_name']}</strong></span></div>
                    <div class="detail-row"><span class="label">📅 Date</span><span class="value">{booking_details['event_date']}</span></div>
                    <div class="detail-row"><span class="label">⏰ Time</span><span class="value">{booking_details['event_time']}</span></div>
                    <div class="detail-row"><span class="label">📍 Venue</span><span class="value">{booking_details['venue']}</span></div>
                    <div class="detail-row"><span class="label">🍽️ Food</span><span class="value">{booking_details['food']}</span></div>
                    <div class="detail-row"><span class="label">💳 Payment</span><span class="value">{booking_details['payment']}</span></div>
                    <div class="detail-row"><span class="label">🎟️ Tickets</span><span class="value">{booking_details['tickets']}</span></div>
                </div>
                
                <div class="total">
                    <div class="label">Total Amount</div>
                    <div class="amount">${booking_details['total_price']}</div>
                </div>
                
                <div class="info">
                    <p><strong>📌 Booking ID:</strong> #{booking_details['booking_id']}</p>
                    <p><strong>📅 Booked on:</strong> {booking_details['booked_date']}</p>
                    <p><strong>📧 Email:</strong> {user_email}</p>
                </div>
                
                <div class="footer">
                    <p>Thank you for booking with <strong>EventVault</strong>!</p>
                    <p style="font-size:12px;color:#9ca3af;">Present this QR code at the entrance for check-in.</p>
                </div>
            </div>
        </body>
        </html>
        """

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        email_log.append({
            'to': user_email,
            'booking_id': booking_details['booking_id'],
            'timestamp': datetime.now().isoformat(),
            'status': 'sent'
        })
        return True
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        email_log.append({
            'to': user_email,
            'booking_id': booking_details['booking_id'],
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'error': str(e)
        })
        return False

# ========== HTML TEMPLATE ==========
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EventVault · Premium Event Management</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', system-ui, sans-serif; transition: all 0.2s; }
        :root {
            --bg-main: #f4f6fa;
            --bg-card: #ffffff;
            --bg-card-alt: #f0f2f6;
            --text-main: #1e1e2f;
            --text-muted: #3a3a4e;
            --border-light: #d0d5dd;
            --shadow: 0 8px 20px rgba(0,0,0,0.04);
            --accent: #4f46e5;
            --accent-soft: #e0e7ff;
            --success: #16a34a;
            --danger: #dc2626;
            --warning: #f59e0b;
            --gold: #f59e0b;
        }
        body.dark {
            --bg-main: #12121c;
            --bg-card: #1e1e2f;
            --bg-card-alt: #2a2a3e;
            --text-main: #eaeef2;
            --text-muted: #b0b8c5;
            --border-light: #32324a;
            --shadow: 0 8px 20px rgba(0,0,0,0.6);
            --accent: #818cf8;
            --accent-soft: #2e2a4a;
        }
        body { background: var(--bg-main); color: var(--text-main); min-height: 100vh; }
        .app-wrapper { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
        .login-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, var(--accent), #7c3aed); padding: 1rem; }
        .login-box { background: var(--bg-card); padding: 2.5rem; border-radius: 2rem; box-shadow: var(--shadow); width: 100%; max-width: 440px; border: 1px solid var(--border-light); }
        .login-box h2 { margin-bottom: 0.5rem; font-size: 2rem; }
        .login-box .subtitle { color: var(--text-muted); margin-bottom: 1.5rem; }
        .login-box input { width: 100%; padding: 0.8rem 1rem; margin-bottom: 0.8rem; border: 1px solid var(--border-light); border-radius: 0.8rem; background: var(--bg-main); color: var(--text-main); font-size: 1rem; }
        .login-box button { width: 100%; padding: 0.8rem; background: var(--accent); color: white; border: none; border-radius: 0.8rem; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .login-box button:hover { opacity: 0.9; }
        .login-box .error { color: var(--danger); margin-top: 0.5rem; text-align: center; }
        .login-box .success { color: var(--success); margin-top: 0.5rem; text-align: center; }
        .login-box .toggle-link { color: var(--accent); cursor: pointer; text-decoration: underline; font-weight: 500; }
        .login-box .demo-cred { margin-top: 1.5rem; padding: 1rem; background: var(--bg-card-alt); border-radius: 0.8rem; font-size: 0.9rem; color: var(--text-muted); }
        .hidden { display: none !important; }
        
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; margin-bottom: 2rem; border-bottom: 1px solid var(--border-light); flex-wrap: wrap; gap: 1rem; }
        .navbar .logo h1 { font-size: 1.8rem; font-weight: 600; }
        .navbar .logo i { color: var(--accent); margin-right: 6px; }
        .navbar .nav-actions { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; }
        .navbar .nav-actions button { background: none; border: 1px solid var(--border-light); padding: 0.4rem 0.8rem; border-radius: 40px; cursor: pointer; color: var(--text-main); transition: all 0.2s; }
        .navbar .nav-actions button:hover { background: var(--accent-soft); transform: scale(1.05); }
        .navbar .user-badge { padding: 0.4rem 1rem; background: var(--accent-soft); border-radius: 40px; font-size: 0.9rem; }
        
        .dashboard-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; margin-bottom: 2rem; }
        .stat-card { background: var(--bg-card); border-radius: 1.2rem; padding: 1.2rem; box-shadow: var(--shadow); border: 1px solid var(--border-light); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
        .stat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.1); }
        .stat-card .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); }
        .stat-card .value { font-size: 2rem; font-weight: 600; margin: 0.2rem 0; }
        .stat-card .sub { font-size: 0.75rem; color: var(--text-muted); }
        .stat-card i { color: var(--accent); margin-right: 6px; }
        
        .analytics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; margin-bottom: 2rem; }
        .analytics-card { background: var(--bg-card); border-radius: 1.2rem; padding: 1.2rem; box-shadow: var(--shadow); border: 1px solid var(--border-light); }
        .analytics-card .label { font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); }
        .analytics-card .value { font-size: 1.8rem; font-weight: 700; margin: 0.2rem 0; }
        .analytics-card .change { font-size: 0.75rem; color: var(--success); }
        .analytics-card .change.down { color: var(--danger); }
        .analytics-card i { color: var(--accent); margin-right: 6px; }
        
        .two-col { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
        .card { background: var(--bg-card); border-radius: 1.2rem; padding: 1.2rem 1.5rem; box-shadow: var(--shadow); border: 1px solid var(--border-light); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 0.5rem; }
        .card-header h3 { font-weight: 600; font-size: 1.2rem; }
        .chart-container { height: 180px; }
        .badge { background: var(--badge-bg); border-radius: 30px; padding: 0.2rem 0.8rem; font-size: 0.7rem; font-weight: 500; }
        .badge-success { background: #16a34a20; color: #16a34a; }
        .badge-danger { background: #dc262620; color: #dc2626; }
        .badge-info { background: #3b82f620; color: #3b82f6; }
        .badge-gold { background: #f59e0b20; color: #f59e0b; }
        .badge-purple { background: #8b5cf620; color: #8b5cf6; }
        
        .food-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.8rem; margin-top: 0.5rem; }
        .food-card {
            background: var(--bg-card);
            border-radius: 1rem;
            padding: 0.8rem;
            border: 2px solid var(--border-light);
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        .food-card:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .food-card.selected { border-color: var(--accent); background: var(--accent-soft); box-shadow: 0 0 0 3px var(--accent); }
        .food-card .food-emoji { font-size: 2.5rem; display: block; }
        .food-card .food-name { font-weight: 600; font-size: 0.85rem; }
        .food-card .food-price { color: var(--accent); font-weight: 700; }
        .food-card .food-cuisine { font-size: 0.65rem; color: var(--text-muted); background: var(--bg-card-alt); padding: 0.1rem 0.5rem; border-radius: 10px; display: inline-block; margin-top: 0.2rem; }
        .food-card .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 4px; }
        .food-card .status-dot.available { background: var(--success); }
        .food-card .status-dot.unavailable { background: var(--danger); }
        .food-card.unavailable { opacity: 0.5; cursor: not-allowed; }
        
        .option-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; max-height: 200px; overflow-y: auto; }
        .option-chip {
            background: var(--bg-card-alt);
            padding: 0.3rem 0.8rem;
            border-radius: 30px;
            font-size: 0.8rem;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s;
            user-select: none;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .option-chip:hover { transform: scale(1.05); border-color: var(--accent); }
        .option-chip.selected { border-color: var(--accent); background: var(--accent-soft); box-shadow: 0 0 0 2px var(--accent); }
        .option-chip .price-tag { font-size: 0.65rem; background: var(--badge-bg); padding: 0.1rem 0.4rem; border-radius: 10px; margin-left: 4px; }
        .option-chip .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 4px; }
        .option-chip .status-dot.available { background: var(--success); }
        .option-chip .status-dot.unavailable { background: var(--danger); }
        .option-chip.unavailable { opacity: 0.5; cursor: not-allowed; }
        
        .selection-feedback { margin-top: 0.5rem; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.85rem; background: var(--accent-soft); display: none; }
        .selection-feedback.show { display: block; }
        
        .booking-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 1rem; align-items: end; }
        .booking-section { margin-top: 1rem; padding: 1rem; background: var(--accent-soft); border-radius: 1rem; border: 2px dashed var(--accent); }
        .booking-section select, .booking-section input { padding: 0.4rem 0.8rem; border-radius: 20px; border: 1px solid var(--border-light); background: var(--bg-main); color: var(--text-main); width: 100%; }
        .booking-section .ticket-counter { display: inline-flex; align-items: center; gap: 0.5rem; background: var(--bg-card); padding: 0.2rem 0.8rem; border-radius: 30px; }
        .booking-section .ticket-counter button { background: none; border: none; cursor: pointer; font-size: 1.2rem; color: var(--accent); padding: 0 0.3rem; }
        .booking-section .btn-gold { background: var(--gold); color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 30px; cursor: pointer; font-weight: 600; width: 100%; transition: all 0.3s; }
        .booking-section .btn-gold:hover { opacity: 0.9; transform: scale(1.02); }
        
        .three-col { display: grid; grid-template-columns: 1fr 1.5fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
        
        .qr-scanner { background: var(--bg-card); border-radius: 1.2rem; padding: 1.5rem; border: 2px dashed var(--accent); text-align: center; }
        .qr-scanner .qr-placeholder { width: 200px; height: 200px; margin: 0 auto; background: var(--bg-card-alt); border-radius: 1rem; display: flex; align-items: center; justify-content: center; font-size: 4rem; border: 2px solid var(--border-light); }
        .qr-scanner .qr-input { display: flex; gap: 0.5rem; margin-top: 1rem; }
        .qr-scanner .qr-input input { flex: 1; padding: 0.6rem; border-radius: 20px; border: 1px solid var(--border-light); background: var(--bg-main); color: var(--text-main); }
        .qr-scanner .qr-input button { background: var(--accent); color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 20px; cursor: pointer; }
        
        .map-container { height: 300px; border-radius: 1rem; overflow: hidden; border: 1px solid var(--border-light); }
        .map-container iframe { width: 100%; height: 100%; border: none; }
        
        .chat-feedback-row { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
        .chat-box { background: var(--bg-card); border-radius: 1.2rem; padding: 1.2rem; border: 1px solid var(--border-light); box-shadow: var(--shadow); }
        .chat-messages { background: var(--chat-bot-bg); border-radius: 1rem; padding: 0.8rem; height: 120px; overflow-y: auto; margin-bottom: 0.7rem; font-size: 0.9rem; border: 1px solid var(--border-light); }
        .chat-messages .bot-msg { color: var(--accent); }
        .chat-messages .user-msg { color: var(--text-main); }
        .chat-input-row { display: flex; gap: 0.5rem; }
        .chat-input-row input { flex: 1; padding: 0.6rem 1rem; border-radius: 40px; border: 1px solid var(--border-light); background: var(--bg-main); color: var(--text-main); }
        .chat-input-row button { background: var(--accent); border: none; color: white; padding: 0.6rem 1.2rem; border-radius: 40px; font-weight: 500; cursor: pointer; }
        .feedback-area textarea { width: 100%; padding: 0.6rem; border-radius: 0.8rem; border: 1px solid var(--border-light); background: var(--bg-main); color: var(--text-main); resize: vertical; margin-top: 0.4rem; }
        .feedback-area button { margin-top: 0.5rem; background: var(--accent); border: none; color: white; padding: 0.4rem 1.2rem; border-radius: 40px; cursor: pointer; }
        
        .upcoming-grid { display: flex; flex-direction: column; gap: 0.4rem; max-height: 200px; overflow-y: auto; }
        .upcoming-item { display: flex; justify-content: space-between; background: var(--bg-card-alt); padding: 0.5rem 0.8rem; border-radius: 40px; font-size: 0.85rem; border: 1px solid var(--border-light); cursor: pointer; }
        .upcoming-item:hover { background: var(--accent-soft); }
        
        .event-list { max-height: 400px; overflow-y: auto; }
        .event-item { display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 0; border-bottom: 1px solid var(--border-light); flex-wrap: wrap; gap: 0.5rem; }
        .event-item:last-child { border: none; }
        .event-name { font-weight: 500; }
        .event-date { font-size: 0.8rem; color: var(--text-muted); }
        .event-actions { display: flex; gap: 0.5rem; }
        .event-actions button { background: none; border: none; cursor: pointer; padding: 0.2rem 0.5rem; border-radius: 20px; font-size: 0.8rem; }
        .event-actions .edit-btn { color: var(--accent); }
        .event-actions .delete-btn { color: var(--danger); }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; }
        .modal.active { display: flex; }
        .modal-content { background: var(--bg-card); padding: 2rem; border-radius: 1.5rem; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto; border: 1px solid var(--border-light); }
        .modal-content h2 { margin-bottom: 1.5rem; }
        .modal-content input, .modal-content select, .modal-content textarea { width: 100%; padding: 0.6rem 1rem; margin-bottom: 1rem; border: 1px solid var(--border-light); border-radius: 0.8rem; background: var(--bg-main); color: var(--text-main); }
        .modal-actions { display: flex; gap: 1rem; margin-top: 1rem; }
        .modal-actions button { flex: 1; padding: 0.6rem; border: none; border-radius: 0.8rem; font-weight: 600; cursor: pointer; }
        .btn-primary { background: var(--accent); color: white; }
        .btn-secondary { background: var(--bg-card-alt); color: var(--text-main); border: 1px solid var(--border-light); }
        .btn-danger { background: var(--danger); color: white; }
        .btn-gold { background: var(--gold); color: white; }
        
        .toast { position: fixed; bottom: 20px; right: 20px; padding: 1rem 1.5rem; border-radius: 1rem; background: var(--bg-card); border: 1px solid var(--border-light); box-shadow: var(--shadow); z-index: 2000; max-width: 450px; animation: slideIn 0.3s ease; border-left: 4px solid var(--success); }
        .toast.error { border-left-color: var(--danger); }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        
        .booking-item { padding: 0.6rem; border-bottom: 1px solid var(--border-light); font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center; }
        .email-status { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; margin-left: 8px; }
        .email-status.sent { background: #16a34a20; color: #16a34a; }
        
        .footer-credit { text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border-light); font-size: 0.8rem; color: var(--text-muted); }
        
        .checkin-list { max-height: 150px; overflow-y: auto; }
        .checkin-item { padding: 0.3rem 0; border-bottom: 1px solid var(--border-light); font-size: 0.85rem; display: flex; justify-content: space-between; }
        
        @media (max-width: 900px) {
            .dashboard-grid { grid-template-columns: 1fr 1fr; }
            .analytics-grid { grid-template-columns: 1fr 1fr; }
            .two-col { grid-template-columns: 1fr; }
            .three-col { grid-template-columns: 1fr; }
            .chat-feedback-row { grid-template-columns: 1fr; }
            .booking-grid { grid-template-columns: 1fr 1fr; }
        }
        @media (max-width: 500px) {
            .dashboard-grid { grid-template-columns: 1fr; }
            .analytics-grid { grid-template-columns: 1fr; }
            .navbar { flex-direction: column; align-items: stretch; }
            .navbar .nav-actions { justify-content: center; }
            .booking-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<!-- ===== LOGIN PAGE ===== -->
<div id="loginPage" class="login-container">
    <div class="login-box">
        <h2><i class="fas fa-calendar-check" style="color:var(--accent);"></i> EventVault</h2>
        <p class="subtitle" id="loginSubtitle">Sign in to manage your events</p>
        <input type="text" id="loginName" placeholder="Full Name" style="display:none;">
        <input type="text" id="loginUser" placeholder="Username">
        <input type="email" id="loginEmail" placeholder="Email Address">
        <input type="password" id="loginPass" placeholder="Password">
        <button id="loginBtn" onclick="handleLogin()"><i class="fas fa-sign-in-alt"></i> Login</button>
        <div id="loginError" class="error"></div>
        <div id="loginSuccess" class="success"></div>
        <p style="margin-top:1rem;text-align:center;font-size:0.9rem;">
            <span class="toggle-link" onclick="toggleAuthMode()" id="authToggle">Create an account</span>
        </p>
        <div class="demo-cred">
            <strong>Quick Access:</strong><br>
            Username: <strong>admin</strong> · Password: <strong>admin123</strong>
        </div>
    </div>
</div>

<!-- ===== MAIN APP ===== -->
<div id="mainApp" class="app-wrapper hidden">
    <nav class="navbar">
        <div class="logo"><h1><i class="fas fa-calendar-check"></i> EventVault</h1></div>
        <div class="nav-actions">
            <span class="user-badge"><i class="fas fa-user"></i> <span id="userDisplay">User</span></span>
            <span class="user-badge"><i class="fas fa-envelope"></i> <span id="userEmailDisplay">email</span></span>
            <button onclick="toggleTheme()"><i class="fas fa-moon" id="themeIcon"></i></button>
            <button onclick="showAddEvent()"><i class="fas fa-plus"></i> Add Event</button>
            <button onclick="showMyBookings()"><i class="fas fa-ticket-alt"></i> Bookings</button>
            <button onclick="handleLogout()"><i class="fas fa-sign-out-alt"></i> Logout</button>
        </div>
    </nav>

    <!-- Real-time Analytics Dashboard -->
    <div class="analytics-grid">
        <div class="analytics-card">
            <div class="label"><i class="fas fa-eye"></i> Page Views</div>
            <div class="value" id="pageViews">0</div>
            <div class="change">+12% today</div>
        </div>
        <div class="analytics-card">
            <div class="label"><i class="fas fa-shopping-cart"></i> Bookings Today</div>
            <div class="value" id="bookingsToday">0</div>
            <div class="change">+8% from yesterday</div>
        </div>
        <div class="analytics-card">
            <div class="label"><i class="fas fa-check-circle"></i> Check-ins Today</div>
            <div class="value" id="checkInsToday">0</div>
            <div class="change">+15% from yesterday</div>
        </div>
        <div class="analytics-card">
            <div class="label"><i class="fas fa-dollar-sign"></i> Revenue Today</div>
            <div class="value" id="revenueToday">$0</div>
            <div class="change">+10% from yesterday</div>
        </div>
    </div>

    <div class="two-col">
        <div class="card">
            <div class="card-header"><h3><i class="fas fa-chart-pie" style="color:var(--accent);"></i> Event Categories</h3></div>
            <div class="chart-container"><canvas id="eventChart"></canvas></div>
        </div>
        <div class="card">
            <div class="card-header"><h3><i class="fas fa-clock"></i> Upcoming Events</h3><span class="badge" id="upcomingBadge">0</span></div>
            <div class="upcoming-grid" id="upcomingEvents"></div>
        </div>
    </div>

    <!-- QR Code Scanner & Check-in -->
    <div class="two-col">
        <div class="qr-scanner">
            <h3><i class="fas fa-qrcode" style="color:var(--accent);"></i> QR Code Scanner</h3>
            <p style="color:var(--text-muted);font-size:0.9rem;margin-bottom:1rem;">Scan or enter booking ID for check-in</p>
            <div class="qr-placeholder">
                <i class="fas fa-qrcode" style="font-size:4rem;color:var(--accent);"></i>
            </div>
            <div class="qr-input">
                <input type="text" id="qrInput" placeholder="Enter Booking ID (e.g., 1001)">
                <button onclick="scanQRCode()"><i class="fas fa-check"></i> Check-in</button>
            </div>
            <div id="qrResult" style="margin-top:0.5rem;font-weight:600;"></div>
        </div>
        <div class="card">
            <div class="card-header">
                <h3><i class="fas fa-user-check"></i> Recent Check-ins</h3>
                <span class="badge badge-success">Live</span>
            </div>
            <div class="checkin-list" id="checkinList">
                <p style="color:var(--text-muted);font-size:0.85rem;">No check-ins yet</p>
            </div>
        </div>
    </div>

    <!-- Interactive Food Cards -->
    <div class="card">
        <div class="card-header">
            <h3><i class="fas fa-utensils" style="color:var(--accent);"></i> 🍽️ Food Options <span class="badge badge-info">10 options</span></h3>
            <span class="badge badge-gold">⭐ Click to select</span>
        </div>
        <div class="food-grid" id="foodList"></div>
        <div id="foodFeedback" class="selection-feedback">
            <i class="fas fa-check-circle" style="color:var(--success);"></i>
            <span id="foodSelectionText">No food selected</span>
        </div>
    </div>

    <!-- Venues & Payment & Map -->
    <div class="three-col">
        <div class="card">
            <div class="card-header"><h3><i class="fas fa-map-pin"></i> Venues <span class="badge badge-info">9</span></h3></div>
            <div class="option-grid" id="venuesList"></div>
            <div id="venueFeedback" class="selection-feedback"><i class="fas fa-check-circle" style="color:var(--success);"></i> <span id="venueSelectionText">No venue selected</span></div>
        </div>
        <div class="card">
            <div class="card-header"><h3><i class="fas fa-credit-card"></i> Payment <span class="badge badge-info">7</span></h3></div>
            <div class="option-grid" id="paymentsList"></div>
            <div id="paymentFeedback" class="selection-feedback"><i class="fas fa-check-circle" style="color:var(--success);"></i> <span id="paymentSelectionText">No payment selected</span></div>
        </div>
        <div class="card">
            <div class="card-header"><h3><i class="fas fa-map-marked-alt"></i> Venue Location</h3></div>
            <div class="map-container" id="mapContainer">
                <iframe id="mapFrame" src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=40.7128,-74.0060" allowfullscreen></iframe>
            </div>
            <div style="margin-top:0.5rem;font-size:0.85rem;color:var(--text-muted);">
                <i class="fas fa-location-dot" style="color:var(--accent);"></i> <span id="venueAddress">Grand Hall, 123 Main St, NYC</span>
                <button onclick="openGoogleMaps()" style="float:right;background:var(--accent);color:white;border:none;padding:0.2rem 0.8rem;border-radius:20px;cursor:pointer;">Get Directions</button>
            </div>
        </div>
    </div>

    <!-- Booking Section -->
    <div class="card">
        <div class="card-header">
            <h3><i class="fas fa-ticket-alt" style="color:var(--gold);"></i> Book & Get QR Code</h3>
            <span class="badge badge-gold">📱 QR Code for Entrance</span>
        </div>
        <div class="booking-section">
            <div class="booking-grid">
                <div>
                    <select id="bookingEvent" style="width:100%;"></select>
                </div>
                <div>
                    <div class="ticket-counter">
                        <button onclick="changeTickets(-1)">−</button>
                        <span id="ticketCount" style="min-width:30px;text-align:center;">1</span>
                        <button onclick="changeTickets(1)">+</button>
                    </div>
                </div>
                <div>
                    <input type="email" id="bookingEmail" placeholder="Your Email">
                </div>
                <div>
                    <button class="btn-gold" onclick="bookEvent()" style="padding:0.6rem;"><i class="fas fa-envelope"></i> Book & Get QR</button>
                </div>
            </div>
            <div id="bookingStatus" style="margin-top:0.5rem;font-size:0.85rem;"></div>
            <div id="emailStatus" style="margin-top:0.3rem;font-size:0.8rem;"></div>
            <div id="qrCodeDisplay" style="margin-top:1rem;text-align:center;display:none;">
                <p><strong>Your QR Code for Entrance</strong></p>
                <img id="qrCodeImg" style="max-width:200px;border:2px solid var(--accent);border-radius:12px;padding:10px;background:white;">
                <p style="font-size:0.8rem;color:var(--text-muted);margin-top:0.5rem;">Show this QR code at the entrance for check-in</p>
            </div>
        </div>
    </div>

    <div class="chat-feedback-row">
        <div class="chat-box">
            <div class="card-header"><h3><i class="fas fa-robot" style="color:var(--accent);"></i> AI Assistant</h3><span class="badge badge-success">online</span></div>
            <div class="chat-messages" id="chatMessages"><div class="bot-msg">🤖 Hello! Ask me about events, venues, QR codes, or check-in!</div></div>
            <div class="chat-input-row">
                <input type="text" id="chatInput" placeholder="Ask me anything...">
                <button onclick="sendChat()"><i class="fas fa-paper-plane"></i> Send</button>
            </div>
        </div>
        <div class="card feedback-area">
            <div class="card-header"><h3><i class="fas fa-comment-dots"></i> Live Feedback</h3><span class="badge badge-success">real-time</span></div>
            <textarea id="feedbackInput" rows="2" placeholder="Share your experience..."></textarea>
            <button onclick="submitFeedback()"><i class="fas fa-pen"></i> Submit</button>
            <div id="feedbackList" style="margin-top:1rem;max-height:150px;overflow-y:auto;"></div>
            <div id="feedbackStatus" style="margin-top:0.5rem;font-size:0.8rem;color:var(--text-muted);"></div>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <h3><i class="fas fa-list"></i> All Events <span class="badge badge-info">20 events</span></h3>
            <select id="filterCategory" onchange="filterEvents(this.value)" style="padding:0.3rem 0.8rem;border-radius:20px;border:1px solid var(--border-light);background:var(--bg-main);color:var(--text-main);">
                <option value="all">All Categories</option>
                <option value="Conference">Conference</option>
                <option value="Workshop">Workshop</option>
                <option value="Social">Social</option>
                <option value="Networking">Networking</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Wellness">Wellness</option>
            </select>
        </div>
        <div class="event-list" id="eventList"></div>
    </div>

    <div class="footer-credit">EventVault · QR Code Check-in · Google Maps · Real-time Analytics</div>
</div>

<!-- ===== BOOKINGS MODAL ===== -->
<div id="bookingsModal" class="modal">
    <div class="modal-content">
        <h2><i class="fas fa-ticket-alt" style="color:var(--gold);"></i> My Bookings</h2>
        <div id="bookingsList" style="max-height:400px;overflow-y:auto;"></div>
        <div class="modal-actions"><button class="btn-secondary" onclick="closeBookingsModal()"><i class="fas fa-times"></i> Close</button></div>
    </div>
</div>

<!-- ===== ADD/EDIT EVENT MODAL ===== -->
<div id="eventModal" class="modal">
    <div class="modal-content">
        <h2 id="modalTitle"><i class="fas fa-plus-circle"></i> Add New Event</h2>
        <input type="hidden" id="editEventId">
        <input type="text" id="eventName" placeholder="Event Name">
        <input type="date" id="eventDate">
        <input type="time" id="eventTime">
        <select id="eventCategory">
            <option value="Conference">Conference</option>
            <option value="Workshop">Workshop</option>
            <option value="Social">Social</option>
            <option value="Networking">Networking</option>
            <option value="Entertainment">Entertainment</option>
            <option value="Wellness">Wellness</option>
        </select>
        <select id="eventVenue">
            <option value="Grand Hall">Grand Hall</option>
            <option value="Garden Plaza">Garden Plaza</option>
            <option value="The Loft">The Loft</option>
            <option value="Bayview">Bayview</option>
            <option value="City Center">City Center</option>
            <option value="Rooftop Lounge">Rooftop Lounge</option>
            <option value="Beachfront Resort">Beachfront Resort</option>
            <option value="Art Gallery">Art Gallery</option>
            <option value="Conference Room A">Conference Room A</option>
        </select>
        <input type="number" id="eventPrice" placeholder="Price ($)" value="0">
        <input type="number" id="eventAttendees" placeholder="Attendees" value="0">
        <input type="number" id="eventCapacity" placeholder="Capacity" value="500">
        <input type="text" id="eventOrganizer" placeholder="Organizer">
        <input type="text" id="eventLat" placeholder="Latitude" value="40.7128">
        <input type="text" id="eventLng" placeholder="Longitude" value="-74.0060">
        <select id="eventStatus">
            <option value="upcoming">Upcoming</option>
            <option value="past">Past</option>
        </select>
        <textarea id="eventDescription" placeholder="Event Description"></textarea>
        <div class="modal-actions">
            <button class="btn-primary" onclick="saveEvent()"><i class="fas fa-save"></i> Save</button>
            <button class="btn-secondary" onclick="closeModal()"><i class="fas fa-times"></i> Cancel</button>
        </div>
    </div>
</div>

<script>
    let currentUser = null, currentUserEmail = null, allEvents = [], currentFilter = 'all';
    let eventChart = null, selectedVenue = null, selectedFood = null, selectedPayment = null;
    let feedbackInterval = null, analyticsInterval = null, ticketCount = 1, bookings = [], isRegisterMode = false;
    let checkIns = [];

    // ===== AUTH =====
    function toggleAuthMode() {
        isRegisterMode = !isRegisterMode;
        const btn = document.getElementById('loginBtn');
        const toggle = document.getElementById('authToggle');
        const subtitle = document.getElementById('loginSubtitle');
        const nameField = document.getElementById('loginName');
        const emailField = document.getElementById('loginEmail');
        if (isRegisterMode) {
            btn.innerHTML = '<i class="fas fa-user-plus"></i> Register';
            toggle.textContent = 'Already have an account? Login';
            subtitle.textContent = 'Create your free account';
            nameField.style.display = 'block';
            emailField.placeholder = 'Email Address *';
        } else {
            btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
            toggle.textContent = 'Create an account';
            subtitle.textContent = 'Sign in to manage your events';
            nameField.style.display = 'none';
            emailField.placeholder = 'Email Address';
        }
    }

    async function handleLogin() {
        const username = document.getElementById('loginUser').value.trim();
        const password = document.getElementById('loginPass').value;
        const email = document.getElementById('loginEmail').value.trim();
        const name = document.getElementById('loginName').value.trim();
        const errorDiv = document.getElementById('loginError');
        const successDiv = document.getElementById('loginSuccess');
        errorDiv.textContent = ''; successDiv.textContent = '';
        if (!username || !password) { errorDiv.textContent = 'Please fill in all required fields'; return; }
        if (isRegisterMode) {
            if (!email || !name) { errorDiv.textContent = 'Please fill in all fields'; return; }
            try {
                const response = await fetch('/api/register', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, email, name })
                });
                const data = await response.json();
                if (data.success) {
                    successDiv.textContent = '✅ Account created! Please login.';
                    toggleAuthMode();
                    document.getElementById('loginUser').value = username;
                    document.getElementById('loginEmail').value = email;
                    showToast('✅ Account created! Please login.', 'success');
                } else {
                    errorDiv.textContent = data.error || 'Registration failed';
                }
            } catch (error) { errorDiv.textContent = 'Connection error'; }
            return;
        }
        try {
            const response = await fetch('/api/login', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (data.success) {
                currentUser = data.user;
                currentUserEmail = data.email || email || 'user@example.com';
                document.getElementById('userDisplay').textContent = currentUser;
                document.getElementById('userEmailDisplay').textContent = currentUserEmail;
                document.getElementById('bookingEmail').value = currentUserEmail;
                document.getElementById('loginPage').classList.add('hidden');
                document.getElementById('mainApp').classList.remove('hidden');
                initializeApp();
                startFeedbackPolling();
                startAnalyticsPolling();
                loadBookings();
                loadCheckIns();
                showToast('👋 Welcome back, ' + currentUser + '!', 'success');
            } else {
                errorDiv.textContent = data.error || 'Login failed';
            }
        } catch (error) { errorDiv.textContent = 'Connection error'; }
    }

    function handleLogout() {
        fetch('/api/logout', { method: 'POST' }).then(() => {
            currentUser = null;
            document.getElementById('loginPage').classList.remove('hidden');
            document.getElementById('mainApp').classList.add('hidden');
            if (feedbackInterval) clearInterval(feedbackInterval);
            if (analyticsInterval) clearInterval(analyticsInterval);
            showToast('👋 Logged out', 'success');
        });
    }

    // ===== THEME =====
    function toggleTheme() {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        document.getElementById('themeIcon').className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
    if (localStorage.getItem('theme') === 'dark') { document.body.classList.add('dark'); document.getElementById('themeIcon').className = 'fas fa-sun'; }

    // ===== TICKETS =====
    function changeTickets(delta) { ticketCount = Math.max(1, ticketCount + delta); document.getElementById('ticketCount').textContent = ticketCount; }

    // ===== QR CODE SCANNER =====
    async function scanQRCode() {
        const input = document.getElementById('qrInput');
        const bookingId = input.value.trim();
        if (!bookingId) { showToast('Please enter a booking ID', 'error'); return; }
        
        try {
            const response = await fetch('/api/checkin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ booking_id: bookingId })
            });
            const data = await response.json();
            const resultDiv = document.getElementById('qrResult');
            if (data.success) {
                resultDiv.innerHTML = `<span style="color:var(--success);"><i class="fas fa-check-circle"></i> ✅ ${data.message}</span>`;
                showToast(`✅ ${data.message}`, 'success');
                loadCheckIns();
                loadAnalytics();
                input.value = '';
            } else {
                resultDiv.innerHTML = `<span style="color:var(--danger);"><i class="fas fa-times-circle"></i> ❌ ${data.message}</span>`;
                showToast(`❌ ${data.message}`, 'error');
            }
        } catch (error) {
            showToast('Error processing check-in', 'error');
        }
    }

    // ===== GOOGLE MAPS =====
    function updateMap(lat, lng, venueName, address) {
        const iframe = document.getElementById('mapFrame');
        iframe.src = `https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${lat},${lng}`;
        document.getElementById('venueAddress').textContent = `${venueName}, ${address}`;
    }

    function openGoogleMaps() {
        const lat = document.getElementById('mapFrame').src.match(/q=([^&]+)/);
        if (lat) {
            window.open(`https://www.google.com/maps/search/?api=1&query=${lat[1]}`, '_blank');
        }
    }

    // ===== BOOKING =====
    async function bookEvent() {
        const eventSelect = document.getElementById('bookingEvent');
        const eventId = parseInt(eventSelect.value);
        const event = allEvents.find(e => e.id === eventId);
        const email = document.getElementById('bookingEmail').value.trim();
        if (!event) { showToast('Please select an event', 'error'); return; }
        if (!email) { showToast('Please enter your email', 'error'); return; }
        if (!selectedVenue) { showToast('Please select a venue', 'error'); return; }
        if (!selectedFood) { showToast('Please select a food option', 'error'); return; }
        if (!selectedPayment) { showToast('Please select a payment method', 'error'); return; }
        const totalPrice = event.price * ticketCount;
        const bookingData = {
            event_id: event.id, event_name: event.name, event_date: event.date, event_time: event.time || 'TBD',
            venue: selectedVenue.name, food: selectedFood.name, payment: selectedPayment.name,
            tickets: ticketCount, total_price: totalPrice, attendees_name: currentUser || 'Guest', user_email: email
        };
        const statusDiv = document.getElementById('bookingStatus');
        statusDiv.innerHTML = '<span style="color:var(--warning);"><i class="fas fa-spinner fa-spin"></i> Processing booking & generating QR code...</span>';
        try {
            const response = await fetch('/api/book', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData)
            });
            const data = await response.json();
            if (data.success) {
                statusDiv.innerHTML = `<span style="color:var(--success);"><i class="fas fa-check-circle"></i> Booking #${data.booking_id} confirmed! QR code generated.</span>`;
                showToast(`🎫 Booking #${data.booking_id} confirmed!`, 'success');
                loadBookings();
                loadAnalytics();
                document.getElementById('emailStatus').innerHTML = data.email_sent ? 
                    '<span class="email-status sent">✅ Email sent to ' + email + '</span>' : 
                    '<span class="email-status sent">✅ QR code ready!</span>';
                
                // Show QR Code
                if (data.qr_code) {
                    document.getElementById('qrCodeDisplay').style.display = 'block';
                    document.getElementById('qrCodeImg').src = 'data:image/png;base64,' + data.qr_code;
                }
            } else {
                statusDiv.innerHTML = `<span style="color:var(--danger);">❌ Booking failed</span>`;
                showToast('Booking failed', 'error');
            }
        } catch (error) {
            statusDiv.innerHTML = `<span style="color:var(--danger);">❌ Error</span>`;
            showToast('Booking error', 'error');
        }
    }

    async function loadBookings() {
        try { const response = await fetch('/api/bookings'); bookings = await response.json(); } catch (error) {}
    }

    async function loadCheckIns() {
        try {
            const response = await fetch('/api/checkins');
            checkIns = await response.json();
            const container = document.getElementById('checkinList');
            if (checkIns.length === 0) {
                container.innerHTML = '<p style="color:var(--text-muted);font-size:0.85rem;">No check-ins yet</p>';
                return;
            }
            container.innerHTML = checkIns.slice(-10).reverse().map(c => `
                <div class="checkin-item">
                    <span><strong>${c.booking_id}</strong> - ${c.event_name}</span>
                    <span style="color:var(--success);">${c.time}</span>
                </div>
            `).join('');
        } catch (error) {}
    }

    function showMyBookings() {
        const container = document.getElementById('bookingsList');
        if (bookings.length === 0) {
            container.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No bookings yet.</p>';
        } else {
            container.innerHTML = bookings.map(b => `
                <div class="booking-item">
                    <div><strong>${b.event_name}</strong><div style="font-size:0.75rem;color:var(--text-muted);">${b.event_date} · ${b.venue}</div></div>
                    <div>
                        <span class="badge badge-success">${b.tickets} tickets</span>
                        <span style="font-weight:600;color:var(--accent);">$${b.total_price}</span>
                        <span class="email-status sent">✅ QR Code</span>
                    </div>
                </div>
            `).join('');
        }
        document.getElementById('bookingsModal').classList.add('active');
    }
    function closeBookingsModal() { document.getElementById('bookingsModal').classList.remove('active'); }

    // ===== ANALYTICS =====
    function startAnalyticsPolling() {
        if (analyticsInterval) clearInterval(analyticsInterval);
        loadAnalytics();
        analyticsInterval = setInterval(loadAnalytics, 5000);
    }

    async function loadAnalytics() {
        try {
            const response = await fetch('/api/analytics');
            const data = await response.json();
            document.getElementById('pageViews').textContent = data.page_views || 0;
            document.getElementById('bookingsToday').textContent = data.bookings_today || 0;
            document.getElementById('checkInsToday').textContent = data.check_ins_today || 0;
            document.getElementById('revenueToday').textContent = '$' + (data.revenue_today || 0);
            document.getElementById('upcomingBadge').textContent = data.upcoming_events || 0;
        } catch (error) {}
    }

    // ===== FEEDBACK =====
    function startFeedbackPolling() {
        if (feedbackInterval) clearInterval(feedbackInterval);
        loadFeedback();
        feedbackInterval = setInterval(loadFeedback, 3000);
    }

    async function loadFeedback() {
        try {
            const response = await fetch('/api/feedback');
            const feedbacks = await response.json();
            const container = document.getElementById('feedbackList');
            if (feedbacks.length === 0) {
                container.innerHTML = '<p style="color:var(--text-muted);font-size:0.85rem;">No feedback yet.</p>';
                return;
            }
            container.innerHTML = feedbacks.slice(-5).reverse().map(f => `
                <div style="padding:0.4rem 0;border-bottom:1px solid var(--border-light);font-size:0.85rem;">
                    <strong style="color:var(--accent);">${f.user || 'Anonymous'}</strong>: ${f.feedback}
                    <span style="font-size:0.7rem;color:var(--text-muted);float:right;">${new Date(f.timestamp).toLocaleTimeString()}</span>
                </div>
            `).join('');
        } catch (error) {}
    }

    async function submitFeedback() {
        const input = document.getElementById('feedbackInput');
        const text = input.value.trim();
        const status = document.getElementById('feedbackStatus');
        if (!text) { status.textContent = '⚠️ Please write feedback.'; status.style.color = '#dc2626'; return; }
        try {
            const response = await fetch('/api/feedback', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback: text, rating: 5, user: currentUser || 'anonymous' })
            });
            const data = await response.json();
            status.textContent = '✅ Feedback submitted! (ID: ' + data.id + ')';
            status.style.color = '#16a34a';
            input.value = '';
            loadFeedback();
            setTimeout(() => { status.textContent = ''; }, 4000);
        } catch (error) {
            status.textContent = '⚠️ Error submitting feedback.';
            status.style.color = '#dc2626';
        }
    }

    // ===== SELECTION FUNCTIONS =====
    function selectVenue(id, name, available, lat, lng, address) {
        if (!available) { showToast('Venue unavailable', 'error'); return; }
        selectedVenue = { id, name };
        document.querySelectorAll('#venuesList .option-chip').forEach(el => el.classList.remove('selected'));
        const el = document.querySelector(`#venuesList .option-chip[data-id="${id}"]`);
        if (el) el.classList.add('selected');
        document.getElementById('venueSelectionText').textContent = 'Selected: ' + name;
        document.getElementById('venueFeedback').classList.add('show');
        showToast('✅ Venue "' + name + '" selected!', 'success');
        updateMap(lat, lng, name, address);
        fetch('/api/select/venue', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ venue: name }) });
    }

    function selectFood(id, name, available) {
        if (!available) { showToast('Food unavailable', 'error'); return; }
        selectedFood = { id, name };
        document.querySelectorAll('.food-card').forEach(el => el.classList.remove('selected'));
        const el = document.querySelector(`.food-card[data-id="${id}"]`);
        if (el) el.classList.add('selected');
        document.getElementById('foodSelectionText').textContent = 'Selected: ' + name;
        document.getElementById('foodFeedback').classList.add('show');
        showToast('🍽️ "' + name + '" selected!', 'success');
        fetch('/api/select/food', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ food: name }) });
    }

    function selectPayment(id, name, available) {
        if (!available) { showToast('Payment unavailable', 'error'); return; }
        selectedPayment = { id, name };
        document.querySelectorAll('#paymentsList .option-chip').forEach(el => el.classList.remove('selected'));
        const el = document.querySelector(`#paymentsList .option-chip[data-id="${id}"]`);
        if (el) el.classList.add('selected');
        document.getElementById('paymentSelectionText').textContent = 'Selected: ' + name;
        document.getElementById('paymentFeedback').classList.add('show');
        showToast('💳 "' + name + '" selected!', 'success');
        fetch('/api/select/payment', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ payment: name }) });
    }

    function showToast(message, type = 'success') {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();
        const toast = document.createElement('div');
        toast.className = `toast ${type === 'error' ? 'error' : ''}`;
        toast.innerHTML = message;
        document.body.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; setTimeout(() => toast.remove(), 300); }, 4000);
    }

    // ===== INITIALIZE =====
    async function initializeApp() {
        await loadDashboardData();
        await loadOptions();
        await loadAllEvents();
        await loadFeedback();
        await loadBookings();
        await loadCheckIns();
        await loadAnalytics();
        populateBookingEvents();
    }

    function populateBookingEvents() {
        const select = document.getElementById('bookingEvent');
        const upcoming = allEvents.filter(e => e.status === 'upcoming');
        select.innerHTML = upcoming.map(e => `<option value="${e.id}">${e.emoji || '📅'} ${e.name} - $${e.price}</option>`).join('');
        if (upcoming.length === 0) select.innerHTML = '<option value="">No upcoming events</option>';
    }

    async function loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard');
            const data = await response.json();
            document.getElementById('totalEvents').textContent = data.total_events || 0;
            document.getElementById('upcomingCount').textContent = data.upcoming_events || 0;
            document.getElementById('pastCount').textContent = (data.total_events - data.upcoming_events) || 0;
            document.getElementById('totalAttendees').textContent = data.total_attendees || 0;
            if (data.categories && eventChart) {
                const labels = Object.keys(data.categories);
                const values = Object.values(data.categories);
                eventChart.data.labels = labels;
                eventChart.data.datasets[0].data = values;
                eventChart.update();
            }
        } catch (error) {}
    }

    async function loadAllEvents() {
        try {
            const response = await fetch('/api/events');
            allEvents = await response.json();
            renderEvents(currentFilter);
            renderUpcoming();
            populateBookingEvents();
        } catch (error) {}
    }

    function renderEvents(filter) {
        let events = allEvents;
        if (filter === 'upcoming') events = events.filter(e => e.status === 'upcoming');
        else if (filter === 'past') events = events.filter(e => e.status === 'past');
        else if (filter !== 'all' && filter !== '') events = events.filter(e => e.category === filter);
        const container = document.getElementById('eventList');
        if (events.length === 0) { container.innerHTML = '<p style="text-align:center;padding:2rem;color:var(--text-muted);">No events found</p>'; return; }
        container.innerHTML = events.map(e => `
            <div class="event-item">
                <div>
                    <div class="event-name">${e.emoji || '📅'} ${e.name}</div>
                    <div class="event-date">${e.date} · ${e.time || 'TBD'} · ${e.venue}</div>
                    <div>
                        <span class="badge badge-${e.status === 'upcoming' ? 'success' : 'danger'}">${e.status}</span>
                        <span class="badge">${e.category}</span>
                        <span class="badge">$${e.price || 0}</span>
                        <span class="badge badge-info"><i class="fas fa-users"></i> ${e.capacity || 'N/A'}</span>
                    </div>
                </div>
                <div class="event-actions">
                    <button class="edit-btn" onclick="editEvent(${e.id})"><i class="fas fa-edit"></i></button>
                    <button class="delete-btn" onclick="deleteEvent(${e.id})"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `).join('');
    }

    function renderUpcoming() {
        const upcoming = allEvents.filter(e => e.status === 'upcoming').slice(0, 5);
        const container = document.getElementById('upcomingEvents');
        if (upcoming.length === 0) { container.innerHTML = '<p style="text-align:center;padding:1rem;color:var(--text-muted);">No upcoming events</p>'; return; }
        container.innerHTML = upcoming.map(e => `
            <div class="upcoming-item" onclick="viewEvent(${e.id})">
                <span>${e.emoji || '📅'} ${e.name}</span>
                <span>${e.date}</span>
            </div>
        `).join('');
    }

    function filterEvents(filter) { currentFilter = filter; renderEvents(filter); }

    async function loadOptions() {
        try {
            const vRes = await fetch('/api/venues');
            const venues = await vRes.json();
            document.getElementById('venuesList').innerHTML = venues.map(v => `
                <span class="option-chip ${!v.available ? 'unavailable' : ''}" data-id="${v.id}" 
                      onclick="selectVenue(${v.id}, '${v.name}', ${v.available}, ${v.lat}, ${v.lng}, '${v.address}')">
                    ${v.emoji || '📍'} ${v.name}
                    <span class="status-dot ${v.available ? 'available' : 'unavailable'}"></span>
                    <span class="price-tag">$${v.price}</span>
                    <span class="rating-star">⭐ ${v.rating || 4.5}</span>
                </span>
            `).join('');
            
            const fRes = await fetch('/api/food');
            const food = await fRes.json();
            document.getElementById('foodList').innerHTML = food.map(f => `
                <div class="food-card ${!f.available ? 'unavailable' : ''}" data-id="${f.id}"
                     onclick="selectFood(${f.id}, '${f.name}', ${f.available})"
                     style="border-color: ${f.color || '#ddd'};">
                    <span class="food-emoji">${f.emoji || '🍽️'}</span>
                    <div class="food-name">${f.name}</div>
                    <div class="food-price">$${f.price}</div>
                    <div class="food-rating">⭐ ${f.rating || 4.5}</div>
                    <span class="food-cuisine">${f.cuisine || 'Various'}</span>
                    <span class="status-dot ${f.available ? 'available' : 'unavailable'}"></span>
                </div>
            `).join('');
            
            const pRes = await fetch('/api/payments');
            const payments = await pRes.json();
            document.getElementById('paymentsList').innerHTML = payments.map(p => `
                <span class="option-chip ${!p.available ? 'unavailable' : ''}" data-id="${p.id}"
                      onclick="selectPayment(${p.id}, '${p.name}', ${p.available})">
                    <i class="fab ${p.icon || 'fa-credit-card'}"></i> ${p.name}
                    <span class="status-dot ${p.available ? 'available' : 'unavailable'}"></span>
                    <span class="price-tag">${p.fee > 0 ? p.fee + '%' : '0%'}</span>
                </span>
            `).join('');
        } catch (error) {}
    }

    const ctx = document.getElementById('eventChart').getContext('2d');
    eventChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Conference', 'Workshop', 'Social', 'Networking', 'Entertainment', 'Wellness'],
            datasets: [{ data: [25, 15, 20, 15, 20, 5], backgroundColor: ['#4f46e5', '#818cf8', '#a5b4fc', '#c7d2fe', '#6366f1', '#34d399'], borderWidth: 0 }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, cutout: '60%' }
    });

    // ===== CHATBOT =====
    async function sendChat() {
        const input = document.getElementById('chatInput');
        const msg = input.value.trim();
        if (!msg) return;
        const messages = document.getElementById('chatMessages');
        const userDiv = document.createElement('div');
        userDiv.className = 'user-msg';
        userDiv.textContent = '🧑 ' + msg;
        messages.appendChild(userDiv);
        input.value = '';
        try {
            const response = await fetch('/api/chat', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await response.json();
            const botDiv = document.createElement('div');
            botDiv.className = 'bot-msg';
            botDiv.textContent = '🤖 ' + data.reply;
            messages.appendChild(botDiv);
            messages.scrollTop = messages.scrollHeight;
        } catch (error) {
            const fallback = getLocalReply(msg);
            const botDiv = document.createElement('div');
            botDiv.className = 'bot-msg';
            botDiv.textContent = '🤖 ' + fallback;
            messages.appendChild(botDiv);
        }
    }

    function getLocalReply(msg) {
        const lower = msg.toLowerCase();
        if (lower.includes('qr') || lower.includes('scan')) return '📱 To check-in, enter your Booking ID in the QR scanner or scan the QR code from your email at the entrance!';
        if (lower.includes('map') || lower.includes('location')) return '📍 Select a venue to see its location on Google Maps. Click "Get Directions" for navigation!';
        if (lower.includes('check')) return '✅ Check-in is done by scanning the QR code at the entrance. Each booking gets a unique QR code!';
        if (lower.includes('analytics')) return '📊 The dashboard shows real-time analytics: page views, bookings today, check-ins, and revenue!';
        if (lower.includes('venue')) return '🎯 We have 9 venues with Google Maps integration! Select one to see its location.';
        if (lower.includes('food')) return '🍽️ We offer 10 food options with pictures! Italian, Seafood, French, Indian, and more!';
        if (lower.includes('event')) return '📅 We have 20 events! Book now to get your QR code for entrance!';
        return '🤔 I can help with QR codes, check-in, Google Maps, events, venues, food, and analytics!';
    }

    // ===== EVENT CRUD =====
    function showAddEvent() {
        document.getElementById('modalTitle').innerHTML = '<i class="fas fa-plus-circle"></i> Add New Event';
        document.getElementById('editEventId').value = '';
        document.getElementById('eventName').value = '';
        document.getElementById('eventDate').value = '';
        document.getElementById('eventTime').value = '';
        document.getElementById('eventCategory').value = 'Conference';
        document.getElementById('eventVenue').value = 'Grand Hall';
        document.getElementById('eventPrice').value = 0;
        document.getElementById('eventAttendees').value = 0;
        document.getElementById('eventCapacity').value = 500;
        document.getElementById('eventOrganizer').value = '';
        document.getElementById('eventLat').value = '40.7128';
        document.getElementById('eventLng').value = '-74.0060';
        document.getElementById('eventStatus').value = 'upcoming';
        document.getElementById('eventDescription').value = '';
        document.getElementById('eventModal').classList.add('active');
    }

    function editEvent(id) {
        const event = allEvents.find(e => e.id === id);
        if (!event) return;
        document.getElementById('modalTitle').innerHTML = '<i class="fas fa-edit"></i> Edit Event';
        document.getElementById('editEventId').value = id;
        document.getElementById('eventName').value = event.name;
        document.getElementById('eventDate').value = event.date;
        document.getElementById('eventTime').value = event.time || '12:00';
        document.getElementById('eventCategory').value = event.category;
        document.getElementById('eventVenue').value = event.venue;
        document.getElementById('eventPrice').value = event.price || 0;
        document.getElementById('eventAttendees').value = event.attendees || 0;
        document.getElementById('eventCapacity').value = event.capacity || 500;
        document.getElementById('eventOrganizer').value = event.organizer || '';
        document.getElementById('eventLat').value = event.lat || '40.7128';
        document.getElementById('eventLng').value = event.lng || '-74.0060';
        document.getElementById('eventStatus').value = event.status;
        document.getElementById('eventDescription').value = event.description || '';
        document.getElementById('eventModal').classList.add('active');
    }

    function closeModal() { document.getElementById('eventModal').classList.remove('active'); }

    async function saveEvent() {
        const id = document.getElementById('editEventId').value;
        const eventData = {
            name: document.getElementById('eventName').value,
            date: document.getElementById('eventDate').value,
            time: document.getElementById('eventTime').value,
            category: document.getElementById('eventCategory').value,
            venue: document.getElementById('eventVenue').value,
            price: parseInt(document.getElementById('eventPrice').value) || 0,
            attendees: parseInt(document.getElementById('eventAttendees').value) || 0,
            capacity: parseInt(document.getElementById('eventCapacity').value) || 500,
            organizer: document.getElementById('eventOrganizer').value,
            lat: parseFloat(document.getElementById('eventLat').value) || 40.7128,
            lng: parseFloat(document.getElementById('eventLng').value) || -74.0060,
            status: document.getElementById('eventStatus').value,
            description: document.getElementById('eventDescription').value
        };
        if (!eventData.name || !eventData.date) { alert('Please fill in all required fields'); return; }
        try {
            const url = id ? `/api/events/${id}` : '/api/events';
            const method = id ? 'PUT' : 'POST';
            const response = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(eventData) });
            closeModal();
            await loadAllEvents();
            await loadDashboardData();
            showToast(id ? '✅ Event updated!' : '✅ Event created!', 'success');
        } catch (error) { alert('Error saving event'); }
    }

    async function deleteEvent(id) {
        if (!confirm('Delete this event?')) return;
        try { await fetch(`/api/events/${id}`, { method: 'DELETE' }); await loadAllEvents(); await loadDashboardData(); showToast('🗑️ Event deleted', 'success'); } 
        catch (error) { alert('Error deleting event'); }
    }

    function viewEvent(id) {
        const event = allEvents.find(e => e.id === id);
        if (event) {
            alert(`${event.emoji || '📅'} ${event.name}\n📆 ${event.date} at ${event.time || 'TBD'}\n📍 ${event.venue}\n💰 $${event.price}\n👥 ${event.attendees} attendees\n📍 Location: ${event.lat}, ${event.lng}\n${event.description || ''}`);
        }
    }

    // Enter key support
    document.getElementById('chatInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') sendChat(); });
    document.getElementById('loginPass').addEventListener('keydown', (e) => { if (e.key === 'Enter') handleLogin(); });
    document.getElementById('qrInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') scanQRCode(); });
</script>
</body>
</html>'''

# ========== FLASK ROUTES ==========

@app.route('/')
def index():
    # Track page view
    analytics_data['page_views'] += 1
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    name = data.get('name')
    
    if not all([username, password, email, name]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    if username in users:
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    for u in users.values():
        if u.get('email') == email:
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
    
    users[username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'role': 'user',
        'email': email,
        'name': name,
        'created': datetime.now().isoformat()
    }
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username in users:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if users[username]['password'] == hashed:
            session['user_id'] = username
            session['role'] = users[username]['role']
            session['email'] = users[username].get('email', '')
            return jsonify({
                'success': True,
                'user': username,
                'role': users[username]['role'],
                'email': users[username].get('email', '')
            })
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/select/venue', methods=['POST'])
def select_venue():
    data = request.get_json()
    selected_options['venue'] = data.get('venue')
    return jsonify({'status': 'success'})

@app.route('/api/select/food', methods=['POST'])
def select_food():
    data = request.get_json()
    selected_options['food'] = data.get('food')
    return jsonify({'status': 'success'})

@app.route('/api/select/payment', methods=['POST'])
def select_payment():
    data = request.get_json()
    selected_options['payment'] = data.get('payment')
    return jsonify({'status': 'success'})

@app.route('/api/book', methods=['POST'])
def book_event():
    data = request.get_json()
    booking_id = len(event_registrations) + 1001
    user_email = data.get('user_email', session.get('email', 'user@example.com'))
    
    # Generate QR Code data
    qr_data = f"Booking ID: {booking_id}\nEvent: {data.get('event_name')}\nAttendee: {data.get('attendees_name')}\nEmail: {user_email}"
    qr_code_img = generate_qr_code(qr_data)
    
    booking = {
        'booking_id': booking_id,
        'event_id': data.get('event_id'),
        'event_name': data.get('event_name'),
        'event_date': data.get('event_date'),
        'event_time': data.get('event_time'),
        'venue': data.get('venue'),
        'food': data.get('food'),
        'payment': data.get('payment'),
        'tickets': data.get('tickets', 1),
        'total_price': data.get('total_price'),
        'attendees_name': data.get('attendees_name'),
        'user_email': user_email,
        'booked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'qr_code': qr_code_img,
        'checked_in': False
    }
    event_registrations.append(booking)
    qr_codes[booking_id] = qr_code_img
    
    # Update analytics
    analytics_data['bookings_today'] += 1
    analytics_data['revenue_today'] += data.get('total_price', 0)
    hour = datetime.now().strftime('%H') + ':00'
    if hour in analytics_data['hourly_activity']:
        analytics_data['hourly_activity'][hour] += 1
    
    # Send email with QR code
    email_sent = send_booking_email(user_email, data.get('attendees_name', 'Guest'), booking, qr_code_img)
    
    return jsonify({
        'success': True,
        'booking_id': booking_id,
        'email_sent': email_sent,
        'qr_code': qr_code_img
    })

@app.route('/api/checkin', methods=['POST'])
def check_in():
    data = request.get_json()
    booking_id = data.get('booking_id')
    
    if not booking_id:
        return jsonify({'success': False, 'message': 'Booking ID required'}), 400
    
    # Find booking
    booking = next((b for b in event_registrations if str(b['booking_id']) == str(booking_id)), None)
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    if booking.get('checked_in'):
        return jsonify({'success': False, 'message': 'Already checked in'}), 400
    
    booking['checked_in'] = True
    check_ins.append({
        'booking_id': booking_id,
        'event_name': booking['event_name'],
        'attendee': booking['attendees_name'],
        'time': datetime.now().strftime('%I:%M %p'),
        'timestamp': datetime.now().isoformat()
    })
    
    # Update analytics
    analytics_data['check_ins_today'] += 1
    
    return jsonify({
        'success': True,
        'message': f"Check-in successful for {booking['attendees_name']} at {booking['event_name']}",
        'booking': booking
    })

@app.route('/api/checkins', methods=['GET'])
def get_checkins():
    return jsonify(check_ins)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    upcoming = len([e for e in events_data if e['status'] == 'upcoming'])
    return jsonify({
        'page_views': analytics_data['page_views'],
        'bookings_today': analytics_data['bookings_today'],
        'check_ins_today': analytics_data['check_ins_today'],
        'revenue_today': analytics_data['revenue_today'],
        'upcoming_events': upcoming,
        'popular_events': analytics_data['popular_events'],
        'hourly_activity': analytics_data['hourly_activity']
    })

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    user_email = session.get('email', 'user@example.com')
    if session.get('role') == 'admin':
        return jsonify(event_registrations)
    user_bookings = [b for b in event_registrations if b.get('user_email') == user_email]
    return jsonify(user_bookings)

@app.route('/api/dashboard')
def dashboard():
    total = len(events_data)
    upcoming = len([e for e in events_data if e['status'] == 'upcoming'])
    total_attendees = sum(e.get('attendees', 0) for e in events_data)
    categories = {}
    for e in events_data:
        cat = e.get('category', 'Other')
        categories[cat] = categories.get(cat, 0) + 1
    return jsonify({
        'total_events': total,
        'upcoming_events': upcoming,
        'past_events': total - upcoming,
        'total_attendees': total_attendees,
        'categories': categories
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    category = request.args.get('category')
    if category and category != 'all':
        return jsonify([e for e in events_data if e['category'] == category])
    return jsonify(events_data)

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()
    new_event = {
        'id': max([e['id'] for e in events_data]) + 1 if events_data else 1,
        'name': data.get('name', 'Untitled'),
        'date': data.get('date', ''),
        'time': data.get('time', '12:00'),
        'category': data.get('category', 'Other'),
        'venue': data.get('venue', 'TBD'),
        'price': data.get('price', 0),
        'attendees': data.get('attendees', 0),
        'capacity': data.get('capacity', 500),
        'organizer': data.get('organizer', ''),
        'lat': data.get('lat', 40.7128),
        'lng': data.get('lng', -74.0060),
        'status': data.get('status', 'upcoming'),
        'description': data.get('description', ''),
        'emoji': data.get('emoji', '📅')
    }
    events_data.append(new_event)
    return jsonify(new_event), 201

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = next((e for e in events_data if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    data = request.get_json()
    event.update({
        'name': data.get('name', event['name']),
        'date': data.get('date', event['date']),
        'time': data.get('time', event.get('time', '12:00')),
        'category': data.get('category', event['category']),
        'venue': data.get('venue', event['venue']),
        'price': data.get('price', event.get('price', 0)),
        'attendees': data.get('attendees', event.get('attendees', 0)),
        'capacity': data.get('capacity', event.get('capacity', 500)),
        'organizer': data.get('organizer', event.get('organizer', '')),
        'lat': data.get('lat', event.get('lat', 40.7128)),
        'lng': data.get('lng', event.get('lng', -74.0060)),
        'status': data.get('status', event['status']),
        'description': data.get('description', event.get('description', ''))
    })
    return jsonify(event)

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    global events_data
    event = next((e for e in events_data if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    events_data = [e for e in events_data if e['id'] != event_id]
    return jsonify({'success': True})

@app.route('/api/venues')
def get_venues():
    return jsonify(venues_data)

@app.route('/api/food')
def get_food():
    return jsonify(food_data)

@app.route('/api/payments')
def get_payments():
    return jsonify(payment_data)

@app.route('/api/feedback', methods=['GET', 'POST'])
def handle_feedback():
    if request.method == 'POST':
        data = request.get_json()
        entry = {
            'id': len(feedback_storage) + 1,
            'feedback': data.get('feedback', ''),
            'rating': data.get('rating', 0),
            'timestamp': datetime.now().isoformat(),
            'user': data.get('user', session.get('user_id', 'anonymous'))
        }
        feedback_storage.append(entry)
        return jsonify({'status': 'success', 'id': entry['id']})
    return jsonify(feedback_storage)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '').lower().strip()
    
    responses = {
        'qr': '📱 Each booking gets a unique QR code! Scan it at the entrance or enter your Booking ID in the QR scanner for check-in.',
        'scan': '📱 Each booking gets a unique QR code! Scan it at the entrance or enter your Booking ID in the QR scanner for check-in.',
        'check': '✅ Check-in is quick and easy! Just present your QR code or enter your Booking ID in the scanner.',
        'map': '📍 Select a venue to see its location on Google Maps. Click "Get Directions" for navigation!',
        'location': '📍 Select a venue to see its location on Google Maps. Click "Get Directions" for navigation!',
        'analytics': '📊 The real-time dashboard shows: Page Views, Bookings Today, Check-ins Today, and Revenue Today!',
        'venue': '🎯 We have 9 venues with Google Maps integration! Select one to see its location and get directions.',
        'venues': '🎯 We have 9 venues with Google Maps integration! Select one to see its location and get directions.',
        'food': '🍽️ We offer 10 food options with pictures! Italian, Seafood, French, Indian, Mexican, and more!',
        'event': '📅 We have 20 events! Book now to get your QR code for entrance.',
        'events': '📅 We have 20 events! Book now to get your QR code for entrance.',
        'book': '🎫 To book: select an event, choose options, enter your email, and click "Book & Get QR"!',
        'hello': '👋 Hello! I can help with QR codes, check-in, Google Maps, events, venues, food, and analytics!',
        'hi': '👋 Hello! I can help with QR codes, check-in, Google Maps, events, venues, food, and analytics!',
        'help': '🆘 I can help with: QR code scanning, check-in, Google Maps navigation, events, venues, food, and analytics!'
    }
    
    reply = None
    for keyword, response in responses.items():
        if keyword in msg:
            reply = response
            break
    
    if not reply:
        reply = "🤔 I can help with QR codes, check-in, Google Maps, events, venues, food, and analytics! What would you like to know?"
    
    return jsonify({'reply': reply})

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 EventVault Premium - QR Code, Maps & Real-time Analytics")
    print("=" * 70)
    print("📊 Dashboard: http://localhost:5000")
    print("")
    print("🔑 Login: admin/admin123")
    print("")
    print("🎯 New Features:")
    print("   📱 QR Code Generation for each booking")
    print("   ✅ QR Code Scanner for check-in at entrance")
    print("   🗺️ Google Maps integration with venue locations")
    print("   📊 Real-time Analytics Dashboard")
    print("   📧 Email with QR code attachment")
    print("   🎫 20 Events with locations")
    print("   🍽️ 10 Food Cards with pictures")
    print("   🏢 9 Venues with Google Maps")
    print("   💳 7 Payment Methods")
    print("   🤖 AI Chatbot Assistant")
    print("=" * 70)
    print("📧 Email: " + ("✅ ENABLED" if EMAIL_ENABLED else "❌ DISABLED"))
    print("🗺️ Google Maps: Integrated with venue locations")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)