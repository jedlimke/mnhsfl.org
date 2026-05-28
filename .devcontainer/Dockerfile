FROM mcr.microsoft.com/devcontainers/ruby:3.3

# Install inotify-tools so the fencing-results watcher works out of the box.
RUN apt-get update && apt-get install -y inotify-tools && rm -rf /var/lib/apt/lists/*
