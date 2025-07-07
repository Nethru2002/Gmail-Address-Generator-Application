# gmail-generator/app.py

# --- 1. Imports ---
# Flask is the web framework. render_template serves the HTML page.
# request handles incoming data, and jsonify formats our response as JSON.
from flask import Flask, render_template, request, jsonify
# Flask-CORS handles Cross-Origin Resource Sharing, allowing our frontend JS to talk to this backend.
from flask_cors import CORS
import random
import re  # 're' is the regular expressions module, used for cleaning the input name.

# --- 2. App Initialization ---
app = Flask(__name__)
# Enable CORS for all routes, allowing requests from any origin.
CORS(app)

# --- 3. Core Logic Function ---
def generate_emails(name, quantity):
    """
    Generates a list of unique email addresses based on a name.

    Args:
        name (str): The user's full name.
        quantity (int): The number of email addresses to generate.

    Returns:
        list: A list of unique email address strings.
    """
    if not name or not name.strip():
        return []

    # Sanitize the name: remove special characters (except spaces) and convert to lowercase.
    # This ensures "John-Doe!" becomes "john doe".
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name).lower()
    parts = name.split()
    
    if not parts:
        return []
        
    first_name = parts[0]
    last_name = parts[-1] if len(parts) > 1 else ""

    # Create a set of base variations to avoid duplicates.
    base_variations = set()
    
    # Generate common username patterns
    if last_name:
        base_variations.add(f"{first_name}{last_name}")
        base_variations.add(f"{first_name}.{last_name}")
        base_variations.add(f"{last_name}{first_name}")
        base_variations.add(f"{last_name}.{first_name}")
        base_variations.add(f"{first_name}{last_name[0]}")
        base_variations.add(f"{first_name}.{last_name[0]}")
        base_variations.add(f"{first_name[0]}{last_name}")
        base_variations.add(f"{first_name[0]}.{last_name}")
        base_variations.add(f"{first_name}_{last_name}")
        base_variations.add(f"{last_name}_{first_name}")
    else:
        # If only a first name is provided
        base_variations.add(first_name)

    base_variations_list = list(base_variations)
    if not base_variations_list:
        return []

    # Use a set for the final list to guarantee all emails are unique.
    generated_emails = set()
    
    # First, add the clean base variations if the quantity allows
    for variation in base_variations_list:
        if len(generated_emails) < quantity:
            generated_emails.add(f"{variation}@gmail.com")
        else:
            break

    # If more emails are needed, add random numbers to the base variations
    while len(generated_emails) < quantity:
        base = random.choice(base_variations_list)
        number = random.randint(10, 9999)
        separator = random.choice(['', '.', '_'])
        
        # To avoid double separators like "name..123"
        if base.endswith('.') or base.endswith('_'):
            separator = ''

        new_email = f"{base}{separator}{number}@gmail.com"
        generated_emails.add(new_email)
        
    return list(generated_emails)

# --- 4. API and Page Routes ---

@app.route('/')
def index():
    """
    This route serves the main web page (index.html).
    Flask will look for 'index.html' in a folder named 'templates'.
    """
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def handle_generation_request():
    """
    This is the API endpoint that receives the generation request from the frontend.
    It expects a JSON payload with 'name' and 'quantity'.
    """
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # --- Input Validation ---
    if not data or 'name' not in data or 'quantity' not in data:
        return jsonify({"error": "Invalid input. 'name' and 'quantity' are required."}), 400
        
    name = data.get('name')
    try:
        quantity = int(data.get('quantity'))
        # Set a reasonable limit to prevent server overload
        if not (0 < quantity <= 5000):
             return jsonify({"error": "Quantity must be an integer between 1 and 5000."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity must be a valid integer."}), 400

    # Call the core logic function
    emails = generate_emails(name, quantity)
    
    # Return the generated emails as a JSON response
    return jsonify({"emails": emails})

# --- 5. Run the Application ---
if __name__ == '__main__':
    # This block runs only when the script is executed directly (not imported)
    # host='0.0.0.0' makes the server accessible on your local network
    # debug=True enables auto-reloading and provides detailed error pages
    app.run(host='0.0.0.0', port=5000, debug=True)