import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from uuid import uuid4

# Page layout
st.set_page_config(page_title="InnerLevel | Gamification Tracker", layout="wide")

# Custom CSS function
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inline CSS for cases where you want to define styles directly
def set_page_style():
    st.markdown("""
    <style>
    /* Add any additional inline styles here */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Make the app header more prominent */
    .main h1 {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply custom styling
try:
    local_css("style.css")
except FileNotFoundError:
    st.warning("style.css file not found. Using default styling.")

# Apply inline styles
set_page_style()

# Custom UI Component Functions
def render_metric_card(title, value, delta=None, icon=None):
    """Renders a beautiful metric card with optional trend indicator"""
    # Create a container for the card
    with st.container():
        # Create the card content
        st.markdown(f'<div style="background-color: white; border-radius: 10px; padding: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 1rem;">', unsafe_allow_html=True)
        
        # Add icon and title
        if icon:
            st.markdown(f'<div style="color: #7f8c8d; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">{icon} {title}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color: #7f8c8d; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">{title}</div>', unsafe_allow_html=True)
        
        # Add the metric value
        st.metric(label="", value=value, delta=delta)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_task_card(task, due_date, priority, status, points, task_id):
    """Renders a beautiful task card with priority color coding"""
    priority_color = {
        "High": "#e74c3c",
        "Medium": "#f39c12",
        "Low": "#2ecc71"
    }.get(priority, "#7f8c8d")
    
    html = f"""
    <div id="task-{task_id}" style="background-color: white; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); border-left: 4px solid {priority_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-weight: bold; font-size: 1.1rem; color: #2c3e50;">{task}</div>
                <div style="color: #7f8c8d; font-size: 0.875rem; margin-top: 0.25rem;">
                    Due: {due_date} | Status: {status} | Points: {points}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    if not completed:
        col1, col2 = st.columns([1, 1])
        with col1:
            complete = st.button("Complete", key=f"complete_{task_id}")
        with col2:
            remove = st.button("Remove", key=f"remove_{task_id}")
        return complete, remove
    else:
        remove = st.button("Remove", key=f"remove_{task_id}")
        return False, remove

def render_reward_card(name, description, category, points_required, progress, reward_id):
    """Renders a beautiful reward card with progress bar"""
    progress_percentage = min(100, (progress / points_required) * 100)
    progress_color = "#2ecc71" if progress >= points_required else "#3498db"
    
    html = f"""
    <div style="background-color: white; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <div style="margin-bottom: 0.5rem;">
            <div style="font-weight: bold; font-size: 1.1rem; color: #2c3e50;">{name}</div>
            <div style="color: #7f8c8d; font-size: 0.875rem; margin-top: 0.25rem;">{description}</div>
        </div>
        <div style="margin-top: 0.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span style="color: #7f8c8d; font-size: 0.875rem;">Progress</span>
                <span style="color: #7f8c8d; font-size: 0.875rem;">{progress}/{points_required} points</span>
            </div>
            <div style="background-color: #ecf0f1; border-radius: 5px; height: 8px; overflow: hidden;">
                <div style="background-color: {progress_color}; width: {progress_percentage}%; height: 100%; transition: width 0.3s ease;"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_habit_button(habit_name, category, points, date):
    """Renders a clickable habit button for quick logging"""
    category_colors = {
        "Professional": "#3498db",
        "Personal": "#9b59b6"
    }
    
    color = category_colors.get(category, "#95a5a6")
    
    html = f"""
    <div style="display: inline-block; margin-right: 10px; margin-bottom: 10px;">
        <button style="background-color: {color}; color: white; border: none; border-radius: 20px; padding: 10px 20px; 
                      font-weight: 600; display: flex; align-items: center; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            {habit_name} <span style="margin-left: 8px; background-color: rgba(255,255,255,0.3); 
                                     padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;">
                         {points} pts
                         </span>
        </button>
    </div>
    """
    return html

# Function to add JavaScript animations
def add_animations():
    """Add JavaScript animations to the app"""
    js = """
    <script>
    // Animation for task completion
    function animateCompletion(elementId) {
        const element = document.getElementById(elementId);
        element.style.transition = "all 0.5s ease";
        element.style.transform = "scale(1.05)";
        element.style.boxShadow = "0 10px 20px rgba(0,0,0,0.2)";
        
        setTimeout(() => {
            element.style.transform = "scale(1)";
            element.style.opacity = "0.6";
            element.style.textDecoration = "line-through";
        }, 500);
    }
    
    // Confetti animation for achievements
    function showConfetti() {
        // Create canvas element
        const canvas = document.createElement('canvas');
        canvas.id = 'confetti-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.pointerEvents = 'none';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '9999';
        document.body.appendChild(canvas);
        
        // Initialize confetti
        const confetti = {
            maxCount: 100,
            speed: 2,
            frameInterval: 15,
            alpha: 1.0,
            particles: [],
            active: true,
            colors: [
                [85, 71, 106],
                [174, 61, 99],
                [219, 56, 83],
                [244, 92, 68],
                [248, 182, 70]
            ],
            context: canvas.getContext('2d'),
            width: window.innerWidth,
            height: window.innerHeight
        };
        
        // Initialize particles
        for (let i = 0; i < confetti.maxCount; i++) {
            confetti.particles.push({
                x: Math.random() * confetti.width,
                y: Math.random() * confetti.height - confetti.height,
                r: Math.random() * 4 + 1,
                d: Math.random() * 3 + 2,
                color: confetti.colors[Math.floor(Math.random() * confetti.colors.length)],
                tilt: Math.random() * 10 - 10,
                tiltAngle: Math.random() * 0.1 - 0.05,
                tiltAngleIncrement: Math.random() * 0.1 - 0.05
            });
        }
        
        // Animation loop
        function animate() {
            if (!confetti.active) {
                canvas.remove();
                return;
            }
            
            confetti.context.clearRect(0, 0, confetti.width, confetti.height);
            
            confetti.particles.forEach((particle, index) => {
                particle.y += particle.d;
                particle.tiltAngle += particle.tiltAngleIncrement;
                particle.tilt = Math.sin(particle.tiltAngle) * 15;
                
                if (particle.y > confetti.height) {
                    particle.y = -particle.r;
                    particle.x = Math.random() * confetti.width;
                }
                
                confetti.context.beginPath();
                confetti.context.lineWidth = particle.r;
                confetti.context.strokeStyle = `rgba(${particle.color[0]}, ${particle.color[1]}, ${particle.color[2]}, ${confetti.alpha})`;
                confetti.context.moveTo(particle.x + particle.tilt + particle.r, particle.y);
                confetti.context.lineTo(particle.x + particle.tilt, particle.y + particle.tilt);
                confetti.context.stroke();
            });
            
            requestAnimationFrame(animate);
        }
        
        // Start animation
        animate();
        
        // Stop after 3 seconds
        setTimeout(() => {
            confetti.active = false;
        }, 3000);
    }
    
    // Add hover effects to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        });
    });
    
    // Add click animations to buttons
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', () => {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 100);
        });
    });
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

