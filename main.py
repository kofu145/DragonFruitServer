from flask import Flask, jsonify, request, send_file, send_from_directory
from werkzeug.utils import secure_filename
import json
import uuid
import os
import copy
from tesseract_analyzer import TextAnalyzer
from invalidusage import InvalidUsage
import shutil

app = Flask('app')
local_url = "http://traptrixden.ddns.net:5698/"

textAnalyzer = TextAnalyzer()

with open("posts.json", "rb") as f:
	posts = json.load(f)

with open("users.json", "rb") as f:
	users = json.load(f)

with open("sessions.json", "rb") as f:
	sessions = json.load(f)



def authenticate(auth_token):
	authenticated=False
	for session in sessions:
		if session["auth"] == auth_token:
			authenticated=True
	return authenticated

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response


@app.route("/", methods=["GET", "POST"])
def hello_world():
	return jsonify({"message": "hello world!"})

@app.route("/image", methods=["POST"])
def process_image():
	# byte file
	print(request.files)
	print(request.form)
	"""
	file = request.files['image'].read()
	npimg = np.fromstring(file, np.uint8)
	img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
	if os.path.exists("./results"):
		shutil.rmtree("./results")
	trashAnalyzer.process_image(img)"""
	f = request.files['image']
	filename = "analyze" + os.path.splitext(f.filename)[1]
	print(secure_filename(filename))
	f.save(secure_filename(filename))
	msg = textAnalyzer.analyze_text(filename)
	print(msg)
	print(filename)
	return jsonify({"message": "{}".format(msg)}), 200

@app.route("/profile_images/<path:filename>", methods=["GET"])
def download(filename):
	uploads = "profile_pictures/"
	return send_from_directory(uploads, filename)

@app.route("/login", methods=["POST"])
def login():
	print(request.form)
	for session in sessions:
		if session["username"] == request.form["username"]:
			response = {
				"username": request.form["username"],
				"name": session["name"],
				"email": session["email"],
				"grade": session["grade"],
				"points": session["points"],
				"languages": session["languages"],
				"auth": session["auth"],
				"profilepicture": local_url + "profile_images/" + session["username"] + ".jpg",
				"message": "Already logged in!"
			}
			return jsonify(response), 200

	user_exists=False
	for user in users:
		if user["username"] == request.form["username"]:
			user_exists=True

	if not user_exists:
		raise InvalidUsage("Not signed up!", status_code=400)
	new_auth = {}
	# extremely unsecure and not great way to save/check passwords but this is a hackathon what do you want
	pwd_check = False
	for user in users:
		if request.form["password"] == user["password"]:
			new_auth = {
				"username": user["username"],
				"name": user["name"],
				"email": user["email"],
				"grade": user["grade"],
				"points": user["points"],
				"languages": user["languages"],
				"profilepicture": local_url + "profile_images/" + user["username"] + ".jpg",
				"auth": str(uuid.uuid4())
			}
			pwd_check = True

	if not pwd_check:
		raise InvalidUsage("Invalid Password!", status_code=401)

	

	sessions.append(new_auth)
	with open("sessions.json", "w") as f:
		json.dump(sessions, f, indent=2)

	new_auth["message"] = "Successfully logged in!"

	return jsonify(new_auth), 200


@app.route("/signup", methods=["POST"])
def signup():
	print(request.form)
	if request.form["username"] == "":
		raise InvalidUsage("Username cannot be empty!", status_code=400)

	if request.form["username"] not in users:
		users.append(request.form["username"])
		with open("users.json", "w") as f:
			json.dump(users, f, indent=2)

	else:
		raise InvalidUsage("Username already exists!", status_code=400)

	return jsonify({"message": "Account Created!"}), 200

@app.route("/buddies", methods=["GET"])
def find_buddies():
	if not authenticate(request.args.get("auth")):
		raise InvalidUsage("Invalid authentication token!", status_code=400)
	return_users = []
	for user in users:
		add_user = copy.deepcopy(user)
		add_user["profilepicture"] = local_url + "profile_images/" + user["username"] + ".jpg"
		return_users.append(add_user)
	return jsonify(return_users), 200

@app.route("/posts", methods=["POST", "GET"])
def modify_posts():	

	if (request.method == "POST"):

		if not authenticate(request.form["auth"]):
			raise InvalidUsage("Invalid authentication token!", status_code=400)
		# request form is appended 
		post = {
			"author": request.form["author"],
			"profilepicture": local_url + "profile_images/" + request.form["author"] + ".jpg",
			"title": request.form["title"],
			"is_qa": False,
			"name": request.form["name"],
			"points": 0,
			"replies": [],
			"reply_count": 0,
			"content": request.form["content"],
			"points": 0
		}
		posts.append(post)

		with open("posts.json", "wb") as f:
			json.dump(posts, f, indent=2)
		return jsonify({"message": "Successfully made new post!"}), 200

	if (request.method == "GET"):
		if not authenticate(request.args.get("auth")):
			raise InvalidUsage("Invalid authentication token!", status_code=400)

		return jsonify(posts), 200

	raise InvalidUsage("Invalid method!", status_code=400)

app.run(host='0.0.0.0', port=5698) #ssl_context="adhoc")