# 🏎️ HotWheels Collection Manager

A modern Flask web application for managing your HotWheels car collection with AI-powered features.

## 📸 Screenshots
*Dashboard • Car Details • AI Integration*

## ✨ Features

### 🔐 Authentication
- User registration and login system
- Secure session management
- Personalized collections

### 🚗 Collection Management
- Add cars via camera capture or file upload
- View collection in organized dashboard
- Delete cars from collection
- Car details with images and notes

### 🤖 AI Integration
- Fetch detailed car information using Gemini API
- Automated car data enrichment
- Smart categorization

### 🎨 User Experience
- Fully responsive design
- Clean, modern interface
- Mobile-friendly layout
- Intuitive navigation

## 🛠️ Tech Stack

- **Backend**: Flask, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **AI**: Gemini API integration
- **File Handling**: Image uploads & camera capture

## 📦 Installation

### Prerequisites
- Python 3.8+
- Git
- Web browser with camera support

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone https://github.com/harshitbhardwaj14/HotWheels_App.git
cd HotWheels_App
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- **Windows:**
```bash
venv\Scripts\activate
```
- **Mac/Linux:**
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set environment variables**
```bash
# Windows
set FLASK_APP=app.py
set FLASK_ENV=development
set GEMINI_API_URL="https://your-gemini-endpoint.com/v1/generate"
set GEMINI_API_KEY="your_api_key_here"

# Mac/Linux
export FLASK_APP=app.py
export FLASK_ENV=development
export GEMINI_API_URL="https://your-gemini-endpoint.com/v1/generate"
export GEMINI_API_KEY="your_api_key_here"
```

6. **Run the application**
```bash
python app.py
```

7. **Access the application**
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📁 Project Structure

```
HotWheels_app/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
├── instance/
│   └── hotwheels.db      # SQLite database (auto-generated)
│
├── static/
│   └── uploads/          # User-uploaded car images
│
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── signup.html       # User registration
    ├── login.html        # User login
    ├── collection.html   # Collection dashboard
    └── car_detail.html   # Car details page
```

## 🔧 Configuration

### Environment Variables
- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Development/Production mode
- `GEMINI_API_URL`: Gemini API endpoint
- `GEMINI_API_KEY`: Your Gemini API key

### Database
The application uses SQLite with the following tables:
- `users`: User authentication data
- `cars`: Car collection data

## 🚀 Usage

### Getting Started
1. **Register** a new account or **login** if you already have one
2. **Access your dashboard** to view your collection
3. **Add cars** using camera capture or file upload
4. **View details** and use AI to fetch more information
5. **Manage your collection** by deleting cars as needed

### Adding Cars
1. Click "Add Car" in your dashboard
2. Choose between:
   - **Camera Capture**: Take a photo using your device camera
   - **File Upload**: Select an image from your device
3. Add optional notes about the car
4. Save to add to your collection

### AI Features
- Click "Get More Info" on any car to fetch AI-generated details
- The Gemini API will analyze the car image and provide additional information

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Secure file upload handling
- SQL injection prevention

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page redirect |
| GET | `/signup` | User registration form |
| POST | `/signup` | Create new user |
| GET | `/login` | User login form |
| POST | `/login` | Authenticate user |
| GET | `/logout` | User logout |
| GET | `/collection` | User's car collection |
| POST | `/add_car` | Add new car to collection |
| GET | `/car/<id>` | View car details |
| POST | `/get_car_info/<id>` | Fetch AI-generated car info |
| POST | `/delete_car/<id>` | Remove car from collection |

## 🐛 Troubleshooting

### Common Issues

**Database errors:**
```bash
# Delete and recreate database
rm instance/hotwheels.db
python app.py
```

**Port already in use:**
```bash
# Kill process on port 5000
npx kill-port 5000
```

**Missing dependencies:**
```bash
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

**Camera not working:**
- Ensure HTTPS in production
- Check browser permissions
- Use file upload as alternative

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Harshit Bhardwaj**
- GitHub: [@harshitbhardwaj14](https://github.com/harshitbhardwaj14)

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Gemini API for AI capabilities
- HotWheels enthusiasts for inspiration

---

**⭐ Star this repo if you find it helpful!**
