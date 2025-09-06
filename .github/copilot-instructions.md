# Today I Learned - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Repository Overview

Today I Learned (TIL) is a Python-based static site generator that converts Markdown files into a searchable SQLite database served via Datasette. The site displays technical learning notes organized by topic with full-text search capabilities.

**Architecture**: Markdown files → Python build script → SQLite database → Datasette web interface

## Working in Restricted Environments

### When pip Install Fails Completely
If you encounter persistent network timeouts or ReadTimeoutError:

1. **Verify the exact error**: 
   ```bash
   python3 build_database.py
   # Expected: ModuleNotFoundError: No module named 'bs4'
   ```

2. **Check available system resources**:
   ```bash
   which python3 sqlite3 docker git
   python3 --version  # Should show 3.12+
   docker --version   # Should show 28.0+
   sqlite3 --version  # Should show 3.45+
   ```

3. **Document the limitation**: 
   ```bash
   echo "Environment has network restrictions preventing pip installs"
   echo "Development requires Docker or alternative environment setup"
   ```

4. **Use alternative validation**:
   - Validate file structure manually: `ls -la *.py *.yml requirements.txt`
   - Check git functionality: `git log --oneline -5`
   - Verify Docker can start builds: `timeout 60s docker build --progress=plain --target builder .`

### Working Effectively

### Environment Setup
- Create Python virtual environment: `python3 -m venv venv`
- Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Install build dependencies: `pip install -r requirements.txt` -- may take 10-15 minutes with network delays. Set timeout to 20+ minutes.
- Install runtime dependencies only: `pip install -r requirements.web.txt` -- takes 2-3 minutes

### Core Build Process
- **NEVER CANCEL**: Build database: `python build_database.py` -- takes 15-30 seconds normally, up to 5 minutes if calling GitHub API heavily. Set timeout to 10+ minutes.
- Update README index: `python update_readme.py --rewrite` -- takes 2-3 seconds
- The build creates `tils.db` which contains all processed markdown content

### Running the Application
#### Local Development (Datasette)
- Start server: `datasette serve tils.db -m metadata.yml --template-dir templates` -- starts immediately
- Access at: `http://localhost:8001` (default port)
- Alternative port: add `--port 8000` to change port

#### Docker Build and Run
- **NEVER CANCEL**: Build image: `docker build -t til-site .` -- takes 15-25 minutes due to dependency installation and git operations. Set timeout to 45+ minutes.
- Run container: `docker run -p 8000:8000 til-site`
- Access at: `http://localhost:8000`

**CRITICAL BUILD TIMING**: Docker builds frequently fail due to network issues (certificate problems, timeouts). If Docker build fails, use local Python development instead.

## Validation

### Manual Testing Scenarios
After making changes, ALWAYS test these scenarios:
1. **Build validation**: Run `python build_database.py` and verify `tils.db` is created/updated
2. **Content rendering**: Start Datasette and verify markdown content displays correctly 
3. **Search functionality**: Test search with queries like "python", "authentication", etc.
4. **Topic navigation**: Click on topic headers and verify filtering works
5. **Individual post viewing**: Click on post titles and verify full content displays

### Build Artifact Validation
- Verify `tils.db` exists and is not empty: `ls -la *.db`
- Check database contents: `sqlite3 tils.db "SELECT count(*) FROM til"`
- Validate no missing dependencies: `python -c "import sqlite_utils, httpx, git, bs4"`

### Network Dependencies
- GitHub API calls for markdown rendering may fail due to rate limits
- Set `MARKDOWN_GITHUB_TOKEN` environment variable to avoid rate limits
- Docker builds may fail with certificate errors - this is a known environment limitation
- **pip install failures**: Environment may have severe network restrictions causing timeouts
- **Workaround**: If pip fails completely, development must use Docker or alternative environment

## Key Files and Locations

### Build Scripts
- `build_database.py` - Main build script that processes all .md files
- `update_readme.py` - Updates README.md with automatic index of posts
- `requirements.txt` - All dependencies including build tools
- `requirements.web.txt` - Runtime dependencies only (for Docker)

### Content Organization
- Markdown files organized in topic directories: `AWS/`, `python/`, `github-actions/`, etc.
- Each .md file becomes a database record with metadata
- README.md contains auto-generated index (do not edit manually)

### Configuration and Templates
- `metadata.yml` - Datasette configuration including site title, plugins
- `templates/` - Custom Jinja2 templates for the web interface
- `pages/` - Static pages served by Datasette
- `Dockerfile` - Multi-stage build for production deployment

