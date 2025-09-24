# ProjectSigma - WSL2 Setup Guide

This guide will help you set up ProjectSigma with MongoDB running in WSL2 on Windows.

## Prerequisites

1. **Windows 10/11** with WSL2 enabled
2. **Ubuntu 20.04+** in WSL2
3. **Docker Desktop** for Windows with WSL2 backend enabled
4. **Node.js 18+** (optional, for local development)

## WSL2 Setup Instructions

### 1. Enable WSL2 and Install Ubuntu

```powershell
# Run in PowerShell as Administrator
wsl --install
# or for specific Ubuntu version
wsl --install -d Ubuntu-20.04
```

### 2. Install Docker in WSL2

```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start
```

### 3. Install Node.js (for local development)

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 4. Clone and Setup ProjectSigma

```bash
# Navigate to your development directory
cd ~/projects

# Clone the repository (if using git)
# git clone <repository-url> projectsigma
# cd projectsigma

# Or if you have the files locally, copy them to WSL2
# Copy your project files to WSL2 filesystem
```

### 5. Environment Configuration

```bash
# Copy environment files
cp server/.env.example server/.env

# Edit the environment file
nano server/.env
```

Update the `.env` file with your configuration:

```env
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb://admin:password123@localhost:27017/projectsigma?authSource=admin
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRE=7d
BCRYPT_ROUNDS=12
CORS_ORIGIN=http://localhost:3000
```

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Local Development

```bash
# Install dependencies
npm run install:all

# Start MongoDB
docker-compose up -d mongodb

# Start backend (in one terminal)
cd server
npm run dev

# Start frontend (in another terminal)
cd client
npm run dev
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **MongoDB Express**: http://localhost:8081 (admin/admin123)
- **MongoDB**: localhost:27017

## MongoDB Connection Details

- **Host**: localhost (from Windows) or mongodb (from Docker containers)
- **Port**: 27017
- **Database**: projectsigma
- **Username**: admin
- **Password**: password123
- **Authentication Database**: admin

## Development Workflow

### 1. Database Management

```bash
# Connect to MongoDB shell
docker exec -it projectsigma-mongodb mongosh -u admin -p password123 --authenticationDatabase admin

# Use the projectsigma database
use projectsigma

# View collections
show collections

# View users
db.users.find().pretty()

# View projects
db.projects.find().pretty()
```

### 2. Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Follow logs in real-time
docker-compose logs -f backend
```

### 3. Database Backup and Restore

```bash
# Backup database
docker exec projectsigma-mongodb mongodump --username admin --password password123 --authenticationDatabase admin --db projectsigma --out /backup

# Copy backup from container
docker cp projectsigma-mongodb:/backup ./mongodb-backup

# Restore database
docker exec -i projectsigma-mongodb mongorestore --username admin --password password123 --authenticationDatabase admin --db projectsigma /backup/projectsigma
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port
   sudo netstat -tulpn | grep :3000
   # Kill process
   sudo kill -9 <PID>
   ```

2. **Docker permission denied**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

3. **MongoDB connection failed**
   ```bash
   # Check if MongoDB is running
   docker-compose ps
   # Restart MongoDB
   docker-compose restart mongodb
   ```

4. **WSL2 networking issues**
   ```bash
   # Restart WSL2
   wsl --shutdown
   # Then restart your WSL2 instance
   ```

### Performance Optimization

1. **Increase WSL2 memory limit**
   Create/edit `.wslconfig` in your Windows user directory:
   ```ini
   [wsl2]
   memory=8GB
   processors=4
   ```

2. **Use WSL2 filesystem for better performance**
   ```bash
   # Always work in WSL2 filesystem, not Windows filesystem
   cd ~/projects/projectsigma
   ```

## Security Considerations

1. **Change default passwords** in production
2. **Use environment variables** for sensitive data
3. **Enable MongoDB authentication** in production
4. **Use HTTPS** in production
5. **Regular security updates** for all components

## Next Steps

1. Set up SSL certificates for HTTPS
2. Configure production environment variables
3. Set up monitoring and logging
4. Implement CI/CD pipeline
5. Add automated testing

## Support

For issues and questions:
- Check the logs: `docker-compose logs`
- Verify services: `docker-compose ps`
- Test connectivity: `curl http://localhost:5000/api/health`
