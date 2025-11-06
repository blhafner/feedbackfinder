# Web Version Setup

The web version is in `app.py` and uses Streamlit. It's completely separate from the desktop app (`win8.py`).

## Quick Start

1. Install Streamlit:
```bash
pip install streamlit pandas
```

2. Run the web app:
```bash
streamlit run app.py
```

3. Open your browser to the URL shown (usually http://localhost:8501)

## Deploy to Web

### Option 1: Streamlit Cloud (Free)
1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Select `app.py` as the main file
5. Deploy!

### Option 2: Heroku
1. Create a `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Deploy using Heroku CLI

### Option 3: Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Notes
- The web version reuses the same API logic as the desktop app
- No changes were made to `win8.py` - it still works perfectly
- Both versions can coexist

