# dashboard.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import MusicTrack, User
import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    user = User.query.get(current_user.id)
    recent_tracks = MusicTrack.query.filter_by(user_id=current_user.id)\
                          .order_by(MusicTrack.created_at.desc())\
                          .limit(5).all()
    total_tracks = MusicTrack.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', 
                         tracks=recent_tracks,
                         user=user,
                         total_tracks=total_tracks)

@dashboard_bp.route('/generate', methods=['POST'])
@login_required
def generate_track():  # Changed function name from generate_music to generate_track
    genre = request.form.get('genre')
    mood = request.form.get('mood')
    instruments = request.form.get('instruments', type=int)
    temperature = request.form.get('temperature', type=float)
    
    new_track = MusicTrack(
        title=f"{genre} {mood} track",
        genre=genre,
        mood=mood,
        instruments=instruments,
        temperature=temperature,
        file_path="",
        user_id=current_user.id,
        created_at=datetime.datetime.utcnow()
    )

    db.session.add(new_track)
    db.session.commit()
    
    flash('New track generated successfully!', 'success')
    return redirect(url_for('dashboard.dashboard'))


# # dashboard.py (updated)
# from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
# from flask_login import login_required, current_user
# from extensions import db
# from models import MusicTrack, User
# import datetime
# import torch
# from models.music_transformer import MusicTransformer
# import os

# dashboard_bp = Blueprint('dashboard', __name__)

# # Load the trained model
# def load_model():
#     model_path = os.path.join(os.path.dirname(__file__), 'music_transformer_final.pt')
#     if not os.path.exists(model_path):
#         return None
    
#     checkpoint = torch.load(model_path, map_location='cpu')
#     model = MusicTransformer(checkpoint['vocab_size'])
#     model.load_state_dict(checkpoint['model_state_dict'])
#     model.eval()
#     return model, checkpoint['vocab']

# music_model, vocab = load_model()

# @dashboard_bp.route('/generate', methods=['POST'])
# @login_required
# def generate_track():
#     if not music_model:
#         flash('Music generation model not loaded', 'error')
#         return redirect(url_for('dashboard.dashboard'))
    
#     genre = request.form.get('genre')
#     mood = request.form.get('mood')
#     instruments = request.form.get('instruments', type=int)
#     temperature = request.form.get('temperature', type=float)
    
#     # Generate music based on parameters
#     try:
#         # Convert parameters to initial sequence
#         init_seq = [
#             f"GENRE_{genre.upper()}",
#             f"MOOD_{mood.upper()}",
#             f"INST_{instruments}",
#             f"TEMP_{temperature}"
#         ]
        
#         # Convert to indices
#         init_indices = [vocab[event] for event in init_seq if event in vocab]
        
#         # Generate music
#         generated_seq = generate_music_sequence(music_model, init_indices, vocab, 
#                                               temperature=temperature, 
#                                               max_length=200)
        
#         # Convert back to musical events
#         idx_to_event = {v: k for k, v in vocab.items()}
#         generated_events = [idx_to_event[idx] for idx in generated_seq]
        
#         # Create MIDI file from events
#         midi_file = events_to_midi(generated_events)
#         file_path = save_midi_file(midi_file, current_user.id)
        
#         # Save to database
#         new_track = MusicTrack(
#             title=f"{genre} {mood} track",
#             genre=genre,
#             mood=mood,
#             instruments=instruments,
#             temperature=temperature,
#             file_path=file_path,
#             user_id=current_user.id,
#             created_at=datetime.datetime.utcnow()
#         )
        
#         db.session.add(new_track)
#         db.session.commit()
        
#         flash('New track generated successfully!', 'success')
#         return jsonify({
#             'success': True,
#             'file_path': file_path,
#             'track_id': new_track.id
#         })
    
#     except Exception as e:
#         flash(f'Error generating music: {str(e)}', 'error')
#         return jsonify({'success': False, 'error': str(e)})

# def generate_music_sequence(model, init_seq, vocab, temperature=0.5, max_length=200):
#     """Generate a sequence of music events using the model"""
#     model.eval()
#     device = next(model.parameters()).device
    
#     with torch.no_grad():
#         # Start with initial sequence
#         generated = torch.tensor(init_seq, dtype=torch.long).unsqueeze(0).to(device)
        
#         for _ in range(max_length - len(init_seq)):
#             output = model(generated)
#             # Apply temperature to logits
#             logits = output[:, -1, :] / temperature
#             probs = torch.softmax(logits, dim=-1)
#             next_token = torch.multinomial(probs, num_samples=1)
#             generated = torch.cat((generated, next_token), dim=1)
            
#             # Stop if we generate the end token
#             if next_token.item() == vocab.get('END', -1):
#                 break
        
#         return generated.squeeze().tolist()

# def events_to_midi(events):
#     """Convert generated events back to MIDI"""
#     midi = pretty_midi.PrettyMIDI()
#     piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
#     piano = pretty_midi.Instrument(program=piano_program)
    
#     current_time = 0
#     current_notes = {}
    
#     for event in events:
#         if event.startswith('TIME_'):
#             time_shift = int(event.split('_')[1])
#             current_time += 0.01 * (2 ** time_shift)
#         elif event.startswith('NOTE_'):
#             pitch = int(event.split('_')[1])
#             current_notes[pitch] = {'start': current_time}
#         elif event.startswith('DUR_'):
#             duration = int(event.split('_')[1])
#             for pitch, note_info in current_notes.items():
#                 if 'duration' not in note_info:
#                     note_info['duration'] = 0.01 * (2 ** duration)
#         elif event.startswith('VEL_'):
#             velocity = int(event.split('_')[1]) * 4
#             for pitch, note_info in current_notes.items():
#                 if 'velocity' not in note_info:
#                     note_info['velocity'] = velocity
#                     # Create the note
#                     note = pretty_midi.Note(
#                         velocity=note_info['velocity'],
#                         pitch=pitch,
#                         start=note_info['start'],
#                         end=note_info['start'] + note_info['duration']
#                     )
#                     piano.notes.append(note)
#                     del current_notes[pitch]
    
#     midi.instruments.append(piano)
#     return midi

# def save_midi_file(midi, user_id):
#     """Save MIDI file to disk and return path"""
#     os.makedirs('static/audio', exist_ok=True)
#     filename = f"track_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mid"
#     filepath = os.path.join('static/audio', filename)
#     midi.write(filepath)
#     return filepath