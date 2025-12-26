<<<<<<< HEAD
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_it'

# OMDb API Configuration (You already have this!)
# OMDB_API_KEY = '41e6a6fc'  # Your existing API key
OMDB_API_KEY = '90998eb3'  # Your existing API key
# OMDB_API_KEY = 'e94ca55c'  # Your existing API key prafulla api key
OMDB_BASE_URL = 'http://www.omdbapi.com/'

# Load datasets
def load_datasets():
    hollywood_df = pd.read_csv('dataset.csv')
    
    # For now, using hollywood dataset as template
    # You'll replace these with actual Bollywood and Web Series datasets
    try:
        bollywood_df = pd.read_csv('bollywood.csv')
    except FileNotFoundError:
        bollywood_df = pd.DataFrame()
    
    try:
        webseries_df = pd.read_csv('webseries.csv')
    except FileNotFoundError:
        webseries_df = pd.DataFrame()
    
    return hollywood_df, bollywood_df, webseries_df

hollywood_movies, bollywood_movies, webseries = load_datasets()

# Combine all datasets for search and filter
def get_all_movies():
    dfs = []
    if not hollywood_movies.empty:
        hollywood_copy = hollywood_movies.copy()
        hollywood_copy['category'] = 'Hollywood'
        dfs.append(hollywood_copy)
    if not bollywood_movies.empty:
        bollywood_copy = bollywood_movies.copy()
        bollywood_copy['category'] = 'Bollywood'
        dfs.append(bollywood_copy)
    if not webseries.empty:
        webseries_copy = webseries.copy()
        webseries_copy['category'] = 'Web Series'
        dfs.append(webseries_copy)
    
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# Get movie details from OMDb API
def get_omdb_details(movie_title):
    try:
        url = OMDB_BASE_URL
        params = {
            'apikey': OMDB_API_KEY,
            't': movie_title,
            'plot': 'full'
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('Response') == 'True':
            # Extract relevant information
            poster = data.get('Poster') if data.get('Poster') != 'N/A' else None
            
            # Parse cast (Actors field)
            cast = data.get('Actors', '').split(', ')[:5] if data.get('Actors') != 'N/A' else []
            
            # Get director
            director = data.get('Director', 'N/A')
            
            # Get IMDB link
            imdb_id = data.get('imdbID')
            imdb_link = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else None
            
            # Get runtime (convert "142 min" to 142)
            runtime_str = data.get('Runtime', 'N/A')
            runtime = int(runtime_str.split()[0]) if runtime_str != 'N/A' and runtime_str.split()[0].isdigit() else None
            
            # Get release date
            release_date = data.get('Released', 'N/A')
            
            return {
                'poster': poster,
                'cast': cast,
                'director': director,
                'imdb_link': imdb_link,
                'runtime': runtime,
                'release_date': release_date,
                'plot': data.get('Plot', ''),
                'rated': data.get('Rated', 'N/A'),
                'awards': data.get('Awards', 'N/A'),
                'trailer': None  # OMDb doesn't provide trailers
            }
    except Exception as e:
        print(f"OMDb API Error: {e}")
    
    return None

# Content-based recommendation
def recommend_movies(movie_title, dataset, num_recommendations=8):
    if dataset.empty or movie_title not in dataset['title'].values:
        return []
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(dataset['overview'].fillna(''))
    
    movie_idx = dataset[dataset['title'] == movie_title].index[0]
    similarity_scores = cosine_similarity(tfidf_matrix[movie_idx], tfidf_matrix).flatten()
    
    similar_idx = similarity_scores.argsort()[-(num_recommendations + 1):-1][::-1]
    recommendations = dataset.iloc[similar_idx][['title', 'genre']].to_dict('records')
    
    # Add posters
    for movie in recommendations:
        omdb_data = get_omdb_details(movie['title'])
        movie['poster'] = omdb_data['poster'] if omdb_data else None
    
    return recommendations

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('welcome'))
    
    # Get popular movies for landing page
    all_movies = get_all_movies()
    if not all_movies.empty and 'popularity' in all_movies.columns:
        popular = all_movies.nlargest(12, 'popularity')[['title', 'genre', 'vote_average', 'category']].to_dict('records')
        
        for movie in popular:
            omdb_data = get_omdb_details(movie['title'])
            movie['poster'] = omdb_data['poster'] if omdb_data else None
    else:
        popular = []
    
    return render_template('index.html', movies=popular, username=session.get('username'))

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('welcome.html')

@app.route('/hollywood')
def hollywood():
    if 'username' not in session:
        return redirect(url_for('welcome'))
    
    movies = hollywood_movies.head(20)[['title', 'genre', 'vote_average']].to_dict('records')
    
    for movie in movies:
        omdb_data = get_omdb_details(movie['title'])
        movie['poster'] = omdb_data['poster'] if omdb_data else None
    
    return render_template('category.html', movies=movies, category='Hollywood', username=session.get('username'))

