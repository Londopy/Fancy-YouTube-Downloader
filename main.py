try:
	import tkinter as tk
	from tkinter import *
	from tkinter import filedialog
	from pytube import YouTube, Search, Playlist
	import os
	import sys
	import re
	import requests
	import json
	import subprocess
	import webbrowser
	import urllib.request, urlopen
	from PIL import Image, ImageTk
	import google.oauth2.credentials
	from googleapiclient.discovery import build
	from googleapiclient.errors import HttpError
except ModuleNotFoundError:
	from subprocess import call
	modules = ["pytube","google-api-python-client","Pillow","python-tk"]
	call("pip install " + ' '.join(modules), shell=True)

def run_as_admin():
	"""Run the program as an administrator."""
	if os.name == "nt" and sys.platform.startswith("win"):
		# Get the path of the current script
		script_path = os.path.abspath(sys.argv[0])

		# Run the script as an administrator using the "runas" command
		subprocess.run(["runas", "/user:Administrator", script_path])
		sys.exit()


"""
def play_video(downloaded_file):
	# Play the video in a new window.
	player_window = tk.Toplevel(root)
	player_window.geometry('640x360')
	player_window.title('Video Preview')

	# Create a video player using OpenCV
	import cv2
	cap = cv2.VideoCapture(downloaded_file)

	# Define the function to update the video frame
	def update_frame():
		ret, frame = cap.read()
		if ret:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			frame_image = Image.fromarray(frame)
			frame_tk = ImageTk.PhotoImage(frame_image)
			player_canvas.create_image(0, 0, anchor=NW, image=frame_tk)
			player_canvas.image = frame_tk
			player_canvas.after(10, update_frame)
		else:
			cap.release()

	# Create a canvas to hold the video frame
	player_canvas = Canvas(player_window, width=640, height=360, bg='black')
	player_canvas.pack()

	# Start playing the video
	update_frame()
"""



def update_video_list():
	search_term = search_entry.get()
	search_results = Search(search_term).results[:10]
	create_video_window = tk.Toplevel(root)
	create_video_window.title("YouTube Search Results")
	create_video_window.geometry("900x700")
	create_video_window.iconbitmap('yt.ico')
	create_video_window.configure(background='#bec8d1')

	# Create a canvas to hold the video list and add a scrollbar
	canvas = Canvas(create_video_window, bg='white')
	scrollbar = Scrollbar(create_video_window, orient='vertical', command=canvas.yview)
	canvas.configure(yscrollcommand=scrollbar.set)
	scrollbar.pack(side='right', fill='y')
	canvas.pack(side='left', fill='both', expand=True)

	# Bind the mouse scroll event to the canvas widget
	canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

	# Create a frame to hold the video list inside the canvas
	video_frame = Frame(canvas, bg='white')
	video_frame.pack(side='top', fill='both', expand=True)

	# Add the video list to the frame
	for i, video in enumerate(search_results):
		# get thumbnail
		img_url = video.thumbnail_url
		with open(f"thumbnail_{i}.jpg", "wb") as file:
			file.write(requests.get(img_url).content)
		thumbnail = Image.open(f"thumbnail_{i}.jpg")
		thumbnail = thumbnail.resize((200, 150))
		thumbnail_tk = ImageTk.PhotoImage(thumbnail)

		# create video thumbnail label
		thumbnail_label = Label(video_frame, image=thumbnail_tk)
		thumbnail_label.image = thumbnail_tk
		thumbnail_label.grid(row=i, column=0)

		# Bind the click event to the thumbnail label
		thumbnail_label.bind('<Button-1>', lambda event, index=i: select_video(event, index, search_results))

		# create video title label
		title_label = Label(video_frame, text=video.title, font=('times', 12, 'bold'))
		title_label.grid(row=i, column=1)

	# create load more button
	load_more_button = Button(video_frame, text="Load More", font=('times', 12, 'bold'), command=lambda: load_more_videos(canvas, video_frame, search_term))
	load_more_button.grid(row=len(search_results), column=1, pady=10)

	# Set the scrollable region to the frame
	video_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
	canvas.create_window((0, 0), window=video_frame, anchor='nw')

