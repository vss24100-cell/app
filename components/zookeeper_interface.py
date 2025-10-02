import streamlit as st
from datetime import datetime, date
from zoo_model import zoo_model
from data_manager import data_manager

# Audio input is now natively available in Streamlit
AUDIO_AVAILABLE = True

def show_zookeeper_interface():
    """Display zoo keeper interface with calendar and observation input"""
    st.title("🦁 Zoo Keeper Dashboard")
    
    # Create tabs for different functions
    tab1, tab2 = st.tabs(["📝 New Observation", "📋 My Observations"])
    
    with tab1:
        show_observation_form()
    
    with tab2:
        show_my_observations()

def show_observation_form():
    """Show form for creating new observations"""
    st.header("Daily Animal Observation Entry")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Calendar date selection
        st.subheader("📅 Select Date")
        selected_date = st.date_input(
            "Observation Date",
            value=date.today(),
            max_value=date.today()
        )
        
        # Check if observation already exists for this date
        existing_obs = data_manager.get_observation(
            selected_date.strftime("%Y-%m-%d"), 
            st.session_state.username
        )
        
        if existing_obs:
            st.warning(f"⚠️ Observation already exists for {selected_date.strftime('%Y-%m-%d')}")
            if st.button("Edit Existing Observation", use_container_width=True):
                st.session_state.edit_mode = True
                st.session_state.edit_date = selected_date.strftime("%Y-%m-%d")
                st.session_state.edit_observation = existing_obs.get("raw_observation", "")
    
    with col2:
        st.subheader("🔍 Observation Details")
        
        # Check if in edit mode
        edit_mode = getattr(st.session_state, 'edit_mode', False)
        edit_date = getattr(st.session_state, 'edit_date', None)
        default_text = getattr(st.session_state, 'edit_observation', "") if edit_mode else ""
        
        # Input method selection
        if AUDIO_AVAILABLE:
            input_method = st.radio(
                "Choose Input Method:",
                ["📝 Text Input", "🎤 Hindi Voice Input"],
                horizontal=True
            )
        else:
            input_method = "📝 Text Input"
            st.info("🎤 Audio recording feature is currently unavailable. Please use text input.")
        
        observation_text = ""
        audio_data = None
        
        if input_method == "📝 Text Input":
            # Text area for manual input
            observation_text = st.text_area(
                "Enter your animal observations:",
                value=default_text,
                height=300,
                placeholder="""Enter detailed observations about:
- Animal behavior and activity levels
- Feeding times and appetite
- Enclosure cleanliness and maintenance
- Water availability and cleanliness
- Any unusual behaviors or concerns
- Health observations
- Medication given (if any)
- Visitor interactions
- Weather conditions affecting animals
- Any maintenance issues noticed

Example: "Morning rounds at 8 AM. Lions were active and alert. Fed at scheduled time, all animals ate well. Water bowls clean and full. Enclosure cleaned yesterday evening. No unusual behaviors observed. Temperature mild, animals comfortable."
                """,
                help="Be as detailed as possible. The AI will structure your observations into a formal report."
            )
        
        else:  # Hindi Voice Input
            st.markdown("**🎤 Record your observations in Hindi:**")
            st.info("💡 Click the microphone button below to record your observations in Hindi, then click 'Process Observation' to auto-fill the form")
            
            # Use native Streamlit audio input
            audio_data = st.audio_input("Record your observations in Hindi")
            
            # Show success message if audio is recorded
            if audio_data is not None:
                st.success("✅ Audio recorded successfully! Click 'Process Observation' to auto-fill the form.")
            else:
                st.info("🎤 Please record your observations in Hindi using the microphone button above.")
        
        # Processing and submission
        col3, col4 = st.columns(2)
        
        # For audio input, check if we have valid audio data
        can_process = False
        if input_method == "📝 Text Input":
            can_process = observation_text.strip()
        else:  # Hindi Voice Input
            can_process = audio_data is not None
        
        with col3:
            process_button = st.button(
                "🤖 Process Observation" if not edit_mode else "🔄 Update Observation",
                use_container_width=True,
                disabled=not can_process
            )
        
        with col4:
            if edit_mode:
                if st.button("❌ Cancel Edit", use_container_width=True):
                    st.session_state.edit_mode = False
                    st.session_state.edit_date = None
                    st.session_state.edit_observation = ""
                    st.rerun()
        
        if process_button and can_process:
            with st.spinner("🔄 Processing observation with AI model..."):
                try:
                    # Use edit date if in edit mode, otherwise use selected date
                    obs_date = edit_date if edit_mode else selected_date.strftime("%Y-%m-%d")
                    
                    # Process based on input method
                    if input_method == "📝 Text Input":
                        # Process text observation
                        structured_data = zoo_model.process_observation(observation_text, obs_date)
                        final_observation_text = observation_text
                    else:
                        # Process audio observation (transcribe + structure)
                        try:
                            # Read audio bytes from st.audio_input
                            if audio_data is not None:
                                audio_bytes = audio_data.read()
                                
                                structured_data = zoo_model.process_audio_observation(audio_bytes, obs_date, language="hi")
                                
                                # Get the transcribed text for storage
                                final_observation_text = zoo_model.transcribe_audio(audio_bytes, language="hi")
                            else:
                                final_observation_text = "No audio data"
                                structured_data = zoo_model._create_fallback_data(final_observation_text, obs_date)
                        except Exception as e:
                            st.error(f"Audio processing error: {e}")
                            final_observation_text = "Audio processing failed"
                            structured_data = zoo_model._create_fallback_data(final_observation_text, obs_date)
                    
                    # Convert to dictionary for storage
                    if hasattr(structured_data, 'dict'):
                        structured_dict = structured_data.dict()
                    else:
                        structured_dict = dict(structured_data)
                    
                    # Save to file system
                    file_path = data_manager.save_observation(
                        obs_date,
                        st.session_state.username,
                        final_observation_text,
                        structured_dict
                    )
                    
                    # Success message
                    st.success("✅ Observation processed and saved successfully!")
                    
                    # Show transcribed text if it was audio input
                    if input_method == "🎤 Hindi Voice Input":
                        with st.expander("🔤 Transcribed Text"):
                            st.text_area("Hindi → English Transcription:", value=final_observation_text, height=100, disabled=True)
                    
                    # Show auto-filled form with structured data
                    st.markdown("---")
                    st.subheader("📋 Auto-Filled Observation Form")
                    st.info("✨ The AI has automatically filled out the following form based on your observation:")
                    
                    with st.form(key="observation_form_display"):
                        st.markdown("### 🐾 Animal Information")
                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            st.text_input("Name of the animal", value=structured_dict.get("animal_name", ""), disabled=True)
                        with col_a2:
                            st.text_input("Date or day of observation", value=structured_dict.get("date_or_day", ""), disabled=True)
                        
                        st.markdown("### ✅ Daily Check Items")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.checkbox("Was the animal seen at the scheduled observation time?", 
                                       value=structured_dict.get("animal_observed_on_time", False), disabled=True)
                            st.checkbox("Was clean drinking water available?", 
                                       value=structured_dict.get("clean_drinking_water_provided", False), disabled=True)
                            st.checkbox("Was the enclosure cleaned as required?", 
                                       value=structured_dict.get("enclosure_cleaned_properly", False), disabled=True)
                        with col2:
                            st.checkbox("Is the animal showing normal behaviour and activity?", 
                                       value=structured_dict.get("normal_behaviour_status", False), disabled=True)
                            st.checkbox("Was feed and supplements available?", 
                                       value=structured_dict.get("feed_and_supplements_available", False), disabled=True)
                            st.checkbox("Was the feed given as prescribed?", 
                                       value=structured_dict.get("feed_given_as_prescribed", False), disabled=True)
                        
                        st.markdown("### 📝 Additional Details")
                        abnormal_details = structured_dict.get("normal_behaviour_details", "") or "No abnormal behaviour observed"
                        st.text_area("If abnormal behaviour observed, provide details", 
                                    value=abnormal_details, height=80, disabled=True)
                        
                        other_requirements = structured_dict.get("other_animal_requirements", "") or "No special requirements"
                        st.text_area("Any other special needs or requirements", 
                                    value=other_requirements, height=80, disabled=True)
                        
                        st.text_input("Signature of caretaker or in-charge", 
                                     value=structured_dict.get("incharge_signature", ""), disabled=True)
                        
                        st.markdown("### 📊 Summary Reports")
                        st.text_area("Summary of daily animal health monitoring", 
                                    value=structured_dict.get("daily_animal_health_monitoring", ""), 
                                    height=100, disabled=True)
                        
                        st.text_area("Summary of carnivorous animal feeding chart", 
                                    value=structured_dict.get("carnivorous_animal_feeding_chart", ""), 
                                    height=100, disabled=True)
                        
                        st.text_area("Summary of medicine stock register", 
                                    value=structured_dict.get("medicine_stock_register", ""), 
                                    height=100, disabled=True)
                        
                        st.text_area("Summary of daily wildlife monitoring observations", 
                                    value=structured_dict.get("daily_wildlife_monitoring", ""), 
                                    height=100, disabled=True)
                        
                        st.form_submit_button("📄 Form Complete (View Only)", disabled=True)
                    
                    st.info(f"📁 Saved to: {file_path}")
                    
                    # Reset edit mode
                    if edit_mode:
                        st.session_state.edit_mode = False
                        st.session_state.edit_date = None
                        st.session_state.edit_observation = ""
                    
                    # Option to create another entry
                    if st.button("➕ Create Another Entry", key="another_entry"):
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error processing observation: {str(e)}")