# Files for data storage
TASKS_FILE = "task_log.csv"
HABITS_FILE = "habits.json"
TODO_FILE = "todo.csv"
REWARDS_FILE = "rewards.json"

# Initialize files if they don't exist
if not os.path.exists(TASKS_FILE):
    df_init = pd.DataFrame(columns=["Date", "Category", "Task", "Points", "Comment"])
    df_init.to_csv(TASKS_FILE, index=False)

if not os.path.exists(TODO_FILE):
    todo_init = pd.DataFrame(columns=["ID", "Task", "Due Date", "Priority", "Status", "Points"])
    todo_init.to_csv(TODO_FILE, index=False)

if not os.path.exists(HABITS_FILE):
    habits_init = {
        "habits": [
            {"name": "Daily Coding", "category": "Professional", "points": 5},
            {"name": "LinkedIn Post", "category": "Professional", "points": 10},
            {"name": "Job Application", "category": "Professional", "points": 15},
            {"name": "Exercise", "category": "Personal", "points": 5},
            {"name": "Reading", "category": "Personal", "points": 3}
        ]
    }
    with open(HABITS_FILE, "w") as f:
        json.dump(habits_init, f, indent=4)

# Initialize the rewards file
if not os.path.exists(REWARDS_FILE):
    rewards_init = {
        "rewards": [
            {"id": str(uuid4()), "name": "Coffee Shop Visit", "description": "Treat yourself to a nice coffee", "points_required": 50, "category": "Small Treat", "redeemed": False},
            {"id": str(uuid4()), "name": "Movie Night", "description": "Watch that movie you've been wanting to see", "points_required": 100, "category": "Entertainment", "redeemed": False},
            {"id": str(uuid4()), "name": "New Book", "description": "Buy that book from your wishlist", "points_required": 200, "category": "Learning", "redeemed": False}
        ],
        "redeemed_history": []
    }
    with open(REWARDS_FILE, "w") as f:
        json.dump(rewards_init, f, indent=4)

# Load existing data
tasks_df = pd.read_csv(TASKS_FILE)
todo_df = pd.read_csv(TODO_FILE)

with open(HABITS_FILE, "r") as f:
    habits_data = json.load(f)

# Sidebar navigation
st.sidebar.title("🎮 InnerLevel")
page = st.sidebar.radio("Navigation", [
    "🏠 Dashboard",
    "📝 Log Activity",
    "⚡ Manage Habits",
    "📋 To-Do List", 
    "🎁 Rewards",
    "📊 Analytics"
])

