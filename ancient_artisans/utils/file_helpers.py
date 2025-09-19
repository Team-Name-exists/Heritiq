import os
from werkzeug.utils import secure_filename
import uuid

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, file_type='products'):
    """Save uploaded file with unique filename"""
    if file and allowed_file(file.filename):
        # Secure the filename and add unique identifier
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads', file_type)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        return f"{file_type}/{unique_filename}"
    
    return None