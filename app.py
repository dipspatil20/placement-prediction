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