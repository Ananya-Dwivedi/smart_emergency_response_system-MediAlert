from flask import Flask, render_template, request,redirect,url_for,session
import pandas as pd
import pickle 
import os
from datetime import datetime
import sqlite3

def get_connection():
    conn=sqlite3.connect('emergency.db')
    return conn

def create_db():

    conn=get_connection()
    cursor=conn.cursor()
    #USERS TABLE 
    cursor.execute('create table if not exists users(id integer primary key autoincrement,username varchar not null unique,password varchar not null)')
    
    #HOSPITALS TABLE
    cursor.execute('create table if not exists hospitals(id integer primary key autoincrement,name varchar not null,beds int ,ambulances int , distance int, area varchar, contact text )')
    
    #EMERGENCIES TABLE
    cursor.execute('create table if not exists emergencies(id integer primary key autoincrement,user_id int,patient_name varchar not null,age int check (age>0),gender varchar,blood_group varchar, contact varchar,city varchar,landmark varchar, emergency_type varchar ,consciousness varchar , breathing text,bleeding varchar,urgency_score int,hospital_id int,predicted_time float,priority varchar,priority_color varchar,priority_msg varchar ,status varchar,timestamp datetime default current_timestamp,foreign key(user_id) references users(id),foreign key(hospital_id) references hospitals(id))')


    # print('Database and tables are created successfully !')

    conn.commit()
    conn.close()
    
               
create_db() 

app = Flask(__name__) 

app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-only-for-testing')



with open('model.pkl', 'rb') as f:  # as the model.py ---> model.pkl and now no need to be trained everytime we run the url.
    model = pickle.load(f)


@app.route('/') 
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    
    return render_template('index.html')  


@app.route('/login',methods=['GET','POST'])
def login():
    
    conn=get_connection()
    cursor=conn.cursor()
 
    if request.method == 'GET':
        
        return render_template('login_page.html')
    
    if request.method == 'POST':
       
        username = request.form.get('username')
        password = request.form.get('password')
        
        
        cursor.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        
        if user:
            
            session['user_id'] = user[0]  
            return redirect(url_for('home'))  
        else:

            return render_template('login_page.html', error='Invalid credentials') 


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign_up.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            if not username or len(username) < 3:
                return render_template('sign_up.html', error='Username must be 3+ characters')

            if not password or len(password) < 6:
                return render_template('sign_up.html', error='Password must be 6+ characters')
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                          (username, password))
            conn.commit()
            
           
            cursor.execute('SELECT id FROM users WHERE username=?', (username,))
            user = cursor.fetchone()
           
            
            
            session['user_id'] = user[0]
            
            
            return redirect(url_for('home'))
        
        except sqlite3.IntegrityError:

            return render_template('sign_up.html', error='Username already exists')
        
        except sqlite3.Error as e:

            return render_template('sign_up.html', error='Database error. Try again.')
            
        except:
            
            return render_template('sign_up.html', error='Username already exists')

        finally:
            conn.close()


