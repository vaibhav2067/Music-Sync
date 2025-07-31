from flask import Flask, render_template, request
from flask_login import LoginManager
from extensions import db
from models import User, MusicTrack, ContactMessage  # IMPORT ALL MODELS HERE
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music_sync.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/audio'

    # Initialize extensions
    db.init_app(app)

    # Create folders and database
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Login Manager setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.auth'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import blueprints
    from auth import auth_bp
    from dashboard import dashboard_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Routes
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/contact')
    def contact():
        return render_template('contact.html')
    
    @app.route('/api/contact', methods=['POST'])
    def api_contact():
        from contact_handler import handle_contact_form
        return handle_contact_form(request)
    
    # Initialize database
    with app.app_context():
        # First check if tables exist
        inspector = db.inspect(db.engine)
        if not inspector.has_table('users'):
            db.create_all()
            print("✅ Database tables created!")
        else:
            print("✅ Database already exists")
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)