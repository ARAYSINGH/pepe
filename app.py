from flask import Flask, request, render_template_string, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# HTML template for the form and results page
html_template = '''
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Clubhouse User</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f7f7f7; }
        .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); border-radius: 10px; }
        h1 { text-align: center; color: #333; }
        form { margin-bottom: 20px; }
        input, button { display: block; width: 100%; margin-top: 10px; padding: 10px; }
        input[type="text"] { border: 2px solid #ccc; border-radius: 5px; font-size: 16px; }
        button {
            background-color: #4CAF50; 
            color: white; 
            font-size: 16px;
            border: none; 
            border-radius: 5px;
            padding: 12px; 
            cursor: pointer; 
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        .result { margin-top: 20px; }
        .error { color: red; font-size: 16px; }
        .profile-info { background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px; }
        .profile-info p { margin: 5px 0; }
        .profile-info h2 { color: #4CAF50; }
        .profile-info img { width: 100px; height: 100px; border-radius: 50%; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search Clubhouse User</h1>
        <form id="searchForm" method="POST">
            <input type="text" id="username" name="username" required placeholder="Enter Username">
            <button type="submit">Search</button>
        </form>
        
        <div id="result" class="result"></div>
    </div>
    <script>
        document.getElementById("searchForm").onsubmit = async function(event) {
            event.preventDefault();
            const username = document.getElementById("username").value;
            const response = await fetch("/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: username })
            });
            const resultDiv = document.getElementById("result");
            if (response.ok) {
                const data = await response.json();
                resultDiv.innerHTML = `
                    <div class="profile-info">
                        <h2>Profile Information</h2>
                        <img src="${data.photo_url}" alt="Profile Picture">
                        <p><strong>Username:</strong> ${data.username}</p>
                        <p><strong>Name:</strong> ${data.name}</p>
                        <p><strong>Display Name:</strong> ${data.displayname}</p>
                        <p><strong>Bio:</strong> ${data.bio}</p>
                        <p><strong>Date Created:</strong> ${data.date_created}</p>
                        <p><strong>Time Created:</strong> ${data.time_created}</p>
                        <p><strong>Followers:</strong> ${data.num_followers}</p>
                        <p><strong>Following:</strong> ${data.num_following}</p>
                    </div>
                `;
            } else {
                const error = await response.json();
                resultDiv.innerHTML = `<p class="error">${error.error}</p>`;
            }
        };
    </script>
</body>
</html>
'''

# Function to search for users by name
def search_users(user_query):
    url = 'https://www.clubhouseapi.com/api/search_users'
    headers = {
        'CH-Languages': 'en-US',
        'CH-Locale': 'en_US',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'CH-AppBuild': '304',
        'CH-AppVersion': '0.1.28',
        'CH-UserID': '1387526936',  # Replace with your user ID
        'User-Agent': 'clubhouse/304 (iPhone; iOS 14.4; Scale/2.00)',
        'Connection': 'close',
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Token 71d83ef4c8c92e7a00d5a75cec4a0786cfa37bec'  # Replace with your token
    }
    data = {
        "cofollows_only": False,
        "following_only": False,
        "followers_only": False,
        "query": user_query
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to get the profile of a user by user ID
def get_user_profile(user_id):
    url = 'https://www.clubhouseapi.com/api/get_profile'
    headers = {
        'CH-Languages': 'en-US',
        'CH-Locale': 'en_US',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'CH-AppBuild': '304',
        'CH-AppVersion': '0.1.28',
        'CH-UserID': '1387526936',  # Replace with your user ID
        'User-Agent': 'clubhouse/304 (iPhone; iOS 14.4; Scale/2.00)',
        'Connection': 'close',
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Token 71d83ef4c8c92e7a00d5a75cec4a0786cfa37bec'  # Replace with your token
    }
    
    data = {
        "user_id": user_id
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Route for the main page
@app.route('/')
def index():
    return render_template_string(html_template)

# Route for handling the search request
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    user_query = data.get('username')
    search_results = search_users(user_query)

    if search_results and 'users' in search_results and search_results['users']:
        first_user_id = search_results['users'][0]['user_id']
        user_profile = get_user_profile(first_user_id)
        
        if user_profile:
            profile_info = user_profile['user_profile']
            time_created = profile_info['time_created']

            utc_time = datetime.fromisoformat(time_created[:-6])  # Parse time without timezone
            formatted_time = utc_time.strftime('%I:%M:%S %p')
            fractional_seconds = time_created.split('.')[1].split('+')[0]
            
            date_created = time_created.split('T')[0]
            time_with_format = f"{formatted_time} and {fractional_seconds} microseconds"

            result = {
                'username': profile_info['username'],
                'name': profile_info['name'],
                'displayname': profile_info['displayname'],
                'bio': profile_info['bio'],
                'photo_url': profile_info.get('photo_url', ''),
                'date_created': date_created,
                'time_created': time_with_format,
                'num_following': profile_info['num_following'],
                'num_followers': profile_info['num_followers']
            }
            return jsonify(result)

    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9992, debug=True)
