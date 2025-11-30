# Minnesota High School Fencing League (MNHSFL) – Website Repository

Minnesota High School Fencing League (MNHSFL) website repo.

## Testing Locally

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

This uses Jekyll with the Minima v2.5.0 theme as a base.

For style changes, edit `_sass/custom.scss`. `assets/main.scss` is necessary for Jekyll & Minima to find our `custom.scss` file but nothing else.

# *NOTES FOR JED:*

TO BE HONEST, we don't need to require a specific CSV format for the results... we simply need to turn that CSV into a table as-is and attach front matter. That makes it less fragile to however the MNHSFL admin wants to provide the data. Maybe they'll want to include more info someday... or less... being content-agnostic will give them more flexibility.

Ideally we would attach some JS/sort crap to the table headers, though, and maybe some filtering library. jquery in 2025, anyone?

ALSO, maybe instead of filenames, we require the uploader to put files into folders instead--that'd allow us to handle more than one CSV or more than one MD... perhaps stitched together in some sort of alphabetical-order... it's a thought. We might be able to handle metadata in that file, too... I don't want things too complicated but I'm imagining a situation where they want more than one thing on a particular landing... but then again, they could use a blog post and stitch things together with that, instead... hmm. COMPLEXITY vs. USEFULNESS...