def select_video(event, index, search_results):
	# Get the video URL for the clicked thumbnail
	video_url = search_results[index].watch_url

	# Set the URL as the text of the 'entry' widget
	entry.delete(first=0, last=50)
	entry.insert(0, video_url)


def select_video(event, index, search_results):
	# Get the video URL for the clicked thumbnail
	video_url = search_results[index].watch_url

	# Set the URL as the text of the 'entry' widget
	entry.delete(first=0, last=50)
	entry.insert(0, video_url)
	
def load_more_videos(canvas, video_frame, search_term):
	# Remove the existing "Load More" button
	for widget in video_frame.winfo_children():
		if isinstance(widget, Button) and widget["text"] == "Load More":
			widget.destroy()

	current_videos = len(video_frame.winfo_children())
	search_results = Search(search_term).results[current_videos:current_videos+10]
	for i, video in enumerate(search_results):
		# get thumbnail
		img_url = video.thumbnail_url
		with open(f"thumbnail_{i+current_videos}.jpg", "wb") as file:
			file.write(requests.get(img_url).content)
		thumbnail = Image.open(f"thumbnail_{i+current_videos}.jpg")
		thumbnail = thumbnail.resize((200, 150))
		thumbnail_tk = ImageTk.PhotoImage(thumbnail)

		# create video thumbnail label
		thumbnail_label = Label(video_frame, image=thumbnail_tk)
		thumbnail_label.image = thumbnail_tk
		thumbnail_label.grid(row=current_videos+i, column=0)

		# create video title label
		title_label = Label(video_frame, text=video.title, font=('times', 12, 'bold'))
		title_label.grid(row=current_videos+i, column=1)

#		# create video button
#		download_button = Button(video_frame, text="Download", font=('times', 12, 'bold'), command=lambda v=video: download_video_from_result(v))
#		download_button.grid(row=current_videos+i, column=3)

	# update current_videos
	current_videos += len(search_results)

	# create load more button
	load_more_button = Button(video_frame, text="Load More", font=('times', 12, 'bold'), command=lambda: load_more_videos(canvas, video_frame, search_term))
	load_more_button.grid(row=current_videos, column=1, pady=10)

	# Set the scrollable region to the frame
	video_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
	canvas.create_window((0, 0), window=video_frame, anchor='nw')

def search_videos(query):
	API_KEY = "API_KEY"
	BASE_URL = "https://www.googleapis.com/youtube/v3"
	search_url = f"{BASE_URL}/search?key={API_KEY}&part=snippet&q={query}&type=video&maxResults=10"
	response = requests.get(search_url)
	json_data = json.loads(response.text)
	search_results = []
	for item in json_data['items']:
		search_result = {}
		search_result['id'] = item['id']['videoId']
		search_result['title'] = item['snippet']['title']
		search_result['thumbnail_url'] = item['snippet']['thumbnails']['medium']['url']
		search_results.append(search_result)
	return search_results

def create_video_window(search_results):
	video_window = Toplevel(root)
	video_window.title("YouTube Videos")
	video_window.geometry("800x600")
	video_window.iconbitmap('yt.ico')
	video_window.configure(background='#bec8d1')

	row_num = 0
	for video in search_results:
		# Get thumbnail image
		response = requests.get(video['thumbnail_url'])
		img_data = response.content
		img = Image.open(io.BytesIO(img_data))
		img = img.resize((160, 90), Image.ANTIALIAS)
		thumbnail = ImageTk.PhotoImage(img)

		# Create video frame
		video_frame = Frame(video_window)
		video_frame.grid(row=row_num, column=0, padx=10, pady=10)
		video_frame.bind("<Button-1>", lambda event, url=f"https://www.youtube.com/watch?v={video['id']}": select_video(url))

		# Add thumbnail to frame
		thumbnail_label = Label(video_frame, image=thumbnail)
		thumbnail_label.image = thumbnail
		thumbnail_label.pack()

		# Add title to frame
		title_label = Label(video_frame, text=video['title'],font=("Arial",12))
		title_label.pack()


