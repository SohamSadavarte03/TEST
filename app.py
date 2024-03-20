from flask import Flask, render_template, request, flash, redirect, url_for, session, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone
from moviepy.editor import *
from PIL import Image
import tempfile
import numpy as np
import cv2
import time
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.VideoClip import ImageClip 

def img_to_nparray(img):
   
    nparr = np.frombuffer(img.img, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame


app = Flask(__name__, static_folder='static')

app.config.update(

    DROPZONE_MAX_FILE_SIZE=1024,  
    DROPZONE_TIMEOUT=5 * 60 * 1000  
)

dropzone = Dropzone(app)



app.config['SQLALCHEMY_DATABASE_URI'] = "cockroachdb://soham:x8CB0wqFZiiOx4JGlaeQJQ@aksphotoshop-8972.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/iss?sslmode=verify-full"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '3306'


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'home'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    username = db.Column(db.String(150))
    videos_made = db.Column(db.Integer)
    img = db.relationship('Img', backref='user')
    videos = db.relationship('Video', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username

    def get_num_images_uploaded(self):
        return len(self.img)

class Img(db.Model):
    __tablename__ = 'img'
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary(length=(2**32)-1))
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.LargeBinary(length=(2**32)-1))
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    user_id=session.get('user_id')
    if user_id:
        user=User.query.get(user_id)
        if user.email=="soham@123":
            return redirect(url_for('users'))
        if user.email=="krishiv@123":
            return redirect(url_for('users'))
        if user.email=="atharva@123":
            return redirect(url_for('users'))
        if user:
            login_user(user, remember=True)
            if user.email=="soham@123":
                return redirect(url_for('users'))
            if user.email=="krishiv@123":
                return redirect(url_for('users'))
            if user.email=="atharva@123":
                return redirect(url_for('users'))
            return redirect(url_for('home2'))
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    user=current_user
    if request.method == 'POST':
        users=User.query.all()
        email = request.form.get('email')
        password = request.form.get('password')

        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            session['user_id'] = user.id
            if(email=="soham@123" and password=="12345678"):
                # session['user_id'] = -1
                return redirect(url_for('users'))
        
            if(email=="krishiv@123" and password=="12345678"):
                # session['user_id'] = -1
                return redirect(url_for('users'))
            
            if(email=="atharva@123" and password=="12345678"):
                # session['user_id'] = -1
                return redirect(url_for('users'))
            
            return redirect(url_for('home2'))
        else:
            flash('Incorrect email or password. Please try again.', category='error')
    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['newEmail']
        first_name = request.form['newName']
        username = request.form['newUsername']
        password = generate_password_hash(request.form['newPassword'], method='pbkdf2:sha1')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            return render_template("signup.html")
        if len(email) < 4:
            flash('Email must be bigger than 4.', category='error')
        elif len(first_name) < 2:
            flash('Name must be bigger than 2.', category='error')
        elif len(username) < 2 :
            flash('Username must be bigger than 2.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=password, username=username, videos_made=0)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            session['user_id'] = new_user.id 
            return redirect(url_for('home2'))
    return render_template("signup.html")

@app.route('/home2', methods=['GET', 'POST'])
@login_required
def home2(user=None):
    user = current_user
    return render_template("home2.html", user=user)


@app.route('/slideshow', methods=['GET', 'POST'])
def slideshow(user=None):
    user = current_user
    user = User.query.options(db.joinedload(User.img)).filter_by(id=user.id).first()
    # print("why_such_skill_issue")
    if request.method=="POST": 
        # print("HI")
        selected_img=request.form.getlist("selected_images[]")
        print(selected_img)
        durations=request.form.getlist("duration")
        durations = [x for x in durations if x.strip()]
        print(durations)
        
        transitions=request.form.getlist("transition")
        print(transitions)
        
        audio_selection=[]
        transitions_selection=[]
        for i in selected_img:
            audio_selection.append(request.form.get(f"audio_{i}"))
            
        for i in selected_img:    
                transition_key = f"transition_{i}"
                transition_value = request.form.get(transition_key)
                print(f"Key: {transition_key}, Value: {transition_value}")
                transitions_selection.append(transition_value)
            
        print(transitions_selection)
        print(audio_selection)
        audio1=AudioFileClip('static/audio1.mp3')
        audio2=AudioFileClip('static/audio2.mp3')
        audio3=AudioFileClip('static/audio3.mp3')
        audio4=AudioFileClip('static/audio4.mp3')
        audio5=AudioFileClip('static/audio5.mp3')
        audio1_du=audio1.duration
        audio2_du=audio2.duration
        audio3_du=audio3.duration
        audio4_du=audio4.duration
        audio5_du=audio5.duration
        
        # print(img.img)
        selected_images=[]
        for i in selected_img:
            img = Img.query.filter_by(id=i).first()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(img.img)
                selected_images.append(temp_file.name)
        fixed_image_size = (1920, 1080)  # Fixed dimensions for all images
        resized_images = []
        for image_path in selected_images:
            try:
                image = Image.open(image_path)
                resized_image = image.resize(fixed_image_size)
                resized_image_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
                resized_image.save(resized_image_path)
                resized_images.append(resized_image_path)
            except Exception as e:
                print(f"Error processing image: {str(e)}")
        if resized_images:
            # Create image sequence clip
            print(resized_images)
            # image_duration = 1 
            # image_clip = ImageSequenceClip(resized_images, durations=[image_duration] * len(resized_images), fps=1)
            # clips=[]
            audios_list=[]
            j=0
            summ=0
            for i in resized_images:
                if audio_selection[j]=="audio1":
                    loop_count = int(float(durations[j]) / float(audio1_du)) + 1
                    # audio_clip = audio1.loop(duration=audio1_du*loop_count)
                    audio_clip=afx.audio_loop( audio1, duration=audio1_du*loop_count)
                    audio_clip = audio_clip.subclip(0, durations[j])
                    audios_list.append(audio_clip)
                if audio_selection[j]=="audio2":
                    loop_count = int(float(durations[j]) / float(audio2_du)) + 1
                    # audio_clip = audio1.loop(duration=audio1_du*loop_count)
                    audio_clip=afx.audio_loop( audio2, duration=audio2_du*loop_count)
                    audio_clip = audio_clip.subclip(0, durations[j])
                    audios_list.append(audio_clip)
                if audio_selection[j]=="audio3":
                    loop_count = int(float(durations[j]) / float(audio3_du)) + 1
                    # audio_clip = audio1.loop(duration=audio1_du*loop_count)
                    audio_clip=afx.audio_loop( audio3, duration=audio3_du*loop_count)
                    audio_clip = audio_clip.subclip(0, durations[j])
                    audios_list.append(audio_clip)
                if audio_selection[j]=="audio4":
                    loop_count = int(float(durations[j]) / float(audio4_du)) + 1
                    # audio_clip = audio1.loop(duration=audio1_du*loop_count)
                    audio_clip=afx.audio_loop( audio4, duration=audio4_du*loop_count)
                    audio_clip = audio_clip.subclip(0, durations[j])
                    audios_list.append(audio_clip)
                if audio_selection[j]=="audio5":
                    loop_count = int(float(durations[j]) / float(audio5_du)) + 1
                    # audio_clip = audio1.loop(duration=audio1_du*loop_count)
                    audio_clip=afx.audio_loop( audio5, duration=audio5_du*loop_count)
                    audio_clip = audio_clip.subclip(0, durations[j])
                    audios_list.append(audio_clip)
                summ+=int(durations[j])
                j+=1
        
            final_audio_clip = concatenate_audioclips(audios_list)
            clips = []
            j = 0

            for i in resized_images:
                    x=ImageClip(i).set_duration(durations[j])
                    x = fadein(x, duration=1)
                    clips.append(x)
            j=0
            videos=[]
            for i in resized_images:
                if transitions_selection[j]=="transition4":  
                    clips[j]=CompositeVideoClip([clips[j].fx(transfx.slide_in, duration=1, side="right").fx(transfx.fadein, duration=1)]) 
                    videos.append(clips[j]) 
                if transitions_selection[j]=="transition2":  
                    clips[j]=CompositeVideoClip([clips[j].fx(transfx.slide_in, duration=1, side="top").fx(transfx.fadein, duration=1)]) 
                    videos.append(clips[j])
                if transitions_selection[j]=="transition1":  
                    clips[j]=CompositeVideoClip([clips[j].fx(transfx.slide_in, duration=1, side="bottom").fx(transfx.fadein, duration=1)]) 
                    videos.append(clips[j])    
                if transitions_selection[j]=="transition3":  
                    clips[j]=CompositeVideoClip([clips[j].fx(transfx.slide_in, duration=1, side="left").fx(transfx.fadein, duration=1)]) 
                    videos.append(clips[j])         
                j+=1         
            # videos= [CompositeVideoClip([
            #                 clip.fx(transfx.slide_in, duration=0.4, side="top")])
            #                 for clip in clips
            #             ]
            video = concatenate_videoclips(videos, method="compose")
            video = video.set_audio(final_audio_clip)
            video_720p = video.resize(width=1280, height=720)
            video_144p = video.resize(width=256, height=144)
            # video=video.resize(width=256, height=144)
            # video.write_videofile("static/output.mp4",fps=24)   
            with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
                video.write_videofile(temp_file.name, fps=24)
                video_data = temp_file.read()
            with tempfile.NamedTemporaryFile(suffix='_720p.mp4') as temp_file_720p:
                # Resize the video to 720p
               
                video_720p.write_videofile(temp_file_720p.name, fps=24)
                video_720p_data = temp_file_720p.read()
            with tempfile.NamedTemporaryFile(suffix='_144p.mp4') as temp_file_144p:
                # Resize the video to 144p
                video_144p.write_videofile(temp_file_144p.name, fps=24)
                video_144p_data = temp_file_144p.read()
                
            new_video_720p = Video(user_id=user.id, vid=video_720p_data, name="output_720p.mp4")
            new_video_144p = Video(user_id=user.id, vid=video_144p_data, name="output_144p.mp4")
            # Save the video data to the database
            new_video = Video(user_id=user.id, vid=video_data, name="output.mp4")
            for video in user.videos:
                db.session.delete(video)
            # user.videos_made+=1
            db.session.commit()
            db.session.add(new_video)
            db.session.add(new_video_720p)
            db.session.add(new_video_144p)
            db.session.commit()
            timestamp = int(time.time())
            return render_template("slideshow.html", user=user, timestamp=timestamp)
            
            # for i in range(len(resized_images)):
            #     # resized_images[i]=fadein(resized_images[i],duration=1)
            #     image_clip = ImageClip(resized_images[i]).set_duration(durations[j])
            #     if(i==0):
            #         image_clip=fadein(image_clip,1)
            #     # Convert ImageClip to VideoClip by setting dummy audio
            #     audio = AudioClip(lambda t: [0], duration=image_clip.duration)
            #     video_clip = image_clip.set_audio(audio)
            #     clips.append(video_clip)


            # overlap = 2
            # composite_clips = [clips[0].crossfadeout(overlap)]

            # for i in range(1, len(clips)):
            #     start_time = sum(clip.duration for clip in clips[:i]) - overlap
            #     composite_clips.append(clips[i].set_start(start_time).crossfadein(overlap))

            # # final_clip = CompositeVideoClip(composite_clips)
            # image_clip=concatenate_videoclips(composite_clips,method="compose")
            # image_clip = image_clip.set_audio(final_audio_clip)
            # image_clip.write_videofile('static/output.mp4', fps=24)
            
            
            
            
            # audio_clip = AudioFileClip('static/Easter-chosic.com_.mp3')
            # audio_clip = audio_clip.set_duration(summ)
            # image_clip=concatenate_videoclips(clips,method="compose")
            # image_clip = image_clip.set_audio(final_audio_clip)
            # looped_audio = audio_clip.fx(vfx.audi o_loop, duration=image_clip.duration)
            # image_clip=image_clip.set_audio(audio_clip)
            # Export the final video
            # image_clip.write_videofile('static/output.mp4', fps=24)

                # Redirect to the same page with the generated video URL
            # return redirect(url_for('display'))
        else:
            print("No valid images found.")

            
        
        
    return render_template("slideshow.html", user=user)

@app.route('/dropphoto', methods=['GET', 'POST'])
def dropphoto(user=None):
    user = current_user
    print(request.method)
    # if request.method == "POST":    

    #     if 'file' not in request.files:
    #         return 'No file part'
        
    #     files = request.files.getlist('file')
    #     for pic in files:
    #         filename = secure_filename(pic.filename)
    #         mimetype = pic.mimetype
    #         if filename == "":
    #             continue
    #         img = Img(img=pic.read(), name=filename, mimetype=mimetype, user_id=user.id)
    #         db.session.add(img)
    #         db.session.commit()
    if request.method == "POST":
        # Check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part', category='error')
            return redirect(request.url)

        files = request.files.getlist('file')
        for pic in files:
            # Validate the file type if necessary
            if pic.filename == '':
                # flash('No selected file', category='error')
                continue
            if pic:
                # Read the file content
                file_content = pic.read()
                # Check if the file content is empty
                if len(file_content) == 0:
                    # flash('Empty file uploaded', category='error')
                    continue
                # Store the image in the database
                img = Img(img=file_content, name=secure_filename(pic.filename), mimetype=pic.mimetype, user_id=user.id)
                db.session.add(img)
                db.session.commit()
                # flash('File uploaded successfully', category='success')




    return render_template("dropphoto.html", user=user)

@app.route('/display')
def display():
    user=current_user
    timestamp = int(time.time())
    return render_template("display.html", user=user, timestamp=timestamp)
    
@app.route('/get_video/<int:user_id>')
def get_video(user_id):
    user = User.query.get(user_id)
    if not user:
        return 'User not found', 404
    
    # Assuming there is only one video per user for simplicity
    video = user.videos[0]
    if not video:
        return 'Video not found', 404
    
    # Return the video data as a response
    return Response(video.vid, mimetype='video/mp4')

@app.route('/users')
def users():
    user=current_user
    users=User.query.all()
    return render_template("users.html", yes=user, users=users)

@app.route('/get_video_720/<int:user_id>')
def get_video_720(user_id):
    user = User.query.get(user_id)
    if not user:
        return 'User not found', 404
    
    # Assuming there is only one video per user for simplicity
    video = user.videos[1]
    if not video:
        return 'Video not found', 404
    
    # Return the video data as a response
    return Response(video.vid, mimetype='video/mp4')


@app.route('/get_video_144/<int:user_id>')
def get_video_144(user_id):
    user = User.query.get(user_id)
    if not user:
        return 'User not found', 404
    
    # Assuming there is only one video per user for simplicity
    # video = user.videos[2]
    for i in user.videos:
        if i.name=="output_144p.mp4":
            video=i
            break
    
    if not video:
        return 'Video not found', 404
    
    # Return the video data as a response
    return Response(video.vid, mimetype='video/mp4')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('home'))




@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Please log in to access this page.', category='error')
    return redirect(url_for('login'))


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    create_tables()

    app.run(debug=True, port=9000)




