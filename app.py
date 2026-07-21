import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar
import json
import os

# Hier kommt das Styling hin:
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Seiteneinstellungen
st.set_page_config(page_title="Mein Task-Board", page_icon="☑️", layout="wide")

# --- PASSWORT-SCHUTZ ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "Berrysweety1!":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Bitte Passwort eingeben:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Bitte Passwort eingeben:", type="password", on_change=password_entered, key="password")
        st.error("😕 Das war leider das falsche Passwort")
        return False
    else:
        return True

if not check_password():
    st.stop()
# -----------------------

# Custom CSS für farbiges Design
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f8f5;
    }
    h1 {
        color: #1b4d3e !important;
        font-weight: 700;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e8f5e9;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #2c6e49;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2c6e49 !important;
        color: white !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #c8e6c9 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
        margin-bottom: 0px !important;
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-bottom: 0px !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #eaf4ed;
        border-right: 1px solid #c8e6c9;
    }
    .stButton>button {
        background-color: #2c6e49 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background-color: #1b4d3e !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "tasks.json"
TEMPLATES_FILE = "templates.json"

def format_date_german(date_str):
    if not date_str or date_str == "-":
        return "-"
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            y, m, d = parts
            return f"{d}.{m}.{y[2:]}"
    except:
        pass
    return date_str

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for idx, task in enumerate(data):
                if "order" not in task:
                    task["order"] = idx
            return data
    return [
        {"id": 1, "title": "Reli Ub Dekan", "prio": "Schule", "intervals": ["Einmalig"], "due_date": None, "completed": False, "completed_at": None, "order": 0},
        {"id": 2, "title": "Chicks Insta", "prio": "Prio 1 (Heute)", "intervals": ["Täglich"], "due_date": str(date.today()), "completed": False, "completed_at": None, "order": 1},
    ]

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_templates():
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"id": 1, "title": "Müll rausbringen", "prio": "Prio 2"},
        {"id": 2, "title": "Zimmer aufräumen", "prio": "Ohne Prio"}
    ]

def save_templates(data):
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()

if "templates" not in st.session_state:
    st.session_state.templates = load_templates()

if "editing_template" not in st.session_state:
    st.session_state.editing_template = None

if "deleting_template" not in st.session_state:
    st.session_state.deleting_template = None

if "deleting_task" not in st.session_state:
    st.session_state.deleting_task = None

if "action_history" not in st.session_state:
    st.session_state.action_history = {}

def calc_single_next_date(interval, ref_date):
    if interval == "Täglich":
        return ref_date + timedelta(days=1)
    elif interval == "Alle 2 Tage":
        return ref_date + timedelta(days=2)
    elif interval == "Alle 3 Tage":
        return ref_date + timedelta(days=3)
    elif interval == "Wöchentlich":
        return ref_date + timedelta(days=7)
    elif interval == "Alle 2 Wochen":
        return ref_date + timedelta(days=14)
    elif interval == "Alle 3 Wochen":
        return ref_date + timedelta(days=21)
    elif interval == "Monatlich":
        return ref_date + timedelta(days=30)
    elif interval == "Alle 3 Monate":
        return ref_date + timedelta(days=90)
    elif interval == "Halbjährlich":
        return ref_date + timedelta(days=182)
    elif interval == "Jährlich":
        return ref_date + timedelta(days=365)
    elif interval == "Immer zum 1. des Monats":
        next_m = ref_date.month + 1 if ref_date.month < 12 else 1
        next_y = ref_date.year if ref_date.month < 12 else ref_date.year + 1
        return date(next_y, next_m, 1)
    elif interval == "Immer zum letzten Tag des Monats":
        last_day_this = calendar.monthrange(ref_date.year, ref_date.month)[1]
        if ref_date.day < last_day_this:
            return date(ref_date.year, ref_date.month, last_day_this)
        else:
            next_m = ref_date.month + 1 if ref_date.month < 12 else 1
            next_y = ref_date.year if ref_date.month < 12 else ref_date.year + 1
            last_day_next = calendar.monthrange(next_y, next_m)[1]
            return date(next_y, next_m, last_day_next)
    elif interval.startswith("Jeden "):
        day_name = interval.replace("Jeden ", "")
        days_map = {"Montag": 0, "Dienstag": 1, "Mittwoch": 2, "Donnerstag": 3, "Freitag": 4, "Samstag": 5, "Sonntag": 6}
        target_day = days_map.get(day_name, 0)
        current_day = ref_date.weekday()
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        return ref_date + timedelta(days=days_ahead)
    return ref_date + timedelta(days=1)

