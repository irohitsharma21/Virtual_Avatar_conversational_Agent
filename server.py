import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from livekit import api

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/token', methods=['POST'])
def generate_token():
    data = request.json or {}
    room = data.get('room')
    identity = data.get('identity')

    if not room or not identity:
        return jsonify({"error": "Missing 'room' or 'identity' parameters."}), 400

    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([url, api_key, api_secret]):
        return jsonify({"error": "LiveKit credentials are not fully configured on the server."}), 500

    try:
        # Generate the access token using the LiveKit SDK
        dispatch = api.RoomAgentDispatch(agent_name="my-agent")
        room_config = api.RoomConfiguration(agents=[dispatch])

        token_generator = (
            api.AccessToken(api_key, api_secret)
            .with_identity(identity)
            .with_name(identity)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room,
                )
            )
            .with_room_config(room_config)
        )
        
        jwt_token = token_generator.to_jwt()
        
        return jsonify({
            "token": jwt_token,
            "url": url
        })
    except Exception as e:
        app.logger.error(f"Error generating token: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the server on port 5000
    print("--------------------------------------------------")
    print("  Real-time Avatar Client Server running at:      ")
    print("  http://localhost:5000                           ")
    print("--------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=True)
