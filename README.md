# Study App for CyberSecurity Certification

[English](./README.md) | [Português (Portugal)](./README.pt.md)

## Overview

An interactive study app that simulates a real exam with 90 questions in 90 minutes based on official exam objectives.

Available locally or online. For local setup, follow the instructions below. Online version: https://miguke.github.io/CyberCertPrepExams/

## Features

- **Study Mode**: Practice by specific topics.
- **Exam Simulation**: Simulates a real exam with 90 questions in 90 minutes.
- **Immediate Feedback**: Detailed explanations for each answer.
- **Progress Tracking**: Real-time performance statistics.
- **Responsive UI**: Works on desktop, tablet, and mobile.
- **Results and Stats**: Review your results and statistics at the end of the exam simulation.

## Motivation

Learning today isn’t what it was 5–10 years ago. I believe interactive study is the best way to learn—especially with immediate feedback and the ability to practice anywhere, anytime. I built this app to let me practice questions aligned with the exam objectives and study whenever and wherever I want. And because it’s in the palm of your hand, it helps turn social media time into productive study time.

## How was the app built?

My background is not in programming. A long-time friend, João Guerreiro (@jqsguerreiro), introduced me to Windsurf. The entire development was done with the help of AI, with minimal manual intervention.

Questions were collected from publicly available sources, such as websites and PDFs found via Google using the dork "filetype:pdf" with targeted keywords.

After gathering the PDFs, I noticed that AI couldn’t process them or reliably extract the questions and explanations. Through Cascade AI, Python scripts were created to process the PDFs and extract that content; my role was mainly to guide the AI.

I also spent time testing, fixing, and tweaking those scripts so the parser could extract questions and explanations correctly. That’s when @jqsguerreiro suggested using MCP servers.

Now that the MCP server is running smoothly, the AI can process PDFs, without the need to create scripts, and extract questions and explanations reliably using official study materials—and, importantly, correct questions and explanations from some PDFs.

## Run Locally

1. **Prerequisites**:
   - Python 3.6 or higher
   - Modern browser (Chrome, Firefox, Edge, Safari)

2. **Install**:
   ```bash
   # Clone the repository
   git clone [REPOSITORY_URL]
   cd CyberCertPrepExams
   ```

3. **Start the development server**:
   ```bash
   python server.py
   ```
   This will start a local server at `http://localhost:8080` and automatically open your browser.

4. **Access the app**:
   - Open your browser and go to `http://localhost:8080`.
   - Select the course you want.
   - Choose between Study Mode or Exam Simulation.

### Customize the Theme

To customize colors, fonts, and layout, edit the CSS files in the `css/` folder.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to João Guerreiro (@jqsguerreiro) for recommending Windsurf and helping me understand GitHub and how Git works.
