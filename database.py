import mysql.connector
from tkinter import messagebox

class DatabaseManager:
    def __init__(self):
        self.sql = mysql.connector.connect(
            host="localhost",
            user="todouser",
            password="123",
            database="todo",
            port="3306"
        )
        self.cursor = self.sql.cursor()

    def close_connection(self):
        self.sql.close()

    def execute_sqlcommand(self, sqlcommand, input=None):
        try:
            if input:
                self.cursor.execute(sqlcommand, input)
            else:
                self.cursor.execute(sqlcommand)
            self.sql.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"{err}")

    def fetch_sqldata(self, sqlcommand, input=None):
        try:
            if input:
                self.cursor.execute(sqlcommand, input)
            else:
                self.cursor.execute(sqlcommand)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"{err}")
            return []