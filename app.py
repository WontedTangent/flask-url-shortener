import psycopg2
import string
import random
from flask import Flask, request, redirect

app = Flask(__name__)

# Provided PostgreSQL connection string.
DATABASE_URL = "REDACTED"

def get_connection():
    """Connects to PostgreSQL using the provided DATABASE_URL."""
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Initializes the database by creating the 'urls' table if it doesn't exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    short_url TEXT UNIQUE NOT NULL,
                    long_url TEXT NOT NULL
                )
            """)
            conn.commit()

# Initialize the database table on startup.
init_db()

def generate_short_url():
    """Generates a random 6-character string for the short URL."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=6))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form.get("long_url")
        if not long_url:
            return "Please enter a valid URL", 400
        
        # Generate a short URL code.
        short_url = generate_short_url()
        
        # Insert the mapping into the database.
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO urls (short_url, long_url)
                    VALUES (%s, %s)
                    RETURNING id
                """, (short_url, long_url))
                conn.commit()
        
        # Display the complete short URL.
        return f"Short URL: {request.host_url}{short_url}"
    
    # Return a simple HTML form on GET.
    return '''
    <form method="POST">
      <input name="long_url" placeholder="Enter a long URL" required>
      <button type="submit">Shorten</button>
    </form>
    '''

@app.route("/<short_url>")
def redirect_short_url(short_url):
    # Look up the long URL in the database.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT long_url FROM urls WHERE short_url = %s", (short_url,))
            row = cur.fetchone()
    if row:
        return redirect(row[0])
    return "Short URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)
