# University Course Recommender

An AI-powered university course recommendation system designed specifically for UK Year 11-13 students. This system helps students discover the perfect university courses based on their A-level subjects, predicted grades, and personal preferences.

## 🎯 Project Overview

This project addresses the challenge faced by UK students when choosing university courses. With over 50,000 courses available across 150+ universities, students often struggle to find courses that match their academic profile and career aspirations.

### Key Features

- **Smart Matching Algorithm**: Advanced recommendation engine that matches courses based on multiple weighted criteria
- **Personalized Results**: Tailored recommendations based on A-level subjects, predicted grades, and preferences
- **Comprehensive Database**: Access to all UK university courses with detailed entry requirements
- **User-Friendly Interface**: Modern, responsive design optimized for students
- **Export Functionality**: Download recommendations as CSV or PDF
- **Secure Authentication**: JWT-based user authentication with profile management

## 🛠️ Technical Stack

### Backend (Python/Flask)
- **Flask**: Lightweight web framework for API development
- **MongoDB**: NoSQL database for flexible course data storage
- **PyMongo**: MongoDB driver for Python
- **JWT**: Secure authentication with JSON Web Tokens
- **bcrypt**: Password hashing for security
- **Pandas/NumPy**: Data processing for recommendation algorithms
- **scikit-learn**: Machine learning for advanced matching

### Frontend (React/Next.js)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **React Hook Form**: Form management
- **Headless UI**: Accessible UI components
- **Framer Motion**: Smooth animations

### DevOps
- **Docker**: Containerization for easy deployment
- **Docker Compose**: Multi-container orchestration
- **MongoDB Express**: Database administration interface

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **MongoDB** (or Docker)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd university-course-recommender
   ```

2. **Install dependencies**
   ```bash
   npm run install:all
   ```

3. **Set up environment variables**
   ```bash
   # Copy environment file
   cp server/.env.example server/.env
   
   # Edit the environment file
   nano server/.env
   ```

4. **Start with Docker (Recommended)**
   ```bash
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

5. **Or start locally**
   ```bash
   # Start MongoDB
   docker-compose up -d mongodb
   
   # Start backend (Terminal 1)
   cd server
   python app.py
   
   # Start frontend (Terminal 2)
   cd client
   npm run dev
   ```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **MongoDB Express**: http://localhost:8081 (admin/admin123)

## 📊 Recommendation Algorithm

The system uses a sophisticated weighted scoring algorithm that considers:

### Core Matching Criteria (Weighted)

1. **Subject Match (30%)**: Alignment between student's A-level subjects and course requirements
2. **Grade Match (25%)**: Comparison of predicted grades with entry requirements
3. **Preference Match (20%)**: Student preferences (location, budget, university size)
4. **University Ranking (15%)**: University prestige and subject-specific rankings
5. **Employability (10%)**: Graduate employment rates and salary prospects

### Advanced Features

- **Grade Conversion**: A* to U grade system with numerical scoring
- **Regional Matching**: UK geographical preferences
- **Budget Filtering**: Tuition fee constraints
- **Career Alignment**: Subject-specific career pathway matching
- **Flexible Requirements**: Handles various entry requirement formats

## 🖥️ Platform Support

This project works on **Windows**, **macOS**, and **Linux**!

- **Windows:** See `SETUP_INSTRUCTIONS.md`
- **macOS:** See `SETUP_INSTRUCTIONS_MAC.md` 
- **Linux:** Similar to macOS (use `SETUP_INSTRUCTIONS_MAC.md`)
- **Cross-platform guide:** See `PLATFORM_COMPATIBILITY.md`

**Key difference:** Windows uses `python`, macOS/Linux use `python3` - everything else is identical!

## 🗄️ Database Schema

### Students Collection
```javascript
{
  email: String (unique, required)
  password: String (hashed, required)
  firstName: String (required)
  lastName: String (required)
  yearGroup: String (Year 11/12/13)
  aLevelSubjects: [String]
  predictedGrades: {subject: grade}
  preferences: {
    preferredRegion: String
    maxBudget: Number
    preferredUniSize: String
    careerInterests: [String]
  }
  createdAt: Date
  lastLogin: Date
}
```