@app.route('/predict', methods=['POST'])   
def predict():

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    try:

  
        patient_name   = request.form.get('patient_name', '').strip()
        age            =int(request.form.get('age', 'N/A'))   
        gender         = request.form.get('gender', 'N/A')
        blood_group    = request.form.get('blood_group', 'Unknown')
        contact        = request.form.get('contact', 'N/A').strip()
        if (not contact.isdigit() or len(contact) != 10 or contact[0] not in "6789"):
            return render_template(
            "index.html",
            error="Enter a valid Indian mobile number - a valid 10 digit."
        )
        area           = request.form.get('area', '').strip()
        landmark       = request.form.get('landmark', 'N/A').strip()
        emergency_type = request.form.get('emergency_type', 'Other')
        consciousness  = request.form.get('consciousness', 'fully_conscious')
        breathing      = request.form.get('breathing', 'normal')
        bleeding       = request.form.get('bleeding', 'no_bleeding')
        

        # ──────────────────────────────────────────────────
        #   — Derive URGENCY level  from patient condition
        #  patients symptoms --> severity level  will decide urgency as 1(mild/stable),2(urgent),3(critical). 
        #  We do NOT ask the user for urgency directly.
        #  A panicking caller always says "CRITICAL".
        #  Instead we calculate it from real clinical inputs:
        #  consciousness + breathing + bleeding
        #
        #  T
        # ──────────────────────────────────────────────────
        urgency = 1  # default: mild

        # Consciousness check
        if consciousness == 'unconscious':
            urgency = 3
        elif consciousness in ['confused', 'semi_conscious']:
            urgency = max(urgency, 2)

        # Breathing check
        if breathing == 'absent':
            urgency = 3
        elif breathing in ['laboured', 'rapid']:
            urgency = max(urgency, 2)

        # Bleeding overrides
        if bleeding == 'severe':
            urgency = 3
        elif bleeding == 'moderate':
            urgency = max(urgency, 2)

        # ──────────────────────────────────────────────────
        #   — Derive TRAFFIC level from current time
        #
        #  We do NOT ask the user for traffic.
        #  A panicking caller doesn't notice traffic.
        #  We check the clock instead.
        #
        #  Lucknow rush hours: 8–10am and 5–8pm
        # ──────────────────────────────────────────────────
        hour = datetime.now().hour  #2026-05-29 18:45:12----> only the hour part i.e.  18 as in 6 pm 

        if 8 <= hour <= 10 or 17 <= hour <= 20:
            traffic = 3   # rush hour — heavy
        elif 11 <= hour <= 16:
            traffic = 2   # afternoon — moderate
        else:
            traffic = 1   # night/early morning — clear

    



        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute('select * from hospitals where area = ? and beds>0 and ambulances> 0 order by distance limit 1',(area,))
        best=cursor.fetchone()
            
        if best is None :
    
            cursor.execute('select * from hospitals where beds>0 and ambulances> 0 order by distance limit 1')
            best=cursor.fetchone()
            if best is None :
                return render_template('result.html',error='NO HOSPITAL AVAILABLE RIGHT NOW. PLEASE CALL 108.')

        
        hospital_id=best[0]
        distance  = (best[4])
    


        input_data = pd.DataFrame({
                'Distance': [distance],
                'Traffic':  [traffic],
                'Urgency':  [urgency]
            })

        predicted_time = round(float(model.predict(input_data)[0]), 1)


        if predicted_time <= 10:
                priority       = "P3 — Stable"
                priority_color = "green"
                priority_msg   = "Ambulance dispatched. Proceed to hospital."
        elif predicted_time <= 20:
                priority       = "P2 — Urgent"
                priority_color = "orange"
                priority_msg   = "Moving fast. Hospital has been alerted."
        else:
                priority       = "P1 — Critical"
                priority_color = "red"
                priority_msg   = "CRITICAL — ICU being prepared. Do not wait."




        cursor.execute('''
        INSERT INTO emergencies (
        user_id,patient_name, age, gender, blood_group, contact, 
            city, landmark, emergency_type, consciousness, breathing, 
            bleeding, urgency_score, hospital_id, predicted_time,priority,priority_color,priority_msg, status
        ) 
        VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ? , ?)
    ''', (
        user_id, patient_name, age, gender, blood_group, contact, area, landmark,
        emergency_type, consciousness, breathing, bleeding, urgency, 
        hospital_id, 
        predicted_time, priority,priority_color,priority_msg,'pending'
    ))  
            
    

    

        cursor.execute('update hospitals set beds=beds-1 ,ambulances=ambulances-1 where id =?',(hospital_id,))

        conn.commit()
        conn.close()
            

    
        return redirect(url_for('success'))
    
    except sqlite3.Error as e:
        return render_template('index.html', error='Database error. Please try again.')
    except Exception as e:
        return render_template('index.html', error='An error occurred. Please try again.')



@app.route('/success')
def success():

    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Get the LAST emergency from database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emergencies WHERE user_id = ? ORDER BY id DESC LIMIT 1',
    (session['user_id'],))
    # cursor.execute('SELECT * FROM emergencies ORDER BY id DESC LIMIT 1')  # get the recent emergency details
    emergency = cursor.fetchone()
    if not emergency:
        conn.close()
        return redirect(url_for('home'))  
    
    
 
    # Get hospital info for that emergency
    hospital_id = emergency[14]
    cursor.execute('SELECT * FROM hospitals WHERE id = ?', (hospital_id,))
    hospital = cursor.fetchone()
    
    conn.close()
    
    # Extract data
    patient_name = emergency[2]
    age = emergency[3]
    gender = emergency[4]
    blood_group = emergency[5]
    contact = emergency[6]
    landmark = emergency[8]
    emergency_type = emergency[9]
    consciousness = emergency[10]
    breathing = emergency[11]
    bleeding = emergency[12]
    urgency = emergency[13]
    predicted_time = emergency[15]
    priority = emergency[16]
    priority_color = emergency[17]
    priority_msg = emergency[18]
    
   
    hospital_name = hospital[1]
    hospital_area = hospital[5]
    distance = hospital[4]
    beds = hospital[2]
    ambulances = hospital[3]
    hosp_contact = hospital[6]
    
 
    
    return render_template('result.html',
                           patient_name=patient_name,
                           age=age,
                           gender=gender,
                           blood_group=blood_group,
                           contact=contact,
                           landmark=landmark,
                           emergency_type=emergency_type,
                           consciousness=consciousness,
                           breathing=breathing,
                           bleeding=bleeding,
                           urgency=urgency,
                           hospital_name=hospital_name,
                           area=hospital_area,
                           distance=distance,
                           beds=beds,
                           ambulance=ambulances,
                           hosp_contact=hosp_contact,
                           predicted_time=predicted_time,
                           priority=priority,
                           priority_color=priority_color,
                           priority_msg=priority_msg)
   

if __name__ == '__main__':
    app.run(debug=False)
