import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import random
import os
import json
import csv

# 🎨 Color and font scheme
BG_MAIN = "#f0f4fc"
BG_FRAME = "#e6eefd"
BTN_COLOR = "#4481eb"
BTN_HOVER = "#2a64c5"
TREE_HEADER_BG = "#274b8e"
TREE_HEADER_FG = "#ffffff"
ROW_EVEN = "#e6eefd"
ROW_ODD = "#f0f4fc"
VARIGNON_BG = "#ffe6b3"   # Soft orange for Varignon
SOLDOUT_BG = "#f8c6ca"
LABEL_COLOR = "#274b8e"
WARNING_COLOR = "#e64242"
FONT_HEADER = ("Helvetica", 18, "bold")
FONT_LABEL = ("Helvetica", 13, "bold")
FONT_NORMAL = ("Helvetica", 12)

# ✨ Emojis
EMOJI_VARIGNON = "🚀"
EMOJI_NORMAL = "🚌"
EMOJI_SEAT = "💺"
EMOJI_SOLDOUT = "❌"
EMOJI_TICKET = "🎫"
EMOJI_HISTORY = "📜"
EMOJI_RESET = "🔄"
EMOJI_USER = "👤"
EMOJI_SUCCESS = "✅"
EMOJI_FAIL = "⚠️"
EMOJI_EXPORT = "🗂️"
EMOJI_PAYMENT = "💳"

transport_options = [
    {'name': 'Varignon Express', 'start_time': '05:30', 'price': 25, 'type': 'varignon'},
    {'name': 'Express A', 'start_time': '06:00', 'price': 15, 'type': 'normal'},
    {'name': 'Express B', 'start_time': '06:25', 'price': 20, 'type': 'normal'},
    {'name': 'Express C', 'start_time': '06:50', 'price': 15, 'type': 'normal'},
]

STATE_FILE = "transport_state.json"
HISTORY_FILE = "booking_history.txt"
CSV_FILE = "booking_history.csv"

def generate_schedule(start_time_str, count=10):
    schedule = []
    start_time = datetime.datetime.strptime(start_time_str, '%H:%M')
    for i in range(count):
        time = start_time + datetime.timedelta(minutes=25 * i)
        schedule.append(time.strftime('%H:%M'))
    return schedule

def transport_emoji(typ):
    return EMOJI_VARIGNON if typ == "varignon" else EMOJI_NORMAL

class TransportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Varignon Electronics Transport System "+EMOJI_VARIGNON)
        self.root.configure(bg=BG_MAIN)
        self.transport_data = {}
        self.booking_history = []
        self.username = ""

        self.create_widgets()
        self.prompt_username()
        self.load_state()
        self.load_history()
        self.refresh_treeview()

    def prompt_username(self):
        self.username = simpledialog.askstring("User Login "+EMOJI_USER, "Enter your username "+EMOJI_USER+":")
        if not self.username:
            self.username = "guest"

    def create_widgets(self):
        header = ttk.Label(self.root, text=f"{EMOJI_VARIGNON} Varignon Electronics Transport Options", font=FONT_HEADER, foreground=LABEL_COLOR, background=BG_MAIN)
        header.pack(pady=10)

        columns = ('Name', 'Next Departure', 'Price', 'Available Seats', 'Type')
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background=TREE_HEADER_BG, foreground=TREE_HEADER_FG, font=FONT_LABEL)
        style.configure("Treeview", rowheight=28, font=FONT_NORMAL)
        style.map("Treeview", background=[('selected', BTN_COLOR)])

        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=170, anchor='center')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

        self.tree.tag_configure('evenrow', background=ROW_EVEN)
        self.tree.tag_configure('oddrow', background=ROW_ODD)
        self.tree.tag_configure('varignon', background=VARIGNON_BG)
        self.tree.tag_configure('soldout', background=SOLDOUT_BG)

        style.configure("Accent.TButton", background=BTN_COLOR, foreground="white", font=FONT_LABEL, borderwidth=0)
        style.map("Accent.TButton", background=[("active", BTN_HOVER)], foreground=[("active", "white")])

        btn_frame = tk.Frame(self.root, bg=BG_FRAME)
        btn_frame.pack(pady=10, fill='x')
        ttk.Button(btn_frame, text=EMOJI_TICKET+" Buy Ticket", style="Accent.TButton", command=self.buy_ticket).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text=EMOJI_HISTORY+" Show Booking History", style="Accent.TButton", command=self.show_history).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text=EMOJI_EXPORT+" Export to CSV", style="Accent.TButton", command=self.export_csv).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text=EMOJI_PAYMENT+" Simulate USSD Payment", style="Accent.TButton", command=self.simulate_ussd).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text=EMOJI_RESET+" Admin: Reset Seats", style="Accent.TButton", command=self.reset_seats).grid(row=0, column=4, padx=5)

    def refresh_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, (name, data) in enumerate(self.transport_data.items()):
            display_name = f"{transport_emoji(data['type'])} {name}"
            display_type = f"{transport_emoji(data['type'])} {data['type'].capitalize()}"
            tags = ()
            if data['seats'] == 0:
                tags = ('soldout',)
                display_name += " "+EMOJI_SOLDOUT
            elif data['type'] == 'varignon':
                tags = ('varignon',)
            else:
                tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
            self.tree.insert('', 'end', iid=name, values=(
                display_name,
                data['next_departure'],
                f"${data['price']}",
                f"{EMOJI_SEAT} {data['seats']}",
                display_type
            ), tags=tags)

    def buy_ticket(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(EMOJI_FAIL + " No selection", "Please select a transport option "+EMOJI_TICKET+".")
            return
        name = selected_item[0]
        data = self.transport_data[name]
        seats = data['seats']
        price = data['price']
        departure = data['next_departure']
        option_type = data['type']

        if seats <= 0:
            messagebox.showinfo(EMOJI_SOLDOUT + " Sold Out", "No seats available "+EMOJI_SOLDOUT+".")
            return

        confirm = messagebox.askyesno(
            EMOJI_TICKET + " Confirm Purchase",
            f"Buy ticket for {transport_emoji(option_type)} {name} at {departure}?\nPrice: ${price} {EMOJI_TICKET}\nRemaining seats: {seats} {EMOJI_SEAT}"
        )
        if confirm:
            ussd_code = f"*182*1*1*0795311916*{price*100}#"
            proceed = messagebox.askyesno(
                EMOJI_PAYMENT + " USSD Payment",
                f"Dial {ussd_code} to pay?\nProceed? {EMOJI_PAYMENT}"
            )
            if proceed:
                self.complete_purchase(name)

    def complete_purchase(self, name):
        data = self.transport_data[name]
        seats = data['seats']
        if seats > 0:
            data['seats'] -= 1
            data['schedule_index'] = (data['schedule_index'] + 1) % len(data['schedule'])
            data['next_departure'] = data['schedule'][data['schedule_index']]
            self.refresh_treeview()
            entry = {
                'name': name,
                'departure': data['next_departure'],
                'price': data['price'],
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'user': self.username
            }
            self.booking_history.append(entry)
            self.save_history()
            self.save_state()
            messagebox.showinfo(EMOJI_SUCCESS + " Success", f"Your ticket has been booked {EMOJI_TICKET}. Thank you {EMOJI_USER}!")
        else:
            messagebox.showinfo(EMOJI_SOLDOUT + " Sold Out", "No seats available "+EMOJI_SOLDOUT+".")

    def show_history(self):
        if not self.booking_history:
            messagebox.showinfo(EMOJI_HISTORY + " Booking History", "No bookings yet "+EMOJI_FAIL+".")
            return
        history_str = f"{EMOJI_HISTORY} Booking History for {self.username} {EMOJI_USER}\n\n"
        for idx, entry in enumerate(self.booking_history, start=1):
            typ = 'varignon' if entry['name'] == 'Varignon Express' else 'normal'
            history_str += f"{idx}. {transport_emoji(typ)} {entry['name']} at {entry['departure']} on {entry['date']} - ${entry['price']} (User: {entry['user']}) {EMOJI_TICKET}\n"
        messagebox.showinfo(EMOJI_HISTORY + " Booking History", history_str)

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                for entry in self.booking_history:
                    line = f"{entry['name']}|{entry['departure']}|{entry['price']}|{entry['date']}|{entry['user']}\n"
                    f.write(line)
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return
        try:
            with open(HISTORY_FILE, "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 5:
                        self.booking_history.append({
                            'name': parts[0],
                            'departure': parts[1],
                            'price': int(parts[2]),
                            'date': parts[3],
                            'user': parts[4]
                        })
        except Exception as e:
            print(f"Error loading history: {e}")

    def save_state(self):
        try:
            state = {}
            for name, data in self.transport_data.items():
                state[name] = {
                    'seats': data['seats'],
                    'schedule_index': data['schedule_index']
                }
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error saving state: {e}")

    def load_state(self):
        state = {}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
            except Exception as e:
                print(f"Error loading state: {e}")
        for option in transport_options:
            schedule = generate_schedule(option['start_time'])
            seats = 15
            schedule_index = 0
            name = option['name']
            if name in state:
                seats = state[name].get('seats', 15)
                schedule_index = state[name].get('schedule_index', 0)
            next_departure = schedule[schedule_index]
            self.transport_data[name] = {
                'seats': seats,
                'price': option['price'],
                'next_departure': next_departure,
                'type': option['type'],
                'schedule': schedule,
                'schedule_index': schedule_index
            }

    def reset_seats(self):
        confirm = messagebox.askyesno(EMOJI_RESET+" Reset All Seats", "Are you sure you want to reset all seats to 15 and schedules to the start? "+EMOJI_RESET)
        if confirm:
            for option in transport_options:
                schedule = generate_schedule(option['start_time'])
                next_departure = schedule[0]
                seats = 15
                price = option['price']
                name = option['name']
                option_type = option['type']
                self.transport_data[name] = {
                    'seats': seats,
                    'price': price,
                    'next_departure': next_departure,
                    'type': option_type,
                    'schedule': schedule,
                    'schedule_index': 0
                }
            self.save_state()
            self.refresh_treeview()
            messagebox.showinfo(EMOJI_RESET+" Reset Complete", "All seats and schedules have been reset "+EMOJI_SUCCESS+".")

    def simulate_ussd(self):
        ussd_input = simpledialog.askstring(EMOJI_PAYMENT+" USSD Simulation", "Enter USSD code "+EMOJI_PAYMENT+":")
        if ussd_input:
            if ussd_input.startswith("*182*") and ussd_input.endswith("#"):
                response = random.choice([EMOJI_SUCCESS+" Payment Successful", EMOJI_FAIL+" Payment Failed", EMOJI_FAIL+" Network Error"])
                messagebox.showinfo(EMOJI_PAYMENT + " USSD Response", response)
            else:
                messagebox.showerror(EMOJI_FAIL + " Invalid USSD", "The entered code is invalid "+EMOJI_FAIL+".")

    def export_csv(self):
        if not self.booking_history:
            messagebox.showinfo(EMOJI_EXPORT + " Export CSV", "No bookings to export "+EMOJI_FAIL+".")
            return
        try:
            with open(CSV_FILE, "w", newline='') as csvfile:
                fieldnames = ['name', 'departure', 'price', 'date', 'user']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for entry in self.booking_history:
                    writer.writerow(entry)
            messagebox.showinfo(EMOJI_EXPORT + " Export CSV", f"Booking history exported to {CSV_FILE} {EMOJI_SUCCESS}")
        except Exception as e:
            messagebox.showerror(EMOJI_FAIL + " Export CSV", f"Failed to export CSV: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TransportApp(root)
    root.mainloop()