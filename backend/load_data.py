import pandas as pd
import os
from pathlib import Path

def load_all_courses():
    """
    Load all CSV files from Bachelor, Masters, and PHD folders
    Returns a single DataFrame with all courses
    """
    all_courses = []
    
    # Define folder names and their degree types
    folders = {
        'Bachelor': 'Bachelor',
        'Masters': 'Masters', 
        'PHD': 'PhD'
    }
    
    for folder, degree_type in folders.items():
        folder_path = Path(folder)
        
        # Check if folder exists
        if not folder_path.exists():
            print(f"⚠️  Folder '{folder}' not found, skipping...")
            continue
        
        # Find all CSV files in the folder
        csv_files = list(folder_path.glob('*.csv'))
        
        print(f"📂 Loading {len(csv_files)} file(s) from {folder}/")
        
        for csv_file in csv_files:
            try:
                # Read CSV file
                df = pd.read_csv(csv_file)
                
                # Add degree type column
                df['degree_type'] = degree_type
                
                # Add source file column
                df['source_file'] = csv_file.name
                
                all_courses.append(df)
                print(f"   ✓ Loaded {len(df)} courses from {csv_file.name}")
                
            except Exception as e:
                print(f"   ✗ Error loading {csv_file.name}: {e}")
    
    # Combine all DataFrames
    if all_courses:
        combined_df = pd.concat(all_courses, ignore_index=True)
        print(f"\n✅ Total courses loaded: {len(combined_df)}")
        return combined_df
    else:
        print("❌ No courses loaded!")
        return pd.DataFrame()


def prepare_course_text(row):
    """
    Convert a course row into searchable text
    This is what we'll store in the vector database
    """
    text_parts = []
    
    # Add course name
    if pd.notna(row.get('course')):
        text_parts.append(f"Course: {row['course']}")
    
    # Add institution
    if pd.notna(row.get('institution')):
        text_parts.append(f"Institution: {row['institution']}")
    
    # Add degree type
    if pd.notna(row.get('degree_type')):
        text_parts.append(f"Degree: {row['degree_type']}")
    
    # Add admission requirements
    if pd.notna(row.get('admission req')):
        text_parts.append(f"Admission Requirements: {row['admission req']}")
    
    # Add language requirements
    if pd.notna(row.get('language req')):
        text_parts.append(f"Language Requirements: {row['language req']}")
    
    # Add deadline
    if pd.notna(row.get('deadline')):
        text_parts.append(f"Deadline: {row['deadline']}")
    
    return "\n".join(text_parts)


if __name__ == "__main__":
    # Test the loading
    courses_df = load_all_courses()
    if not courses_df.empty:
        print("\n📊 Sample course:")
        print(courses_df.iloc[0])
        print("\n📝 Prepared text:")
        print(prepare_course_text(courses_df.iloc[0]))