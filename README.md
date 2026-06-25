# MediAlert — A Smart Emergency Response System


Emergency intake system that finds nearest hospitals and predicts ambulance arrival time using machine learning.

## Features
- User authentication (login/signup)
- Emergency intake form with patient details
- ML model predicts ambulance ETA (based on distance, traffic, urgency)
- Automatic hospital assignment (nearest available)
- Real-time countdown timer
- Dark theme professional UI
- SQLite database for persistence

## Tech Stack
**Backend:**
- Flask (Python web framework)
- SQLite (database)
- Scikit-learn (machine learning)
- Gunicorn (production server)

**Frontend:**
- HTML5
- CSS3 (dark theme)
- Vanilla JavaScript (countdown timer)

**Deployment:**
- Render (free tier)

## Live
https://medialert-led1.onrender.com


## Project Structure
medialert/

├── app.py                    # Main Flask application

├── model.py                  # ML model training script

├── model.pkl                 # Trained RandomForest model

├── requirements.txt          # Python packages

├── Procfile                  # Render deployment

├── emergency.db              # SQLite database

├── templates/                # HTML files

│   ├── index.html           # Emergency form

│   ├── login_page.html      # Login page

│   ├── sign_up.html         # Signup page

│   └── result.html          # Result/response page

└── static/                   # CSS & JavaScript

├── style.css            # Styling

└── script.js            # Form handling + countdown


## Database Schema

**users table**
- id (primary key)
- username (unique)
- password

**hospitals table**
- id (primary key)
- name
- beds
- ambulances
- distance (km)
- area
- contact

**emergencies table**
- id (primary key)
- user_id (foreign key)
- patient_name
- age, gender, blood_group, contact
- area, landmark
- emergency_type
- consciousness, breathing, bleeding
- urgency_score (1-3)
- hospital_id (foreign key)
- predicted_time (minutes)
- priority (P1/P2/P3)
- status
- timestamp

## How to Use

**Signup:**
1. Visit the live URL
2. Click "Sign up"
3. Create username (3+ characters) and password (6+ characters)
4. Auto-login happens

**Submit Emergency:**
1. Fill patient details (name, age, blood group, contact)
2. Select area in Lucknow
3. Describe patient condition (consciousness, breathing, bleeding)
4. Click "REQUEST EMERGENCY ASSISTANCE"

**View Result:**
1. See assigned hospital name and details
2. Watch ETA countdown (updates every second)
3. Priority badge (green=stable, orange=urgent, red=critical)
4. Click "Report Another Emergency" to submit again
5. Click "Logout" to exit

## How ML Model Works

**Training:**
- 500 synthetic emergency cases
- Input: distance (1-19 km), traffic (1-3), urgency (1-3)
- Output: ambulance arrival time (3-60 minutes)
- Model: RandomForest with 100 decision trees

**Prediction:**
1. User submits form
2. System calculates urgency from symptoms
3. System calculates traffic from current time (rush hours: 8-10am, 5-8pm)
4. Nearest hospital's distance is fetched
5. Model predicts ETA: time = f(distance, traffic, urgency)
6. Result shown with countdown timer

**Priority Assignment:**
- P3 (Stable): ETA ≤ 10 minutes
- P2 (Urgent): ETA 10-20 minutes
- P1 (Critical): ETA > 20 minutes

## Local Setup

```bash
# Clone and install
git clone https://github.com/Ananya-Dwivedi/smart_emergency_response_system-MediAlert.git
cd medialert
pip install -r requirements.txt

# Train model
python model.py

# Run app
python app.py

# Visit
http://localhost:5000
```

## Deployment (Render)

1. Create GitHub repo
2. Push code
3. Connect to Render
4. Add SECRET_KEY environment variable
5. Deploy with: `gunicorn app:app`

## Key Features Implemented

✅ Login/Logout with session management
✅ Signup with validation (username 3+, password 6+)
✅ Form validation (phone number, age range)
✅ ML prediction for ETA
✅ Hospital database with 47 Lucknow hospitals
✅ Real-time countdown timer
✅ Dynamic priority badges (color-coded)
✅ Error handling (no hospitals available, database errors)
✅ Protected routes (check session before access)
✅ Responsive design (mobile + desktop)

## Testing

**Test User (if pre-created):**
- Username: testuser
- Password: password123

Or create your own via signup.

## Files Size
- model.pkl: ~500 KB (trained ML model)
- emergency.db: ~100 KB (SQLite database)
- CSS: ~8 KB
- JS: ~2 KB

## Future Improvements
- Add user dashboard (view past emergencies)
- SMS/email notifications
- Real ambulance tracking
- Admin panel for hospital management
- Payment integration
