# contact_handler.py
from flask import jsonify, request
from models import ContactMessage
from extensions import db
from flask_login import current_user

def handle_contact_form(request):
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return jsonify({'message': 'All fields are required.'}), 400

    # Store the message in database
    new_message = ContactMessage(
        name=name,
        email=email,
        message=message,
        user_id=current_user.get_id() if current_user.is_authenticated else None
    )
    
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': "Thanks for reaching out! We'll get back to you soon."}), 200