### Database Schema
```sql
-- Table: til
CREATE TABLE til (
    path TEXT PRIMARY KEY,  -- e.g., "AWS_lightsale.md" 
    slug TEXT,              -- filename without extension
    topic TEXT,             -- directory name
    title TEXT,             -- extracted from first # heading
    url TEXT,               -- source file URL
    body TEXT,              -- raw markdown content
    html TEXT,              -- rendered HTML from GitHub API
    summary TEXT,           -- first paragraph text
    created TEXT,           -- ISO timestamp from git history
    created_utc TEXT,       -- UTC version of created
    updated TEXT,           -- ISO timestamp from git history  
    updated_utc TEXT        -- UTC version of updated
);
```

## Common Tasks

### Adding New Content
- Create a markdown file in an appropriate topic directory (e.g., `python/new_feature.md`)
- Start with a `#` heading for the title
- Run `python build_database.py` to process the new file
- Run `python update_readme.py --rewrite` to update the index
- Test locally with `datasette serve tils.db -m metadata.yml --template-dir templates`

### Modifying Build Process
- Changes to `build_database.py` require testing with: `python build_database.py && datasette serve tils.db -m metadata.yml --template-dir templates`
- Always backup `tils.db` before testing build changes
- Database schema changes require deleting `tils.db` and rebuilding

### Deployment
- Production uses Docker: `docker build -t til-site . && docker run -p 8000:8000 til-site`
- Environment variable `MARKDOWN_GITHUB_TOKEN` recommended for production to avoid API rate limits

## Known Issues and Limitations

### Network Connectivity
- **pip installs fail frequently** due to timeout issues - retry with longer timeouts
- **pip install may fail completely** with ReadTimeoutError - environment may have network restrictions
- **Docker builds fail** with certificate errors during git clone - use local development as fallback
- **GitHub API rate limits** affect markdown rendering - set `MARKDOWN_GITHUB_TOKEN`
- **Alternative**: If pip completely fails, use system packages where available or Docker-based development

### Environment-Specific Issues
- **Tested Python version**: 3.12.3 (confirmed working)
- **Tested Docker version**: 28.0.4 (confirmed working)
- **SQLite availability**: System sqlite3 3.45.1 available
- **Git functionality**: Confirmed working for commit history extraction

### Build Process Gotchas
- `build_database.py` calls GitHub API for each markdown file - can be slow with many files
- Build script has retry logic with 60-second delays for API failures
- Git history is required for timestamp extraction - shallow clones may cause issues
- Empty search queries can cause FTS errors (handled in templates)

### Development Environment
- Virtual environment required - system packages insufficient
- BeautifulSoup4, GitPython, sqlite-utils, httpx are critical dependencies
- Python 3.12+ recommended (tested version)
- No traditional unit tests - rely on manual validation scenarios

## File Outputs Reference

### Repository Root Contents
```
.dockerignore     - Docker build exclusions
.gitignore        - Git exclusions (includes *.db, .venv)  
Dockerfile        - Multi-stage build configuration
README.md         - Auto-generated index (do not edit manually)
build_database.py - Main build script
metadata.yml      - Datasette configuration
requirements.txt  - Build dependencies
requirements.web.txt - Runtime dependencies
update_readme.py  - README index generator
[topic-dirs]/     - Markdown content organized by topic
templates/        - Jinja2 templates for web interface
pages/            - Static pages for Datasette
```

### Generated Files (Not in Git)
```
tils.db          - SQLite database (generated by build_database.py)
venv/            - Python virtual environment
```

## Troubleshooting Commands

### Dependency Issues
```bash
# Full clean install
rm -rf venv tils.db
python3 -m venv venv
source venv/bin/activate  
pip install --upgrade pip
pip install -r requirements.txt  # May timeout - retry if needed

# If pip fails completely due to network issues:
echo "ERROR: ModuleNotFoundError: No module named 'bs4'"
echo "ERROR: ModuleNotFoundError: No module named 'sqlite_utils'"
echo "SOLUTION: Use Docker build or alternative environment"
```

### Docker-Only Development (Network Issues Fallback)
```bash
# Build with local context (avoids remote git clone issues)
docker build --build-arg REPO_URL=. -t til-site .
# Note: This modifies Dockerfile to use local context instead of remote git
```

### Build Issues  
```bash
# Reset database and rebuild
rm tils.db
python build_database.py
python update_readme.py --rewrite
```

### Runtime Issues
```bash
# Test database integrity
sqlite3 tils.db "SELECT count(*) FROM til"
sqlite3 tils.db ".schema til"

# Test server startup
datasette serve tils.db -m metadata.yml --template-dir templates
```

Always use these validated commands and timeouts when working in this repository. When in doubt, use the manual validation scenarios to verify your changes work correctly.