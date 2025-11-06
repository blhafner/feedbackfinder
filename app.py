"""
Streamlit Web Version of Feedback Finder
This is a separate web version - the desktop app (win8.py) remains unchanged.
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time

# Page config MUST be first
st.set_page_config(
    page_title="Feedback Finder 🦊",
    page_icon="🦊",
    layout="wide"
)

# Consensys Brand Colors
CONSENSYS_COLORS = {
    'primary': '#6B46C1',      # Primary purple
    'primary_dark': '#553C9A', # Dark purple
    'primary_light': '#8B5CF6', # Light purple
    'secondary': '#EC4899',    # Accent pink
    'bg': '#F9FAFB',           # Light background
    'card': '#FFFFFF',          # White cards
    'text': '#1F2937',          # Dark text
    'text_secondary': '#6B7280', # Gray text
    'success': '#10B981',       # Green
    'warning': '#F59E0B',       # Orange
    'error': '#EF4444'          # Red
}

# Apply Consensys branding with dark mode support
# Read dark mode state (will be updated by toggle)
dark_mode = st.session_state.get('dark_mode', False)
bg_color = "#1E1E1E" if dark_mode else CONSENSYS_COLORS['bg']
text_color = "#E0E0E0" if dark_mode else CONSENSYS_COLORS['text']
card_bg = "#2D2D2D" if dark_mode else "rgba(255, 255, 255, 0.7)"
sidebar_bg = "#252525" if dark_mode else "rgba(255, 255, 255, 0.95)"
header_bg = "#252525" if dark_mode else "rgba(255, 255, 255, 0.9)"

st.markdown(f"""
<style>
    .stApp {{
        background: {bg_color};
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(107, 70, 193, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(236, 72, 153, 0.05) 0%, transparent 50%);
        color: {text_color};
    }}
    
    .main {{
        color: {text_color};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(107, 70, 193, 0.1);
        color: {text_color};
    }}
    
    [data-testid="stHeader"] {{
        background-color: {header_bg};
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(107, 70, 193, 0.1);
    }}
    
    .element-container {{
        background-color: {card_bg};
        backdrop-filter: blur(5px);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(107, 70, 193, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        color: {text_color};
    }}
    
    .element-container:hover {{
        background-color: {"#3D3D3D" if dark_mode else "rgba(255, 255, 255, 0.9)"};
        box-shadow: 0 8px 12px rgba(107, 70, 193, 0.1);
        transform: translateY(-2px);
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {CONSENSYS_COLORS['primary'] if not dark_mode else "#8B5CF6"} !important;
        text-shadow: 0 2px 4px rgba(107, 70, 193, 0.2);
    }}
    
    p, div, span, label {{
        color: {text_color} !important;
    }}
    
    .stSelectbox label, .stTextInput label, .stDateInput label {{
        color: {text_color} !important;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {CONSENSYS_COLORS['primary']}, {CONSENSYS_COLORS['primary_light']});
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(107, 70, 193, 0.3);
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, {CONSENSYS_COLORS['primary_dark']}, {CONSENSYS_COLORS['primary']});
        box-shadow: 0 6px 12px rgba(107, 70, 193, 0.4);
        transform: translateY(-2px);
    }}
    
    .metric-card {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {CONSENSYS_COLORS['primary']};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        color: {text_color};
    }}
    
    [data-testid="stDataFrame"] {{
        background-color: {card_bg};
        backdrop-filter: blur(10px);
        border-radius: 8px;
        border: 1px solid rgba(107, 70, 193, 0.1);
    }}
    
    .terminal-log {{
        background-color: {"#1a1a1a" if dark_mode else "#f5f5f5"};
        color: {"#d4d4d4" if dark_mode else "#1a1a1a"};
        font-family: 'Courier New', monospace;
        font-size: 11px;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid {"#333" if dark_mode else "#ddd"};
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        line-height: 1.5;
    }}
    
    .terminal-log::-webkit-scrollbar {{
        width: 8px;
    }}
    
    .terminal-log::-webkit-scrollbar-track {{
        background: {"#2a2a2a" if dark_mode else "#e0e0e0"};
    }}
    
    .terminal-log::-webkit-scrollbar-thumb {{
        background: {"#555" if dark_mode else "#999"};
        border-radius: 4px;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'admin_map' not in st.session_state:
    st.session_state.admin_map = {}
if 'team_map' not in st.session_state:
    st.session_state.team_map = {}
if 'team_admins_map' not in st.session_state:
    st.session_state.team_admins_map = {}
if 'final_report_data' not in st.session_state:
    st.session_state.final_report_data = []
if 'translations_cache' not in st.session_state:
    st.session_state.translations_cache = {}
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'terminal_log' not in st.session_state:
    st.session_state.terminal_log = []

def add_log(message, level="info"):
    """Add a log message to the log container"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.log_messages.append({
        "time": timestamp,
        "message": message,
        "level": level
    })
    # Keep only last 100 messages
    if len(st.session_state.log_messages) > 100:
        st.session_state.log_messages = st.session_state.log_messages[-100:]

def add_terminal_log(message, log_container=None):
    """Add a message to the terminal log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    st.session_state.terminal_log.append(log_line)
    # Keep only last 500 lines
    if len(st.session_state.terminal_log) > 500:
        st.session_state.terminal_log = st.session_state.terminal_log[-500:]
    
    # Update the log container if provided
    if log_container:
        log_text = "\n".join(st.session_state.terminal_log)
        log_container.markdown(f'<div class="terminal-log">{log_text}</div>', unsafe_allow_html=True)

def fetch_teams_and_admins(token, log_container=None):
    """Fetch teams and admins from Intercom API"""
    admin_map = {}
    team_map = {}
    team_admins_map = {}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    add_log("On the hunt for teammates...", "info")
    if log_container:
        add_terminal_log("🦊 On the hunt for teammates...", log_container)
    
    # Fetch teams
    try:
        teams_url = "https://api.intercom.io/teams"
        teams_response = requests.get(teams_url, headers=headers)
        teams_response.raise_for_status()
        teams_data = teams_response.json()
        for team in teams_data.get('teams', []):
            name = team.get('name', 'Unknown')
            team_id = team.get('id')
            if name and team_id:
                team_map[name] = str(team_id)
                team_admins_map[str(team_id)] = []
    except requests.exceptions.RequestException as e:
        add_log(f"Note: Couldn't sniff out teams (that's okay, we'll keep hunting): {e}", "warning")
        if log_container:
            add_terminal_log(f"🦊 Note: Couldn't sniff out teams (that's okay, we'll keep hunting): {e}", log_container)
    
    # Fetch admins
    url = "https://api.intercom.io/admins"
    params = {"page": 1}
    try:
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            for admin in data.get('admins', []):
                name = admin.get('name', 'Unknown')
                email = admin.get('email', '')
                admin_id = admin.get('id')
                admin_teams = admin.get('team_ids', [])
                admin_map[f"{name} ({email})"] = str(admin_id)
                
                # Map admin to teams
                for team_id in admin_teams:
                    team_id_str = str(team_id)
                    if team_id_str in team_admins_map:
                        team_admins_map[team_id_str].append(str(admin_id))
            if data.get('pages') and data['pages'].get('next'):
                params['page'] += 1
            else:
                break
        add_log(f"✅ Successfully loaded {len(admin_map)} active teammates.", "success")
        if team_map:
            add_log(f"✅ Successfully loaded {len(team_map)} teams.", "success")
        if len(admin_map) > 0:
            add_log("(Teammates Loaded)", "info")
        return admin_map, team_map, team_admins_map
    except requests.exceptions.RequestException as e:
        add_log(f"Oof! Failed to fetch teammates: {e}", "error")
        add_log("(Check your token - might need more permissions)", "warning")
        if log_container:
            add_terminal_log(f"🦊 ❌ Oof! Failed to fetch teammates: {e}", log_container)
            add_terminal_log("🦊 ⚠️ Check your token - might need more permissions", log_container)
        return None, None, None

def translate_if_non_english(text, log_container=None):
    """Translate text if not English"""
    if not text:
        return text
    try:
        if text in st.session_state.translations_cache:
            return st.session_state.translations_cache[text]
        translator = GoogleTranslator(source='auto', target='en')
        translated = translator.translate(text)
        if translated.lower() == text.lower():
            st.session_state.translations_cache[text] = text
            return text
        st.session_state.translations_cache[text] = translated
        if log_container:
            add_terminal_log(f"🦊 Translation: {translated[:60]}{'...' if len(translated) > 60 else ''}", log_container)
        return translated
    except Exception as e:
        if log_container:
            add_terminal_log(f"🦊 Translation error (no worries, using original): {e}", log_container)
        return text

def process_query_batch(intercom_url, intercom_headers, payload, batch_num, progress_bar=None, status_text=None, log_container=None):
    """Process a single batch query"""
    batch_results = []
    page = 1
    
    while True:
        try:
            if status_text:
                status_text.text(f"🦊 Batch {batch_num} - Fetching page {page}...")
            if log_container:
                add_terminal_log(f"🦊 Batch {batch_num} - Fetching page {page}...", log_container)
            
            response = requests.post(intercom_url, headers=intercom_headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            conversations = data.get("conversations", [])
            if not conversations:
                break
            
            if status_text:
                status_text.text(f"🦊 Batch {batch_num} - Processing {len(conversations)} conversations from page {page}...")
            if log_container:
                add_terminal_log(f"🦊 Batch {batch_num} - Processing {len(conversations)} conversations from page {page}...", log_container)
            
            for idx, convo in enumerate(conversations, 1):
                if (convo.get("conversation_rating") and convo["conversation_rating"].get("remark") is not None):
                    remark = convo['conversation_rating'].get('remark')
                    rating = convo['conversation_rating'].get('rating', 'N/A')
                    convo_id = convo.get('id', 'Unknown')
                    convo_date = convo.get('created_at', 0)
                    readable_date = datetime.fromtimestamp(convo_date).strftime('%Y-%m-%d %H:%M') if convo_date else 'N/A'
                    
                    if log_container:
                        add_terminal_log(f"  🦊 Batch {batch_num} - Conversation {idx}/{len(conversations)} (ID: {convo_id[:8]}...): Rating {rating}", log_container)
                    
                    translated_remark = translate_if_non_english(remark, log_container)
                    
                    report_item = {
                        "id": convo_id,
                        "rating": rating,
                        "date": convo_date,
                        "remark": remark
                    }
                    if translated_remark != remark:
                        report_item["translated_remark"] = translated_remark
                    batch_results.append(report_item)
            
            pages_data = data.get("pages", {})
            if pages_data.get("next"):
                next_cursor = pages_data["next"].get("starting_after")
                if next_cursor:
                    payload["pagination"] = {"per_page": 49, "starting_after": next_cursor}
                    page += 1
                else:
                    break
            else:
                break
        except requests.exceptions.RequestException as e:
            error_msg = f"🦊 Oof! INTERCOM API ERROR in batch {batch_num}: {e}"
            if log_container:
                add_terminal_log(f"❌ {error_msg}", log_container)
            if status_text:
                status_text.error(error_msg)
            break
    
    if log_container:
        add_terminal_log(f"✅ 🦊 Batch {batch_num} complete! Found {len(batch_results)} remarks. Nice catch!", log_container)
    return batch_results

def run_api_search(token, admin_id, start_date_str, end_date_str, team_id=None, admin_map=None, team_map=None, log_container=None):
    """Run the API search"""
    try:
        start_ts = str(int(datetime.strptime(start_date_str, "%Y-%m-%d").timestamp()))
        end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
        end_ts = str(int(end_date_dt.timestamp()))
    except Exception as e:
        error_msg = f"!!! Date conversion error: {e}"
        add_log(error_msg, "error")
        if log_container:
            add_terminal_log(f"❌ {error_msg}", log_container)
        return []
    
    intercom_url = "https://api.intercom.io/conversations/search"
    intercom_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    base_filters = [
        {"field": "created_at", "operator": ">", "value": start_ts},
        {"field": "created_at", "operator": "<", "value": end_ts},
        {"field": "conversation_rating.score", "operator": "IN", "value": [1, 2, 3, 4, 5]}
    ]
    
    # Build search info string
    search_info = []
    if team_id and team_map:
        team_name = [name for name, tid in team_map.items() if tid == team_id]
        search_info.append(f"team: {team_name[0] if team_name else team_id}")
    if admin_id and admin_map:
        admin_name = [name for name, aid in admin_map.items() if aid == admin_id]
        search_info.append(f"admin: {admin_name[0] if admin_name else admin_id}")
    search_str = ", ".join(search_info) if search_info else "all conversations"
    
    search_msg = f"🦊 On the hunt! Fetching remarks for {search_str} from {start_date_str} to {end_date_str}..."
    add_log(search_msg, "info")
    if log_container:
        add_terminal_log(search_msg, log_container)
    
    all_results = []
    
    # Handle team selection
    if team_id:
        team_admin_ids = st.session_state.team_admins_map.get(team_id, [])
        if not team_admin_ids:
            warning_msg = f"🦊 Hmm, no admins in this team? That's sus, fren. Can't hunt without targets!"
            add_log(warning_msg, "warning")
            if log_container:
                add_terminal_log(f"⚠️ {warning_msg}", log_container)
            return []
        
        if admin_id and admin_id in team_admin_ids:
            # Single admin in team
            admin_filter = {"field": "admin_assignee_id", "operator": "=", "value": admin_id}
            query_filters = base_filters + [admin_filter]
            query_operator = "AND"
        else:
            if admin_id:
                warning_msg = f"🦊 Oops! That admin isn't in this team. Hunting all team admins instead."
                add_log(warning_msg, "warning")
                if log_container:
                    add_terminal_log(f"⚠️ {warning_msg}", log_container)
            
            # Multiple admins - check if we need batching
            num_admins = len(team_admin_ids)
            MAX_OR_CONDITIONS = 15
            
            info_msg = f"🦊 Team has {num_admins} admins. Building the query..."
            add_log(info_msg, "info")
            if log_container:
                add_terminal_log(info_msg, log_container)
            
            if num_admins <= MAX_OR_CONDITIONS:
                admin_or_conditions = []
                for aid in team_admin_ids:
                    admin_or_conditions.append({"field": "admin_assignee_id", "operator": "=", "value": aid})
                query_filters = base_filters + [
                    {"operator": "OR", "value": admin_or_conditions}
                ]
                query_operator = "AND"
            else:
                # Batch processing
                batch_msg = f"🦊 Big team alert! Splitting {num_admins} admins into batches of {MAX_OR_CONDITIONS}..."
                add_log(batch_msg, "info")
                if log_container:
                    add_terminal_log(batch_msg, log_container)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(0, num_admins, MAX_OR_CONDITIONS):
                    batch = team_admin_ids[i:i + MAX_OR_CONDITIONS]
                    batch_num = i // MAX_OR_CONDITIONS + 1
                    
                    batch_info = f"🦊 Processing batch {batch_num} with {len(batch)} admins..."
                    add_log(batch_info, "info")
                    if log_container:
                        add_terminal_log(batch_info, log_container)
                    
                    admin_or_conditions = []
                    for aid in batch:
                        admin_or_conditions.append({"field": "admin_assignee_id", "operator": "=", "value": aid})
                    
                    payload = {
                        "query": {
                            "operator": "AND",
                            "value": base_filters + [{"operator": "OR", "value": admin_or_conditions}]
                        },
                        "pagination": {"per_page": 49}
                    }
                    
                    batch_results = process_query_batch(intercom_url, intercom_headers, payload, batch_num, progress_bar, status_text, log_container)
                    all_results.extend(batch_results)
                    progress_bar.progress(min((i + len(batch)) / num_admins, 1.0))
                
                progress_bar.empty()
                status_text.empty()
                
                complete_msg = f"\n🦊 Hunt complete! Found {len(all_results)} total remarks across all batches. That's a lot of feedback!"
                add_log(complete_msg, "success")
                if log_container:
                    add_terminal_log(f"✅ {complete_msg}", log_container)
                if len(all_results) > 50:
                    add_log("(That's a lot of feedback to hunt through!)", "info")
                    if log_container:
                        add_terminal_log("(That's a lot of feedback to hunt through!)", log_container)
                
                return all_results
    elif admin_id:
        # No team, just admin
        admin_filter = {"field": "admin_assignee_id", "operator": "=", "value": admin_id}
        query_filters = base_filters + [admin_filter]
        query_operator = "AND"
    else:
        # No filters
        query_filters = base_filters
        query_operator = "AND"
    
    # Single query
    payload = {
        "query": {
            "operator": query_operator,
            "value": query_filters
        },
        "pagination": {"per_page": 49}
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    page = 1
    total_convos = 0
    total_pages = 1
    is_first_page = True
    
    while True:
        try:
            page_msg = f"🦊 Fetching page {page}..."
            if log_container:
                add_terminal_log(page_msg, log_container)
            status_text.text(page_msg)
            
            response = requests.post(intercom_url, headers=intercom_headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            if is_first_page:
                total_convos = data.get('total_count', 0)
                total_pages = data.get('pages', {}).get('total_pages', 1)
                stats_msg = f"🦊 Nice! Found {total_convos} total conversations across {total_pages} pages. Time to dig in!"
                add_log(stats_msg, "success")
                if log_container:
                    add_terminal_log(f"✅ {stats_msg}", log_container)
                is_first_page = False
            
            conversations = data.get("conversations", [])
            if not conversations:
                no_more_msg = "🦊 No more conversations to hunt. We got 'em all!"
                add_log(no_more_msg, "info")
                if log_container:
                    add_terminal_log(no_more_msg, log_container)
                break
            
            process_msg = f"🦊 Processing {len(conversations)} conversations from page {page}..."
            if log_container:
                add_terminal_log(process_msg, log_container)
            status_text.text(process_msg)
            
            found_on_page = 0
            for idx, convo in enumerate(conversations, 1):
                convo_id = convo.get('id', 'Unknown')
                if (convo.get("conversation_rating") and convo["conversation_rating"].get("remark") is not None):
                    remark = convo['conversation_rating'].get('remark')
                    rating = convo['conversation_rating'].get('rating', 'N/A')
                    convo_date = convo.get('created_at', 0)
                    readable_date = datetime.fromtimestamp(convo_date).strftime('%Y-%m-%d %H:%M') if convo_date else 'N/A'
                    
                    if log_container:
                        add_terminal_log(f"  🦊 Conversation {idx}/{len(conversations)} (ID: {convo_id[:8]}...): Rating {rating}, Date: {readable_date}", log_container)
                        add_terminal_log(f"    Processing remark: {remark[:80]}{'...' if len(remark) > 80 else ''}", log_container)
                    
                    translated_remark = translate_if_non_english(remark, log_container)
                    
                    report_item = {
                        "id": convo_id,
                        "rating": rating,
                        "date": convo_date,
                        "remark": remark
                    }
                    if translated_remark != remark:
                        report_item["translated_remark"] = translated_remark
                    results.append(report_item)
                    found_on_page += 1
                else:
                    if log_container:
                        add_terminal_log(f"  ○ Conversation {idx}/{len(conversations)} (ID: {convo_id[:8]}...): No remark found (nothing to see here)", log_container)
            
            page_complete_msg = f"🦊 Page {page} complete! Found {found_on_page} remarks out of {len(conversations)} conversations. Nice catch!"
            add_log(page_complete_msg, "success")
            if log_container:
                add_terminal_log(f"✅ {page_complete_msg}", log_container)
            
            pages_data = data.get("pages", {})
            if pages_data.get("next"):
                next_cursor = pages_data["next"].get("starting_after")
                if next_cursor:
                    payload["pagination"] = {"per_page": 49, "starting_after": next_cursor}
                    page += 1
                    progress_bar.progress(min(page / total_pages, 1.0))
                else:
                    break
            else:
                break
        except requests.exceptions.RequestException as e:
            error_msg = f"🦊 Oof! INTERCOM API ERROR: {e}"
            add_log(error_msg, "error")
            if log_container:
                add_terminal_log(f"❌ {error_msg}", log_container)
            if status_text:
                status_text.error(error_msg)
            break
    
    progress_bar.empty()
    status_text.empty()
    
    if not results:
        no_results_msg = "🦊 No remarks found for this query. Maybe try a different date range?"
        add_log(no_results_msg, "warning")
        if log_container:
            add_terminal_log(f"⚠️ {no_results_msg}", log_container)
    else:
        complete_msg = f"\n🦊 Hunt complete! Found {len(results)} total remarks."
        add_log(complete_msg, "success")
        if log_container:
            add_terminal_log(f"✅ {complete_msg}", log_container)
        if len(results) > 100:
            add_log("(That's a lot of feedback to hunt through!)", "info")
            if log_container:
                add_terminal_log("(That's a lot of feedback to hunt through!)", log_container)
    
    return results

# UI
st.title("🦊 fdbckfndr")
st.markdown("### Quickly Hunt, Gather, and Analyze customer feedback from Intercom")

# Sidebar for credentials
with st.sidebar:
    st.header("Configuration")
    
    # Dark mode toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    intercom_token = st.text_input("Intercom Access Token", type="password")
    
    if st.button("Load Teammates & Teams"):
        if intercom_token:
            with st.spinner("🦊 Sniffing out teammates..."):
                admin_map, team_map, team_admins_map = fetch_teams_and_admins(intercom_token, None)
                if admin_map:
                    st.session_state.admin_map = admin_map
                    st.session_state.team_map = team_map
                    st.session_state.team_admins_map = team_admins_map
                    st.success(f"✅ Successfully loaded {len(admin_map)} teammates and {len(team_map)} teams")
                    if len(admin_map) > 0:
                        st.info("(Teammates Loaded)")
                else:
                    st.error("Failed to load teammates. Check your token.")
        else:
            st.warning("Please enter your Intercom token first.")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Filters")
    
    # Team selection
    team_options = ["All Teams"] + sorted(st.session_state.team_map.keys())
    selected_team = st.selectbox("Team (Optional)", team_options)
    team_id = None
    if selected_team and selected_team != "All Teams":
        team_id = st.session_state.team_map[selected_team]
    
    # Admin selection
    admin_options = ["(Optional - not needed if team selected)"] + sorted(st.session_state.admin_map.keys())
    selected_admin = st.selectbox("Admin Assignee", admin_options)
    admin_id = None
    if selected_admin and selected_admin != "(Optional - not needed if team selected)":
        if selected_admin in st.session_state.admin_map:
            admin_id = st.session_state.admin_map[selected_admin]
    
    # Date range
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col_date2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    if st.button("🔍 Fetch Report Data", type="primary", use_container_width=True):
        if not intercom_token:
            st.error("Please enter your Intercom token in the sidebar.")
        elif not team_id and not admin_id:
            st.error("Please select either a team or an admin (or both).")
        else:
            # Create terminal log container
            st.session_state.terminal_log = []  # Clear previous log
            with st.expander("📋 Activity Log", expanded=True):
                log_messages_container = st.empty()
                # Initialize empty terminal log display
                if not st.session_state.terminal_log:
                    log_messages_container.markdown('<div class="terminal-log">[Ready] Waiting for activity...</div>', unsafe_allow_html=True)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            results = run_api_search(
                intercom_token, 
                admin_id, 
                start_date_str, 
                end_date_str, 
                team_id,
                st.session_state.admin_map,
                st.session_state.team_map,
                log_messages_container
            )
            
            st.session_state.final_report_data = results
            
            if results:
                st.success(f"✅ Hunt complete! Found {len(results)} remarks. Nice work!")
            else:
                st.info("No remarks found for this query.")

with col2:
    st.subheader("Results")
    
    if st.session_state.final_report_data:
        st.metric("Total Remarks", len(st.session_state.final_report_data))
        
        # Display data
        df_data = []
        for item in st.session_state.final_report_data:
            readable_date = datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S') if item['date'] else 'N/A'
            row = {
                "ID": item['id'],
                "Rating": item['rating'],
                "Date": readable_date,
                "Remark": item['remark'],
                "Translated Remark": item.get('translated_remark', '')
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Export options
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"remarks-report-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_export2:
            if st.button("📋 Copy Remarks", use_container_width=True):
                remarks_text = "\n".join([item.get('translated_remark', item['remark']) for item in st.session_state.final_report_data])
                st.code(remarks_text, language=None)
                st.info("Click the code block above and copy the text")
                if len(st.session_state.final_report_data) > 20:
                    st.info("(That's a lot of data - hope your clipboard can handle it!)")
    else:
        st.info("Fetch data to see results here.")
