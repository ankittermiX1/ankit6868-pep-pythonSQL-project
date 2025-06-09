import csv
import sqlite3
import os

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():
    # Get the directory of the current script for dynamic path resolution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..')
    resources_dir = os.path.join(project_root, 'resources')

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # Load data and generate analytics
    load_and_clean_users(os.path.join(resources_dir, 'users.csv'))
    load_and_clean_call_logs(os.path.join(resources_dir, 'callLogs.csv'))
    write_user_analytics(os.path.join(resources_dir, 'userAnalytics.csv'))
    write_ordered_calls(os.path.join(resources_dir, 'orderedCalls.csv'))

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Skip header row
            next(reader, None)
            
            for row in reader:
                # Clean the data: only insert records with exactly 2 non-empty values
                if len(row) == 2 and all(field.strip() for field in row):
                    first_name = row[0].strip()
                    last_name = row[1].strip()
                    
                    cursor.execute('''INSERT INTO users (firstName, lastName) 
                                     VALUES (?, ?)''', (first_name, last_name))
        
        conn.commit()
        print("Users data loaded and cleaned successfully")
        
    except FileNotFoundError:
        print(f"File {file_path} not found")
    except Exception as e:
        print(f"Error loading users data: {e}")


# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Skip header row
            next(reader, None)
            
            for row in reader:
                # Clean the data: only insert records with exactly 5 non-empty values
                if len(row) == 5 and all(field.strip() for field in row):
                    phone_number = row[0].strip()
                    start_time = row[1].strip()
                    end_time = row[2].strip()
                    direction = row[3].strip()
                    user_id = row[4].strip()
                    
                    # Validate that start_time, end_time, and user_id are numeric
                    try:
                        start_time_int = int(start_time)
                        end_time_int = int(end_time)
                        user_id_int = int(user_id)
                        
                        cursor.execute('''INSERT INTO callLogs (phoneNumber, startTime, endTime, direction, userId) 
                                         VALUES (?, ?, ?, ?, ?)''', 
                                      (phone_number, start_time_int, end_time_int, direction, user_id_int))
                    except ValueError:
                        # Skip rows with non-numeric values for time or userId
                        continue
        
        conn.commit()
        print("Call logs data loaded and cleaned successfully")
        
    except FileNotFoundError:
        print(f"File {file_path} not found")
    except Exception as e:
        print(f"Error loading call logs data: {e}")


# This function will write analytics data to userAnalytics.csv - average call time, and number of calls per user.
def write_user_analytics(csv_file_path):
    try:
        # Query to get analytics data: userId, average duration, and number of calls
        cursor.execute('''
            SELECT userId, 
                   AVG(endTime - startTime) as avgDuration,
                   COUNT(*) as numCalls
            FROM callLogs 
            GROUP BY userId
            ORDER BY userId
        ''')
        
        results = cursor.fetchall()
        
        # Write to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['userId', 'avgDuration', 'numCalls'])
            
            # Write data rows
            for row in results:
                user_id, avg_duration, num_calls = row
                writer.writerow([user_id, avg_duration, num_calls])
        
        print("User analytics written successfully")
        
    except Exception as e:
        print(f"Error writing user analytics: {e}")


# This function will write the callLogs ordered by userId, then start time.
def write_ordered_calls(csv_file_path):
    try:
        # Query to get call logs ordered by userId, then startTime
        cursor.execute('''
            SELECT callId, phoneNumber, startTime, endTime, direction, userId
            FROM callLogs 
            ORDER BY userId, startTime
        ''')
        
        results = cursor.fetchall()
        
        # Write to CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['callId', 'phoneNumber', 'startTime', 'endTime', 'direction', 'userId'])
            
            # Write data rows
            for row in results:
                writer.writerow(row)
        
        print("Ordered call logs written successfully")
        
    except Exception as e:
        print(f"Error writing ordered calls: {e}")


# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():
    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()