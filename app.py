from flask import Flask, render_template, request
import webview
from downloader import readm
from tinymongo import TinyMongoClient
import multiprocessing
import psutil
import json

# Define flask app and window
app = Flask(__name__, static_url_path='/static')
window = webview.create_window('Manga Downloader', app, width=1100, height=700, frameless=True)

@app.route('/')
def index():
    downloads = db.downloads.find()
    return render_template('index.html', downloads = downloads)

@app.route('/close_window', methods=["POST"])
def close_window():
    window.destroy()
    return "closed_window"

@app.route('/minimize_window', methods=["POST"])
def minimize_window():
    window.minimize()
    return "minimized_wwindow"

@app.route('/maximize_window', methods=["POST"])
def maximize_window():
    if window.width == 1084:
        window.resize(width=1250, height=850)
    else:
        window.resize(width=1084, height=661)
    return "maximized_window"

@app.route('/start_download', methods=['POST'])
def start_download():
    supported_websites = ['readm']
    download_link = request.form['download_link']

    if download_link.strip() == "" or download_link.split(".")[1] not in supported_websites:
        return {"success": False}

    # Get Manga details from website
    website_name = download_link.split(".")[1]
    if website_name == "readm":
        download_id = db.downloads.insert_one({
            "website_name": website_name,
            "download_link": download_link
        }).inserted_id
        download_data = readm.get_details(download_link, website_name)

        # Start download in background process
        process = multiprocessing.Process(target=readm.download, args=(download_link, download_data['title'], download_id,))
        process.start()
        process_id = process.pid

    db.downloads.update({"_id":download_id},{
        "website_name": website_name,
        "domain": download_data['domain'],
        "image_url": download_data['image_url'],
        "title": download_data['title'],
        "chapters": download_data['chapters'],
        "status": "Downloading",
        "process_id": process_id,
        "progress": 0
        })

    download = db.downloads.find_one({"_id": download_id})

    return {"success": True, "download_data": download}

@app.route('/delete_download', methods=['POST'])
def delete_download():
    download_id = request.form['download_id']

    # Get download from database
    download = db.downloads.find_one({"_id": download_id})

    # If download is still in progress then stop process
    if download['status'] == "Downloading":
        process_id = download['process_id']

        #Kill process
        try:
            process = psutil.Process(process_id)
            process.terminate()
        except:
            pass #process already closed

    # Delete download from database
    db.downloads.delete_one({'_id': download_id})

    return {"success": True}

@app.route('/get_progress', methods=['GET'])
def get_progress():
    # Get downloads from database
    downloads = list(db.downloads.find())

    return {"downloads": downloads}

if __name__ == "__main__":
    #Connect to the database
    connection = TinyMongoClient("database")
    db = connection.database

    #Start flask app
    webview.start()
    #app.run(debug=True)