def calculate_next_date_multi(intervals, base_date=None):
    ref_date = base_date if base_date else date.today()
    possible_dates = []
    for inter in intervals:
        possible_dates.append(calc_single_next_date(inter, ref_date))
    return min(possible_dates) if possible_dates else ref_date + timedelta(days=1)

def is_task_due_on_date(task, check_date):
    intervals = task.get("intervals", task.get("interval", ["Einmalig"]))
    if isinstance(intervals, str):
        intervals = [intervals]
    
    due_str = task.get("due_date")
    if not due_str:
        return False
    
    try:
        task_start = date.fromisoformat(due_str)
    except:
        return False

    if check_date < task_start:
        return False

    if "Einmalig" in intervals or "Keins" in intervals or len(intervals) == 0:
        return check_date == task_start
    
    curr = task_start
    while curr <= check_date:
        if curr == check_date:
            return True
        curr = calculate_next_date_multi(intervals, curr)
    return False

def complete_task(task_id):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            if task_id not in st.session_state.action_history:
                st.session_state.action_history[task_id] = []
            st.session_state.action_history[task_id].append(json.dumps(t))
            
            intervals = t.get("intervals", t.get("interval", ["Einmalig"]))
            if isinstance(intervals, str):
                intervals = [intervals]
            
            if "Einmalig" in intervals or "Keins" in intervals or len(intervals) == 0:
                t["completed"] = True
                t["completed_at"] = str(date.today())
            else:
                next_date = calculate_next_date_multi(intervals, date.today())
                t["due_date"] = str(next_date)
            
            save_data(st.session_state.tasks)
            st.rerun()

def undo_task(task_id):
    if task_id in st.session_state.action_history and st.session_state.action_history[task_id]:
        last_json = st.session_state.action_history[task_id].pop()
        old_task_data = json.loads(last_json)
        for idx, t in enumerate(st.session_state.tasks):
            if t["id"] == task_id:
                st.session_state.tasks[idx] = old_task_data
                save_data(st.session_state.tasks)
                st.rerun()

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    if task_id in st.session_state.action_history:
        del st.session_state.action_history[task_id]
    save_data(st.session_state.tasks)
    st.session_state.deleting_task = None
    st.rerun()

