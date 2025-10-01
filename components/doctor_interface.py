import streamlit as st
from datetime import datetime, date, timedelta
from data_manager import data_manager

def show_doctor_interface():
    """Display doctor interface for reviewing observations and adding comments"""
    st.title("🩺 Doctor Dashboard")
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📋 Review Observations", "📊 Analytics", "🔍 Search"])
    
    with tab1:
        show_observation_review()
    
    with tab2:
        show_analytics()
    
    with tab3:
        show_search_interface()

def show_observation_review():
    """Show observations for doctor review"""
    st.header("📋 Animal Observation Reviews")
    
    # Date filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "From Date",
            value=date.today() - timedelta(days=7),
            max_value=date.today()
        )
    
    with col2:
        end_date = st.date_input(
            "To Date",
            value=date.today(),
            max_value=date.today()
        )
    
    with col3:
        # Filter button
        filter_observations = st.button("🔍 Filter Observations", use_container_width=True)
    
    # Get observations
    if filter_observations or "doctor_observations" not in st.session_state:
        observations = data_manager.get_observations_by_date_range(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        st.session_state.doctor_observations = observations
    else:
        observations = st.session_state.get("doctor_observations", [])
    
    if not observations:
        st.info("🔍 No observations found for the selected date range.")
        return
    
    st.success(f"📊 Found {len(observations)} observations")
    
    # Display observations
    for idx, obs in enumerate(observations):
        obs_date = obs.get("date", "Unknown")
        keeper_name = obs.get("username", "Unknown")
        obs_time = obs.get("timestamp", "")
        raw_obs = obs.get("raw_observation", "")
        structured_data = obs.get("structured_data", {})
        
        with st.expander(f"📅 {obs_date} - Zoo Keeper: {keeper_name} ({datetime.fromisoformat(obs_time).strftime('%H:%M') if obs_time else ''})"):
            
            # Display observation content
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Raw Observation:**")
                st.text_area("", value=raw_obs, height=120, disabled=True, key=f"doctor_raw_{idx}")
                
                # Key structured data highlights
                if structured_data:
                    st.markdown("**Key Health Indicators:**")
                    
                    # Health status indicators
                    health_indicators = {
                        "Animal Observed On Time": structured_data.get("animal_observed_on_time", "Unknown"),
                        "Normal Behavior": structured_data.get("normal_behaviour_status", "Unknown"),
                        "Clean Water Provided": structured_data.get("clean_drinking_water_provided", "Unknown"),
                        "Feed Given as Prescribed": structured_data.get("feed_given_as_prescribed", "Unknown"),
                        "Enclosure Cleaned": structured_data.get("enclosure_cleaned_properly", "Unknown")
                    }
                    
                    cols = st.columns(len(health_indicators))
                    for i, (indicator, value) in enumerate(health_indicators.items()):
                        with cols[i]:
                            if value is True:
                                st.success(f"✅ {indicator}")
                            elif value is False:
                                st.error(f"❌ {indicator}")
                            else:
                                st.warning(f"⚠️ {indicator}: {value}")
                    
                    # Show abnormal behavior details if any
                    abnormal_details = structured_data.get("normal_behaviour_details")
                    if abnormal_details and abnormal_details.strip():
                        st.warning(f"**Abnormal Behavior Noted:** {abnormal_details}")
                    
                    # Show other requirements
                    other_req = structured_data.get("other_animal_requirements")
                    if other_req and other_req.strip():
                        st.info(f"**Special Requirements:** {other_req}")
            
            with col2:
                st.markdown("**Medical Assessment:**")
                
                # Doctor's comment section
                comment_key = f"doctor_comment_{obs_date}_{keeper_name}"
                doctor_comment = st.text_area(
                    "Medical Notes/Comments:",
                    key=comment_key,
                    height=100,
                    placeholder="Enter medical assessment, recommendations, or concerns..."
                )
                
                # Priority/Urgency selector
                priority = st.selectbox(
                    "Priority Level:",
                    ["Normal", "Monitor", "Urgent", "Critical"],
                    key=f"priority_{obs_date}_{keeper_name}"
                )
                
                # Add comment button
                if st.button(f"💬 Add Medical Comment", key=f"add_comment_{obs_date}_{keeper_name}"):
                    if doctor_comment.strip():
                        comment_text = f"[Priority: {priority}] {doctor_comment}"
                        success = data_manager.save_comment(
                            obs_date,
                            keeper_name,
                            st.session_state.username,
                            comment_text,
                            "doctor"
                        )
                        
                        if success:
                            st.success("✅ Medical comment added!")
                            st.rerun()
                        else:
                            st.error("❌ Error adding comment!")
                    else:
                        st.warning("⚠️ Please enter a comment!")
                
                # Download report
                if st.button(f"📄 Download Report", key=f"download_{obs_date}_{keeper_name}"):
                    # Generate downloadable report
                    report_content = generate_medical_report(obs, structured_data)
                    st.download_button(
                        label="📥 Download Medical Report",
                        data=report_content,
                        file_name=f"medical_report_{obs_date}_{keeper_name}.txt",
                        mime="text/plain",
                        key=f"dl_{obs_date}_{keeper_name}"
                    )
            
            # Show existing comments
            comments = data_manager.get_comments(obs_date, keeper_name)
            if comments:
                st.markdown("**Previous Comments:**")
                for comment in comments:
                    author = comment.get("comment_author", "Unknown")
                    role = comment.get("author_role", "").title()
                    text = comment.get("comment_text", "")
                    timestamp = comment.get("timestamp", "")
                    
                    # Style based on role
                    if role.lower() == "doctor":
                        st.info(f"**Dr. {author}** - {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else ''}\n\n{text}")
                    else:
                        st.markdown(f"**{author}** ({role}) - {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else ''}\n\n{text}")

def show_analytics():
    """Show analytics dashboard for doctors"""
    st.header("📊 Medical Analytics Dashboard")
    
    # Get all observations for analysis
    all_observations = data_manager.get_all_observations()
    
    if not all_observations:
        st.info("📊 No data available for analysis.")
        return
    
    # Analytics metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Observations", len(all_observations))
    
    with col2:
        # Count observations from last 7 days
        recent_obs = [obs for obs in all_observations 
                     if obs.get("date", "") >= (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")]
        st.metric("Last 7 Days", len(recent_obs))
    
    with col3:
        # Count unique zoo keepers
        unique_keepers = len(set(obs.get("username", "") for obs in all_observations))
        st.metric("Active Keepers", unique_keepers)
    
    with col4:
        # Count observations with abnormal behavior
        abnormal_count = 0
        for obs in all_observations:
            structured = obs.get("structured_data", {})
            if not structured.get("normal_behaviour_status", True):
                abnormal_count += 1
        st.metric("Abnormal Behaviors", abnormal_count, delta=None)
    
    st.markdown("---")
    
    # Health trends
    st.subheader("🏥 Health Trend Analysis")
    
    # Analyze key health indicators
    health_metrics = {
        "Animals Observed On Time": [],
        "Normal Behavior": [],
        "Clean Water Available": [],
        "Proper Feeding": [],
        "Clean Enclosures": []
    }
    
    dates = []
    for obs in sorted(all_observations, key=lambda x: x.get("date", "")):
        structured = obs.get("structured_data", {})
        dates.append(obs.get("date", ""))
        
        health_metrics["Animals Observed On Time"].append(structured.get("animal_observed_on_time", False))
        health_metrics["Normal Behavior"].append(structured.get("normal_behaviour_status", False))
        health_metrics["Clean Water Available"].append(structured.get("clean_drinking_water_provided", False))
        health_metrics["Proper Feeding"].append(structured.get("feed_given_as_prescribed", False))
        health_metrics["Clean Enclosures"].append(structured.get("enclosure_cleaned_properly", False))
    
    # Display trends
    for metric, values in health_metrics.items():
        if values:
            percentage = (sum(values) / len(values)) * 100
            st.progress(percentage / 100, text=f"{metric}: {percentage:.1f}% compliance")

def show_search_interface():
    """Show search interface for doctors"""
    st.header("🔍 Advanced Search")
    
    # Search filters
    col1, col2 = st.columns(2)
    
    with col1:
        search_text = st.text_input("🔍 Search in observations:", placeholder="Enter keywords...")
        search_keeper = st.selectbox("👤 Filter by Zoo Keeper:", ["All"] + list(set(obs.get("username", "") for obs in data_manager.get_all_observations())))
    
    with col2:
        search_priority = st.multiselect("⚠️ Filter by Priority:", ["Normal", "Monitor", "Urgent", "Critical"])
        abnormal_only = st.checkbox("🚨 Show only abnormal behaviors")
    
    if st.button("🔍 Search", use_container_width=True):
        results = search_observations(search_text, search_keeper, search_priority, abnormal_only)
        
        if results:
            st.success(f"✅ Found {len(results)} matching observations")
            
            for obs in results:
                obs_date = obs.get("date", "Unknown")
                keeper_name = obs.get("username", "Unknown")
                raw_obs = obs.get("raw_observation", "")
                
                with st.expander(f"📅 {obs_date} - {keeper_name}"):
                    st.text_area("Observation:", value=raw_obs, height=100, disabled=True)
                    
                    # Show why this matched
                    if search_text and search_text.lower() in raw_obs.lower():
                        st.info(f"🎯 Matched search term: '{search_text}'")
        else:
            st.info("🔍 No observations match your search criteria.")

def search_observations(search_text, keeper_filter, priority_filter, abnormal_only):
    """Search observations based on criteria"""
    all_observations = data_manager.get_all_observations()
    results = []
    
    for obs in all_observations:
        # Text search
        if search_text and search_text.lower() not in obs.get("raw_observation", "").lower():
            continue
        
        # Keeper filter
        if keeper_filter != "All" and obs.get("username", "") != keeper_filter:
            continue
        
        # Abnormal behavior filter
        if abnormal_only:
            structured = obs.get("structured_data", {})
            if structured.get("normal_behaviour_status", True):
                continue
        
        # Priority filter (check comments)
        if priority_filter:
            comments = data_manager.get_comments(obs.get("date", ""), obs.get("username", ""))
            comment_priorities = []
            for comment in comments:
                comment_text = comment.get("comment_text", "")
                for priority in priority_filter:
                    if f"[Priority: {priority}]" in comment_text:
                        comment_priorities.append(priority)
            
            if not any(p in comment_priorities for p in priority_filter):
                continue
        
        results.append(obs)
    
    return results

def generate_medical_report(obs, structured_data):
    """Generate medical report content"""
    report = f"""MEDICAL OBSERVATION REPORT
========================

Date: {obs.get('date', 'Unknown')}
Zoo Keeper: {obs.get('username', 'Unknown')}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Medical Review by: Dr. {st.session_state.username}

RAW OBSERVATION:
{obs.get('raw_observation', 'No observation data')}

STRUCTURED ASSESSMENT:
- Animal observed on schedule: {'Yes' if structured_data.get('animal_observed_on_time') else 'No'}
- Normal behavior observed: {'Yes' if structured_data.get('normal_behaviour_status') else 'No'}
- Clean water provided: {'Yes' if structured_data.get('clean_drinking_water_provided') else 'No'}
- Feed given as prescribed: {'Yes' if structured_data.get('feed_given_as_prescribed') else 'No'}
- Enclosure properly cleaned: {'Yes' if structured_data.get('enclosure_cleaned_properly') else 'No'}

BEHAVIORAL NOTES:
{structured_data.get('normal_behaviour_details', 'No abnormal behavior noted')}

SPECIAL REQUIREMENTS:
{structured_data.get('other_animal_requirements', 'None noted')}

HEALTH MONITORING SUMMARY:
{structured_data.get('daily_animal_health_monitoring', 'Standard monitoring protocol followed')}

FEEDING NOTES:
{structured_data.get('carnivorous_animal_feeding_chart', 'Standard feeding schedule maintained')}

MEDICINE STOCK STATUS:
{structured_data.get('medicine_stock_register', 'Stock levels adequate')}

WILDLIFE MONITORING:
{structured_data.get('daily_wildlife_monitoring', 'Routine monitoring completed')}

MEDICAL COMMENTS:
"""
    
    # Add comments
    comments = data_manager.get_comments(obs.get('date', ''), obs.get('username', ''))
    for comment in comments:
        if comment.get('author_role') == 'doctor':
            author = comment.get('comment_author', 'Unknown')
            text = comment.get('comment_text', '')
            timestamp = comment.get('timestamp', '')
            report += f"\nDr. {author} ({timestamp}): {text}\n"
    
    report += f"\n\nReport End\n========================"
    
    return report
