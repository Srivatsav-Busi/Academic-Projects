# UPSC AI Platform - Local Setup Guide

## Overview
UPSC AI Platform is a comprehensive mobile-first web application designed for UPSC (Union Public Service Commission) exam preparation. The platform features AI-powered test generation, mains answer evaluation, and detailed analytics.

## Features
- **Prelims Test Generator**: Create customized practice tests with real-time scoring
- **Mains Answer Evaluation**: AI-powered assessment of descriptive answers
- **Analytics Dashboard**: Track progress with interactive charts and insights
- **Mobile-Optimized**: Touch-friendly interface with responsive design

## File Structure
```
upsc-ai-platform/
├── index.html              # Main Prelims test generator page
├── mains-evaluation.html   # Mains answer evaluation interface
├── analytics.html          # Progress tracking and analytics
├── main.js                 # Core JavaScript functionality
├── resources/              # Images and media assets
│   ├── hero-study.png      # Hero image for main page
│   ├── ai-evaluation.png   # AI evaluation visualization
│   └── progress-journey.png # Progress tracking illustration
└── README.md              # This file
```

## Quick Start

### Method 1: Simple HTTP Server (Recommended)
1. **Extract the package**:
   ```bash
   tar -xzf upsc-ai-platform.tar.gz
   cd output
   ```

2. **Start a local HTTP server**:
   ```bash
   # Using Python 3
   python -m http.server 8000
   
   # Using Python 2
   python -m SimpleHTTPServer 8000
   
   # Using Node.js (if you have http-server installed)
   npx http-server
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

### Method 2: Direct File Opening
1. Extract the package as shown above
2. Open `index.html` directly in your web browser
3. Note: Some features may work better with a local server

### Method 3: Using Live Server (VS Code)
1. Install the "Live Server" extension in VS Code
2. Open the extracted folder in VS Code
3. Right-click on `index.html` and select "Open with Live Server"

## Browser Compatibility
- Chrome/Chromium 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Technical Requirements
- No additional dependencies required
- All external libraries (Tailwind CSS, Anime.js, ECharts) are loaded via CDN
- Works offline once loaded in browser
- Local storage for saving drafts and progress

## Navigation
- **Bottom Navigation Bar**: Switch between Prelims Test, Mains Evaluation, and Analytics
- **Responsive Design**: Optimized for mobile devices with touch gestures

## Features Guide

### Prelims Test Generator
1. Select subjects from the grid
2. Configure test settings (question count, difficulty, time limit)
3. Take the test with real-time timer
4. View immediate results and explanations

### Mains Evaluation
1. Select subject and year from dropdowns
2. Choose a question to answer
3. Write your answer in the rich text editor
4. Submit for AI-powered evaluation and feedback

### Analytics Dashboard
1. View overall performance statistics
2. Analyze subject-wise performance with interactive charts
3. Track study progress with the calendar
4. Monitor goals and achievements

## Customization
- Modify colors in CSS custom properties (`:root` variables)
- Add more questions to the `questionBank` object in `main.js`
- Customize feedback algorithms in the evaluation system
- Extend analytics with additional metrics

## Development Notes
- Built with vanilla JavaScript (no frameworks)
- Uses modern ES6+ features
- Mobile-first responsive design
- Progressive enhancement approach

## Troubleshooting
- **Images not loading**: Ensure you're using a local HTTP server
- **JavaScript errors**: Check browser console for specific error messages
- **Styling issues**: Verify all external CDN links are accessible

## Support
For issues or questions about the platform functionality, refer to the inline code comments or check the browser console for error messages.

---

**Note**: This is a demo platform with mock data and simulated AI evaluation for demonstration purposes.