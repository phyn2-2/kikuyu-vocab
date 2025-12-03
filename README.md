# 🌍 Kikuyu Vocabulary Platform

A collaborative language learning platform for preserving and teaching the Kikuyu language through community contributions.

![Django](https://img.shields.io/badge/Django-5.2.8-092E20?style=flat&logo=django)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 📚 **Browse Vocabulary** - Explore Kikuyu words with English translations
- 🎵 **Audio Pronunciations** - Listen to native speakers
- 🖼️ **Visual Context** - Images for better understanding
- 🔍 **Advanced Search** - Filter by category, difficulty, language
- 👥 **Community Driven** - Authenticated users can contribute
- ✅ **Quality Control** - Admin approval workflow
- 💬 **Discussions** - Comment on words and usage
- ❤️ **Favorites** - Save words for later study
- 📱 **Responsive Design** - Works on mobile and desktop

## 🎨 Design

Custom **deep purple theme** with dark web aesthetic:
- Mystical purple (#8b5cf6) accent colors
- Smooth animations and hover effects
- JetBrains Mono monospace font
- Card-based layouts with gradients
- Mobile-responsive design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/kikuyu-vocab-platform.git
cd kikuyu-vocab-platform

# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
# myenv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser

# Create categories (optional)
python manage.py shell
>>> from vocab.models import Category
>>> Category.objects.create(name='Noun', icon='📦', description='People, places, things')
>>> Category.objects.create(name='Verb', icon='⚡', description='Actions')
>>> exit()

# Collect static files
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## 🎯 Usage

### For Learners (Public)
1. Browse vocabulary at `/vocab/`
2. Search and filter words
3. Listen to pronunciations
4. View examples and context

### For Contributors (Authenticated)
1. Create an account (contact admin)
2. Click "Add Word"
3. Fill in word details, upload audio/image
4. Submit for review
5. Track your contributions in "My Words"

### For Admins
1. Access admin panel at `/admin/`
2. Review pending submissions
3. Approve/reject with one click
4. Manage categories and users

## 📂 Project Structure
```
kikuyu-vocab-platform/
├── core/                  # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── templates/admin/   # Custom admin templates
├── vocab/                 # Main vocab app
│   ├── models.py         # Database models
│   ├── views.py          # View logic
│   ├── forms.py          # Form handling
│   ├── admin.py          # Admin customization
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS
├── media/                # User uploads
├── staticfiles/          # Collected static files
├── requirements.txt      # Python dependencies
└── manage.py            # Django management
```

## 🛠️ Tech Stack

- **Backend:** Django 5.2.8
- **Database:** SQLite (dev), PostgreSQL (prod recommended)
- **Frontend:** HTML5, CSS3 (vanilla)
- **Styling:** Custom CSS with CSS variables
- **Font:** JetBrains Mono (monospace)
- **File Storage:** Django FileField (local), S3 (prod recommended)

## 🎓 Models

- **Vocab** - Main word entries with translations, audio, images
- **Category** - Word classifications (Noun, Verb, etc.)
- **Tag** - Flexible contextual tags
- **Comment** - User discussions on words

## 🔐 Security Features

- CSRF protection
- File upload validation (size, format)
- Admin approval workflow
- User authentication
- SQL injection prevention (Django ORM)

## 📈 Future Enhancements

- [ ] Spaced repetition quiz system
- [ ] Progress tracking dashboard
- [ ] Audio recording in-browser
- [ ] Multi-language support (Swahili, etc.)
- [ ] API for mobile apps
- [ ] Social sharing
- [ ] Leaderboards

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file

## 👤 Author

**Your Name**
- Portfolio: [yourwebsite.com]
- GitHub: [@yourusername]
- Email: your.email@example.com

---

Built with 💜 for language preservation

**#Django #LanguageLearning #Kikuyu #OpenSource**
