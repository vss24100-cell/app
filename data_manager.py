import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class DataManager:
    def __init__(self):
        """Initialize data manager for handling observations and comments"""
        self.observations_dir = "data/observations"
        self.comments_dir = "data/comments"
        
        # Ensure directories exist
        os.makedirs(self.observations_dir, exist_ok=True)
        os.makedirs(self.comments_dir, exist_ok=True)
    
    def save_observation(self, date: str, username: str, raw_observation: str, structured_data: dict) -> str:
        """Save observation data to file"""
        filename = f"{date}_{username}.txt"
        filepath = os.path.join(self.observations_dir, filename)
        
        # Create content for text file
        content = f"Zoo Observation Report\n"
        content += f"========================\n"
        content += f"Date: {date}\n"
        content += f"Zoo Keeper: {username}\n"
        content += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content += f"Raw Observation:\n"
        content += f"----------------\n"
        content += f"{raw_observation}\n\n"
        
        content += f"Structured Data:\n"
        content += f"---------------\n"
        for key, value in structured_data.items():
            content += f"{key.replace('_', ' ').title()}: {value}\n"
        
        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Also save metadata as JSON for easier processing
        metadata = {
            "date": date,
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "raw_observation": raw_observation,
            "structured_data": structured_data,
            "filename": filename
        }
        
        metadata_file = os.path.join(self.observations_dir, f"{date}_{username}.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        return filepath
    
    def get_observation(self, date: str, username: str) -> Optional[Dict]:
        """Get specific observation by date and username"""
        metadata_file = os.path.join(self.observations_dir, f"{date}_{username}.json")
        
        if os.path.exists(metadata_file):
            with open(metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def get_all_observations(self) -> List[Dict]:
        """Get all observations sorted by date (newest first)"""
        observations = []
        
        for filename in os.listdir(self.observations_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.observations_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        obs_data = json.load(f)
                        observations.append(obs_data)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        # Sort by date (newest first)
        observations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return observations
    
    def get_observations_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get observations within date range"""
        all_observations = self.get_all_observations()
        filtered = []
        
        for obs in all_observations:
            obs_date = obs.get("date", "")
            if start_date <= obs_date <= end_date:
                filtered.append(obs)
        
        return filtered
    
    def save_comment(self, observation_date: str, observation_username: str, 
                    comment_author: str, comment_text: str, author_role: str) -> bool:
        """Save comment for an observation"""
        comment_data = {
            "observation_date": observation_date,
            "observation_username": observation_username,
            "comment_author": comment_author,
            "author_role": author_role,
            "comment_text": comment_text,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create comment filename
        comment_filename = f"{observation_date}_{observation_username}_comments.json"
        comment_filepath = os.path.join(self.comments_dir, comment_filename)
        
        # Load existing comments or create new list
        comments = []
        if os.path.exists(comment_filepath):
            try:
                with open(comment_filepath, "r", encoding="utf-8") as f:
                    comments = json.load(f)
            except:
                comments = []
        
        # Add new comment
        comments.append(comment_data)
        
        # Save updated comments
        try:
            with open(comment_filepath, "w", encoding="utf-8") as f:
                json.dump(comments, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving comment: {e}")
            return False
    
    def get_comments(self, observation_date: str, observation_username: str) -> List[Dict]:
        """Get all comments for a specific observation"""
        comment_filename = f"{observation_date}_{observation_username}_comments.json"
        comment_filepath = os.path.join(self.comments_dir, comment_filename)
        
        if os.path.exists(comment_filepath):
            try:
                with open(comment_filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def update_observation(self, date: str, username: str, raw_observation: str, structured_data: dict) -> bool:
        """Update existing observation"""
        try:
            self.save_observation(date, username, raw_observation, structured_data)
            return True
        except Exception as e:
            print(f"Error updating observation: {e}")
            return False
    
    def delete_observation(self, date: str, username: str) -> bool:
        """Delete observation and its comments"""
        try:
            # Delete text file
            txt_file = os.path.join(self.observations_dir, f"{date}_{username}.txt")
            if os.path.exists(txt_file):
                os.remove(txt_file)
            
            # Delete metadata file
            json_file = os.path.join(self.observations_dir, f"{date}_{username}.json")
            if os.path.exists(json_file):
                os.remove(json_file)
            
            # Delete comments file
            comment_file = os.path.join(self.comments_dir, f"{date}_{username}_comments.json")
            if os.path.exists(comment_file):
                os.remove(comment_file)
            
            return True
        except Exception as e:
            print(f"Error deleting observation: {e}")
            return False

# Global data manager instance
data_manager = DataManager()
