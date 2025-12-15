# Minnesota High School Fencing League (MNHSFL) – Website Repository

Minnesota High School Fencing League (MNHSFL) website repo.

This is a static site built with Jekyll and deployed to GitHub Pages. During the deployment, the site <insert the magic that happens here at a high level--what they care about is the fact that fencing results get added as posts, that they themselves can create posts by putting them in _posts, etc.>

<list prerequsites and where to get them (they need git, they need docker, they should get vscode IMO)>

<Detail how to create a new post and the naming convention thereof (and frontmatter needs for the date (datetime is allowed, show format simply but accurately)).>

<Detail what's needed for a fencing result and how it can be done with examples (with and without a md, where to put them, etc.)>

<Now Detail the basics of version control with git, ettiquette, etc. Throw in tidbits on branches, PRs, etc. and link them where they can learn more. (perhaps this: https://github.blog/developer-skills/github/beginners-guide-to-github-creating-a-pull-request/) Relate this to what they're doing.>

## Viewing the site locally

To preview the GitHub Pages site locally using Docker:

1. Build the Docker image:
   ```sh
   docker-compose build
   ```
2. Start the Jekyll server:
   ```sh
   docker-compose up
   ```
3. Visit [http://localhost:4000](http://localhost:4000) in your browser.

## Development Notes

### CI/CD

Tests run automatically on GitHub Actions as part of the deployment workflow:
- **Test job** runs first with pytest validation
- **Build job** only runs if tests pass
- **Deploy job** only runs if build succeeds

This ensures broken code never gets deployed to production.

Workflow triggers:
- On push to `master`
- Manual workflow dispatch

See `.github/workflows/jekyll-gh-pages.yml` (integrated test + build + deploy)
- Manual trigger available

See `.github/workflows/test-results-generator.yml`

#### Fencing Results Converter while developing

```sh
_tests/<we should have a script to do this that also uses that python dockerfile or something very similar just to make it so we again don't need python to convert csvs and md's we're actually using for the real site while updating it locally>
```

#### Testing the Fencing Results Converter script

```sh
_tests/run-tests.sh
```

#### <other stuff I'm forgetting>

<Probably a nice mermaid syntax flowchart of what happens when the site gets pushed up to `master`>