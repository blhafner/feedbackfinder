# Feedback Finder 🦊

A Python desktop application for fetching and analyzing customer feedback from Intercom conversations.

Try it here: https://fdbkfndr.streamlit.app/

## Features

- 🔍 Search feedback by team or individual admin
- 📅 Filter by date range with modern calendar pickers
- 🌐 Automatic translation of non-English remarks
- 📊 Export results to CSV
- 🤖 AI-powered sentiment analysis (optional)
- 📋 Copy remarks to clipboard for easy sharing

## Requirements

- Python 3.8+
- Intercom API access token
- OpenAI API key (optional, for AI analysis)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/feedbackfindr.git
cd feedbackfindr
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python win8.py
```

Or use the provided script:
```bash
chmod +x run.sh
./run.sh
```

2. Enter your Intercom access token
3. Click "Load Teammates" to fetch available teams and admins
4. Select a team or admin (or both)
5. Choose your date range
6. Click "Fetch Report Data" to start the search
7. Export results to CSV or copy to clipboard

## Dependencies

- `tkinter` - GUI framework (usually included with Python)
- `requests` - HTTP library for API calls
- `deep-translator` - Translation service
- `openai` - AI analysis (optional)

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

