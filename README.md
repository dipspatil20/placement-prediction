# 🎓 Student Placement Prediction using Machine Learning Techniques

## 📘 Overview
The **Student Placement Prediction System** uses Machine Learning to predict whether a student is likely to get placed based on their academic, technical, and personal attributes.  
It helps educational institutions identify students who may need additional training and improve overall placement outcomes.
<br>Worked along with Google colab : https://colab.research.google.com/drive/1bhJcZlS-zie4XKqIChOlEBpBBmQKjdAB?usp=sharing

## 🧠 Key Features
- Predicts student placement status (Placed / Not Placed)  
- Uses multiple ML models (Logistic Regression, Decision Tree, Random Forest, SVM, KNN, Naïve Bayes)  
- Automatically selects the best-performing model based on accuracy and F1-score  
- Interactive web interface built using **Flask**  
- Visual insights such as feature importance and model performance graphs  

## 🧩 Tech Stack
- **Language:** Python  
- **Libraries:** pandas, NumPy, scikit-learn, matplotlib, seaborn  
- **Framework:** Flask  
- **IDE/Platform:** Google Colab, VS Code, Jupyter Notebook  
- **Frontend:** HTML, CSS  

## 📂 Project Structure
```

main/
│
├── static/
│   └── style.css             # Frontend styling
│
├── templates/
│   └── index.html            # Web interface for input & prediction
│
├── Model.ipynb               # Jupyter notebook for data analysis and model training
├── app.py                    # Flask application for deployment
├── student_placement_data.csv # Dataset used for model training
|── README.md                 # Project documentation
└── requirements.txt          # for installing nessesary Libraries needed to run Flask app

````

## ⚙️ How It Works
1. **Data Collection:** Dataset of 300-400 student records with academic and skill attributes.  
2. **Preprocessing:** Handling missing values, encoding, and scaling.  
3. **Feature Selection:** Important features include CGPA, Technical Skills, Communication Skills, etc.  
4. **Model Training:** Multiple ML models trained; the best one is selected automatically.  
5. **Prediction:** User inputs student details on the Flask app to get placement prediction.  

## 🚀 To Run the Project
1. Clone the repository  
   ```bash
   git clone https://github.com/Chetanpatil03/placement-prediction.git

2. Navigate to the project folder

   ```bash
   cd student-placement-prediction
   ```
3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask application

   ```bash
   python app.py
   ```
5. Open your browser and go to

   ```
   http://127.0.0.1:5000/
   ```

## 📊 Results

* Best Model: Random Forest (Approx. 89% accuracy)
* Key Influencing Features: CGPA, Aptitude Score, Technical & Communication Skills
* Model dynamically selected based on performance metrics

### User Interface 
<img width="1920" height="1080" alt="Screenshot 2025-11-02 231152" src="https://github.com/user-attachments/assets/6199c4d6-f6c8-4afc-90d1-6e76104b902f" />
<img width="1920" height="1080" alt="Screenshot 2025-11-02 231210" src="https://github.com/user-attachments/assets/e15ae6f3-3164-409c-9d15-f194195a0743" />
<img width="1920" height="1080" alt="Screenshot 2025-11-02 231219" src="https://github.com/user-attachments/assets/a38e8866-5375-4cf7-b9b0-04e1aa97fdb5" />



## 👨‍💻 Author
**Chetan Bachchhav**<br>
MCA Student | Machine Learning Enthusiast