def move_task_order(task_id, direction, task_subset):
    task_subset_sorted = sorted(task_subset, key=lambda x: x.get("order", 0))
    ids = [t["id"] for t in task_subset_sorted]
    if task_id in ids:
        idx = ids.index(task_id)
        if direction == "up" and idx > 0:
            prev_id = ids[idx - 1]
            t_curr = next(t for t in st.session_state.tasks if t["id"] == task_id)
            t_prev = next(t for t in st.session_state.tasks if t["id"] == prev_id)
            t_curr["order"], t_prev["order"] = t_prev.get("order", 0), t_curr.get("order", 0)
        elif direction == "down" and idx < len(ids) - 1:
            next_id = ids[idx + 1]
            t_curr = next(t for t in st.session_state.tasks if t["id"] == task_id)
            t_next = next(t for t in st.session_state.tasks if t["id"] == next_id)
            t_curr["order"], t_next["order"] = t_next.get("order", 0), t_curr.get("order", 0)
        save_data(st.session_state.tasks)
        st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("## ➕ Neue Aufgabe")
    new_title = st.text_input("Titel der Aufgabe")
    new_prio = st.selectbox("Priorität / Kategorie", ["Prio 1 (Heute)", "Prio 2", "Prio 3", "Ohne Prio", "Schule"])
    
    interval_options = [
        "Einmalig", 
        "Täglich", "Alle 2 Tage", "Alle 3 Tage", 
        "Wöchentlich", "Alle 2 Wochen", "Alle 3 Wochen",
        "Monatlich", "Alle 3 Monate", "Halbjährlich", "Jährlich",
        "Immer zum 1. des Monats", "Immer zum letzten Tag des Monats",
        "Jeden Montag", "Jeden Dienstag", "Jeden Mittwoch", 
        "Jeden Donnerstag", "Jeden Freitag", "Jeden Samstag", "Jeden Sonntag"
    ]
    
    selected_intervals = st.multiselect("Intervall / Wiederholung(en)", interval_options, default=["Einmalig"])
    
    default_start_date = date.today()
    if selected_intervals and selected_intervals != ["Einmalig"] and selected_intervals != ["Keins"]:
        default_start_date = calculate_next_date_multi(selected_intervals, date.today() - timedelta(days=1))

    start_date = st.date_input("Startdatum / Erstmals fällig am", value=default_start_date)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Erstellen", use_container_width=True):
            if new_title:
                new_id = max([t["id"] for t in st.session_state.tasks], default=0) + 1
                max_order = max([t.get("order", 0) for t in st.session_state.tasks], default=0) + 1
                is_once = "Einmalig" in selected_intervals or len(selected_intervals) == 0
                due = str(start_date) if not is_once else (str(start_date) if start_date != date.today() else None)
                
                st.session_state.tasks.append({
                    "id": new_id,
                    "title": new_title,
                    "prio": new_prio,
                    "intervals": selected_intervals if selected_intervals else ["Einmalig"],
                    "due_date": due,
                    "completed": False,
                    "completed_at": None,
                    "order": max_order
                })
                save_data(st.session_state.tasks)
                st.success("Hinzugefügt!")
                st.rerun()
                
    with col_btn2:
        if st.button("📌 Als Vorlage", use_container_width=True):
            if new_title:
                new_v_id = max([v["id"] for v in st.session_state.templates], default=0) + 1
                st.session_state.templates.append({
                    "id": new_v_id,
                    "title": new_title,
                    "prio": new_prio
                })
                save_templates(st.session_state.templates)
                st.success("Als Vorlage gespeichert!")
                st.rerun()

    st.markdown("---")
    with st.expander("📋 Vorlagen-Manager (Öffnen)"):
        if st.session_state.templates:
            for templ in list(st.session_state.templates):
                with st.container(border=True):
                    if st.session_state.editing_template == templ["id"]:
                        t_edit_title = st.text_input("Titel", value=templ["title"], key=f"templ_title_{templ['id']}")
                        prio_list = ["Prio 1 (Heute)", "Prio 2", "Prio 3", "Ohne Prio", "Schule"]
                        current_prio_idx = prio_list.index(templ["prio"]) if templ["prio"] in prio_list else 0
                        t_edit_prio = st.selectbox("Prio", prio_list, index=current_prio_idx, key=f"templ_prio_{templ['id']}")
                        
                        col_s1, col_s2, col_s3 = st.columns(3)
                        if col_s1.button("💾", key=f"save_{templ['id']}", help="Speichern"):
                            templ["title"] = t_edit_title
                            templ["prio"] = t_edit_prio
                            save_templates(st.session_state.templates)
                            st.session_state.editing_template = None
                            st.rerun()
                        if col_s2.button("🗑️", key=f"del_{templ['id']}", help="Löschen"):
                            st.session_state.deleting_template = templ["id"]
                            st.session_state.editing_template = None
                            st.rerun()
                        if col_s3.button("❌", key=f"cancel_{templ['id']}", help="Abbrechen"):
                            st.session_state.editing_template = None
                            st.rerun()
                    
                    if st.session_state.deleting_template == templ["id"]:
                        st.markdown(f"<span style='color:red; font-size:0.85em;'>'**{templ['title']}**' endgültig löschen?</span>", unsafe_allow_html=True)
                        col_yd, col_nd = st.columns(2)
                        if col_yd.button("Ja, löschen", key=f"yes_del_templ_{templ['id']}"):
                            st.session_state.templates = [v for v in st.session_state.templates if v["id"] != templ["id"]]
                            save_templates(st.session_state.templates)
                            st.session_state.deleting_template = None
                            st.rerun()
                        if col_nd.button("Abbrechen", key=f"no_del_templ_{templ['id']}"):
                            st.session_state.deleting_template = None
                            st.rerun()
                    elif st.session_state.editing_template != templ["id"]:
                        col_title, col_add, col_edit = st.columns([5, 1, 1])
                        with col_title:
                            st.markdown(f"**{templ['title']}**  \n<span style='font-size:0.8em; color:gray;'>{templ['prio']}</span>", unsafe_allow_html=True)
                        
                        if col_add.button("➕", key=f"templ_add_{templ['id']}", help="Als Aufgabe starten"):
                            new_id = max([t["id"] for t in st.session_state.tasks], default=0) + 1
                            max_order = max([t.get("order", 0) for t in st.session_state.tasks], default=0) + 1
                            st.session_state.tasks.append({
                                "id": new_id,
                                "title": templ["title"],
                                "prio": templ["prio"],
                                "intervals": ["Einmalig"],
                                "due_date": str(date.today()),
                                "completed": False,
                                "completed_at": None,
                                "order": max_order
                            })
                            save_data(st.session_state.tasks)
                            st.rerun()
                            
                        if col_edit.button("⚙️", key=f"templ_edit_{templ['id']}", help="Vorlage bearbeiten"):
                            st.session_state.editing_template = templ["id"]
                            st.session_state.deleting_template = None
                            st.rerun()
        else:
            st.caption("Keine Vorlagen gespeichert.")

