# Project Documentation

Welcome to the University Course Recommender documentation. This directory contains comprehensive documentation for all aspects of the project.

## 📚 Documentation Structure

### [Modules](./modules/)
Detailed documentation for core system modules:

- **[RecommendationEngine](./modules/recommendation_engine.md)** - Core recommendation algorithm and matching logic
- **[Flask API (app.py)](./modules/app.md)** - Backend API endpoints and authentication
- **[Data Models](./modules/models.md)** - Student, Course, and University models

### [Setup Guides](./setup/)
Step-by-step setup instructions for different platforms:

- **[Complete Beginner Setup](./setup/COMPLETE_BEGINNER_SETUP_GUIDE.md)** - Full setup guide for beginners
- **[Windows Setup](./setup/SETUP_INSTRUCTIONS_WINDOWS.md)** - Windows-specific instructions
- **[Mac Setup](./setup/SETUP_INSTRUCTIONS_MAC.md)** - macOS-specific instructions
- **[WSL2 Setup](./setup/WSL2_SETUP.md)** - Windows Subsystem for Linux setup
- **[Frontend Setup](./setup/frontend_setup.md)** - Next.js frontend setup
- **[External Access](./setup/external_access.md)** - Configuring external access

### [Database Guides](./database/)
Database setup, migrations, and data import:

- **[Quick Start (Local)](./database/QUICK_START_LOCAL.md)** - Local PostgreSQL setup
- **[Quick Start (Discover Uni)](./database/QUICK_START_DISCOVER_UNI.md)** - Discover Uni data import
- **[Migrations Guide](./database/MIGRATIONS_STEP_BY_STEP.md)** - Database migration process
- **[HESA Data Import](./database/POSTGRESQL_MIGRATION_SUMMARY.md)** - HESA data integration
- **[Run Feedback Migration](./database/run_feedback_migration.md)** - Feedback system migration

### [User Guides](./guides/)
How-to guides for using and managing the system:

- **[Career Interests Management](./guides/career_interests.md)** - Managing career interests in the database
- **[Feedback System](./guides/feedback_system.md)** - How the feedback system works
- **[HESA Data](./guides/hesa_data.md)** - Understanding and importing HESA data
- **[Profile Management](./guides/profile_management.md)** - Managing student profiles

### [Troubleshooting](./troubleshooting/)
Solutions to common problems:

- **[Login Errors](./troubleshooting/login_errors.md)** - Fixing login and authentication issues
- **[Quick Fix Login](./troubleshooting/quick_fix_login.md)** - Quick login troubleshooting
- **[Password Setup](./troubleshooting/password_setup.md)** - Password configuration issues
- **[Update Password](./troubleshooting/update_password.md)** - Changing passwords
- **[Python Compatibility](./troubleshooting/python_compatibility.md)** - Python version issues
- **[Frontend Errors](./troubleshooting/frontend_errors.md)** - Frontend build and runtime errors

### [Design](./design/)
System design and architecture:

- **[High-Level Design](./design/HIGH_LEVEL_DESIGN.md)** - System architecture overview
- **[Wireframes](./design/wireframes.md)** - UI/UX wireframes

### [Requirements](./requirements/)
Project requirements and specifications:

- **[Requirements](./requirements/REQUIREMENTS.md)** - Functional and non-functional requirements
- **[Marking Scheme Summary](./requirements/markingschemeSummary.md)** - Assessment criteria

## 🚀 Quick Links

### Getting Started
1. [Complete Beginner Setup Guide](./setup/COMPLETE_BEGINNER_SETUP_GUIDE.md)
2. [Local Database Setup](./database/QUICK_START_LOCAL.md)
3. [Frontend Setup](./setup/frontend_setup.md)

### Core Components
1. [RecommendationEngine Module](./modules/recommendation_engine.md)
2. [Flask API Documentation](./modules/app.md)
3. [Data Models](./modules/models.md)

### Common Tasks
1. [Managing Career Interests](./guides/career_interests.md)
2. [Importing HESA Data](./guides/hesa_data.md)
3. [Profile Management](./guides/profile_management.md)

### Troubleshooting
1. [Login Issues](./troubleshooting/login_errors.md)
2. [Frontend Errors](./troubleshooting/frontend_errors.md)
3. [Python Compatibility](./troubleshooting/python_compatibility.md)

## 📖 Documentation Standards

### Module Documentation
Each module documentation includes:
- **Overview**: Purpose and location
- **Architecture**: Design patterns and structure
- **Key Components**: Main classes, methods, and functions
- **API Reference**: Method signatures and parameters
- **Usage Examples**: Code examples
- **Related Modules**: Cross-references

### Guide Documentation
Each guide includes:
- **Prerequisites**: What you need before starting
- **Step-by-step Instructions**: Detailed walkthrough
- **Troubleshooting**: Common issues and solutions
- **Next Steps**: What to do after completion

## 🔍 Finding Documentation

### By Topic
- **Setup**: See [setup/](./setup/)
- **Database**: See [database/](./database/)
- **API**: See [modules/app.md](./modules/app.md)
- **Algorithms**: See [modules/recommendation_engine.md](./modules/recommendation_engine.md)
- **Errors**: See [troubleshooting/](./troubleshooting/)

### By Component
- **Backend**: [modules/app.md](./modules/app.md), [modules/models.md](./modules/models.md)
- **Frontend**: [setup/frontend_setup.md](./setup/frontend_setup.md)
- **Database**: [database/](./database/)
- **Recommendation Engine**: [modules/recommendation_engine.md](./modules/recommendation_engine.md)

## 📝 Contributing to Documentation

When adding new documentation:
1. Place in the appropriate directory
2. Follow existing documentation structure
3. Include code examples where relevant
4. Cross-reference related documentation
5. Update this README if adding new sections

## 🔗 External Resources

- [Project README](../README.md) - Main project overview
- [GitHub Repository](https://github.com/yap1co/projectsigma) - Source code
- [Flask Documentation](https://flask.palletsprojects.com/) - Flask framework docs
- [Next.js Documentation](https://nextjs.org/docs) - Next.js framework docs
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - PostgreSQL database docs