"""
def youtube_search(query):
	youtube = build('youtube', 'v3', developerKey='AIzaSyD9w-gPF5uKf8JUSmLSm4jRfo04NMiI-oU')
	request = youtube.search().list(
		part='id,snippet',
		q=query,
		type='video',
		maxResults=12
	)
	response = request.execute()
	return response['items']
"""

def download_video():
	url = entry.get()
#	option = video_option.get()
	save_path = file_path_entry.get()
	
	# Download video
	if options == "Video (mp4)":
		yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
		yt.streams.first().download(save_path)
		downloaded_file = os.path.join(save_path, YouTube(url).title + ".mp4")
		subprocess.Popen('start "" /select "{}"'.format(downloaded_file))
#		download_label.config(text=f"Download complete! Check your {selected_path} folder.", fg="green")
		message_window = tk.Toplevel(root)
		message_window.title("Download Complete!")
		message_label = tk.Label(message_window, text="Download Complete!")
		message_label.pack()
		message_ok_button = tk.Button(message_window, text="OK", command=message_window.destroy)
		message_ok_button.pack()
		message_window.focus_set()
		message_window.grab_set()
	else:
		yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
		yt.streams.filter(only_audio=True).first().download(save_path)
		downloaded_file = os.path.join(save_path, YouTube(url).title + ".mp3")
		subprocess.Popen('start "" /select "{}"'.format(downloaded_file))
#		download_label.config(text=f"Download complete! Check your {selected_path} folder.", fg="green")
		message_window = tk.Toplevel(root)
		message_window.title("Download Complete!")
		message_label = tk.Label(message_window, text="Download Complete!")
		message_label.pack()
		message_ok_button = tk.Button(message_window, text="OK", command=message_window.destroy)
		message_ok_button.pack()
		message_window.focus_set()
		message_window.grab_set()


def browse_file_path():
	selected_path = filedialog.askdirectory()
	file_path_entry.delete(0, tk.END)
	file_path_entry.insert(0, selected_path)

def clear():
	entry.delete(first=0, last=50)
	file_path_entry.delete(first=0, last=50)
	search_entry.delete(first=0, last=50)


root = tk.Tk()
root.title("YouTube Downloader!")
width, height = root.winfo_screenwidth()/2, root.winfo_screenheight()/1.5
root.geometry('%dx%d+0+0' % (width,height))
root.iconbitmap('yt.ico')
root.configure(background='#bec8d1')

folder_path = StringVar()


message = tk.Label(root,  text = "Youtube downloader!", bg="#137a7f",
			fg="#373b3e", height=2, width=int(root.winfo_screenwidth()/2), font=('times', 30, 'italic bold ')).pack()

#Notification = tk.Label(root, text="Video Downloaded Successfully", bg="lime green", fg="white", width=int(root.winfo_screenwidth()/2),
#				   height=2, font=('times', 18, 'bold'))

search_entry_label = tk.Label(root, text="Search Vid : ", width=10, height=2, fg="black", bg="#bec8d1", font=('times', 15, ' bold '))
search_entry_label.place(x=20, y=150)

