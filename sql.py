import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

conn = psycopg2.connect("dbname='usermgt2' user='amandaleech' host='localhost'")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY, 
        first_name VARCHAR NOT NULL,
        last_name VARCHAR,
        email VARCHAR NOT NULL UNIQUE,
        phone VARCHAR,
        city VARCHAR,
        state VARCHAR,
        active BOOLEAN NOT NULL DEFAULT True
);
''')
conn.commit()

def get_user_from_list(user_fields):
    return {
        'user_id':user_fields[0],
        'first_name':user_fields[1],
        'last_name':user_fields[2],
        'email':user_fields[3],
        'phone':user_fields[4],
        'city':user_fields[5],
        'state':user_fields[6],
        'active':user_fields[7]
    }    

@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.json
    '''
    {
        "first_name":"Billy",
        "last_name":"Jones",
        "email":"billyjones43244324@gmail.com",
        "phone":"8018018011",
        "city":"Provo",
        "state":"Utah"
    }
    '''
    first_name = data.get('first_name') 
    last_name = data.get('last_name')  
    email = data.get('email') 
    if not email:
        return "Email must be a non-empty string", 400 
    phone = data.get('phone') 
    if len(phone) > 20:
        return "Phone number cannot be longer than 20 characters", 400 
    city = data.get('city') 
    state = data.get('state') 
    cursor.execute('''
        INSERT INTO users (first_name, last_name, email, phone, city, state)
        VALUES (%s, %s, %s, %s, %s, %s);
        ''', (first_name, last_name, email, phone, city, state))
    conn.commit()
    return 'user added', 201

@app.route('/users/get')
def get_all_active_users():
    results = cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE active = 't';")
    results = cursor.fetchall()
    if results:
        users = []
        for u in results:
            user_record = get_user_from_list(u)
            users.append(user_record)
        return jsonify(results), 200
    return 'User not found', 404

@app.route('/user/deactivate/<user_id>', methods=['POST'])
def deactivate_user__by_id(user_id):
    if not user_id.isnumeric():
        return(f"Invalid user id: {user_id}"), 400
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id = %s;", (user_id))
    results = cursor.fetchone()
    if not results:
        return (f"User {user_id} not found!"), 404
    cursor.execute("UPDATE users SET active='f' WHERE user_id=%s;", (user_id))
    conn.commit()
    user = {}
    return("User deactivated"), 200

@app.route('/user/activate/<user_id>', methods=['POST'])
def activate_user__by_id(user_id):
    if not user_id.isnumeric():
        return(f"Invalid user id: {user_id}"), 400
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id = %s;", (user_id))
    results = cursor.fetchone()
    if not results:
        return (f"User {user_id} not found!"), 404
    cursor.execute("UPDATE users SET active='t' WHERE user_id=%s;", (user_id))
    conn.commit()
    user = {}
    return("User Activated"), 200

@app.route('/user/get/<user_id>')
def get_user_by_id(user_id):
    if not user_id.isnumeric():
        return(f"Invalid user id: {user_id}"), 400
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id = %s;", (user_id))
    u= cursor.fetchone()
    if not u:
        return (f"User {user_id} not found!"), 404
    user_record = get_user_from_list(u)
    return jsonify(user_record), 200

@app.route('/user/update/<user_id>', methods=['POST'])
def update_user(user_id):
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found!"), 404
    request_params = request.json
    fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'city', 'state']
    update_fields = []
    field_values = []
    for field in fields:
        if field in request_params.keys():
            update_fields.append(f'{fields}=%s')
            field_values.append(request_params[field])
    field_values.append(user_id)
    update_query = "UPDATE users SET" + ','.join[update_fields] + "WHERE user_id = %s"
    cursor.execute(update_query, field_values)
    conn.commit()
    return get_user_by_id(user_id)

if __name__ =='__main__':
    app.run(host='0.0.0.0', port=8086)