import streamlit as st
import json
import os
from datetime import datetime

# File to store workout data
WORKOUT_FILE = "workouts.json"

# Load workout data from file
def load_workouts():
    if os.path.exists(WORKOUT_FILE):
        with open(WORKOUT_FILE, "r") as f:
            return json.load(f)
    return {}

# Save workout data to file
def save_workouts(workouts):
    with open(WORKOUT_FILE, "w") as f:
        json.dump(workouts, f, indent=4)

# Initialize session state
if "workouts" not in st.session_state:
    st.session_state.workouts = load_workouts()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home Dashboard", "Create Workout", "Track Workout", "Edit/Delete Workout"])

# Home Dashboard
if page == "Home Dashboard":
    st.title("🏋️ Workout Dashboard")
    
    # Stats
    total_workouts = len(st.session_state.workouts)
    total_exercises = sum(len(workout) for workout in st.session_state.workouts.values())
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Workouts", total_workouts)
    with col2:
        st.metric("Total Exercises", total_exercises)
    
    # Recent Workouts
    st.subheader("Recent Workouts")
    if st.session_state.workouts:
        for workout_name in list(st.session_state.workouts.keys())[-3:]:
            st.write(f"🏋️ {workout_name}")
    else:
        st.write("No workouts yet!")
    
    # Quick Actions
    st.subheader("Quick Actions")
    if st.button("Create New Workout"):
        st.session_state.page = "Create Workout"
    
# Create Workout Page
elif page == "Create Workout":
    st.title("Create New Workout")
    
    workout_name = st.text_input("Workout Name")
    
    if "exercises" not in st.session_state:
        st.session_state.exercises = []
    
    with st.form("exercise_form"):
        ex_name = st.text_input("Exercise Name")
        sets = st.number_input("Sets", min_value=1, value=3)
        reps = st.number_input("Reps", min_value=1, value=10)
        
        if st.form_submit_button("Add Exercise"):
            st.session_state.exercises.append({
                "name": ex_name,
                "sets": sets,
                "reps": reps,
                "tracking_history": []
            })
            st.success(f"Added {ex_name}!")
    
    # Display added exercises
    st.subheader("Current Exercises")
    for idx, ex in enumerate(st.session_state.exercises, 1):
        st.write(f"{idx}. {ex['name']} - {ex['sets']}x{ex['reps']}")
    
    if st.button("Save Workout"):
        if workout_name and st.session_state.exercises:
            st.session_state.workouts[workout_name] = st.session_state.exercises
            save_workouts(st.session_state.workouts)
            st.success("Workout Saved!")
            st.session_state.exercises = []
        else:
            st.error("Please provide workout name and exercises")

# Track Workout Page
elif page == "Track Workout":
    st.title("Track Workout")
    
    if st.session_state.workouts:
        selected = st.selectbox("Select Workout", list(st.session_state.workouts.keys()))
        workout = st.session_state.workouts[selected]
        
        tracking_data = {}
        for ex in workout:
            st.subheader(ex["name"])
            
            # Show previous tracked sets
            if ex["tracking_history"]:
                st.write("Previous Results:")
                for idx, session in enumerate(ex["tracking_history"][-3:], 1):
                    st.write(f"Session {idx}: {session['date']}")
                    st.write(session["sets"])
            
            # Current tracking
            sets = []
            for set_num in range(1, ex["sets"] + 1):
                cols = st.columns(2)
                with cols[0]:
                    reps = st.number_input(f"Reps (Set {set_num})", min_value=0, key=f"reps_{ex['name']}_{set_num}")
                with cols[1]:
                    weight = st.number_input(f"Weight (Set {set_num}) kg", min_value=0, key=f"weight_{ex['name']}_{set_num}")
                sets.append({"reps": reps, "weight": weight})
            
            tracking_data[ex["name"]] = sets
        
        if st.button("Save Tracking Data"):
            for ex in workout:
                ex["tracking_history"].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "sets": tracking_data[ex["name"]]
                })
            save_workouts(st.session_state.workouts)
            st.success("Tracking data saved!")
    else:
        st.warning("No workouts available")

# Edit/Delete Workout Page
elif page == "Edit/Delete Workout":
    st.title("Manage Workouts")
    
    if st.session_state.workouts:
        selected = st.selectbox("Select Workout to Edit", list(st.session_state.workouts.keys()))
        workout = st.session_state.workouts[selected]
        
        # Edit workout name
        new_name = st.text_input("New Workout Name", value=selected)
        
        # Edit exercises
        st.subheader("Edit Exercises")
        new_exercises = []
        for idx, ex in enumerate(workout):
            cols = st.columns(3)
            with cols[0]:
                name = st.text_input("Exercise", value=ex["name"], key=f"name_{idx}")
            with cols[1]:
                sets = st.number_input("Sets", value=ex["sets"], key=f"sets_{idx}")
            with cols[2]:
                reps = st.number_input("Reps", value=ex["reps"], key=f"reps_{idx}")
            new_exercises.append({
                "name": name,
                "sets": sets,
                "reps": reps,
                "tracking_history": ex["tracking_history"]
            })
        
        # Save changes
        if st.button("Save Changes"):
            del st.session_state.workouts[selected]
            st.session_state.workouts[new_name] = new_exercises
            save_workouts(st.session_state.workouts)
            st.success("Workout updated!")
        
        # Delete workout
        if st.button("❌ Delete Workout"):
            del st.session_state.workouts[selected]
            save_workouts(st.session_state.workouts)
            st.success("Workout deleted!")
    else:
        st.warning("No workouts available")