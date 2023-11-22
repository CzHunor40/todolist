import tkinter as tk
from tkinter import messagebox, simpledialog
from database import DatabaseManager

class Todo:
    def __init__(self, root):
        self.root = root
        self.root.title("ToDo")

        self.db_manager = DatabaseManager()

        self.tasks = []
        self.totaltasks = 0
        self.total_points = 0
        self.max_possible_points = 0

        self.task_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=40)
        self.task_listbox.pack(pady=10)

        self.compresbutton_frame = tk.Frame(root)
        self.compresbutton_frame.pack()

        self.complete_button = tk.Button(self.compresbutton_frame, width=15, text="Feladat bepipálása", command=self.complete_task)

        self.complete_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.compresbutton_frame, width=15, text="Feladat ki-pipálása", command=self.reset_task)

        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.totalpoints_label = tk.Label(root, text=f"Teljesített pontok: {self.total_points} / {self.max_possible_points}")

        self.totalpoints_label.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.halfway_notification_sent = False

        self.task_label = tk.Label(root, text="Feladat:")
        self.task_label.pack()

        self.task_entry = tk.Entry(root, width=30)
        self.task_entry.pack(pady=5)

        self.points_label = tk.Label(root, text="Pont:")
        self.points_label.pack()

        self.points_entry = tk.Entry(root, width=10)
        self.points_entry.pack(pady=5)

        self.addremovebutton_frame = tk.Frame(root)
        self.addremovebutton_frame.pack()

        self.add_button = tk.Button(self.addremovebutton_frame, width=15, text="Feladat hozzáadása", command=self.add_task)

        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self.addremovebutton_frame, width=15, text="Feladat eltávolítása", command=self.remove_task)

        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.select_user_button = tk.Button(root, text="Felhasználó kiválasztása", command=self.select_user)
        self.select_user_button.pack()

        self.username = None

        self.load_user_data()
        self.root.after(100, self.select_user)

    def select_user(self):
        self.db_manager.cursor.execute("SELECT DISTINCT username FROM users")
        usernames = [row[0] for row in self.db_manager.cursor.fetchall()]

        user_selection_window = tk.Toplevel(self.root)
        user_selection_window.title("Felhasználó választás")

        user_listbox = tk.Listbox(user_selection_window, width=40)
        for username in usernames:
            user_listbox.insert(tk.END, username)

        user_listbox.pack(padx=20, pady=20)

        select_button = tk.Button(user_selection_window, text="Kiválaszt", width=15, command=lambda: self.on_user_selected(user_listbox.get(tk.ACTIVE), user_selection_window))
        select_button.pack()

        add_user_button = tk.Button(user_selection_window, text="Felhasználó hozzáadása", width=20, command=lambda: self.add_user(user_selection_window))
        add_user_button.pack(side=tk.LEFT, padx=5)

        remove_user_button = tk.Button(user_selection_window, text="Felhasználó törlése", width=20, command=lambda: self.remove_user(user_listbox.get(tk.ACTIVE), user_selection_window))
        remove_user_button.pack(side=tk.LEFT, padx=5)

    def add_user(self,user_selection_window):
        new_username = simpledialog.askstring("Hozzáadás", "Adj meg egy felhasználónevet:")
        if new_username:
            try:
                self.db_manager.execute_sqlcommand("INSERT INTO users (username) VALUES (%s)", (new_username,))
                messagebox.showinfo("Felhasználó hozzáadva", f"{new_username} felhasználó hozzáadva.")
                self.select_user()
                user_selection_window.destroy()

            except Exception as err:
                messagebox.showerror("Error", f"{err} felhasználó létrehozása sikertelen.")

    def remove_user(self,selected_user,user_selection_window):
        confirm = messagebox.askyesno("Törlés", f"Biztos, hogy törölni szeretnéd {selected_user} felhasználót?")
        if confirm:
            if selected_user:
                self.db_manager.execute_sqlcommand(
                    "DELETE FROM tasks WHERE user_id=(SELECT id FROM users WHERE username=%s)", (selected_user,))
                try:
                    self.db_manager.execute_sqlcommand("DELETE FROM users WHERE username=%s", (selected_user,))
                    messagebox.showinfo("Felhasználó törölve", f"{selected_user} felhasználó törölve.")
                    self.select_user()
                    user_selection_window.destroy()
                except Exception as err:
                    messagebox.showerror("Error", f"{err} felhasználó törlése sikertelen.")

    def on_user_selected(self, selected_user, user_selection_window):
        if selected_user:
            self.username = selected_user
            self.tasks = []
            self.total_points = 0
            self.max_possible_points = 0
            self.task_listbox.delete(0, tk.END)
            self.load_user_data()
            user_selection_window.destroy()
            self.update_points_label()

    def load_user_data(self):
        if self.username is not None:
            self.task_listbox.delete(0, tk.END)
            self.tasks = []
            self.total_points = 0
            self.max_possible_points = 0

            self.db_manager.cursor.execute("SELECT * FROM tasks WHERE user_id=(SELECT id FROM users WHERE username=%s)", (self.username,))
            rows = self.db_manager.cursor.fetchall()

            for i, row in enumerate(rows):
                task_data = {"id": row[0], "task": row[2], "completed": row[4], "points": row[3]}
                self.tasks.append(task_data)
                self.max_possible_points += row[3]
                self.totaltasks += 1

                task_display = f"{row[2]} ({row[3]} pont)"
                if row[4]:
                    self.total_points += row[3]
                    task_display += " - Teljesítve"
                    self.task_listbox.insert(tk.END, task_display)
                    self.task_listbox.itemconfig(tk.END, {'fg': 'gray'})
                else:
                    self.task_listbox.insert(tk.END, task_display)

            self.update_points_label()

    def add_task(self):
        task = self.task_entry.get()
        points = self.points_entry.get()

        try:
            points = int(points)
        except ValueError:
            messagebox.showerror("Error", "Kérlek adj meg valós egész számot")
            return

        if task:
            self.tasks.append({"task": task, "completed": False, "points": points})
            self.max_possible_points += points
            self.task_listbox.insert(tk.END, f"{task} ({points} pont)")
            self.task_entry.delete(0, tk.END)
            self.points_entry.delete(0, tk.END)
            self.update_points_label()


            self.db_manager.execute_sqlcommand(
                "INSERT INTO tasks (user_id, task, points, completed) VALUES ((SELECT id FROM users WHERE username=%s), %s, %s, %s)",
                (self.username, task, points, 0))
            self.load_user_data()

    def remove_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_data = self.tasks[selected_index[0]]
            confirm = messagebox.askyesno("Törlés",
                                          f"Biztos törölni szeretnéd a(z) {task_data['task']} ({task_data['points']} pont) feladadtot?")
            if confirm:
                self.task_listbox.delete(selected_index)
                if task_data["completed"]:
                    self.total_points -= task_data["points"]
                self.max_possible_points -= task_data["points"]
                self.tasks.pop(selected_index[0])
                self.update_points_label()

                self.db_manager.execute_sqlcommand(
                    "DELETE FROM tasks WHERE user_id=(SELECT id FROM users WHERE username=%s) AND task=%s AND points=%s AND id=%s",
                    (self.username, task_data["task"], task_data["points"], task_data["id"]))
                self.load_user_data()

    def complete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_data = self.tasks[selected_index[0]]
            task_id = task_data["id"]

            if not task_data["completed"]:
                self.total_points += task_data["points"]
                self.update_points_label()
                task_data["completed"] = True
                task_display = f"{task_data['task']} ({task_data['points']} pont) - Teljesítve"
                self.task_listbox.delete(selected_index)
                self.task_listbox.insert(selected_index, task_display)
                self.task_listbox.itemconfig(selected_index, {'fg': 'gray'})
                messagebox.showinfo("Feladat teljesítve",
                                    f"{task_data['task']} ({task_data['points']} pont) feladat teljesítve.")


                self.db_manager.execute_sqlcommand("UPDATE tasks SET completed=1 WHERE id=%s", (task_id,))
                self.load_user_data()

    def reset_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_data = self.tasks[selected_index[0]]
            if task_data["completed"]:
                self.total_points -= task_data["points"]
                task_data["completed"] = False
                task_display = f"{task_data['task']} ({task_data['points']} pont)"
                self.task_listbox.delete(selected_index)
                self.task_listbox.insert(selected_index, task_display)
                self.task_listbox.itemconfig(selected_index, {'fg': 'black'})
                self.update_points_label()

                self.db_manager.cursor.execute(
                    "UPDATE tasks SET completed=0 WHERE user_id=(SELECT id FROM users WHERE username=%s) AND task=%s AND points=%s AND id=%s",
                    (self.username, task_data["task"], task_data["points"], task_data["id"]))
                self.db_manager.execute_sqlcommand(
                    "UPDATE tasks SET completed=0 WHERE user_id=(SELECT id FROM users WHERE username=%s) AND task=%s AND points=%s AND id=%s",
                    (self.username, task_data["task"], task_data["points"], task_data["id"]))
                messagebox.showinfo("Task Reset",
                                    f"Task '{task_data['task']}' ({task_data['points']} points) has been reset.")

    def update_points_label(self):
        if hasattr(self, 'halfway_notification_sent'):
            halfway_point = self.max_possible_points / 2

            self.totalpoints_label.config(text=f"Teljesített pontok: {self.total_points} / {self.max_possible_points}")
            if self.total_points > self.max_possible_points / 2 and not self.halfway_notification_sent:
                messagebox.showinfo("Gratulálok", f"Sikeresen teljesítetted a kitűzött pontok felét!")
                self.halfway_notification_sent = True
                self.totalpoints_label.config(
                    text=f"Teljesített pontok: {self.total_points} / {self.max_possible_points}")
            elif self.total_points < self.max_possible_points / 2 and self.halfway_notification_sent:
                self.halfway_notification_sent = False
                self.totalpoints_label.config(
                    text=f"Teljesített pontok: {self.total_points} / {self.max_possible_points}")
        else:
            self.totalpoints_label.config(text=f"Teljesített pontok: {self.total_points} / {self.max_possible_points}")

    def on_closing(self):
        confirm = messagebox.askyesno("Kilépés", "Biztos, hogy be szeretnéd zárni az applikációt?")
        if confirm:
            self.db_manager.close_connection()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Todo(root)
    root.mainloop()