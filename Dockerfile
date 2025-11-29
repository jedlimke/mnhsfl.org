FROM ruby:3.3-alpine
LABEL maintainer="MNHSFL"

WORKDIR /site

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    git \
    nodejs \
    npm

# Install bundler
RUN gem install bundler -v '~> 2.5'

# Copy Gemfile and install dependencies
COPY Gemfile* ./
RUN bundle install

# Copy the rest of the site
COPY . .

# Expose Jekyll default port
EXPOSE 4000

# Run Jekyll server
CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--port", "4000", "--livereload", "--force_polling"]