@app.route('/bollywood')
def bollywood():
    if 'username' not in session:
        return redirect(url_for('welcome'))
    
    if bollywood_movies.empty:
        return render_template('category.html', movies=[], category='Bollywood', 
                             message="Bollywood dataset coming soon!", username=session.get('username'))
    
    movies = bollywood_movies.head(20)[['title', 'genre', 'votes']].to_dict('records')
    
    for movie in movies:
        omdb_data = get_omdb_details(movie['title'])
        movie['poster'] = omdb_data['poster'] if omdb_data else None
    
    return render_template('category.html', movies=movies, category='Bollywood', username=session.get('username'))

@app.route('/webseries')
def web_series():
    if 'username' not in session:
        return redirect(url_for('welcome'))
    
    if webseries.empty:
        return render_template('category.html', movies=[], category='Web Series', 
                             message="Web Series dataset coming soon!", username=session.get('username'))
    
    series = webseries.head(20)[['title', 'genre', 'vote_count']].to_dict('records')
    
    for show in series:
        omdb_data = get_omdb_details(show['title'])
        show['poster'] = omdb_data['poster'] if omdb_data else None
    
    return render_template('category.html', movies=series, category='Web Series', username=session.get('username'))

@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('welcome'))
    
    query = request.args.get('q', '').lower()
    all_movies = get_all_movies()
    
    if query and not all_movies.empty:
        results = all_movies[all_movies['title'].str.lower().str.contains(query, na=False)]
        movies = results[['title', 'genre', 'vote_average', 'category']].head(20).to_dict('records')
        
        for movie in movies:
            omdb_data = get_omdb_details(movie['title'])
            movie['poster'] = omdb_data['poster'] if omdb_data else None
    else:
        movies = []
    
    return render_template('search.html', movies=movies, query=query, username=session.get('username'))


@app.route('/filter')
def filter_movies():
    if 'username' not in session:
        return redirect(url_for('welcome'))
    
    all_movies = get_all_movies()
    
    # Get filter parameters
    genre = request.args.get('genre', '')
    min_rating_str = request.args.get('min_rating')
    category = request.args.get('category', '')
    
    filtered = all_movies.copy()
    
    if genre and 'genre' in filtered.columns:
        filtered = filtered[filtered['genre'].str.contains(genre, case=False, na=False)]
    
    if min_rating_str and 'vote_average' in filtered.columns:
        try:
            min_rating = float(min_rating_str)
            numeric_vote_average = pd.to_numeric(filtered['vote_average'], errors='coerce')
            filtered = filtered[numeric_vote_average >= min_rating]
        except(ValueError, TypeError):
            pass
    
    if category and category.strip() and 'category' in filtered.columns:
        filtered = filtered[filtered['category'] == category]
    
    movies = filtered[['title', 'genre', 'vote_average', 'category']].head(20).to_dict('records')
    
    for movie in movies:
        omdb_data = get_omdb_details(movie['title'])
        movie['poster'] = omdb_data['poster'] if omdb_data else None
    
    # --- HERE IS THE KEY CHANGE FOR THE NEW ERROR ---
    # Ensure the genre column is all strings before processing
    if 'genre' in all_movies.columns:
        all_movies['genre'] = all_movies['genre'].astype(str)
        genres = sorted(all_movies['genre'].str.split(',').explode().str.strip().unique().tolist())
    else:
        genres = []
    # --- END OF KEY CHANGE ---
    
    return render_template('filter.html', movies=movies, genres=genres, username=session.get('username'))

@app.route('/movie/<path:movie_title>')
def movie_detail(movie_title):
    if 'username' not in session:
        return redirect(url_for('welcome'))
    
    all_movies = get_all_movies()
    movie_data = all_movies[all_movies['title'] == movie_title]
    
    if movie_data.empty:
        return "Movie not found", 404
    
    movie = movie_data.iloc[0].to_dict()
    
    # Get OMDb details
    omdb_data = get_omdb_details(movie_title)
    if omdb_data:
        movie.update(omdb_data)
    
    # Get recommendations
    category = movie.get('category', 'Hollywood')
    dataset = pd.DataFrame() # Initialize an empty DataFrame    
    if category == 'Hollywood':
        dataset = hollywood_movies
    elif category == 'Bollywood':
        dataset = bollywood_movies
    else:
        dataset = webseries
    
    recommendations = recommend_movies(movie_title, dataset, num_recommendations=6)
    
    return render_template('movie_detail.html', movie=movie, recommendations=recommendations, username=session.get('username'))


@app.route('/recommend')
def recommend():
    if 'username' not in session:
        return redirect(url_for('welcome'))

    query = request.args.get('q', '')
    recommendations = []
    
    if query:
        all_movies = get_all_movies()
        # Find the movie in the combined dataset
        movie_data = all_movies[all_movies['title'].str.lower() == query.lower()]

        if not movie_data.empty:
            movie_title = movie_data.iloc[0]['title']
            # Get the category to use the correct dataset for recommendations
            category = movie_data.iloc[0].get('category', 'Hollywood')
            
            if category == 'Hollywood':
                dataset = hollywood_movies
            elif category == 'Bollywood':
                dataset = bollywood_movies
            else:
                dataset = webseries
            
            recommendations = recommend_movies(movie_title, dataset, num_recommendations=12)

    return render_template('recommendations.html', recommendations=recommendations, query=query, username=session.get('username'))

