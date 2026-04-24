# 🧾 Digital Notice Board System

A real-time web-based Digital Notice Board that allows departments to upload, schedule, and display notices dynamically using Flask and Socket.IO.

---

## 🚀 Features

* 🔐 User Authentication (Login / Signup)
* 🏫 Department-based Admin Panels (CSE, IT, ECE, MECH)
* 📤 Upload Notices (Images, Videos, Audio, Documents)
* ⏰ Schedule Notices for Future Display
* 🗑️ Delete Individual or All Notices
* 📡 Real-time Updates using WebSockets
* 🖥️ Public Slideshow Display (Auto-rotating)
* 📱 Responsive UI

---

## 🧠 Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Flask
* **Database:** SQLite
* **Real-time:** Flask-SocketIO
* **Server:** Gunicorn

---

## 📸 Screenshots

### 🏠 Home Page
![Home](screenshots/home.png)

### 🔐 Login Page
![Login](screenshots/login.png)

### 📊 Dashboard
![Dashboard](screenshots/dashboard.png)

### 🛠️ Admin Panel
![Admin](screenshots/admin.png)

### 🖥️ Slideshow Display
![Slideshow](screenshots/slideshow.png)

### 📱 Mobile View
![Mobile](screenshots/mobile_view.png)

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/digital-notice-board.git
cd digital-notice-board

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
python main.py
```

---

## 🌐 Usage

* Open: http://127.0.0.1:5000
* Login / Signup
* Select Department
* Upload or Schedule Notices
* View slideshow:

```
http://127.0.0.1:5000/slideshow/<department>
```

Example:

```
http://127.0.0.1:5000/slideshow/ece
```

---

## ☁️ Deployment

This project can be deployed on platforms like:

* Render
* Railway
* Heroku

---

## ⚠️ Limitations

* Uploaded files are stored locally
* On free hosting (Render), files may not persist after restart

---

## 🔮 Future Improvements

* Cloud Storage Integration (AWS S3 / Cloudinary)
* Role-based authentication
* Fullscreen TV Mode
* Notice categories & filters

---

## 👨‍💻 Author

**Suraj Golambade**

---

## ⭐ Show your support

If you like this project, give it a ⭐ on GitHub!
