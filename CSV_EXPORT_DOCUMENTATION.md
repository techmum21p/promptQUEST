# CSV Export Feature Documentation

## 🎉 New CSV Export Functionality Added!

Your Prompt Engineering Training app now includes comprehensive data export capabilities while maintaining the existing JSON storage system.

## ✨ What's New

### 1. **CSV Export Feature**
- Export all user data to CSV format for analysis
- Custom filename support or auto-generated timestamps
- Compatible with Excel, Google Sheets, Python, R, and other data tools

### 2. **Data Export Page**
- New "Data Export" section in the navigation
- Real-time analytics summary
- Preview of exported data
- Usage tips and analysis examples

### 3. **Admin Panel**
- Administrative tools for data management
- File information and backup status
- Emergency backup functionality
- Raw JSON data viewer

### 4. **Auto-Backup System**
- Automatic CSV backups every 5 new active users
- Prevents data loss and provides historical snapshots

## 📊 What Data Gets Exported

### User Information
- **username**: User identifier
- **skill_level**: Current skill level (beginner/intermediate/advanced)
- **total_attempts**: Number of scenarios attempted
- **cumulative_score**: Sum of all scores
- **avg_score**: Average score across all attempts
- **badges_count**: Number of badges earned
- **badges**: List of earned badges

### Attempt Details
- **timestamp**: When the attempt was made
- **scenario_id**: Which scenario was attempted (e.g., b1, i2, a3)
- **total_score**: Overall score (0-100)
- **clarity_score**: Clarity component (0-25)
- **specificity_score**: Specificity component (0-25)
- **structure_score**: Structure component (0-25)
- **task_alignment_score**: Task alignment component (0-25)
- **feedback_summary**: Truncated feedback text

## 🚀 How to Use

### Export Data
1. Navigate to **"Data Export"** in the sidebar
2. Optionally enter a custom filename
3. Click **"📊 Export to CSV"**
4. File will be saved in your project directory

### View Analytics
- Summary statistics are shown on the Data Export page
- Preview of exported data is displayed
- Quick analytics including average scores and scenario counts

### Admin Functions
1. Go to **"Admin Panel"** in the sidebar
2. Use admin tools for:
   - Refreshing data from JSON
   - Viewing raw JSON structure
   - Creating emergency backups
   - Monitoring file information

## 📈 Data Analysis Examples

### Excel/Google Sheets
```
1. Open the exported CSV file
2. Create pivot tables:
   - Rows: username
   - Values: avg_score, total_attempts
3. Generate charts showing user progress over time
4. Filter by skill_level or scenario_id for targeted analysis
```

### Python Analysis
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('user_progress_export_YYYYMMDD_HHMMSS.csv')

# User performance analysis
user_stats = df.groupby('username')['total_score'].agg(['mean', 'count', 'std'])
print(user_stats)

# Scenario difficulty analysis
scenario_stats = df.groupby('scenario_id')['total_score'].agg(['mean', 'count'])
print(scenario_stats)

# Progress over time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df_sorted = df.sort_values('timestamp')
plt.plot(df_sorted['timestamp'], df_sorted['total_score'])
plt.title('Score Progression Over Time')
plt.show()

# Score distribution by skill level
df.boxplot(column='total_score', by='skill_level')
plt.title('Score Distribution by Skill Level')
plt.show()
```

## 🔧 Technical Details

### Storage Strategy
- **Primary Storage**: JSON (`user_progress.json`) - Fast read/write for app operations
- **Export Storage**: CSV files - Analysis-friendly format for data science tools
- **Auto-Backup**: Periodic CSV snapshots for data safety

### File Naming
- Manual export: Custom name or `user_progress_export_YYYYMMDD_HHMMSS.csv`
- Auto-backup: `user_progress_export_YYYYMMDD_HHMMSS.csv` every 5 users
- Emergency backup: `emergency_backup_YYYYMMDD_HHMMSS.csv`

### Performance
- Export is triggered on-demand, not affecting app performance
- Large datasets are handled efficiently with pandas
- JSON remains primary storage for speed

## 🔒 Data Safety

### Backup Strategy
1. **JSON File**: Primary storage, updated after each attempt
2. **Auto-Backups**: CSV exports every 5 new users
3. **Manual Exports**: On-demand for analysis
4. **Emergency Backups**: Admin-triggered for critical situations

### Best Practices
- Export data regularly for analysis
- Keep CSV backups before major app updates
- Monitor file sizes as user base grows
- Use version control for code changes

## 🆕 Migration Notes

### No Breaking Changes
- All existing functionality remains unchanged
- JSON storage system continues to work as before
- New features are additive, not replacement

### New Dependencies
- Added `pandas>=2.0.0` to requirements.txt
- Used only for CSV export functionality
- Does not affect core app operations

## 📞 Support

If you encounter any issues with the CSV export functionality:

1. Check that pandas is installed: `pip install pandas`
2. Verify file permissions in the project directory
3. Check the Admin Panel for file information
4. Use the emergency backup feature if needed

The export functionality enhances your data analysis capabilities while maintaining the reliability and simplicity of the existing JSON-based system.