st.title("☑️ Mein Task-Board")

tab_board, tab_all, tab_cal = st.tabs(["📌 Tages-Board", "🗂️ Alle Aufgaben", "📅 Monatskalender"])

# TAB 1: BOARD
with tab_board:
    today_str = str(date.today())
    
    column_config = {
        "Prio 1 (Heute)": {"bg": "#ffebee", "color": "#c62828"},
        "Prio 2":         {"bg": "#fff3e0", "color": "#ef6c00"},
        "Prio 3":         {"bg": "#fffde7", "color": "#fbc02d"},
        "Ohne Prio":      {"bg": "#e8f5e9", "color": "#2c6e49"},
        "Schule":         {"bg": "#e3f2fd", "color": "#1565c0"}
    }
    
    categories = list(column_config.keys())
    cols = st.columns(len(categories))

    for i, cat in enumerate(categories):
        cfg = column_config[cat]
        with cols[i]:
            st.markdown(f"""
                <div style="background-color: {cfg['bg']}; padding: 10px; border-radius: 12px; border: 1px solid #e0e0e0;">
                    <h3 style="color: {cfg['color']} !important; margin-top: 5px; margin-bottom: 0px; font-size: 1.2em; text-align: center;">{cat}</h3>
            """, unsafe_allow_html=True)
            
            cat_tasks = [
                t for t in st.session_state.tasks 
                if t["prio"] == cat and not t.get("completed", False) and (t["due_date"] is None or t["due_date"] <= today_str)
            ]
            cat_tasks = sorted(cat_tasks, key=lambda x: x.get("order", 0))
            
            if cat_tasks:
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            
            for task in cat_tasks:
                with st.container(border=True):
                    c_title, c_up, c_down = st.columns([5, 0.6, 0.6])
                    with c_title:
                        st.markdown(f"<div style='font-weight:bold; margin-bottom: 2px;'>{task['title']}</div>", unsafe_allow_html=True)
                    with c_up:
                        if st.button("▲", key=f"up_board_{task['id']}", help="Nach oben verschieben"):
                            move_task_order(task["id"], "up", cat_tasks)
                    with c_down:
                        if st.button("▼", key=f"down_board_{task['id']}", help="Nach unten verschieben"):
                            move_task_order(task["id"], "down", cat_tasks)
                    
                    info_text = []
                    due_formatted = format_date_german(task.get('due_date'))
                    if due_formatted != "-":
                        info_text.append(f"📅 {due_formatted}")
                        
                    ints = task.get("intervals", [task.get("interval", "Einmalig")])
                    if ints != ["Einmalig"] and ints != ["Keins"] and len(ints) > 0:
                        info_text.append(f"🔄 {', '.join(ints)}")
                        
                    if info_text:
                        st.markdown(f"<div style='font-size:0.85em; color:gray; margin-bottom: 4px;'>{' | '.join(info_text)}</div>", unsafe_allow_html=True)
                    
                    if task["id"] in st.session_state.action_history and st.session_state.action_history[task["id"]]:
                        if st.button("↩️ Rückgängig", key=f"undo_board_{task['id']}", use_container_width=True):
                            undo_task(task["id"])

                    if st.button("✓ Done", key=f"btn_board_{task['id']}", use_container_width=True):
                        complete_task(task["id"])
            
            st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: ALLE AUFGABEN