search_entry = tk.Entry(root, width=40, bg="linen", fg="gray",font=('times', 15, ' bold '))
search_entry.insert(0, "STORMZY - VOSSI BOP")
search_entry.bind('<FocusIn>', lambda event: entry.delete('0', 'end') if entry.get() == 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' else None)
search_entry.bind('<FocusOut>', lambda event: entry.insert(0, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ') if entry.get() == '' else None)
search_entry.place(x=150, y=160)

option_label = tk.Label(root, text="Enter URL : ", width=10, height=2, fg="black", bg="#bec8d1", font=('times', 15, ' bold '))
option_label.place(x=20, y=270)

entry = tk.Entry(root, width=40, bg="linen", fg="gray",font=('times', 15, ' bold '))
entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
entry.bind('<FocusIn>', lambda event: entry.delete('0', 'end') if entry.get() == 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' else None)
entry.bind('<FocusOut>', lambda event: entry.insert(0, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ') if entry.get() == '' else None)
entry.place(x=150, y=280)


file_path_label = tk.Label(root, text="Enter Path : ", width=10, height=2, fg="black", bg="#bec8d1", font=('times', 15, ' bold '))
file_path_label.place(x=20, y=390)

file_path_entry = tk.Entry(root, width=40, bg="linen", fg="gray",textvariable=folder_path, font=('times', 15, ' bold '))
file_path_entry.insert(0, r"C:\Users\Music")
file_path_entry.bind('<FocusIn>', lambda event: file_path_entry.delete('0', 'end') if file_path_entry.get() == r"C:\Users\NAME\Music" else None)
file_path_entry.bind('<FocusOut>', lambda event: file_path_entry.insert(0, r"C:\Users\NAME\Music") if file_path_entry.get() == '' else None)
file_path_entry.place(x=150, y=400)


search = tk.Button(root, text="Search", command=update_video_list,fg='black'  ,bg="#86cecb"  ,width=11 ,height=1 , activebackground = "Red" ,font=('times', 15, ' bold '))
search.place(x=600, y=155)


# OptionMenu Button
options = tk.StringVar(root)
options.trace_add('write', lambda *args: print(options.get()))
options.set("Video (mp4)") # default value

om1 =tk.OptionMenu(root, options, "Video (mp4)","Audio (mp3)")
om1["bg"] = "#86cecb"
om1["highlightthickness"]=0 
om1.config(width=10, height=1, font=('times', 15, ' bold '))
om1['menu'].config(font=('times',(15)),bg='goldenrod1')
om1.place(x=600, y=275)


file_path_button = tk.Button(root, text="Browse", command=browse_file_path,fg='black'  ,bg="#86cecb"  ,width=11 ,height=1 , activebackground = "Red" ,font=('times', 15, ' bold '))
file_path_button.place(x=600, y=395)


#video_option = tk.StringVar(value="Video")

#video_radio_button = tk.Radiobutton(root, text="Video", variable=video_option, value="Video")
#video_radio_button.pack()

#audio_radio_button = tk.Radiobutton(root, text="Audio", variable=video_option, value="Audio")
#audio_radio_button.pack()

clearButton = tk.Button(root, text="Clear",command=clear,fg="black" ,bg="dark turquoise" ,width=10 ,height=2 , activebackground = "Red" ,font=('times', 15, ' bold '))
clearButton.place(x=180, y=470)

download_button = tk.Button(root, text="Download", command=download_video,fg="black" ,bg="yellow green" ,width=10 ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
download_button.place(x=390, y=470)


download_label = tk.Label(root, text="")
download_label.pack()

message = tk.Label(root,  text = "Made by Londø!", bg="#137a7f",
			fg="#373b3e", height=2, width=int(root.winfo_screenwidth()/2), font=('times', 30, 'italic bold ')).pack(side = BOTTOM)

"""
def get_auth_link():
	result = subprocess.run(['your_command'], capture_output=True, text=True)
	output = result.stdout
	
	link_pattern = re.compile(r'Authorization URL:\s+(.*)\n')
	code_pattern = re.compile(r'Enter the authorization code:\s+([\w-]+)')
	
	link_match = link_pattern.search(output)
	code_match = code_pattern.search(output)
	
	link = link_match.group(1)
	code = code_match.group(1)
	
	textbox = tk.Text(root)
	textbox.pack()
	
	textbox.insert(tk.END, f"Link: {link}\n")
	textbox.insert(tk.END, f"Code: {code}\n")

auth_button = tk.Button(root, text="Get Auth Link", command=get_auth_link)
auth_button.pack()

root.mainloop()
"""

root.mainloop()