### Courses Collection
```javascript
{
  name: String (required)
  university: {
    name: String
    location: String
    ranking: {overall: Number, subject: Number}
  }
  subjects: [String]
  entryRequirements: {
    subjects: [String]
    grades: {subject: grade}
    additionalRequirements: String
    interviewRequired: Boolean
    entranceExam: String
  }
  fees: {
    uk: Number
    international: Number
  }
  employability: {
    employmentRate: Number
    averageSalary: Number
    topEmployers: [String]
  }
  duration: Number (years)
  description: String
}
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new student
- `POST /api/auth/login` - Student login
- `GET /api/student/profile` - Get student profile
- `PUT /api/student/profile` - Update student profile

### Recommendations
- `POST /api/recommendations` - Get course recommendations
- `GET /api/courses` - Browse all courses
- `GET /api/universities` - Get all universities

### Export
- `GET /api/export/recommendations/{studentId}?format=csv` - Export as CSV
- `GET /api/export/recommendations/{studentId}?format=pdf` - Export as PDF

### Admin
- `POST /api/admin/courses` - Add new course
- `PUT /api/admin/courses/{id}` - Update course
- `DELETE /api/admin/courses/{id}` - Delete course

## 🧪 Testing

### Backend Tests
```bash
cd server
python -m pytest
```

### Frontend Tests
```bash
cd client
npm test
```

### Integration Tests
```bash
# Test API endpoints
curl http://localhost:5000/api/health

# Test recommendation engine
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"preferredRegion": "London", "maxBudget": 9250}'
```

## 📈 Performance Optimization

### Database Indexing
- Email and username indexes for fast user lookups
- Subject and university indexes for course filtering
- Composite indexes for recommendation queries

### Caching Strategy
- React Query for frontend data caching
- MongoDB query optimization
- Recommendation result caching

### Scalability
- Horizontal scaling with Docker containers
- Database sharding for large datasets
- CDN integration for static assets

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with configurable rounds
- **Input Validation**: Comprehensive data validation
- **CORS Protection**: Cross-origin request security
- **Rate Limiting**: API request throttling
- **Data Encryption**: Sensitive data protection

## 🚀 Deployment

### Production Deployment

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   export FLASK_ENV=production
   export MONGODB_URI=mongodb://user:pass@host:port/db
   export JWT_SECRET_KEY=your-secure-secret-key
   ```

2. **Docker Production**
   ```bash
   # Build production images
   docker-compose -f docker-compose.prod.yml build
   
   # Start production services
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Database Migration**
   ```bash
   # Run database migrations
   python server/migrate.py
   ```

### Monitoring

- **Health Checks**: `/api/health` endpoint
- **Logging**: Structured logging with timestamps
- **Metrics**: Performance monitoring
- **Error Tracking**: Comprehensive error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Educational Value

This project demonstrates advanced computer science concepts:

- **Object-Oriented Programming**: Python classes and inheritance
- **Algorithm Design**: Recommendation engine with weighted scoring
- **Database Design**: NoSQL schema optimization
- **API Development**: RESTful API with Flask
- **Frontend Architecture**: React with modern patterns
- **DevOps**: Docker containerization and deployment
- **Testing**: Unit, integration, and end-to-end testing

## 📞 Support

For support and questions:

1. Check the [documentation](docs/)
2. Review [troubleshooting guide](docs/troubleshooting.md)
3. Open an [issue](https://github.com/your-repo/issues)
4. Contact: your-email@example.com

## 🗺️ Roadmap

- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Integration with UCAS API
- [ ] Machine learning improvements
- [ ] Multi-language support
- [ ] Social features (sharing recommendations)
- [ ] University partnership integrations

---

**University Course Recommender** - Empowering students to make informed decisions about their future.