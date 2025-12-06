from flask import Flask, render_template, request, jsonify
from config import Config
from db import db_instance
from utils.helpers import save_upload
from ai_engine.pipeline import start_job, run_full_pipeline, generate_job_id, get_job_status

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db_instance.uri = app.config['MONGO_URI']
if not db_instance.connect():
    print("WARNING: MongoDB connection failed. check your settings.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filepath, filename = save_upload(file)
    if not filepath:
        return jsonify({"error": "Invalid file type"}), 400
        
    # Start Job
    job_id = generate_job_id()
    # Pass False for is_url
    start_job(job_id, run_full_pipeline, filepath, False)
    
    return jsonify({"message": "Upload successful", "job_id": job_id})

@app.route('/process-url', methods=['POST'])
def process_url():
    data = request.json
    url = data.get('url')
    if not url:
         return jsonify({"error": "No URL provided"}), 400
         
    job_id = generate_job_id()
    start_job(job_id, run_full_pipeline, url, True)
    
    return jsonify({"message": "URL processing started", "job_id": job_id})

@app.route('/status/<job_id>')
def job_status(job_id):
    status = get_job_status(job_id)
    return jsonify(status)

@app.route('/result/<job_id>')
def result_page(job_id):
    # Serve the HTML page. JS will fetch data.
    return render_template('result.html', job_id=job_id)

@app.route('/api/result/<job_id>')
def get_result_data(job_id):
    if db_instance.db is None:
        return jsonify({"error": "Database not connected"}), 500
        
    job = db_instance.db.jobs.find_one({"job_id": job_id})
    if not job or "result_id" not in job:
        return jsonify({"error": "Result not found"}), 404
        
    result = db_instance.db.transcripts.find_one({"_id": job["result_id"]})
    if result:
        # Convert ObjectId to string for JSON serialization
        result["_id"] = str(result["_id"])
        return jsonify(result)
    return jsonify({"error": "Transcript data missing"}), 404

@app.route('/download/<file_type>/<job_id>')
def download_result(file_type, job_id):
    if db_instance.db is None:
         return "Database disconnected", 500
         
    job = db_instance.db.jobs.find_one({"job_id": job_id})
    if not job or "result_id" not in job:
        return "Result not found", 404
        
    result = db_instance.db.transcripts.find_one({"_id": job["result_id"]})
    if not result:
        return "Transcript not found", 404
    
    from utils.exporters import generate_pdf, generate_srt
    import os
    from flask import send_file
    
    filename = f"{job_id}.{file_type}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    if file_type == 'pdf':
        generate_pdf(result['transcript'], result['summary'], filepath)
    elif file_type == 'srt':
        generate_srt(result['transcript'], filepath)
    else:
        return "Invalid format", 400
        
    return send_file(filepath, as_attachment=True, download_name=f"transcript_{job_id}.{file_type}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
