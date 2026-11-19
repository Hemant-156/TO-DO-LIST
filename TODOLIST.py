import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date

FILE = "tasks.json"
class TodoApp:

    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager")
        self.root.geometry("1000x650")
        self.root.configure(bg="#F4F6FA")
        self.root.minsize(800, 550)

        self.tasks = []
        self.load_tasks()

        self.create_widgets()
        self.refresh_tasks()

    def load_tasks(self):
        if os.path.exists(FILE):
            try:
                with open(FILE, "r") as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.tasks = []

    def save_tasks(self):
        with open(FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def create_widgets(self):
        header = tk.Frame(self.root, bg="#243B55", height=90)
        header.pack(fill="x")

        tk.Label(
            header,
            text="MY TO-DO LIST",
            font=("Arial", 23, "bold"),
            bg="#243B55",
            fg="white"
        ).pack(pady=25)

        main = tk.Frame(self.root, bg="#F4F6FA")
        main.pack(fill="both", expand=True, padx=25, pady=20)

        form = tk.LabelFrame(
            main,
            text=" Add New Task ",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        form.pack(fill="x", pady=10)

        tk.Label(form, text="Task Name:", bg="white").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )

        self.task_entry = tk.Entry(form, width=35, font=("Arial", 11))
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Priority:", bg="white").grid(
            row=0, column=2, padx=5
        )

        self.priority = ttk.Combobox(
            form,
            values=["High", "Medium", "Low"],
            state="readonly",
            width=12
        )
        self.priority.set("Medium")
        self.priority.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Due Date (YYYY-MM-DD):",
                 bg="white").grid(row=1, column=0, sticky="w", padx=5)

        self.date_entry = tk.Entry(form, width=35)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=1, padx=5, pady=8)

        tk.Button(
            form,
            text="Add Task",
            bg="#2878D0",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.add_task,
            width=15
        ).grid(row=1, column=3, padx=5)

        search_frame = tk.Frame(main, bg="#F4F6FA")
        search_frame.pack(fill="x", pady=10)

        tk.Label(
            search_frame,
            text="Search Tasks:",
            bg="#F4F6FA",
            font=("Arial", 11)
        ).pack(side="left")

        self.search_entry = tk.Entry(search_frame, width=35)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind(
            "<KeyRelease>", lambda event: self.refresh_tasks()
        )

        table_frame = tk.Frame(main, bg="white")
        table_frame.pack(fill="both", expand=True)

        columns = ("ID", "Task", "Priority", "Due Date", "Status")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Task", width=300)
        self.tree.column("Priority", width=100, anchor="center")
        self.tree.column("Due Date", width=140, anchor="center")
        self.tree.column("Status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        buttons = tk.Frame(main, bg="#F4F6FA")
        buttons.pack(fill="x", pady=15)

        actions = [
            ("Complete", self.complete_task, "#16A085"),
            ("Edit", self.edit_task, "#2878D0"),
            ("Delete", self.delete_task, "#D9534F"),
            ("Refresh", self.refresh_tasks, "#64748B")
        ]

        for text, command, color in actions:
            tk.Button(
                buttons,
                text=text,
                command=command,
                bg=color,
                fg="white",
                width=14,
                font=("Arial", 10, "bold")
            ).pack(side="left", padx=8)

        self.stats = tk.Label(
            main,
            text="",
            bg="#F4F6FA",
            font=("Arial", 12, "bold")
        )
        self.stats.pack(pady=5)

    def add_task(self):
        title = self.task_entry.get().strip()
        due = self.date_entry.get().strip()
        priority = self.priority.get()

        if not title:
            messagebox.showwarning("Warning", "Enter a task name!")
            return

        try:
            date.fromisoformat(due)
        except ValueError:
            messagebox.showwarning(
                "Invalid Date", "Use YYYY-MM-DD format!"
            )
            return

        task = {
            "id": max(
                [t["id"] for t in self.tasks], default=0
            ) + 1,
            "title": title,
            "priority": priority,
            "due_date": due,
            "completed": False
        }

        self.tasks.append(task)
        self.save_tasks()

        self.task_entry.delete(0, tk.END)
        self.refresh_tasks()

        messagebox.showinfo("Success", "Task added successfully!")

    def selected_task(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning", "Please select a task first!"
            )
            return None

        return int(self.tree.item(selected[0], "values")[0])

    def complete_task(self):
        task_id = self.selected_task()

        if task_id is None:
            return

        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                break

        self.save_tasks()
        self.refresh_tasks()

    def delete_task(self):
        task_id = self.selected_task()

        if task_id is None:
            return

        if not messagebox.askyesno(
            "Confirm", "Delete this task?"
        ):
            return

        self.tasks = [
            t for t in self.tasks if t["id"] != task_id
        ]

        self.save_tasks()
        self.refresh_tasks()

    def edit_task(self):
        task_id = self.selected_task()

        if task_id is None:
            return

        task = next(
            (t for t in self.tasks if t["id"] == task_id),
            None
        )

        if task is None:
            return

        window = tk.Toplevel(self.root)
        window.title("Edit Task")
        window.geometry("350x250")
        window.configure(bg="white")
        window.grab_set()

        tk.Label(
            window, text="Task Name:", bg="white"
        ).pack(pady=5)

        title_entry = tk.Entry(window, width=35)
        title_entry.pack()
        title_entry.insert(0, task["title"])

        tk.Label(
            window, text="Priority:", bg="white"
        ).pack(pady=5)

        priority_box = ttk.Combobox(
            window,
            values=["High", "Medium", "Low"],
            state="readonly"
        )
        priority_box.set(task["priority"])
        priority_box.pack()

        tk.Label(
            window, text="Due Date:", bg="white"
        ).pack(pady=5)

        date_box = tk.Entry(window, width=25)
        date_box.pack()
        date_box.insert(0, task["due_date"])

        def save_edit():
            title = title_entry.get().strip()
            due = date_box.get().strip()

            if not title:
                messagebox.showwarning(
                    "Warning", "Task name cannot be empty!"
                )
                return

            try:
                date.fromisoformat(due)
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date", "Use YYYY-MM-DD format!"
                )
                return

            task["title"] = title
            task["priority"] = priority_box.get()
            task["due_date"] = due

            self.save_tasks()
            self.refresh_tasks()
            window.destroy()

        tk.Button(
            window,
            text="Save Changes",
            bg="#2878D0",
            fg="white",
            command=save_edit
        ).pack(pady=15)

    def refresh_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_entry.get().lower()

        for task in self.tasks:
            if search and search not in task["title"].lower():
                continue

            status = (
                "Completed" if task["completed"] else "Pending"
            )

            self.tree.insert(
                "",
                "end",
                values=(
                    task["id"],
                    task["title"],
                    task["priority"],
                    task["due_date"],
                    status
                )
            )

        total = len(self.tasks)
        completed = sum(
            1 for t in self.tasks if t["completed"]
        )
        pending = total - completed

        percentage = completed / total * 100 if total else 0

        self.stats.config(
            text=f"Total: {total}  |  Completed: {completed}  "
                 f"|  Pending: {pending}  |  Progress: {percentage:.1f}%"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
