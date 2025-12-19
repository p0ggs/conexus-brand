# Conexus Brand Guidelines Web Application

A comprehensive web application for displaying Conexus brand guidelines and downloading brand assets.

## Features

- **Brand Colors**: Interactive Conexus color palette (Conexus Dark, Conexus Light, Ebony) with click-to-copy color codes, including CMYK values
- **Typography**: Complete typography system featuring Lato (primary), Crimson Pro (secondary), and Julius Sans One (logo only)
- **Logo Guidelines**: Display of all logo variations (colour, light, dark,) with spacing requirements
- **Identity Shapes**: Showcase of shapes from negative "X" spaces
- **Textures & Backgrounds**: Visual guide for texture and background usage
- **Asset Downloads**: Easy download functionality for all brand assets
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Setup

1. **Add Your Assets**: Place your Conexus brand assets in the `assets/` folder. 
   - See `ASSET_REQUIREMENTS.md` for a complete list of required assets
   - See `assets/README.md` for quick reference

2. **Assets Required**: The application expects the following key assets:
   - Logo files (light, dark, color, texture variants in PNG and SVG)
   - Identity shapes (from negative "X" spaces)
   - Texture files (gradient and abstract)
   - Asset packages (logo-pack.zip, etc.)

3. **Content is Pre-configured**: The application has been customised with:
   - Conexus brand colors (#3b306a, #151833, #dbebfa)
   - Typography system (Lato, Crimson Pro, Julius Sans One)
   - Logo specifications and spacing requirements
   - Texture and gradient guidelines

4. **Serve the Application**: 
   - For local development, you can use a simple HTTP server:
     ```bash
     # Using Python 3
     python3 -m http.server 8000
     
     # Using Node.js (if you have http-server installed)
     npx http-server
     
     # Using PHP
     php -S localhost:8000
     ```
   - Then open `http://localhost:8000` in your browser

## File Structure

```
.
├── index.html          # Main HTML file
├── styles.css          # Stylesheet
├── script.js           # JavaScript for downloads and interactions
├── assets/             # Brand assets folder
│   ├── README.md       # Assets documentation
│   └── [your assets]   # Brand files here
└── README.md           # This file
```

## Brand Specifications

### Colors
- **Conexus Dark**: #3b306a (RGB: 59, 48, 106, CMYK: 44, 55, 0, 58)
- **Ebony**: #151833 (RGB: 21, 24, 51, CMYK: 59, 53, 0, 80)
- **Conexus Light**: #dbebfa (RGB: 219, 235, 250, CMYK: 12, 6, 0, 2)
- **Gradient**: #bbc1f7 → #a4d2f2

### Typography
- **Primary**: Lato (Regular, Light, Semi-bold)
- **Secondary**: Crimson Pro (Regular, Semi-bold) - Use sparingly
- **Logo**: Julius Sans One (Regular) - Logo only, not for text

### Logo Requirements
- Minimum spacing: 3rem / 42px around logo in all directions
- Logo consists of "CONEXUS" (Julius Sans One) and "Wealth" (Crimson Pro)
- Extended "X" links the two words
- Shapes in negative "X" spaces for flexible use

## Customization

If you need to modify the application:
1. Colors: Update CSS variables in `styles.css` `:root` section
2. Typography: Fonts are loaded from Google Fonts in `index.html`
3. Assets: Add files to `assets/` folder and update `data-asset` attributes in `index.html`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Notes

- The download functionality works by creating temporary anchor elements
- For production, consider hosting assets on a CDN
- Ensure all asset files are properly optimized for web use
- The color code copy functionality uses the Clipboard API with fallback support

## Support

- Email hello@pog.gs with any queries or issues