with tab_all:
    st.subheader("🗂️ Gesamtübersicht")
    
    categories_list = ["Prio 1 (Heute)", "Prio 2", "Prio 3", "Ohne Prio", "Schule"]
    all_sorted_tasks = sorted(st.session_state.tasks, key=lambda x: x.get("order", 0))

    einmalig_tasks = []
    intervall_tasks = []
    for t in all_sorted_tasks:
        ints = t.get("intervals", ["Einmalig"])
        if isinstance(ints, str):
            ints = [ints]
        if "Einmalig" in ints or "Keins" in ints or len(ints) == 0:
            einmalig_tasks.append(t)
        else:
            intervall_tasks.append(t)

    def render_task_table(task_list, table_title):
        st.markdown(f"### {table_title}")
        if task_list:
            st.markdown("""
                <div style="background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #c8e6c9; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03); margin-bottom: 25px;">
            """, unsafe_allow_html=True)

            for t in task_list:
                cols = st.columns([0.6, 2.5, 1.8, 1.4, 0.6, 0.6])
                
                with cols[0]:
                    c_u, c_d = st.columns(2)
                    with c_u:
                        if st.button("▲", key=f"up_all_{t['id']}", help="Nach oben"):
                            move_task_order(t["id"], "up", task_list)
                    with c_d:
                        if st.button("▼", key=f"down_all_{t['id']}", help="Nach unten"):
                            move_task_order(t["id"], "down", task_list)
                with cols[1]:
                    st.markdown(f"**{t['title']}**")
                with cols[2]:
                    current_prio_idx = categories_list.index(t["prio"]) if t["prio"] in categories_list else 0
                    new_prio = st.selectbox("Prio", categories_list, index=current_prio_idx, key=f"prio_all_{t['id']}", label_visibility="collapsed")
                    if new_prio != t["prio"]:
                        t["prio"] = new_prio
                        save_data(st.session_state.tasks)
                        st.rerun()
                with cols[3]:
                    due_f = format_date_german(t.get('due_date'))
                    status = "✅ Erledigt" if t.get("completed", False) else f"Fällig: {due_f}"
                    st.caption(status)
                with cols[4]:
                    if st.button("🗑️", key=f"del_all_{t['id']}", help="Löschen"):
                        st.session_state.deleting_task = t["id"]
                        st.rerun()
                with cols[5]:
                    has_history = (t["id"] in st.session_state.action_history and len(st.session_state.action_history[t["id"]]) > 0)
                    if has_history:
                        if st.button("↩️", key=f"undo_all_{t['id']}", help="Rückgängig"):
                            undo_task(t["id"])
                    else:
                        st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                
                if st.session_state.deleting_task == t["id"]:
                    st.markdown(f"<div style='background-color: #ffebee; padding: 8px; border-radius: 6px; margin-top: 4px; margin-bottom: 6px; font-size: 0.9em; color: #c62828;'><strong>Sicher?</strong> Aufgabe wirklich endgültig löschen?</div>", unsafe_allow_html=True)
                    col_y, col_n = st.columns(2)
                    if col_y.button("Ja, endgültig löschen", key=f"confirm_del_{t['id']}"):
                        delete_task(t["id"])
                    if col_n.button("Abbrechen", key=f"cancel_del_{t['id']}"):
                        st.session_state.deleting_task = None
                        st.rerun()

                st.markdown("<hr style='margin: 6px 0px; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(f"Keine Aufgaben in '{table_title}' vorhanden.")

    col_left, col_right = st.columns(2)
    with col_left:
        render_task_table(einmalig_tasks, "📌 Einmalige Aufgaben")
    with col_right:
        render_task_table(intervall_tasks, "🔄 Wiederkehrende Aufgaben / Intervalle")

# TAB 3: MONATSKALENDER
with tab_cal:
    st.subheader("Kalenderübersicht")
    
    if "cal_month" not in st.session_state:
        st.session_state.cal_month = date.today().month
    if "cal_year" not in st.session_state:
        st.session_state.cal_year = date.today().year

    month_names = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

    c_prev, c_label, c_next = st.columns([1, 4, 1])
    with c_prev:
        if st.button("◀ Monat", use_container_width=True):
            if st.session_state.cal_month > 1:
                st.session_state.cal_month -= 1
            else:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            st.rerun()
    with c_label:
        st.markdown(f"<h3 style='text-align: center; margin-top: 0px;'>📅 {month_names[st.session_state.cal_month - 1]} {st.session_state.cal_year}</h3>", unsafe_allow_html=True)
    with c_next:
        if st.button("Monat ▶", use_container_width=True):
            if st.session_state.cal_month < 12:
                st.session_state.cal_month += 1
            else:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            st.rerun()

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(st.session_state.cal_year, st.session_state.cal_month)
    
    headers = st.columns(7)
    day_labels = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    for i, label in enumerate(day_labels):
        headers[i].markdown(f"**{label}**")
        
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day != 0:
                    current_date_obj = date(st.session_state.cal_year, st.session_state.cal_month, day)
                    current_date_str = current_date_obj.isoformat()
                    
                    day_tasks = [
                        t for t in st.session_state.tasks 
                        if not t.get("completed", False) and is_task_due_on_date(t, current_date_obj)
                    ]
                    
                    is_today = (current_date_obj == date.today())
                    
                    with st.container(border=True):
                        if is_today:
                            st.markdown(f"**🟢 {day}**")
                        else:
                            st.markdown(f"**{day}**")
                            
                        for t in day_tasks:
                            st.caption(f"• {t['title']}")
