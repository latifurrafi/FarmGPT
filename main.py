from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv('GENAI_API_KEY')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Configure Google Generative AI
if not API_KEY:
    raise ValueError("Missing API key for Google Generative AI")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Path to store the latest response
RESPONSE_FILE_PATH = 'latest_response.txt'

# Farming recommendation endpoint
# Modify the chat endpoint to store environmental data
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'temperature' not in data or 'humidity' not in data or 'soil_moisture' not in data or 'plant_type' not in data or 'plant_name' not in data:
            return jsonify({'error': 'Invalid input data'}), 400

        # Extract input values
        temperature = data['temperature']
        humidity = data['humidity']
        soil_moisture = data['soil_moisture']
        plant_type = data['plant_type']
        plant_name = data['plant_name']

        # Create prompt context
        context = f"""
        Objective: Generate personalized farming recommendations based on real-time environmental data and plant-specific needs.

        Input Data:
        - Temperature: {temperature}°C
        - Humidity: {humidity}%
        - Soil Moisture: {soil_moisture} (capacitive reading)
        - Plant Type: {plant_type}
        - Plant Name: {plant_name}
        
        Provide a concise recommendation on watering, fertilization, and overall plant care.
        """

        # Generate AI response
        response = model.generate_content(context)
        recommendation = response.text

        # Store data in a text file
        with open(RESPONSE_FILE_PATH, 'w') as file:
            file.write(f"{temperature},{humidity},{soil_moisture}\n{recommendation}")

        return jsonify({'recommendation': recommendation})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Modify latest-response endpoint to return temperature, humidity, and moisture
@app.route('/latest-response', methods=['GET'])
def latest_response():
    try:
        if os.path.exists(RESPONSE_FILE_PATH):
            with open(RESPONSE_FILE_PATH, 'r') as file:
                lines = file.readlines()
                if len(lines) < 2:
                    return jsonify({'error': 'Data format incorrect'}), 500
                
                # Extract stored data
                temp, humidity, moisture = lines[0].strip().split(',')
                recommendation = lines[1].strip()

            return jsonify({
                'temperature': temp,
                'humidity': humidity,
                'soil_moisture': moisture,
                'response': recommendation
            })
        else:
            return jsonify({'error': 'No data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
