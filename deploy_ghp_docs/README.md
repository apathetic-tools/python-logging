# GitHub Pages Documentation

This directory contains the Jekyll documentation site for Apathetic Python Logger, designed to be deployed to GitHub Pages.

## Local Development

To preview the documentation locally:

1. Install Jekyll and dependencies:
   ```bash
   bundle install
   ```

2. Run the Jekyll server:
   ```bash
   bundle exec jekyll serve
   ```

3. Open your browser to `http://localhost:4000`

## Deployment

GitHub Pages will automatically build and deploy this site when:
- Changes are pushed to the `main` branch (if Pages is configured to use `main` branch)
- Changes are pushed to the `gh-pages` branch (if Pages is configured to use `gh-pages` branch)

The site will be available at:
- `https://apathetic-tools.github.io/python-logs/` (if repository is `python-logs`)

## Configuration

The site configuration is in `_config.yml`. Key settings:
- `baseurl`: Set to `/python-logs` (or your repository name)
- `url`: Set to `https://apathetic-tools.github.io`
- `theme`: Uses the `minima` theme (GitHub Pages default)

## Structure

- `index.md` - Homepage
- `installation.md` - Installation guide
- `quickstart.md` - Quick start guide
- `api.md` - Complete API reference
- `examples.md` - Usage examples
- `contributing.md` - Contributing guide

## Notes

- All markdown files use Jekyll front matter with `layout: default`
- Links use Jekyll's `relative_url` filter for proper GitHub Pages URLs
- The site uses the `minima` theme which is supported by GitHub Pages

