# from flask import Flask, render_template, request, redirect, url_for, flash
# from azure.storage.blob import BlobServiceClient
# import mysql.connector
# import os
# from werkzeug.utils import secure_filename
# import datetime

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'

# # Azure Storage Account Information
# ACCOUNT_NAME = "556hello"
# ACCOUNT_KEY = "7nxxfzU/KWdcn1+zd3FFvrTf8ssASRGsvMv+AtRrS0e8YhYZ2zbrXcskLcpnrTS7g0YKLtPwMA2m+AStM+DfNQ=="
# CONTAINER_NAME = "flask"

# # MySQL Database Information
# MYSQL_HOST = "demo-sql.mysql.database.azure.com"
# MYSQL_USER = "mysql"
# MYSQL_PASSWORD = "chatGPT.."
# MYSQL_DB = "mydatabase"

# # Directory for uploaded images
# UPLOADS_DIR = os.path.join(app.root_path, 'static', 'uploads')

# # Ensure the UPLOADS_DIR exists
# os.makedirs(UPLOADS_DIR, exist_ok=True)

# # Function to generate a unique filename based on timestamp
# def get_unique_filename(original_filename):
#     timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
#     secure_name = secure_filename(original_filename)
#     unique_name = f"{timestamp}_{secure_name}"
#     return unique_name

# # Function to get a list of images from the database
# def get_images_from_database():
#     connection = None  # Initialize connection outside the try block
#     try:
#         connection = mysql.connector.connect(
#             host=MYSQL_HOST,
#             user=MYSQL_USER,
#             password=MYSQL_PASSWORD,
#             database=MYSQL_DB
#         )
#         cursor = connection.cursor()

#         # Assuming you have an 'images' table with a 'filename' column
#         query = "SELECT filename FROM images"
#         cursor.execute(query)
#         result = cursor.fetchall()

#         return [{'filename': row[0]} for row in result]

#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#         return []

#     finally:
#         if connection and connection.is_connected():
#             cursor.close()
#             connection.close()

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         flash('No file part', 'error')
#         return redirect(request.url)

#     file = request.files['file']

#     if file.filename == '':
#         flash('No selected file', 'error')
#         return redirect(request.url)

#     try:
#         # Upload to Azure Storage
#         blob_service_client = BlobServiceClient(account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=ACCOUNT_KEY)
#         container_client = blob_service_client.get_container_client(CONTAINER_NAME)

#         # Generate a unique filename
#         unique_filename = get_unique_filename(file.filename)

#         # Upload to Azure Storage using the unique filename
#         blob_client = container_client.get_blob_client(unique_filename)
#         blob_client.upload_blob(file)

#         # Insert into MySQL Database
#         try:
#             connection = mysql.connector.connect(
#                 host=MYSQL_HOST,
#                 user=MYSQL_USER,
#                 password=MYSQL_PASSWORD,
#                 database=MYSQL_DB
#             )
#             cursor = connection.cursor()

#             # Assuming you have an 'images' table with a 'filename' column
#             query = "INSERT INTO images (filename) VALUES (%s)"
#             cursor.execute(query, (unique_filename,))
#             connection.commit()

#             flash('File uploaded successfully', 'success')

#         except mysql.connector.Error as err:
#             flash(f"Error inserting into database: {err}", 'error')

#         finally:
#             if connection.is_connected():
#                 cursor.close()
#                 connection.close()

#     except Exception as e:
#         flash(f"Error uploading to Azure Storage: {e}", 'error')

#     return redirect(url_for('index'))

# @app.route('/list')
# def image_list():
#     images = get_images_from_database()
#     return render_template('list.html', images=images)

# if __name__ == '__main__':
#     app.run(debug=True)






from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient
import os
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Azure Storage Account Information
ACCOUNT_NAME = "556hello"
ACCOUNT_KEY = "7nxxfzU/KWdcn1+zd3FFvrTf8ssASRGsvMv+AtRrS0e8YhYZ2zbrXcskLcpnrTS7g0YKLtPwMA2m+AStM+DfNQ=="
CONTAINER_NAME = "flask"

MYSQL_HOST = "demo-sql.mysql.database.azure.com"
MYSQL_USER = "mysql"
MYSQL_PASSWORD = "chatGPT.."
MYSQL_DB = "mydatabase"

# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for the 'images' table
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)

# Directory for uploaded images
UPLOADS_DIR = os.path.join(app.root_path, 'static', 'uploads')

# Ensure the UPLOADS_DIR exists
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Function to generate a unique filename based on timestamp
def get_unique_filename(original_filename):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    secure_name = secure_filename(original_filename)
    unique_name = f"{timestamp}_{secure_name}"
    return unique_name

@app.route('/list')
def image_list():
    images = File.query.all()
    return render_template('list.html', images=images)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    try:
        # Upload to Azure Storage
        blob_service_client = BlobServiceClient(account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=ACCOUNT_KEY)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        # Generate a unique filename
        unique_filename = get_unique_filename(file.filename)

        # Upload to Azure Storage using the unique filename
        blob_client = container_client.get_blob_client(unique_filename)
        blob_client.upload_blob(file)

        # Insert into MySQL Database using SQLAlchemy
        image = File(filename=unique_filename)
        db.session.add(image)
        db.session.commit()

        flash('File uploaded successfully', 'success')

    except Exception as e:
        flash(f"Error uploading to Azure Storage: {e}", 'error')

    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
    app.run(debug=True)
