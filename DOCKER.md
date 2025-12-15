# Running MNHSFL Website Locally with Docker

This document explains how to run the MNHSFL website locally using Docker, which provides an environment that closely matches GitHub Pages.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

1. **Build and start the site:**
   ```bash
   docker-compose up --build
   ```

2. **View the site:**
   Open your browser to [http://localhost:4000](http://localhost:4000)

3. **Stop the site:**
   Press `Ctrl+C` in the terminal, or run:
   ```bash
   docker-compose down
   ```

## Development Workflow

### First Time Setup

```bash
# Build the Docker image
docker-compose build

# Start the Jekyll server
docker-compose up
```

### Daily Development

```bash
# Start the server (rebuilds if needed)
docker-compose up

# Or run in background
docker-compose up -d

# View logs if running in background
docker-compose logs -f
```

### Making Changes

- Edit files normally on your local machine
- Changes are automatically detected and the site rebuilds
- LiveReload is enabled - your browser will refresh automatically
- Python scripts must be run manually if you add new results:
  ```bash
  python _scripts/convert_fencing_results.py
  ```

### Cleaning Up

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes (clean slate)
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up
```

## Troubleshooting

### Port 4000 is already in use
```bash
# Find what's using port 4000
lsof -i :4000

# Kill the process or change the port in docker-compose.yml
```

### Changes not appearing
```bash
# Rebuild the container
docker-compose down
docker-compose up --build
```

### Bundle install errors
```bash
# Remove the volume and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## What's Configured

- **Ruby version**: 3.3 (Alpine Linux)
- **Jekyll version**: 3.10.0 (via github-pages gem)
- **GitHub Pages gem**: v232 (matches production)
- **LiveReload**: Enabled on port 35729
- **File watching**: Enabled with polling for Docker compatibility

## Differences from GitHub Pages

While this setup closely mirrors GitHub Pages, there are minor differences:

1. **Plugins**: GitHub Pages has some restrictions on plugins
2. **Build environment**: GitHub uses Ubuntu, we use Alpine for efficiency
3. **Remote themes**: May need internet connection to fetch during build

## Accessing the Container

If you need to debug or run commands inside the container:

```bash
# Get a shell in the running container
docker-compose exec jekyll sh

# Run bundle commands
docker-compose exec jekyll bundle update

# Check Jekyll version
docker-compose exec jekyll bundle exec jekyll --version
```

## Performance Tips

- The `bundle_cache` volume speeds up subsequent builds
- LiveReload uses polling which is Docker-friendly but slightly slower
- On macOS, consider using `:delegated` mount option for better performance