@app.context_processor
def inject_current_path():
    return {'current_path': request.path}


@app.route('/about')
def about():
    return render_template('about.html', username=session.get('username', ''))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
=======
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
from datetime import datetime

app = Flask(__name__)

# Global variables for model and encoders
model = None
scaler = None
label_encoders = {}
feature_columns = None

def load_and_train_model():
    """Load dataset and train the model"""
    global model, scaler, label_encoders, feature_columns
    
    # Check if dataset exists
    if not os.path.exists('placement-prediction//student_placement_data.csv'):
        print("Dataset not found. Please upload 'student_placement_data.csv'")
        return False
    
    # Load dataset
    df = pd.read_csv('placement-prediction//student_placement_data.csv')
    
    # Drop name column if exists
    if 'name' in df.columns:
        df = df.drop(columns=['name'])
    
    # Encode categorical columns
    cat_cols = ['gender', 'branch', 'domain', 'internship', 'certifications']
    
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
    
    # Separate features and target
    X = df.drop(columns=['placement_status'])
    y = df['placement_status'].map({'Placed': 1, 'Not Placed': 0}) if df['placement_status'].dtype == 'object' else df['placement_status']
    
    feature_columns = X.columns.tolist()
    
    # Split and scale
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train Random Forest (best performer)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    print("✅ Model trained successfully!")
    print(f"📊 Features used: {feature_columns}")
    return True

def save_to_dataset(student_data):
    """Save student data to CSV"""
    try:
        df = pd.read_csv('placement-prediction//student_placement_data.csv')
        new_row = pd.DataFrame([student_data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv('student_placement_data.csv', index=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        name = request.form.get('name')
        age = int(request.form.get('age'))
        gender = request.form.get('gender')
        branch = request.form.get('branch')
        attendance_percentage = float(request.form.get('attendance_percentage'))
        current_cgpa = float(request.form.get('current_cgpa'))
        graduation_percentage = float(request.form.get('graduation_percentage'))
        hsc = float(request.form.get('hsc'))
        ssc = float(request.form.get('ssc'))
        aptitude_score = int(request.form.get('aptitude_score'))
        communication_skills = int(request.form.get('communication_skills'))
        technical_skills = int(request.form.get('technical_skills'))
        domain = request.form.get('domain')
        internship = request.form.get('internship')
        certifications = request.form.get('certifications')
        
        # Prepare data for prediction (encode categorical variables)
        input_data = {
            'age': age,
            'gender': label_encoders['gender'].transform([gender])[0],
            'branch': label_encoders['branch'].transform([branch])[0],
            'attendance_percentage': attendance_percentage,
            'current_cgpa': current_cgpa,
            'graduation_percentage': graduation_percentage,
            'hsc': hsc,
            'ssc': ssc,
            'aptitude_score': aptitude_score,
            'communication_skills': communication_skills,
            'technical_skills': technical_skills,
            'domain': label_encoders['domain'].transform([domain])[0],
            'internship': label_encoders['internship'].transform([internship])[0],
            'certifications': label_encoders['certifications'].transform([certifications])[0]
        }
        
        # Create DataFrame with correct column order
        input_df = pd.DataFrame([input_data])[feature_columns]
        
        # Scale features
        input_scaled = scaler.transform(input_df)
        
        # Make prediction
        prediction = model.predict(input_scaled)[0]
        probability = model.predict_proba(input_scaled)[0]
        
        # Get placement chance percentage
        placement_chance = round(probability[1] * 100, 2)
        
        # Prepare data to save (with original values)
        data_to_save = {
            'name': name,
            'age': age,
            'gender': gender,
            'branch': branch,
            'attendance_percentage': attendance_percentage,
            'current_cgpa': current_cgpa,
            'graduation_percentage': graduation_percentage,
            'hsc': hsc,
            'ssc': ssc,
            'aptitude_score': aptitude_score,
            'communication_skills': communication_skills,
            'technical_skills': technical_skills,
            'domain': domain,
            'internship': internship,
            'certifications': certifications,
            'placement_status': 'Placed' if prediction == 1 else 'Not Placed'
        }
        
        # Save to dataset
        save_to_dataset(data_to_save)
        
        result = {
            'success': True,
            'prediction': 'Placed' if prediction == 1 else 'Not Placed',
            'placement_chance': placement_chance,
            'name': name
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Train model on startup
    if load_and_train_model():
        app.run(debug=True)
    else:
        print("❌ Failed to load model. Please ensure 'student_placement_data.csv' exists.")
>>>>>>> 3e09f85a95613e3ae468b6290a31b29477359aa8
