import streamlit as st
from datetime import datetime, date, timedelta
from data_manager import data_manager
from auth import add_user, load_users
import json
import os

def show_admin_interface():
    """Display admin interface with full system management"""
    st.title("👨‍💼 Admin Dashboard")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "👥 User Management", "📋 All Observations", "💬 Comment Management", "⚙️ System Settings"])
    
    with tab1:
        show_admin_overview()
    
    with tab2:
        show_user_management()
    
    with tab3:
        show_all_observations()
    
    with tab4:
        show_comment_management()
    
    with tab5:
        show_system_settings()

def show_admin_overview():
    """Show admin dashboard overview"""
    st.header("📊 System Overview")
    
    # Get all system data
    all_observations = data_manager.get_all_observations()
    users_data = load_users()
    
    # Metrics row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Observations", len(all_observations))
    
    with col2:
        total_users = sum(len(role_users) for role_users in users_data.values())
        st.metric("Total Users", total_users)
    
    with col3:
        # Observations today
        today = date.today().strftime("%Y-%m-%d")
        today_obs = [obs for obs in all_observations if obs.get("date") == today]
        st.metric("Today's Observations", len(today_obs))
    
    with col4:
        # Total comments
        comment_count = 0
        for obs in all_observations:
            comments = data_manager.get_comments(obs.get("date", ""), obs.get("username", ""))
            comment_count += len(comments)
        st.metric("Total Comments", comment_count)
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    # Last 7 days activity
    recent_observations = []
    for i in range(7):
        check_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_obs = [obs for obs in all_observations if obs.get("date") == check_date]
        recent_observations.append({
            "date": check_date,
            "count": len(day_obs)
        })
    
    # Display as chart
    if recent_observations:
        chart_data = {"Date": [], "Observations": []}
        for item in reversed(recent_observations):  # Reverse to show oldest first
            chart_data["Date"].append(item["date"])
            chart_data["Observations"].append(item["count"])
        
        st.line_chart(data=chart_data, x="Date", y="Observations")
    
    # User activity breakdown
    st.subheader("👥 User Activity")
    
    user_activity = {}
    for obs in all_observations:
        username = obs.get("username", "Unknown")
        user_activity[username] = user_activity.get(username, 0) + 1
    
    if user_activity:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Observations per Zoo Keeper:**")
            for username, count in sorted(user_activity.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {username}: {count} observations")
        
        with col2:
            # Role distribution
            st.write("**User Distribution by Role:**")
            for role, role_users in users_data.items():
                st.write(f"• {role.title()}: {len(role_users)} users")

def show_user_management():
    """Show user management interface"""
    st.header("👥 User Management")
    
    # Existing users display
    st.subheader("Current Users")
    
    users_data = load_users()
    
    for role, role_users in users_data.items():
        with st.expander(f"{role.title()} Users ({len(role_users)})"):
            if role_users:
                for username in role_users.keys():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"👤 {username}")
                    with col2:
                        if st.button(f"🗑️ Remove", key=f"remove_{role}_{username}"):
                            if remove_user(username, role):
                                st.success(f"✅ User {username} removed!")
                                st.rerun()
                            else:
                                st.error("❌ Error removing user!")
            else:
                st.info(f"No {role} users found.")
    
    st.markdown("---")
    
    # Add new user
    st.subheader("➕ Add New User")
    
    with st.form("add_user_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_username = st.text_input("Username", placeholder="Enter username")
        
        with col2:
            new_password = st.text_input("Password", type="password", placeholder="Enter password")
        
        with col3:
            new_role = st.selectbox("Role", ["zookeeper", "doctor", "admin"])
        
        submit_add_user = st.form_submit_button("➕ Add User", use_container_width=True)
        
        if submit_add_user:
            if new_username and new_password:
                if add_user(new_username, new_password, new_role):
                    st.success(f"✅ User {new_username} added successfully as {new_role}!")
                    st.rerun()
                else:
                    st.error("❌ Error adding user!")
            else:
                st.error("⚠️ Please fill in all fields!")

def show_all_observations():
    """Show all observations with admin controls"""
    st.header("📋 All System Observations")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "From Date",
            value=date.today() - timedelta(days=30),
            max_value=date.today()
        )
    
    with col2:
        end_date = st.date_input(
            "To Date",
            value=date.today(),
            max_value=date.today()
        )
    
    with col3:
        all_observations = data_manager.get_all_observations()
        all_keepers = list(set(obs.get("username", "") for obs in all_observations))
        selected_keeper = st.selectbox("Filter by Keeper", ["All"] + all_keepers)
    
    # Get filtered observations
    observations = data_manager.get_observations_by_date_range(
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    if selected_keeper != "All":
        observations = [obs for obs in observations if obs.get("username") == selected_keeper]
    
    if not observations:
        st.info("🔍 No observations found for the selected criteria.")
        return
    
    st.success(f"📊 Displaying {len(observations)} observations")
    
    # Display observations with admin controls
    for idx, obs in enumerate(observations):
        obs_date = obs.get("date", "Unknown")
        keeper_name = obs.get("username", "Unknown")
        obs_time = obs.get("timestamp", "")
        raw_obs = obs.get("raw_observation", "")
        
        with st.expander(f"📅 {obs_date} - {keeper_name} ({datetime.fromisoformat(obs_time).strftime('%H:%M') if obs_time else ''})"):
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Observation:**")
                st.text_area("", value=raw_obs, height=100, disabled=True, key=f"admin_obs_{idx}")
                
                # Admin comment section
                admin_comment = st.text_area(
                    "Admin Comments:",
                    key=f"admin_comment_{obs_date}_{keeper_name}",
                    placeholder="Add administrative notes, feedback, or instructions..."
                )
                
                if st.button(f"💬 Add Admin Comment", key=f"admin_add_comment_{idx}"):
                    if admin_comment.strip():
                        success = data_manager.save_comment(
                            obs_date,
                            keeper_name,
                            st.session_state.username,
                            admin_comment,
                            "admin"
                        )
                        
                        if success:
                            st.success("✅ Admin comment added!")
                            st.rerun()
                        else:
                            st.error("❌ Error adding comment!")
                    else:
                        st.warning("⚠️ Please enter a comment!")
            
            with col2:
                st.markdown("**Admin Actions:**")
                
                # Download observation
                if st.button(f"📄 Download", key=f"admin_download_{idx}"):
                    report_content = generate_admin_report(obs)
                    st.download_button(
                        label="📥 Download Report",
                        data=report_content,
                        file_name=f"observation_{obs_date}_{keeper_name}.txt",
                        mime="text/plain",
                        key=f"admin_dl_{idx}"
                    )
                
                # Delete observation
                st.markdown("⚠️ **Danger Zone:**")
                if st.button(f"🗑️ Delete", key=f"admin_delete_{idx}", type="secondary"):
                    if data_manager.delete_observation(obs_date, keeper_name):
                        st.success("✅ Observation deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting observation!")
            
            # Show all comments
            comments = data_manager.get_comments(obs_date, keeper_name)
            if comments:
                st.markdown("**All Comments:**")
                for comment in comments:
                    author = comment.get("comment_author", "Unknown")
                    role = comment.get("author_role", "").title()
                    text = comment.get("comment_text", "")
                    timestamp = comment.get("timestamp", "")
                    
                    # Style based on role
                    if role.lower() == "admin":
                        st.error(f"**Admin {author}** - {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else ''}\n\n{text}")
                    elif role.lower() == "doctor":
                        st.info(f"**Dr. {author}** - {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else ''}\n\n{text}")
                    else:
                        st.markdown(f"**{author}** ({role}) - {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else ''}\n\n{text}")

def show_comment_management():
    """Show comment management interface"""
    st.header("💬 Comment Management")
    
    # Get all comments across all observations
    all_observations = data_manager.get_all_observations()
    all_comments = []
    
    for obs in all_observations:
        comments = data_manager.get_comments(obs.get("date", ""), obs.get("username", ""))
        for comment in comments:
            comment["obs_date"] = obs.get("date", "")
            comment["obs_keeper"] = obs.get("username", "")
            all_comments.append(comment)
    
    if not all_comments:
        st.info("💬 No comments found in the system.")
        return
    
    # Sort by timestamp (newest first)
    all_comments.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    st.success(f"💬 Found {len(all_comments)} total comments")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        role_filter = st.selectbox("Filter by Role:", ["All", "Admin", "Doctor", "Zoo Keeper"])
    
    with col2:
        author_filter = st.selectbox("Filter by Author:", ["All"] + list(set(c.get("comment_author", "") for c in all_comments)))
    
    # Apply filters
    filtered_comments = all_comments
    
    if role_filter != "All":
        filtered_comments = [c for c in filtered_comments if c.get("author_role", "").lower() == role_filter.lower().replace(" ", "")]
    
    if author_filter != "All":
        filtered_comments = [c for c in filtered_comments if c.get("comment_author", "") == author_filter]
    
    # Display comments
    for idx, comment in enumerate(filtered_comments):
        author = comment.get("comment_author", "Unknown")
        role = comment.get("author_role", "").title()
        text = comment.get("comment_text", "")
        timestamp = comment.get("timestamp", "")
        obs_date = comment.get("obs_date", "")
        obs_keeper = comment.get("obs_keeper", "")
        
        with st.expander(f"💬 {author} ({role}) - {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') if timestamp else ''} on {obs_date}"):
            st.write(f"**Observation by:** {obs_keeper}")
            st.write(f"**Comment:** {text}")
            
            # Admin can delete comments
            if st.button(f"🗑️ Delete Comment", key=f"delete_comment_{idx}"):
                # This would require implementing comment deletion in data_manager
                st.warning("Comment deletion functionality would be implemented here.")

def show_system_settings():
    """Show system settings and configuration"""
    st.header("⚙️ System Settings")
    
    # System information
    st.subheader("📊 System Information")
    
    # File system info
    obs_dir = "data/observations"
    comments_dir = "data/comments"
    
    obs_files = len([f for f in os.listdir(obs_dir) if f.endswith('.json')]) if os.path.exists(obs_dir) else 0
    comment_files = len([f for f in os.listdir(comments_dir) if f.endswith('.json')]) if os.path.exists(comments_dir) else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Observation Files", obs_files)
    
    with col2:
        st.metric("Comment Files", comment_files)
    
    with col3:
        # Calculate total disk usage
        total_size = 0
        for root, dirs, files in os.walk("data"):
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        st.metric("Data Size", f"{total_size / 1024:.1f} KB")
    
    st.markdown("---")
    
    # Backup and export
    st.subheader("💾 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export All Data", use_container_width=True):
            export_data = {
                "observations": data_manager.get_all_observations(),
                "users": load_users(),
                "export_timestamp": datetime.now().isoformat()
            }
            
            st.download_button(
                label="📥 Download System Export",
                data=json.dumps(export_data, indent=2),
                file_name=f"zoo_system_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🧹 Clean Old Data", use_container_width=True):
            st.warning("Data cleanup functionality would be implemented here.")
    
    st.markdown("---")
    
    # AI Model settings
    st.subheader("🤖 AI Model Configuration")
    
    # Show current model status
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if api_token:
        st.success("✅ Hugging Face API token configured")
    else:
        st.error("❌ Hugging Face API token not found")
    
    # Model test
    if st.button("🧪 Test AI Model"):
        from zoo_model import zoo_model
        test_observation = "Test observation: Animals are active and healthy today."
        
        try:
            with st.spinner("Testing AI model..."):
                result = zoo_model.process_observation(test_observation, date.today().strftime("%Y-%m-%d"))
            st.success("✅ AI model is working correctly!")
            with st.expander("Test Result"):
                st.json(result.dict() if hasattr(result, 'dict') else dict(result))
        except Exception as e:
            st.error(f"❌ AI model test failed: {str(e)}")

def remove_user(username, role):
    """Remove user from the system"""
    try:
        users_data = load_users()
        
        if role in users_data and username in users_data[role]:
            del users_data[role][username]
            
            with open("data/users.json", "w") as f:
                json.dump(users_data, f, indent=2)
            
            return True
        return False
    except Exception as e:
        print(f"Error removing user: {e}")
        return False

def generate_admin_report(obs):
    """Generate admin report for observation"""
    structured_data = obs.get("structured_data", {})
    
    report = f"""ADMINISTRATIVE OBSERVATION REPORT
================================

Date: {obs.get('date', 'Unknown')}
Zoo Keeper: {obs.get('username', 'Unknown')}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Administrative Review by: {st.session_state.username}

RAW OBSERVATION:
{obs.get('raw_observation', 'No observation data')}

STRUCTURED DATA SUMMARY:
"""
    
    for key, value in structured_data.items():
        report += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    report += f"""

ADMINISTRATIVE COMMENTS:
"""
    
    # Add admin comments
    comments = data_manager.get_comments(obs.get('date', ''), obs.get('username', ''))
    for comment in comments:
        if comment.get('author_role') == 'admin':
            author = comment.get('comment_author', 'Unknown')
            text = comment.get('comment_text', '')
            timestamp = comment.get('timestamp', '')
            report += f"\nAdmin {author} ({timestamp}): {text}\n"
    
    report += f"\n\nReport End\n================================"
    
    return report
