# Platform Compatibility Guide

This project is designed to work on **Windows**, **macOS**, and **Linux**. The core functionality is identical across platforms, with minor differences in setup commands.

## ✅ Supported Platforms

- **Windows 10/11** (x64)
- **macOS** (Intel and Apple Silicon M1/M2/M3)
- **Linux** (Ubuntu, Debian, Fedora, etc.)

## 🔄 Cross-Platform Compatibility

### What's the Same

- ✅ Docker Compose configuration
- ✅ PostgreSQL database schema
- ✅ Python import scripts
- ✅ API endpoints
- ✅ Frontend code
- ✅ Database queries and algorithms

### What's Different

| Component | Windows | macOS | Linux |
|-----------|---------|-------|-------|
| **Python Command** | `python` | `python3` | `python3` |
| **File Paths** | `C:\Users\...` | `/Users/...` | `/home/...` |
| **Shell** | PowerShell/CMD | zsh/bash | bash |
| **Docker Paths** | `\\wsl$\...` | `/Users/...` | `/home/...` |
| **Line Endings** | CRLF | LF | LF |
| **Package Manager** | pip | pip3/brew | pip3/apt/yum |

## 📋 Platform-Specific Setup

### Windows
See: `SETUP_INSTRUCTIONS.md`
- Uses `python` command
- PowerShell or CMD
- Docker Desktop for Windows

### macOS
See: `SETUP_INSTRUCTIONS_MAC.md`
- Uses `python3` command
- Terminal.app or iTerm2
- Docker Desktop for Mac
- Apple Silicon (M1/M2/M3) fully supported

### Linux
See: `SETUP_INSTRUCTIONS_LINUX.md` (similar to macOS)
- Uses `python3` command
- Native Docker (not Docker Desktop)
- Package manager: apt/yum/dnf

## 🐳 Docker Compatibility

Docker Compose works identically on all platforms:

```bash
# Same commands work everywhere
docker-compose up -d postgres
docker-compose ps
docker-compose logs postgres
```

**Docker Images:**
- PostgreSQL 15 Alpine: Works on all platforms
- pgAdmin: Works on all platforms
- Backend/Frontend: Platform-agnostic

## 🐍 Python Compatibility

### Windows
```bash
python --version
python import_csv.py
pip install psycopg2-binary pandas
```

### macOS/Linux
```bash
python3 --version
python3 import_csv.py
pip3 install psycopg2-binary pandas
```

**Note:** The import script (`import_csv.py`) works identically on all platforms - only the command differs.

## 📁 File Path Examples

### Windows
```
C:\Users\username\projectsigma\server\database\data\universities.csv
```

### macOS
```
/Users/username/projectsigma/server/database/data/universities.csv
```

### Linux
```
/home/username/projectsigma/server/database/data/universities.csv
```

**In code:** Use relative paths (`server/database/data/`) - works everywhere!

## 🔧 Environment Variables

Same environment variables work on all platforms:

```bash
# Windows (PowerShell)
$env:POSTGRES_DB="university_recommender"

# macOS/Linux (bash/zsh)
export POSTGRES_DB="university_recommender"
```

Or use `.env` file (works identically on all platforms):
```
POSTGRES_DB=university_recommender
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

## 📝 CSV Files

CSV files are **completely cross-platform**:
- ✅ Same format on all platforms
- ✅ UTF-8 encoding (standard)
- ✅ Same import script works everywhere
- ⚠️ Line endings: Windows uses CRLF, macOS/Linux use LF (both work fine)

## 🚀 Quick Start Comparison

### Windows
```powershell
docker-compose up -d postgres
cd server\database
python import_csv.py
```

### macOS
```bash
docker-compose up -d postgres
cd server/database
python3 import_csv.py
```

### Linux
```bash
docker-compose up -d postgres
cd server/database
python3 import_csv.py
```

**Only difference:** `python` vs `python3` command!

## 🐛 Platform-Specific Issues

### Windows
- Docker Desktop uses WSL2 backend
- May need to enable virtualization in BIOS
- File path separators: `\` (but `/` also works)

### macOS
- Apple Silicon: ARM64 architecture (fully supported)
- May need to grant Terminal full disk access
- File path separators: `/`

### Linux
- Native Docker (no Docker Desktop needed)
- May need to add user to docker group: `sudo usermod -aG docker $USER`
- File path separators: `/`

## ✅ Testing Cross-Platform

To verify your setup works:

```bash
# 1. Check Docker
docker --version
docker-compose --version

# 2. Check Python
python --version  # Windows
python3 --version # macOS/Linux

# 3. Check database connection
docker-compose exec postgres pg_isready

# 4. Test import script
cd server/database
python import_csv.py --help  # Windows
python3 import_csv.py --help # macOS/Linux
```

## 📚 Documentation Files

- **Windows:** `SETUP_INSTRUCTIONS.md`
- **macOS:** `SETUP_INSTRUCTIONS_MAC.md`
- **Linux:** Similar to macOS (use `SETUP_INSTRUCTIONS_MAC.md`)

## 🎯 Recommendation

**For macOS users:** Follow `SETUP_INSTRUCTIONS_MAC.md` - it has macOS-specific notes and uses `python3` commands.

**For Windows users:** Follow `SETUP_INSTRUCTIONS.md` - uses `python` commands.

**For Linux users:** Follow `SETUP_INSTRUCTIONS_MAC.md` and replace macOS-specific notes with Linux equivalents.

## 💡 Pro Tips

1. **Use relative paths** in code - works everywhere
2. **Use `.env` files** for environment variables - cross-platform
3. **Docker Compose** abstracts platform differences
4. **Python scripts** work identically - only command differs
5. **CSV files** are universal - no platform-specific format

## ❓ FAQ

**Q: Can I develop on Windows and deploy on macOS/Linux?**
A: Yes! Docker Compose ensures consistency. Only development commands differ slightly.

**Q: Will CSV files work across platforms?**
A: Yes! CSV is a universal format. UTF-8 encoding works everywhere.

**Q: Do I need different Docker images for Apple Silicon?**
A: No! Docker handles architecture automatically. PostgreSQL images support all architectures.

**Q: Can team members use different platforms?**
A: Yes! The project is designed for cross-platform collaboration. Use Git to share code.

**Q: Which platform is recommended?**
A: All platforms work equally well. Choose based on your preference:
- Windows: Familiar, good IDE support
- macOS: Unix-based, great for development
- Linux: Native Docker, lightweight

