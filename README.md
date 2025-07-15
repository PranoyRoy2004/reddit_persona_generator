# Reddit User Persona Generator

The Reddit User Persona Generator is a Python-based analytical tool designed to extract and analyze a Reddit user's publicly available content in order to construct a comprehensive user persona. By combining the Reddit API (via PRAW) with OpenAI's GPT language models, this project leverages natural language processing to infer key psychological, behavioral, and ideological traits—such as interests, values, tone of communication, personality traits, and potential political leanings.

This project is particularly useful for researchers, analysts, marketers, and developers interested in behavioral analysis, user modeling, and natural language understanding from social media data.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Use Cases](#use-cases)
- [Installation](#installation)
- [API Setup](#api-setup)
- [Usage](#usage)
- [Output Format](#output-format)
- [Limitations](#limitations)
- [License](#license)
- [Author](#author)

---

## Features

- Retrieves up to 50 recent Reddit posts and comments from any valid public Reddit profile.
- Performs natural language analysis using OpenAI's GPT models to identify key aspects of the user's online persona.
- Each inferred characteristic is supported with a direct citation from a Reddit post or comment, including full content and permalink.
- Output is saved as a formatted `.txt` file for reference or further processing.
- Simple and configurable design using a `.env` file for API credentials.
- Graceful error handling in case of API issues, rate limits, or invalid user input.

---

## Tech Stack

- **Python 3.10+**
- **PRAW** (Python Reddit API Wrapper) – for fetching Reddit data
- **OpenAI API** – for natural language understanding and persona generation
- **python-dotenv** – for managing API credentials securely

---

## Use Cases

This tool can be used in a variety of domains including but not limited to:

- **Behavioral Research:** Understand how users express themselves online and what it reveals about their personality and values.
- **Digital Marketing and Targeting:** Profile audiences based on their interests and tone to tailor communication strategies.
- **Academic Research:** Study language patterns, ideological expression, and community engagement on social platforms.
- **AI-Based User Modeling:** Develop training datasets or simulate personas for generative AI models or bots.
- **Content Personalization:** Understand user preferences for recommendation systems.

---

## Installation

To get started with the project, clone the repository and set up a virtual environment:

```bash
git clone https://github.com/your-username/reddit-persona-generator.git
cd reddit-persona-generator
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

