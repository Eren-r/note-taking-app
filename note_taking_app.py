import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from cryptography.fernet import Fernet
import os
import speech_recognition as sr



KEY_FILE = "key.key"
NOTES_FILE = "notes_encrypted.txt"
MASTER_PASSWORD = "eren yeagers"  # Change this to your desired password



def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()



def encrypt_note(note, key):
    f = Fernet(key)
    return f.encrypt(note.encode()).decode()

def decrypt_note(encrypted_note, key):
    f = Fernet(key)
    return f.decrypt(encrypted_note.encode()).decode()



def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    with open(NOTES_FILE, "r") as f:
        return f.read().splitlines()

def save_note(note, key):
    encrypted = encrypt_note(note, key)
    with open(NOTES_FILE, "a") as f:
        f.write(encrypted + "\n")



class SecureNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Sticky Notes")
        self.key = load_key()

        self.login_screen()

    def login_screen(self):
        password = simpledialog.askstring("Login", "Enter Master Password:", show="*")
        if password != MASTER_PASSWORD:
            messagebox.showerror("Access Denied", "Incorrect Password!")
            self.root.destroy()
        else:
            self.build_main_ui()

    def build_main_ui(self):
        tk.Label(self.root, text="Secure Notes", font=("Helvetica", 18, "bold")).pack(pady=10)
        tk.Label(self.root, text="by\neren yeager", font=("Helvetica", 10, "bold")).pack(pady=10)

        tk.Button(self.root, text="New Note", width=20, command=self.new_note).pack(pady=5)
        tk.Button(self.root, text="Voice Note", width=20, command=self.voice_note).pack(pady=5)
        tk.Button(self.root, text="View Notes", width=20, command=self.view_notes).pack(pady=5)
        tk.Button(self.root, text="Delete All Notes", width=20, command=self.delete_all_notes).pack(pady=5)
        tk.Button(self.root, text="Exit", width=20, command=self.root.quit).pack(pady=5)

    def new_note(self):
        def save_and_close():
            note_text = text_area.get("1.0", tk.END).strip()
            if note_text:
                save_note(note_text, self.key)
            note_window.destroy()

        note_window = tk.Toplevel(self.root)
        note_window.title("New Note")
        text_area = scrolledtext.ScrolledText(note_window, width=40, height=10)
        text_area.pack(padx=10, pady=10)
        note_window.protocol("WM_DELETE_WINDOW", save_and_close)

    def voice_note(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            messagebox.showinfo("Voice Input", "Speak your note after the beep.")
            self.root.after(500)
            try:
                audio = recognizer.listen(source, timeout=5)
                note_text = recognizer.recognize_google(audio)
                self.save_voice_note(note_text)
            except sr.WaitTimeoutError:
                messagebox.showerror("Timeout", "No speech detected. Try again.")
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Sorry, I couldn't understand.")
            except sr.RequestError as e:
                messagebox.showerror("Error", f"Voice recognition failed: {e}")

    def save_voice_note(self, note_text):
        if note_text:
            save_note(note_text, self.key)
            messagebox.showinfo("Saved", f"Voice note saved:\n\n{note_text}")

    def view_notes(self):
        notes = load_notes()
        view_win = tk.Toplevel(self.root)
        view_win.title("Your Notes")

        if not notes:
            tk.Label(view_win, text="No notes available.", font=("Arial", 12)).pack(pady=20)
            return

        listbox = tk.Listbox(view_win, width=60, height=15)
        for i, enc in enumerate(notes):
            try:
                dec = decrypt_note(enc, self.key)
                listbox.insert(tk.END, f"{i+1}. {dec[:50]}...")
            except Exception:
                listbox.insert(tk.END, f"{i+1}. [Corrupted Note]")

        listbox.pack(padx=10, pady=10)

    def delete_all_notes(self):
        confirm = messagebox.askyesno("Delete All", "Are you sure you want to delete all notes?")
        if confirm:
            if os.path.exists(NOTES_FILE):
                os.remove(NOTES_FILE)
            messagebox.showinfo("Deleted", "All notes have been deleted.")



if __name__ == "__main__":
    root = tk.Tk()
    app = SecureNotesApp(root)
    root.mainloop()
