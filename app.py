import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import Song, Genre


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'Song': Song, 'Genre': Genre}


from app import app

# from flask import Flask, request, jsonify, render_template
# import sqlite3
# import random
#
# app = Flask(__name__)
#
#
# # Function to connect to the SQLite database
# def connect_db():
#     conn = sqlite3.connect('database.db')
#     return conn
#
#
# # Endpoint to handle the user's request
# @app.route('/get-songs', methods=['POST'])
# def get_songs():
#     # Get user inputs from the frontend
#     print("get_songs function reached!")
#     data = request.get_json()
#     genre_id = data['genre']
#     x = float(data['x'])
#     y = float(data['y'])
#     print(x, y)
#
#     happy_prob = x * y
#     aggressive_prob = (1 - x) * y
#     sad_prob = (1 - x) * (1 - y)
#     calm_prob = x * (1 - y)
#     threshold = 0.05
#     # Connect to the database
#     conn = connect_db()
#     cursor = conn.cursor()
#
#     # Query to retrieve songs based on genre and happy_prob, aggressive_prob, sad_prob, calm_prob thresholds
#     query = """
#     SELECT * FROM songs
#     WHERE genre_id = ? AND happy BETWEEN ? AND ?
#     AND aggressive BETWEEN ? AND ? AND sad BETWEEN ? AND ?
#     AND calm BETWEEN ? AND ?
#     """
#     cursor.execute(query, (
#         genre_id,
#         happy_prob - threshold, happy_prob + threshold,
#         aggressive_prob - threshold, aggressive_prob + threshold,
#         sad_prob - threshold, sad_prob + threshold,
#         calm_prob - threshold, calm_prob + threshold))
#
#     # Fetch all matching songs
#     songs = cursor.fetchall()
#
#     # If there are less than 20 songs, increase the threshold until there are 20
#     while len(songs) < 20:
#         threshold += 0.01
#         cursor.execute(query, (
#             genre_id,
#             happy_prob - threshold, happy_prob + threshold,
#             aggressive_prob - threshold, aggressive_prob + threshold,
#             sad_prob - threshold, sad_prob + threshold,
#             calm_prob - threshold, calm_prob + threshold))
#         songs = cursor.fetchall()
#
#     # Randomly select 20 songs
#     selected_songs = random.sample(songs, 20)
#
#     # Close database connection
#     conn.close()
#
#     # Return selected songs to the frontend
#     return jsonify(selected_songs)
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
#     print(app.url_map)
