import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import subprocess

class SpotifyApp:
    def __init__(self, root):
        # API Credentials 
        self.SPOTIPY_CLIENT_ID = 'your_client_id'
        self.SPOTIPY_CLIENT_SECRET = 'your_client_secret'

        # Initialize Spotipy
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.SPOTIPY_CLIENT_ID, client_secret=self.SPOTIPY_CLIENT_SECRET))

        # Dictionary to store album objects and their tracks
        self.albums = {}

        # Spotify color scheme
        self.spotify_green = "#1DB954"
        self.spotify_black = "#191414"
        self.spotify_white = "#FFFFFF"

        # Configure ttk Style
        self.style = ttk.Style()

        # Configure ttk Style for Treeview
        self.style.configure("Custom.Treeview.Heading", font=("Monochrome", 12), background=self.spotify_black, foreground=self.spotify_white)
        self.style.configure("Custom.Treeview", background=self.spotify_black, fieldbackground=self.spotify_black, foreground=self.spotify_white)
        self.style.map("Custom.Treeview", background=[("selected", self.spotify_green)])

        # Configure ttk Style for other widgets
        self.style.configure("TLabel", background=self.spotify_black, foreground=self.spotify_white, font=("Monochrome", 12))
        self.style.configure("TButton", background=self.spotify_green, foreground=self.spotify_black, font=("Monochrome", 12))

        # Configure root window background color
        root.configure(bg=self.spotify_black)

        # Create and place widgets for searching
        self.search_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
        self.search_frame.pack(pady=10, padx=10, side=tk.TOP)

        self.album_label = ttk.Label(self.search_frame, text="Enter Album:", style="TLabel")
        self.album_label.grid(row=0, column=0, padx=5)

        self.album_entry = ttk.Entry(self.search_frame)
        self.album_entry.grid(row=0, column=1, padx=5)

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_album, style="TButton")
        self.search_button.grid(row=0, column=2, padx=5)

        # Create canvas
        self.canvas = tk.Canvas(root, width=700, height=200, background=self.spotify_black)  # Increased dimensions
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)

        # Add the Spotify logo to the bottom left (resized and bigger)
        self.spotify_logo = Image.open("spotify_logo.png")  # Replace with the actual filename of your downloaded image
        self.spotify_logo = self.spotify_logo.resize((100, 100))
        self.spotify_logo = ImageTk.PhotoImage(self.spotify_logo)
        self.logo_label = ttk.Label(root, image=self.spotify_logo, background=self.spotify_black)
        self.logo_label.photo = self.spotify_logo  # Keep a reference to the image to prevent garbage collection
        self.logo_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a Frame for the album history
        self.frame = ttk.Frame(root)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create a Treeview for the album history
        self.album_tree = ttk.Treeview(self.frame, columns=("Album", "Artist"), height=10, show="headings", style="Custom.Treeview")
        self.album_tree.heading("Album", text="Album")
        self.album_tree.heading("Artist", text="Artist")
        self.album_tree.pack(side=tk.LEFT, padx=10)

        # Create a vertical scrollbar for the Treeview
        y_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.album_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.album_tree.configure(yscroll=y_scrollbar.set)

        # Button to clear the album list
        self.clear_button = ttk.Button(root, text="Clear List", command=self.clear_albums, style="TButton")
        self.clear_button.pack(side=tk.LEFT, pady=10)

        # Bind the function to load new songs when an item in the Treeview is selected
        self.album_tree.bind("<<TreeviewSelect>>", self.load_new_songs)

        # Run the installing.py file in a separate process
        subprocess.Popen(["python", "installing.py"])

    def search_album(self):
        album_name = self.album_entry.get()

        # Search for the album
        results = self.sp.search(q=album_name, type='album', limit=1)

        # Extract the album URI
        if results['albums']['items']:
            album_uri = results['albums']['items'][0]['uri']

            # Get all tracks for the album
            all_tracks = self.sp.album_tracks(album_uri)['items']

            # Randomly select 5 songs from the album
            random_tracks = random.sample(all_tracks, min(5, len(all_tracks)))

            # Display the results on the canvas
            self.canvas.delete("result_text")  # Clear previous results
            for i, track in enumerate(random_tracks):
                text = f"{i + 1}. {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}"
                self.canvas.create_text(10, 10 + i * 30, anchor="w", text=text, font=("Arial", 12), fill=self.spotify_white, tags="result_text")

            # Add the album to the dictionary
            self.albums[album_name] = all_tracks

            # Add the album to the Treeview
            self.album_tree.insert("", "end", values=(album_name, ', '.join([artist['name'] for artist in all_tracks[0]['artists']])))

    def load_new_songs(self, event):
        # Get the selected item in the Treeview
        selected_item = self.album_tree.selection()

        if selected_item:
            # Get the album name
            album_name = self.album_tree.item(selected_item, "values")[0]

            # Get all tracks for the selected album
            all_tracks = self.albums.get(album_name, [])

            # Randomly select 5 songs from the album
            random_tracks = random.sample(all_tracks, min(5, len(all_tracks)))

            # Display the results on the canvas
            self.canvas.delete("result_text")  # Clear previous results
            for i, track in enumerate(random_tracks):
                text = f"{i + 1}. {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}"
                self.canvas.create_text(10, 10 + i * 30, anchor="w", text=text, font=("Arial", 12), fill=self.spotify_white, tags="result_text")

    def clear_albums(self):
        self.albums = {}
        self.album_tree.delete(*self.album_tree.get_children())
        self.canvas.delete("result_text")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Spotify Top 5 Search")

    app = SpotifyApp(root)

    # Start the Tkinter event loop
    root.mainloop()