def show_my_observations():
    """Show zoo keeper's previous observations"""
    st.header("📋 My Previous Observations")
    
    # Get all observations for current user
    all_observations = data_manager.get_all_observations()
    user_observations = [obs for obs in all_observations 
                        if obs.get("username") == st.session_state.username]
    
    if not user_observations:
        st.info("🔍 No observations found. Create your first observation in the 'New Observation' tab!")
        return
    
    # Display observations
    for obs in user_observations:
        obs_date = obs.get("date", "Unknown")
        obs_time = obs.get("timestamp", "")
        raw_obs = obs.get("raw_observation", "")
        
        with st.expander(f"📅 {obs_date} - {datetime.fromisoformat(obs_time).strftime('%H:%M') if obs_time else ''}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Raw Observation:**")
                st.text_area("", value=raw_obs, height=100, disabled=True, key=f"raw_{obs_date}")
            
            with col2:
                st.markdown("**Actions:**")
                if st.button("✏️ Edit", key=f"edit_{obs_date}"):
                    st.session_state.edit_mode = True
                    st.session_state.edit_date = obs_date
                    st.session_state.edit_observation = raw_obs
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{obs_date}"):
                    if data_manager.delete_observation(obs_date, st.session_state.username):
                        st.success("✅ Observation deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting observation!")
            
            # Show structured data
            structured_data = obs.get("structured_data", {})
            if structured_data:
                st.markdown("**Structured Data:**")
                st.json(structured_data)
            
            # Show comments from doctors/admins
            comments = data_manager.get_comments(obs_date, st.session_state.username)
            if comments:
                st.markdown("**Comments from Staff:**")
                for comment in comments:
                    author = comment.get("comment_author", "Unknown")
                    role = comment.get("author_role", "").title()
                    text = comment.get("comment_text", "")
                    timestamp = comment.get("timestamp", "")
                    
                    st.markdown(f"**{author}** ({role}) - {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else ''}")
                    st.markdown(f"> {text}")
                    st.markdown("---")