# Helper functions
def load_task_data():
    try:
        df = pd.read_csv("task_log.csv")
        required_columns = ["Date", "Category", "Task", "Points", "Comment"]
        if not all(col in df.columns for col in required_columns):
            st.error("Invalid CSV format: Missing required columns")
            return pd.DataFrame(columns=required_columns)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Category", "Task", "Points", "Comment"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["Date", "Category", "Task", "Points", "Comment"])

def load_data():
    """Reload all data sources"""
    tasks_df = pd.read_csv(TASKS_FILE)
    todo_df = pd.read_csv(TODO_FILE)
    with open(HABITS_FILE, "r") as f:
        habits_data = json.load(f)
    with open(REWARDS_FILE, "r") as f:
        rewards_data = json.load(f)
    return tasks_df, todo_df, habits_data, rewards_data

def calculate_available_points():
    """Calculate available points (total minus redeemed)"""
    tasks_df = pd.read_csv(TASKS_FILE)
    total_earned = tasks_df["Points"].sum() if not tasks_df.empty else 0
    
    with open(REWARDS_FILE, "r") as f:
        rewards_data = json.load(f)
    
    redeemed_points = sum(item["points_required"] for item in rewards_data["redeemed_history"])
    
    return total_earned - redeemed_points

# Add welcome message and explanation on Dashboard
if page == "🏠 Dashboard":
    st.title("🎯 Welcome to InnerLevel")
    
    # Add a hero section with a motivational quote
    st.markdown("""
    <div style="background: linear-gradient(to right, #3a7bd5, #00d2ff); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h2 style="color: white; margin-bottom: 10px;">Transform Your Learning Journey Into An Adventure</h2>
        <p style="color: white; font-style: italic;">
            "The secret of getting ahead is getting started. The secret of getting started is breaking your complex, 
            overwhelming tasks into small manageable tasks, and then starting on the first one."
            <br>— Mark Twain
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load the latest data
    tasks_df, todo_df, habits_data, rewards_data = load_data()
    
    # Calculate metrics
    total_points = tasks_df["Points"].sum() if not tasks_df.empty else 0
    available_points = calculate_available_points()
    
    if not tasks_df.empty:
        tasks_this_week = tasks_df[tasks_df["Date"] >= (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")]
        points_this_week = tasks_this_week["Points"].sum()
        
        # Get professional vs personal split
        category_split = tasks_df.groupby("Category")["Points"].sum()
        professional_points = category_split.get("Professional", 0)
        personal_points = category_split.get("Personal", 0)
        
        # Calculate streak
        tasks_df_sorted = tasks_df.sort_values(by="Date")
        dates = pd.to_datetime(tasks_df_sorted["Date"]).dt.date.unique()
        today = datetime.date.today()
        
        # Check if there's an entry for today
        current_streak = 0
        if today in dates:
            current_streak = 1
            prev_date = today - datetime.timedelta(days=1)
            while prev_date in dates:
                current_streak += 1
                prev_date = prev_date - datetime.timedelta(days=1)
    else:
        points_this_week = 0
        professional_points = 0
        personal_points = 0
        current_streak = 0
    
    # Display metrics in beautiful cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card("Total Points", total_points, None, "🏆")
    with col2:
        previous_week = 0
        if not tasks_df.empty:
            two_weeks_ago = tasks_df[(tasks_df["Date"] >= (datetime.datetime.now() - datetime.timedelta(days=14)).strftime("%Y-%m-%d")) & 
                                  (tasks_df["Date"] < (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))]
            previous_week = two_weeks_ago["Points"].sum()
        
        delta = 0
        if previous_week > 0:
            delta = ((points_this_week - previous_week) / previous_week) * 100
            delta = round(delta, 1)
        
        render_metric_card("Points This Week", points_this_week, delta, "📅")
    with col3:
        render_metric_card("Current Streak", f"{current_streak} days", None, "🔥")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display progress bars for categories
    st.markdown("### Points by Category")
    
    total_category_points = professional_points + personal_points
    prof_percentage = 0
    pers_percentage = 0
    
    if total_category_points > 0:
        prof_percentage = int((professional_points / total_category_points) * 100)
        pers_percentage = int((personal_points / total_category_points) * 100)
    
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>Professional</span>
            <span>{professional_points} points ({prof_percentage}%)</span>
        </div>
        <div style="width: 100%; background-color: #ecf0f1; border-radius: 10px; height: 10px;">
            <div style="width: {prof_percentage}%; background-color: #3498db; height: 10px; border-radius: 10px;"></div>
        </div>
    </div>
    
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>Personal</span>
            <span>{personal_points} points ({pers_percentage}%)</span>
        </div>
        <div style="width: 100%; background-color: #ecf0f1; border-radius: 10px; height: 10px;">
            <div style="width: {pers_percentage}%; background-color: #9b59b6; height: 10px; border-radius: 10px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create two columns for Recent Activities and Pending Tasks
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.markdown("""
        <div style="background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #3498db; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">
                📝 Recent Activities
            </h3>
        """, unsafe_allow_html=True)
        
        if not tasks_df.empty:
            st.markdown('<div style="height: 300px; overflow-y: auto;">', unsafe_allow_html=True)
            recent_activities = tasks_df.sort_values(by="Date", ascending=False).head(5)
            for _, activity in recent_activities.iterrows():
                category_class = "professional" if activity["Category"] == "Professional" else "personal"
                st.markdown(f"""
                <div style="margin-bottom: 10px; border-left: 3px solid {'#3498db' if category_class == 'professional' else '#9b59b6'}; padding-left: 10px;">
                    <div style="font-weight: bold;">{activity["Task"]}</div>
                    <div style="display: flex; justify-content: space-between; color: #7f8c8d; font-size: 0.8rem;">
                        <span>{activity["Date"]}</span>
                        <span style="background-color: {'#3498db' if category_class == 'professional' else '#9b59b6'}; 
                                     color: white; padding: 2px 8px; border-radius: 10px;">
                            +{activity["Points"]} pts
                        </span>
                    </div>
                    {f'<div style="font-style: italic; margin-top: 5px;">{activity["Comment"]}</div>' if activity["Comment"] else ''}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No activities logged yet. Start by adding some in the 'Log Activity' section!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with right_col:
        st.markdown("""
        <div style="background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #3498db; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">
                📋 Pending Tasks
            </h3>
        """, unsafe_allow_html=True)
        
        if not todo_df.empty:
            st.markdown('<div style="height: 300px; overflow-y: auto;">', unsafe_allow_html=True)
            pending_tasks = todo_df[todo_df["Status"] != "Completed"].sort_values(by="Priority", ascending=True).head(5)
            if not pending_tasks.empty:
                for _, task in pending_tasks.iterrows():
                    priority_color = "#e74c3c" if task["Priority"] == "High" else "#f39c12" if task["Priority"] == "Medium" else "#2ecc71"
                    st.markdown(f"""
                    <div style="margin-bottom: 10px; border-left: 3px solid {priority_color}; padding-left: 10px;">
                        <div style="font-weight: bold;">{task["Task"]}</div>
                        <div style="display: flex; justify-content: space-between; color: #7f8c8d; font-size: 0.8rem;">
                            <span>Due: {task["Due Date"]}</span>
                            <span style="background-color: {priority_color}; color: white; padding: 2px 8px; border-radius: 10px;">
                                {task["Priority"]}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No pending tasks! You're all caught up.")
        else:
            st.info("No to-do items yet. Add some in the 'To-Do List' section!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h3 style="color: #3498db; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">
            ⚡ Quick Actions
        </h3>
    """, unsafe_allow_html=True)
    
    quick_action_col1, quick_action_col2, quick_action_col3 = st.columns([1, 1, 1])
    
    with quick_action_col1:
        if st.button("➕ Log Activity", use_container_width=True):
            # Use session state to switch pages
            st.session_state.page = "📝 Log Activity"
            st.rerun()
    
    with quick_action_col2:
        if st.button("📋 Add Task", use_container_width=True):
            st.session_state.page = "📋 To-Do List"
            st.rerun()
    
    with quick_action_col3:
        if st.button("🎁 View Rewards", use_container_width=True):
            st.session_state.page = "🎁 Rewards"
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Add explanatory text for Log Activity
elif page == "📝 Log Activity":
    st.title("📝 Log Your Activity")
    st.markdown("""
    Track your progress by logging activities. Choose from your preset habits or create a custom entry.
    
    - **Quick Log**: Use your predefined habits for faster logging
    - **Custom Activity**: Log any one-time or unique activities
    """)
    
    tasks_df, todo_df, habits_data, rewards_data = load_data()
    
    # Create tabs for quick log vs. custom log
    log_tab1, log_tab2 = st.tabs(["Quick Log", "Custom Activity"])
    
    with log_tab1:
        st.subheader("Quick Log from Habits")
        
        with st.form(key="quick_log_form"):
            date = st.date_input("Date", datetime.date.today())
            
            # Group habits by category for the selectbox
            habits_by_category = {}
            for habit in habits_data["habits"]:
                category = habit["category"]
                if category not in habits_by_category:
                    habits_by_category[category] = []
                habits_by_category[category].append(f"{habit['name']} ({habit['points']} pts)")
            
            selected_category = st.selectbox("Category", list(habits_by_category.keys()))
            selected_habit_with_points = st.selectbox("Select Habit", habits_by_category[selected_category])
            
            # Extract habit name and points
            habit_name = selected_habit_with_points.split(" (")[0]
            habit_points = int(selected_habit_with_points.split("(")[1].split(" ")[0])
            
            comment = st.text_area("Comment (optional)", key="quick_comment")
            quick_submit = st.form_submit_button("Log Activity")
        
        if quick_submit:
            new_row = pd.DataFrame([[date.strftime("%Y-%m-%d"), selected_category, habit_name, habit_points, comment]],
                                   columns=["Date", "Category", "Task", "Points", "Comment"])
            updated_tasks_df = pd.concat([tasks_df, new_row], ignore_index=True)
            updated_tasks_df.to_csv(TASKS_FILE, index=False)
            st.success(f"✅ Activity logged: {habit_name} for {habit_points} points!")
            
            # Refresh data
            tasks_df = pd.read_csv(TASKS_FILE)
    
    with log_tab2:
        st.subheader("Log Custom Activity")
        
        with st.form(key="custom_log_form"):
            c_date = st.date_input("Date", datetime.date.today(), key="custom_date")
            c_category = st.selectbox("Category", ["Professional", "Personal"], key="custom_category")
            c_task = st.text_input("Activity Description", key="custom_task")
            c_points = st.number_input("Points", min_value=1, max_value=100, value=5, step=1, key="custom_points")
            c_comment = st.text_area("Comment (optional)", key="custom_comment")
            custom_submit = st.form_submit_button("Log Custom Activity")
        
        if custom_submit:
            if not c_task:
                st.error("Please enter an activity description.")
            else:
                new_row = pd.DataFrame([[c_date.strftime("%Y-%m-%d"), c_category, c_task, c_points, c_comment]],
                                       columns=["Date", "Category", "Task", "Points", "Comment"])
                updated_tasks_df = pd.concat([tasks_df, new_row], ignore_index=True)
                updated_tasks_df.to_csv(TASKS_FILE, index=False)
                st.success(f"✅ Custom activity logged: {c_task} for {c_points} points!")
                
                # Refresh data
                tasks_df = pd.read_csv(TASKS_FILE)
    
    # Activity History
    st.subheader("Activity History")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        category_options = ["All"] + list(tasks_df["Category"].unique()) if not tasks_df.empty else ["All"]
        filter_category = st.multiselect("Filter by Category", 
                                        options=category_options,
                                        default="All")
    with col2:
        date_range = st.date_input("Date Range",
                                  value=(datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()),
                                  max_value=datetime.date.today())
    
    # Apply filters
    filtered_df = tasks_df.copy()
    if filter_category and "All" not in filter_category:
        filtered_df = filtered_df[filtered_df["Category"].isin(filter_category)]

    if len(date_range) == 2 and not filtered_df.empty:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df["Date"] >= start_date.strftime("%Y-%m-%d")) & 
                                 (filtered_df["Date"] <= end_date.strftime("%Y-%m-%d"))]
    
    # Show filtered results
    if not filtered_df.empty:
        st.dataframe(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("No activities match your filter criteria.")

# Add explanatory text for Manage Habits
elif page == "⚡ Manage Habits":
    st.title("⚡ Manage Your Habits")
    st.markdown("""
    Create and manage your recurring activities. Good habits are the foundation of progress!
    
    💡 **Tip**: Start with 2-3 key habits and gradually add more as you build consistency.
    """)
    
    tasks_df, todo_df, habits_data, rewards_data = load_data()
    
    # Display existing habits
    st.subheader("Your Current Habits")
    
    # Create a DataFrame for better display
    habits_display_df = pd.DataFrame(habits_data["habits"])
    if not habits_display_df.empty:
        st.dataframe(habits_display_df, use_container_width=True)
    
    # Add new habit
    st.subheader("Add New Habit")
    with st.form(key="add_habit_form"):
        habit_name = st.text_input("Habit Name")
        habit_category = st.selectbox("Category", ["Professional", "Personal"])
        habit_points = st.number_input("Points", min_value=1, max_value=100, value=5, step=1)
        add_habit_submit = st.form_submit_button("Add Habit")
    
    if add_habit_submit:
        if not habit_name:
            st.error("Please enter a habit name.")
        else:
            new_habit = {
                "name": habit_name,
                "category": habit_category,
                "points": habit_points
            }
            habits_data["habits"].append(new_habit)
            
            with open(HABITS_FILE, "w") as f:
                json.dump(habits_data, f, indent=4)
            
            st.success(f"✅ New habit added: {habit_name}")
            
            # Refresh data
            with open(HABITS_FILE, "r") as f:
                habits_data = json.load(f)
    
    # Edit/Remove habits
    st.subheader("Edit or Remove Habits")
    
    if habits_data["habits"]:
        habit_to_edit = st.selectbox("Select Habit to Edit/Remove", 
                                   options=[f"{h['name']} ({h['category']}, {h['points']} pts)" for h in habits_data["habits"]])
        
        # Find the selected habit
        selected_index = -1
        for i, habit in enumerate(habits_data["habits"]):
            if f"{habit['name']} ({habit['category']}, {habit['points']} pts)" == habit_to_edit:
                selected_index = i
                break
        
        if selected_index >= 0:
            selected_habit = habits_data["habits"][selected_index]
            
            col1, col2 = st.columns(2)
            with col1:
                # Edit form
                with st.form(key="edit_habit_form"):
                    edit_name = st.text_input("Habit Name", value=selected_habit["name"])
                    edit_category = st.selectbox("Category", ["Professional", "Personal"], 
                                               index=0 if selected_habit["category"] == "Professional" else 1)
                    edit_points = st.number_input("Points", min_value=1, max_value=100, 
                                                value=selected_habit["points"], step=1)
                    update_habit = st.form_submit_button("Update Habit")
                
                if update_habit:
                    habits_data["habits"][selected_index] = {
                        "name": edit_name,
                        "category": edit_category,
                        "points": edit_points
                    }
                    
                    with open(HABITS_FILE, "w") as f:
                        json.dump(habits_data, f, indent=4)
                    
                    st.success("✅ Habit updated successfully!")
                    
                    # Refresh data
                    with open(HABITS_FILE, "r") as f:
                        habits_data = json.load(f)
            
            with col2:
                # Remove option
                st.write("Remove this habit")
                if st.button("Delete Habit", key="delete_habit"):
                    habits_data["habits"].pop(selected_index)
                    
                    with open(HABITS_FILE, "w") as f:
                        json.dump(habits_data, f, indent=4)
                    
                    st.success("✅ Habit removed successfully!")
                    
                    # Refresh data
                    with open(HABITS_FILE, "r") as f:
                        habits_data = json.load(f)

# Add explanatory text for To-Do List
elif page == "📋 To-Do List":
    st.title("📋 To-Do List")
    st.markdown("""
    Keep track of your tasks and earn points for completing them!
    
    🎯 **Priority Levels:**
    - 🔴 High: Important and urgent
    - 🟠 Medium: Important but not urgent
    - 🟢 Low: Nice to have
    """)
    
    tasks_df, todo_df, habits_data, rewards_data = load_data()
    
    # Create a new todo item
    st.subheader("Add New To-Do Item")
    with st.form(key="add_todo_form"):
        todo_task = st.text_input("Task Description")
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=1))
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        todo_points = st.number_input("Completion Points", min_value=1, max_value=100, value=10, step=1)
        add_todo_submit = st.form_submit_button("Add To-Do Item")
    
    if add_todo_submit:
        if not todo_task:
            st.error("Please enter a task description.")
        else:
            new_todo = pd.DataFrame([[str(uuid4()), todo_task, due_date.strftime("%Y-%m-%d"), priority, "Pending", todo_points]],
                                   columns=["ID", "Task", "Due Date", "Priority", "Status", "Points"])
            todo_df = pd.concat([todo_df, new_todo], ignore_index=True)
            todo_df.to_csv(TODO_FILE, index=False)
            st.success(f"✅ New to-do item added: {todo_task}")
            
            # Refresh data
            todo_df = pd.read_csv(TODO_FILE)
    
    # Display and manage todo items
    st.subheader("Your To-Do List")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "In Progress", "Completed"], index=0)
    with col2:
        priority_filter = st.multiselect("Priority", ["All", "High", "Medium", "Low"], default="All")
    
    # Apply filters
    filtered_todo = todo_df.copy()
    if status_filter != "All":
        filtered_todo = filtered_todo[filtered_todo["Status"] == status_filter]
    
    if priority_filter and "All" not in priority_filter:
        filtered_todo = filtered_todo[filtered_todo["Priority"].isin(priority_filter)]
    
    # Display filtered todo items
    if not filtered_todo.empty:
        for _, row in filtered_todo.sort_values(by=["Priority", "Due Date"]).iterrows():
            task_id = row["ID"]
            task = row["Task"]
            due_date = row["Due Date"]
            priority = row["Priority"]
            status = row["Status"]
            points = row["Points"]
            
            # Create color code based on priority
            priority_color = {
                "High": "🔴",
                "Medium": "🟠",
                "Low": "🟢"
            }
            
            # Create todo item card
            with st.container():
                col1, col2, col3 = st.columns([6, 2, 2])
                
                with col1:
                    st.markdown(f"""
                    <div id="task-{task_id}" style="margin-bottom: 10px; border-left: 3px solid {priority_color}; padding-left: 10px;">
                        <div style="font-weight: bold;">{task}</div>
                        <div style="display: flex; justify-content: space-between; color: #7f8c8d; font-size: 0.8rem;">
                            <span>Due: {due_date} | Status: {status} | Points: {points}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if status != "Completed":
                        if st.button("Mark Complete", key=f"complete_{task_id}"):
                            # Update status to completed
                            todo_df.loc[todo_df["ID"] == task_id, "Status"] = "Completed"
                            todo_df.to_csv(TODO_FILE, index=False)
                            
                            # Log the completed task as an activity
                            new_activity = pd.DataFrame([
                                [datetime.date.today().strftime("%Y-%m-%d"), 
                                 "Personal", 
                                 f"Completed: {task}", 
                                 points, 
                                 f"Completed to-do item: {task}"]
                            ], columns=["Date", "Category", "Task", "Points", "Comment"])
                            
                            tasks_df = pd.concat([tasks_df, new_activity], ignore_index=True)
                            tasks_df.to_csv(TASKS_FILE, index=False)
                            
                            # Add completion animation
                            st.markdown(f"""
                            <script>
                            animateCompletion('task-{task_id}');
                            showConfetti();
                            </script>
                            """, unsafe_allow_html=True)
                            
                            st.success(f"✅ Task completed: {task} (+{points} points)")
                            st.rerun()
                
                with col3:
                    if st.button("Remove", key=f"remove_{task_id}"):
                        todo_df = todo_df[todo_df["ID"] != task_id]
                        todo_df.to_csv(TODO_FILE, index=False)
                        st.success(f"✅ Task removed: {task}")
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No to-do items match your filter criteria.")

# Add explanatory text for Rewards
elif page == "🎁 Rewards":
    st.title("🎁 Rewards")
    st.markdown("""
    Turn your hard work into rewards! Create custom rewards or choose from presets.
    
    ⭐ **Tip**: Set up small rewards for short-term motivation and bigger ones for long-term goals.
    """)
    
    tasks_df, todo_df, habits_data, rewards_data = load_data()
    
    # Calculate available points
    available_points = calculate_available_points()
    
    # Create tabs for rewards management
    reward_tab1, reward_tab2, reward_tab3 = st.tabs(["Available Rewards", "Add New Reward", "Redemption History"])
    
    # Display current points
    st.metric("Available Points", available_points)

    with reward_tab1:
        # Get unredeemed rewards
        unredeemed_rewards = [r for r in rewards_data["rewards"] if not r["redeemed"]]
        
        if unredeemed_rewards:
            st.subheader("Available Rewards")
            
            # Create columns for rewards display
            cols = st.columns(3)
            col_index = 0
            
            for reward in unredeemed_rewards:
                with cols[col_index]:
                    with st.container():
                        st.markdown(f"### {reward['name']}")
                        st.write(f"*{reward['description']}*")
                        st.write(f"**Category:** {reward['category']}")
                        st.write(f"**Points Required:** {reward['points_required']}")
                        
                        # Add redeem button if user has enough points
                        if available_points >= reward['points_required']:
                            if st.button("Redeem Reward", key=f"redeem_{reward['id']}"):
                                # Add to redemption history
                                rewards_data["redeemed_history"].append({
                                    "id": reward["id"],
                                    "name": reward["name"],
                                    "points_cost": reward["points_required"],
                                    "redeemed_on": datetime.date.today().strftime("%Y-%m-%d")
                                })
                                
                                # Mark as redeemed
                                for r in rewards_data["rewards"]:
                                    if r["id"] == reward["id"]:
                                        r["redeemed"] = True
                                        break
                                
                                # Save updated rewards data
                                with open(REWARDS_FILE, "w") as f:
                                    json.dump(rewards_data, f, indent=4)
                                
                                # Show celebration animation
                                st.markdown("""
                                <script>
                                showConfetti();
                                </script>
                                """, unsafe_allow_html=True)
                                
                                st.success(f"✅ Reward redeemed: {reward['name']}")
                                st.rerun()
                        else:
                            st.warning(f"Need {reward['points_required'] - available_points} more points")
                
                # Update column index
                col_index = (col_index + 1) % 3
        else:
            st.info("No rewards available. Add some in the 'Add New Reward' tab!")
    
    with reward_tab2:
        st.subheader("Create a New Reward")
        
        with st.form("add_reward_form"):
            reward_name = st.text_input("Reward Name")
            reward_desc = st.text_area("Description")
            reward_points = st.number_input("Points Required", min_value=1, value=50, step=5)
            reward_category = st.selectbox("Category", [
                "Small Treat", "Entertainment", "Learning", "Self-Care", 
                "Gaming", "Shopping", "Social", "Excursion", "Lazy Day", "Custom"
            ])
            
            if reward_category == "Custom":
                custom_category = st.text_input("Enter Custom Category")
            
            submit_reward = st.form_submit_button("Add Reward")
        
        if submit_reward:
            if not reward_name:
                st.error("Please enter a reward name.")
            else:
                # Create new reward
                new_reward = {
                    "id": str(uuid4()),
                    "name": reward_name,
                    "description": reward_desc,
                    "points_required": reward_points,
                    "category": custom_category if reward_category == "Custom" else reward_category,
                    "redeemed": False
                }
                
                # Add to rewards list
                rewards_data["rewards"].append(new_reward)
                
                # Save updated rewards
                with open(REWARDS_FILE, "w") as f:
                    json.dump(rewards_data, f, indent=4)
                
                st.success(f"✅ New reward added: {reward_name}")
                
                # Refresh data
                with open(REWARDS_FILE, "r") as f:
                    rewards_data = json.load(f)
    
    with reward_tab3:
        st.subheader("Redemption History")
        
        if rewards_data["redeemed_history"]:
            # Convert to DataFrame for better display
            history_df = pd.DataFrame(rewards_data["redeemed_history"])
            history_df = history_df.rename(columns={
                "name": "Reward",
                "points_cost": "Points Cost",
                "redeemed_on": "Redeemed On"
            })
            
            st.dataframe(history_df[["Reward", "Points Cost", "Redeemed On"]].sort_values(
                by="Redeemed On", ascending=False), use_container_width=True)
        else:
            st.info("No rewards have been redeemed yet.")

# Add explanatory text for Analytics
elif page == "📊 Analytics":
    st.title("📊 Performance Analytics")
    st.markdown("""
    Visualize your progress and identify patterns in your activities.
    
    📈 **Track:**
    - Daily and weekly points
    - Most productive days
    - Category distribution
    - Activity streaks
    """)
    
    tasks_df, todo_df, habits_data, rewards_data = load_data()
    
    if not tasks_df.empty:
        # Convert Date to datetime
        tasks_df['Date'] = pd.to_datetime(tasks_df['Date'])
        
        # Create tabs for different analyses
        analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs(["Productivity Analysis", "Trends & Patterns", "Task Categories"])
        
        with analysis_tab1:
            st.subheader("Daily Productivity Analysis")
            
            # Points per day of week
            daily_points = tasks_df.groupby(tasks_df['Date'].dt.day_name())['Points'].agg(['sum', 'count'])
            daily_points = daily_points.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
            
            fig = px.bar(daily_points, 
                        y='sum',
                        title='Points Earned by Day of Week',
                        labels={'sum': 'Total Points', 'index': 'Day of Week'},
                        color='count',
                        color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
            
            # Most productive day
            most_productive = daily_points['sum'].idxmax()
            st.info(f"📌 Your most productive day is **{most_productive}** with {daily_points.loc[most_productive, 'sum']:.0f} total points!")
        
        with analysis_tab2:
            st.subheader("Trends & Patterns")
            
            # Time series of points
            daily_total = tasks_df.groupby('Date')['Points'].sum().reset_index()
            fig_trend = px.line(daily_total, 
                              x='Date', 
                              y='Points',
                              title='Points Earned Over Time')
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Rolling average
            rolling_avg = daily_total.set_index('Date')['Points'].rolling(window=7).mean()
            fig_rolling = px.line(rolling_avg,
                                title='7-Day Rolling Average of Points',
                                labels={'value': 'Points (7-day avg)'})
            st.plotly_chart(fig_rolling, use_container_width=True)
            
            # Streak analysis
            active_days = tasks_df['Date'].dt.date.nunique()
            total_days = (tasks_df['Date'].max() - tasks_df['Date'].min()).days + 1
            activity_rate = (active_days / total_days) * 100
            
            st.metric("Activity Rate", f"{activity_rate:.1f}%", 
                     help="Percentage of days with logged activities")
        
        with analysis_tab3:
            st.subheader("Task Categories Analysis")
            
            # Category distribution
            category_stats = tasks_df.groupby('Category').agg({
                'Points': ['sum', 'mean', 'count']
            }).round(2)
            
            category_stats.columns = ['Total Points', 'Avg Points', 'Number of Tasks']
            st.dataframe(category_stats)
            
            # Category pie chart
            fig_pie = px.pie(tasks_df, 
                           values='Points', 
                           names='Category',
                           title='Distribution of Points by Category')
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Task frequency analysis
            st.subheader("Most Common Tasks")
            task_freq = tasks_df['Task'].value_counts().head(10)
            fig_tasks = px.bar(task_freq,
                             title='Top 10 Most Frequent Tasks',
                             labels={'value': 'Count', 'index': 'Task'})
            st.plotly_chart(fig_tasks, use_container_width=True)
            
    else:
        st.info("Start logging activities to see your analytics!")

# Update the footer with a more engaging message
st.sidebar.markdown("---")
st.sidebar.caption("🎮 InnerLevel - Gamify Your Growth")
st.sidebar.caption("🌱 Making personal development fun and rewarding")
st.sidebar.caption("© 2025 Gabriel Felipe Fernandes Pinheiro")

if 'page' not in st.session_state:
    st.session_state.page = "🏠 Dashboard"

# Add animations at app startup
add_animations()