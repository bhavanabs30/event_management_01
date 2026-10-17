# EventVault — Event Management

EventVault is a Flask-based event management demo. It includes event listings, user registration and sign-in, booking, QR-code check-in, venue maps, and an analytics dashboard.

## Features

- Browse and manage events
- Register and sign in as a user or admin
- Book an event and generate a QR code
- Check attendees in by scanning a QR code or entering a booking ID
- View dashboard analytics and bookings
- Browse venues, food options, and payment methods
- Open venue locations in Google Maps
- Send booking confirmation emails with QR codes when email is configured
- Use the built-in chatbot for basic help

## Requirements

- Python 3.9 or newer
- pip

## Setup

Clone the repository and open its folder:

```bash
git clone https://github.com/bhavanabs30/event_management_01.git
cd event_management_01
```

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirement.txt
pip install "qrcode[pil]"
```

## Run the app

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Demo accounts

The app currently defines these demo accounts:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| User | `demo` | `demo123` |

These credentials are for local demonstration only. Change or remove them before deploying the app or making it available to others.

## Email configuration

Booking emails require valid SMTP settings. In `app.py`, configure the SMTP server, email address, and app password for your mail provider. Do not commit real credentials to GitHub. Use environment variables or another secrets manager for private values.

## Notes

- The app stores bookings and other data in memory, so data resets when the server restarts.
- The listed payment methods are demo options; this project does not process real payments.
- The built-in chatbot provides predefined responses.

## Dependencies

The project uses Flask and Flask-Cors, plus `qrcode[pil]` to generate QR-code images. Consider adding `qrcode[pil]` to `requirement.txt` so all dependencies can be installed with one command.
