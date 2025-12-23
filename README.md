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
- **PostgreSQL**: Relational database for course data storage
- **SQLAlchemy**: Python SQL toolkit and ORM
- **psycopg2**: PostgreSQL adapter for Python
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

## 📚 Documentation

**Comprehensive documentation is available in the [`docs/`](./docs/) directory.**

### Quick Links
- **[Documentation Index](./docs/README.md)** - Complete documentation structure
- **[Module Documentation](./docs/modules/)** - Core system components (RecommendationEngine, API, Models)
- **[Setup Guides](./docs/setup/)** - Installation and setup instructions
- **[User Guides](./docs/guides/)** - How-to guides for system features
- **[Troubleshooting](./docs/troubleshooting/)** - Solutions to common problems

### Key Module Documentation
- **[RecommendationEngine](./docs/modules/recommendation_engine.md)** - Core recommendation algorithm
- **[Flask API](./docs/modules/app.md)** - Backend API endpoints and authentication
- **[Data Models](./docs/modules/models.md)** - Student, Course, and University models

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 12+** (or Docker)
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
   # Create .env file in server directory
   # See docs/database/ for database setup instructions
   ```

4. **Set up PostgreSQL Database**
   ```bash
   # See docs/database/QUICK_START_LOCAL.md for detailed instructions
   # Quick start:
   cd server/database
   python init_db.py
   ```

5. **Start with Docker (Recommended)**
   ```bash
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

6. **Or start locally**
   ```bash
   # Start PostgreSQL
   docker-compose up -d postgres
   
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
- **pgAdmin**: http://localhost:8081 (admin@admin.com/admin123) - PostgreSQL administration

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

- **Windows:** See [docs/setup/SETUP_INSTRUCTIONS_WINDOWS.md](docs/setup/SETUP_INSTRUCTIONS_WINDOWS.md)
- **macOS:** See [docs/setup/SETUP_INSTRUCTIONS_MAC.md](docs/setup/SETUP_INSTRUCTIONS_MAC.md) 
- **Linux:** Similar to macOS (use [docs/setup/SETUP_INSTRUCTIONS_MAC.md](docs/setup/SETUP_INSTRUCTIONS_MAC.md))
- **Cross-platform guide:** See [docs/setup/PLATFORM_COMPATIBILITY.md](docs/setup/PLATFORM_COMPATIBILITY.md)
- **Complete beginner guide:** See [docs/setup/COMPLETE_BEGINNER_SETUP_GUIDE.md](docs/setup/COMPLETE_BEGINNER_SETUP_GUIDE.md)

**Key difference:** Windows uses `python`, macOS/Linux use `python3` - everything else is identical!

## 📚 Documentation

**Comprehensive documentation is available in the [`docs/`](docs/) directory.**

### Quick Links
- **[Documentation Index](docs/README.md)** - Complete documentation structure
- **[Module Documentation](docs/modules/)** - Core system components (RecommendationEngine, API, Models)
- **[Setup Guides](docs/setup/)** - Installation and setup instructions
- **[User Guides](docs/guides/)** - How-to guides for system features
- **[Troubleshooting](docs/troubleshooting/)** - Solutions to common problems
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Quick reference guide

### Key Module Documentation
- **[RecommendationEngine](docs/modules/recommendation_engine.md)** - Core recommendation algorithm
- **[Flask API](docs/modules/app.md)** - Backend API endpoints and authentication
- **[Data Models](docs/modules/models.md)** - Student, Course, and University models

### Additional Documentation
- **[Database Documentation](docs/database/)** - PostgreSQL setup and migration guides
- **[Design Documentation](docs/design/)** - System architecture and wireframes
- **[Requirements](docs/requirements/)** - Project requirements and specifications

## 🗄️ Database Schema

The project uses **PostgreSQL** as the relational database. The schema includes:

- **student** - Student user accounts
- **university** - University information
- **course** - Course information with entry requirements
- **subject** - A-Level subjects catalog
- **student_grade** - Student predicted grades
- **course_requirement** - Course entry requirements
- **recommendation_run** - Recommendation run metadata
- **recommendation_result** - Recommendation results (JSONB)

For detailed database schema documentation, see:
- [docs/database/](docs/database/) - Database setup and migration guides
- [docs/design/HIGH_LEVEL_DESIGN.md](docs/design/HIGH_LEVEL_DESIGN.md) - Complete schema design
- [server/database/migrations/](server/database/migrations/) - SQL migration files

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
   export DATABASE_URL=postgresql://user:pass@host:port/db
   export POSTGRES_DB=university_recommender
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD=your-secure-password
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
- **Database Design**: Relational database schema with PostgreSQL
- **SQL Queries**: Complex joins, indexes, and query optimization
- **API Development**: RESTful API with Flask
- **Frontend Architecture**: React with modern patterns
- **DevOps**: Docker containerization and deployment
- **Testing**: Unit, integration, and end-to-end testing

## 📞 Support

For support and questions:

1. **[Check Documentation](docs/README.md)** - Complete documentation index
2. **[Troubleshooting Guide](docs/troubleshooting/)** - Common issues and solutions
3. **[Quick Reference](docs/QUICK_REFERENCE.md)** - Quick command and API reference
4. **[Module Documentation](docs/modules/)** - Detailed component documentation
5. Open an [issue](https://github.com/your-repo/issues) on GitHub

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