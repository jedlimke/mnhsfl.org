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

# TODOS:

1. ~~Update theme to be snazzier~~ (In progress - custom hero, footer, header done)
2. Rewrite script to be easier to read/break it down following five-lines-of-code principles (I'm thinking folders now in case we have photos and such that need to be incorporated, too)
3. Test script on actual fencer data
4. Add blog post capabilities
5. Figure out images on posts
6. ~~Figure out site logo~~ (Done - using mnhsfl.svg and mnhsfl_block.svg)

## Future Homepage Enhancements

**Goal:** Make the homepage more dynamic and data-driven rather than static content.

**Planned Features:**
- **Schedule Integration:** Pull upcoming events from a CSV or iCal feed to display next tournaments/meets automatically
- **News/Articles Feed:** Use Jekyll's built-in blog functionality to show recent posts on homepage
- **Results Widget:** Dynamically show latest tournament results
- **Possibly more:** Consider what features would be useful

**Reference Site:** Check out [MSHSL.org](https://www.mshsl.org/) for inspiration on sports league website features and UX patterns.

**Note:** Don't implement yet - continue gathering requirements and understanding needs first.