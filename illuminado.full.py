import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
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
ILLUMINADO_BG = "#ffe6b3"
SOLDOUT_BG = "#f8c6ca"
LABEL_COLOR = "#274b8e"
WARNING_COLOR = "#e64242"
FONT_HEADER = ("Helvetica", 18, "bold")
FONT_LABEL = ("Helvetica", 13, "bold")
FONT_NORMAL = ("Helvetica", 12)

# ✨ Emojis
EMOJI_ILLUMINADO = "🚀"
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
EMOJI_LUGGAGE = "🎒"
EMOJI_LANGUAGE = "🌍"
EMOJI_LOYALTY = "⭐"
EMOJI_SAFETY = "🛡️"
EMOJI_WEATHER = "🌦️"
EMOJI_SEAT_SELECT = "💺"
EMOJI_QR = "📱"

# Rwanda Transportation Routes
transport_options = [
    {'name': 'Illuminado Express', 'start_time': '05:00', 'price': 3500, 'type': 'illuminado', 'destination': 'All Major Cities'},
    {'name': 'Express A - Kayonza', 'start_time': '05:30', 'price': 2500, 'type': 'normal', 'destination': 'East'},
    {'name': 'Express B - Rwamagana', 'start_time': '06:00', 'price': 2000, 'type': 'normal', 'destination': 'East'},
    {'name': 'Express C - Nyagatare', 'start_time': '06:30', 'price': 3000, 'type': 'normal', 'destination': 'East'},
    {'name': 'Express D - Kirehe', 'start_time': '07:00', 'price': 2800, 'type': 'normal', 'destination': 'East'},
    {'name': 'Express F - Huye', 'start_time': '05:45', 'price': 2200, 'type': 'normal', 'destination': 'South'},
    {'name': 'Express G - Muhanga', 'start_time': '06:15', 'price': 1800, 'type': 'normal', 'destination': 'South'},
    {'name': 'Express K - Rubavu', 'start_time': '05:15', 'price': 3200, 'type': 'normal', 'destination': 'West'},
    {'name': 'Express L - Karongi', 'start_time': '05:45', 'price': 2900, 'type': 'normal', 'destination': 'West'},
    {'name': 'Express P - Musanze', 'start_time': '05:20', 'price': 2800, 'type': 'normal', 'destination': 'North'},
    {'name': 'Express Z - Kigali CBD Shuttle', 'start_time': '04:30', 'price': 500, 'type': 'normal', 'destination': 'Kigali'},
]

# Configuration files
STATE_FILE = "transport_state.json"
HISTORY_FILE = "booking_history.txt"
CSV_FILE = "booking_history.csv"
USER_PROFILES_FILE = "user_profiles.json"

# Rwanda Mobile Money Providers
MOBILE_MONEY_PROVIDERS = {
    'MTN Mobile Money': "*182*6*1*1*078xxxxxx*{amount}#",
    'Airtel Money': "*182*1*1*078xxxxxx*{amount}#", 
    'Tigo Cash': "*188*1*1*078xxxxxx*{amount}#"
}

# Languages supported
LANGUAGES = {
    'en': "English",
    'rw': "Kinyarwanda", 
    'fr': "French",
    'sw': "Swahili"
}

# Luggage options with prices
LUGGAGE_OPTIONS = {
    'small': {"name": "Small Bag", "price": 0, "emoji": "🎒"},
    'medium': {"name": "Medium Bag", "price": 500, "emoji": "🛄"},
    'large': {"name": "Large Bag", "price": 1000, "emoji": "🧳"},
    'extra': {"name": "Extra Luggage", "price": 2000, "emoji": "📦"}
}

# Loyalty program tiers
LOYALTY_TIERS = {
    'bronze': {"min_rides": 0, "discount": 0, "name": "Bronze"},
    'silver': {"min_rides": 10, "discount": 5, "name": "Silver"},
    'gold': {"min_rides": 25, "discount": 10, "name": "Gold"},
    'platinum': {"min_rides": 50, "discount": 15, "name": "Platinum"}
}

def generate_schedule(start_time_str, count=8):
    schedule = []
    start_time = datetime.datetime.strptime(start_time_str, '%H:%M')
    for i in range(count):
        time = start_time + datetime.timedelta(minutes=30 * i)
        schedule.append(time.strftime('%H:%M'))
    return schedule

def transport_emoji(typ):
    return EMOJI_ILLUMINADO if typ == "illuminado" else EMOJI_NORMAL

class TransportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Illuminado Rwanda Transport System " + EMOJI_ILLUMINADO)
        self.root.configure(bg=BG_MAIN)
        self.root.geometry("1300x800")
        
        self.transport_data = {}
        self.booking_history = []
        self.username = ""
        self.current_language = "en"
        self.user_profiles = {}
        self.loyalty_points = 0
        self.selected_luggage = 'small'
        self.selected_seat = None

        # Load data
        self.load_state()
        self.load_history()
        self.load_user_profiles()

        self.create_widgets()
        self.prompt_username()
        self.refresh_treeview()
        
        # Show weather alert on startup
        self.show_weather_alert()

    def prompt_username(self):
        name = simpledialog.askstring("User Login " + EMOJI_USER, "Enter your username " + EMOJI_USER + ":")
        if name and name.strip():
            self.username = name.strip()
            if self.username not in self.user_profiles:
                self.user_profiles[self.username] = {
                    'loyalty_points': 0,
                    'total_rides': 0,
                    'preferred_language': 'en',
                    'preferred_payment': 'MTN Mobile Money'
                }
        else:
            self.username = "guest"
        
        self.loyalty_points = self.user_profiles.get(self.username, {}).get('loyalty_points', 0)
        self.save_user_profiles()

    def create_widgets(self):
        # Header with loyalty points
        header_frame = tk.Frame(self.root, bg=BG_MAIN)
        header_frame.pack(pady=10, fill='x')
        
        ttk.Label(header_frame, text=f"{EMOJI_ILLUMINADO} Illuminado Rwanda Transport Services", 
                 font=FONT_HEADER, foreground=LABEL_COLOR).pack(side='left', padx=20)
        
        # Loyalty points display
        self.loyalty_label = ttk.Label(header_frame, 
                                     text=f"{EMOJI_LOYALTY} Points: {self.loyalty_points}",
                                     font=FONT_LABEL, foreground=LABEL_COLOR)
        self.loyalty_label.pack(side='right', padx=20)

        # Language selector
        lang_frame = tk.Frame(self.root, bg=BG_FRAME)
        lang_frame.pack(pady=5, fill='x')
        
        ttk.Label(lang_frame, text=f"{EMOJI_LANGUAGE} Language:", font=FONT_LABEL, background=BG_FRAME).pack(side='left', padx=5)
        
        self.lang_var = tk.StringVar(value=self.current_language)
        for code, name in LANGUAGES.items():
            ttk.Radiobutton(lang_frame, text=name, variable=self.lang_var, 
                           value=code, command=self.change_language).pack(side='left', padx=5)

        # Destination filter
        filter_frame = tk.Frame(self.root, bg=BG_FRAME)
        filter_frame.pack(pady=5, fill='x')
        
        ttk.Label(filter_frame, text="Filter by Destination:", font=FONT_LABEL, background=BG_FRAME).grid(row=0, column=0, padx=5)
        self.destination_var = tk.StringVar(value="All")
        destinations = ["All", "East", "South", "West", "North", "Kigali"]
        for i, dest in enumerate(destinations):
            ttk.Radiobutton(filter_frame, text=dest, variable=self.destination_var, 
                           value=dest, command=self.refresh_treeview).grid(row=0, column=i+1, padx=5)

        # Main treeview
        columns = ('Name', 'Destination', 'Next Departure', 'Price (RWF)', 'Available Seats', 'Type')
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        
        style.configure("Treeview.Heading", background=TREE_HEADER_BG, foreground=TREE_HEADER_FG, font=FONT_LABEL)
        style.configure("Treeview", rowheight=28, font=FONT_NORMAL)
        style.map("Treeview", background=[('selected', BTN_COLOR)])

        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Name':
                self.tree.column(col, width=250, anchor='w')
            else:
                self.tree.column(col, width=150, anchor='center')
        self.tree.pack(padx=10, pady=10, fill='both', expand=True)

        # Row/tag styling
        self.tree.tag_configure('evenrow', background=ROW_EVEN)
        self.tree.tag_configure('oddrow', background=ROW_ODD)
        self.tree.tag_configure('illuminado', background=ILLUMINADO_BG)
        self.tree.tag_configure('soldout', background=SOLDOUT_BG)

        # Button styling
        style.configure("Accent.TButton", background=BTN_COLOR, foreground="white", font=FONT_LABEL, borderwidth=0)
        style.map("Accent.TButton", background=[("active", BTN_HOVER)], foreground=[("active", "white")])

        # Main button frame
        btn_frame = tk.Frame(self.root, bg=BG_FRAME)
        btn_frame.pack(pady=10, fill='x')
        
        buttons = [
            (EMOJI_TICKET + " Buy Ticket", self.buy_ticket),
            (EMOJI_SEAT_SELECT + " Select Seat", self.select_seat),
            (EMOJI_HISTORY + " History", self.show_history),
            (EMOJI_EXPORT + " Export CSV", self.export_csv),
            (EMOJI_PAYMENT + " Payment", self.show_payment_options),
            (EMOJI_LOYALTY + " Loyalty", self.show_loyalty_info),
            (EMOJI_SAFETY + " Safety", self.show_safety_info),
            (EMOJI_RESET + " Admin Reset", self.reset_seats)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(btn_frame, text=text, style="Accent.TButton", 
                      command=command).grid(row=0, column=i, padx=2, sticky='ew')
            btn_frame.columnconfigure(i, weight=1)

    def change_language(self):
        self.current_language = self.lang_var.get()
        messagebox.showinfo(EMOJI_LANGUAGE + " Language Changed", 
                          f"Language changed to {LANGUAGES[self.current_language]}")

    def refresh_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_destination = self.destination_var.get()
        
        for idx, (name, data) in enumerate(self.transport_data.items()):
            if filtered_destination != "All" and data.get('destination', '') != filtered_destination:
                continue
                
            display_name = f"{transport_emoji(data['type'])} {name}"
            display_type = f"{transport_emoji(data['type'])} {data['type'].capitalize()}"
            tags = ()
            if data['seats'] == 0:
                tags = ('soldout',)
                display_name += " " + EMOJI_SOLDOUT
            elif data['type'] == 'illuminado':
                tags = ('illuminado',)
            else:
                tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
            
            self.tree.insert('', 'end', iid=name, values=(
                display_name,
                data.get('destination', 'N/A'),
                data['next_departure'],
                f"RWF {data['price']:,}",
                f"{EMOJI_SEAT} {data['seats']}",
                display_type
            ), tags=tags)

    def buy_ticket(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(EMOJI_FAIL + " No selection", "Please select a transport option.")
            return
        
        name = selected_item[0]
        data = self.transport_data[name]
        
        if data['seats'] <= 0:
            messagebox.showinfo(EMOJI_SOLDOUT + " Sold Out", "No seats available.")
            return

        # Show luggage options
        luggage_window = tk.Toplevel(self.root)
        luggage_window.title(EMOJI_LUGGAGE + " Luggage Options")
        luggage_window.geometry("400x300")
        
        ttk.Label(luggage_window, text="Select your luggage option:", font=FONT_LABEL).pack(pady=10)
        
        self.luggage_var = tk.StringVar(value=self.selected_luggage)
        
        for luggage_id, luggage_info in LUGGAGE_OPTIONS.items():
            frame = tk.Frame(luggage_window)
            frame.pack(fill='x', padx=20, pady=5)
            
            ttk.Radiobutton(frame, text=f"{luggage_info['emoji']} {luggage_info['name']} - RWF {luggage_info['price']:,}", 
                           variable=self.luggage_var, value=luggage_id).pack(side='left')
        
        def confirm_luggage():
            self.selected_luggage = self.luggage_var.get()
            luggage_window.destroy()
            self.confirm_ticket_purchase(name, data)
        
        ttk.Button(luggage_window, text="Confirm", command=confirm_luggage).pack(pady=10)

    def confirm_ticket_purchase(self, name, data):
        luggage_price = LUGGAGE_OPTIONS[self.selected_luggage]['price']
        total_price = data['price'] + luggage_price
        
        # Apply loyalty discount
        discount = self.calculate_loyalty_discount()
        discount_amount = total_price * discount // 100
        final_price = total_price - discount_amount
        
        confirm_msg = f"""
Buy ticket for {transport_emoji(data['type'])} {name}
To: {data.get('destination', 'Unknown')}
Departure: {data['next_departure']}

Base Price: RWF {data['price']:,}
Luggage: {LUGGAGE_OPTIONS[self.selected_luggage]['name']} - RWF {luggage_price:,}
Loyalty Discount: {discount}% (-RWF {discount_amount:,})
────────────────────────
TOTAL: RWF {final_price:,}

Remaining seats: {data['seats']} {EMOJI_SEAT}
        """
        
        confirm = messagebox.askyesno(EMOJI_TICKET + " Confirm Purchase", confirm_msg)
        if confirm:
            self.process_payment(name, data, final_price)

    def calculate_loyalty_discount(self):
        user_profile = self.user_profiles.get(self.username, {})
        total_rides = user_profile.get('total_rides', 0)
        
        current_discount = 0
        for tier, info in LOYALTY_TIERS.items():
            if total_rides >= info['min_rides']:
                current_discount = info['discount']
        
        return current_discount

    def process_payment(self, name, data, final_price):
        payment_window = tk.Toplevel(self.root)
        payment_window.title(EMOJI_PAYMENT + " Payment Options")
        payment_window.geometry("500x400")
        
        ttk.Label(payment_window, text="Select payment method:", font=FONT_LABEL).pack(pady=10)
        
        for provider, ussd_template in MOBILE_MONEY_PROVIDERS.items():
            frame = tk.Frame(payment_window)
            frame.pack(fill='x', padx=20, pady=5)
            
            ussd_code = ussd_template.format(amount=final_price)
            
            ttk.Button(frame, text=f"{provider}\n{ussd_code}", 
                      command=lambda p=provider, u=ussd_code: self.complete_payment(name, data, final_price, p, u),
                      width=40).pack(fill='x')

    def complete_payment(self, name, data, final_price, provider, ussd_code):
        # Simulate payment processing
        payment_success = random.choice([True, True, True, False])  # 75% success rate
        
        if payment_success:
            self.complete_purchase(name, data, final_price, provider)
        else:
            messagebox.showerror(EMOJI_FAIL + " Payment Failed", 
                               f"Payment via {provider} failed. Please try again.")

    def complete_purchase(self, name, data, final_price, provider):
        # Update seats and schedule
        data['seats'] -= 1
        data['schedule_index'] = (data['schedule_index'] + 1) % len(data['schedule'])
        data['next_departure'] = data['schedule'][data['schedule_index']]
        
        # Update loyalty points
        self.loyalty_points += final_price // 100  # 1 point per 100 RWF
        if self.username in self.user_profiles:
            self.user_profiles[self.username]['loyalty_points'] = self.loyalty_points
            self.user_profiles[self.username]['total_rides'] = self.user_profiles[self.username].get('total_rides', 0) + 1
        
        # Save booking
        entry = {
            'name': name,
            'destination': data.get('destination', 'Unknown'),
            'departure': data['next_departure'],
            'base_price': data['price'],
            'luggage_price': LUGGAGE_OPTIONS[self.selected_luggage]['price'],
            'total_price': final_price,
            'payment_method': provider,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            'user': self.username,
            'seat': self.selected_seat
        }
        
        self.booking_history.append(entry)
        self.save_history()
        self.save_state()
        self.save_user_profiles()
        
        self.refresh_treeview()
        self.loyalty_label.config(text=f"{EMOJI_LOYALTY} Points: {self.loyalty_points}")
        
        # Generate QR code (simulated)
        qr_info = f"""
{EMOJI_QR} ILLUMINADO E-TICKET {EMOJI_QR}
Route: {name}
Destination: {data.get('destination', 'Unknown')}
Departure: {data['next_departure']}
Seat: {self.selected_seat or 'Any'}
Passenger: {self.username}
Ticket ID: {random.randint(100000, 999999)}
        """
        
        messagebox.showinfo(EMOJI_SUCCESS + " Booking Complete", 
                          f"Payment successful via {provider}!\n\n{qr_info}")

    def select_seat(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(EMOJI_FAIL + " No selection", "Please select a transport option first.")
            return
            
        seat_window = tk.Toplevel(self.root)
        seat_window.title(EMOJI_SEAT_SELECT + " Select Your Seat")
        seat_window.geometry("400x500")
        
        ttk.Label(seat_window, text="Choose your preferred seat:", font=FONT_LABEL).pack(pady=10)
        
        # Create seat map (5 rows, 4 columns)
        seat_frame = tk.Frame(seat_window)
        seat_frame.pack(pady=10)
        
        seats = []
        for row in range(5):
            row_frame = tk.Frame(seat_frame)
            row_frame.pack()
            for col in range(4):
                seat_num = row * 4 + col + 1
                seat_btn = tk.Button(row_frame, text=str(seat_num), width=4, height=2,
                                   command=lambda sn=seat_num: self.confirm_seat(sn, seat_window))
                seat_btn.grid(row=row, column=col, padx=2, pady=2)
                seats.append(seat_btn)
        
        # Mark some seats as occupied
        occupied_seats = random.sample(range(1, 21), 5)
        for seat_num in occupied_seats:
            seats[seat_num-1].config(text="X", state="disabled", bg="red")

    def confirm_seat(self, seat_num, window):
        self.selected_seat = seat_num
        window.destroy()
        messagebox.showinfo(EMOJI_SEAT_SELECT + " Seat Selected", 
                          f"Seat {seat_num} has been selected!")

    def show_payment_options(self):
        payment_info = """
Available Payment Methods:

MTN Mobile Money: *182*6*1*1*078xxxxxx*amount#
Airtel Money: *182*1*1*078xxxxxx*amount#  
Tigo Cash: *188*1*1*078xxxxxx*amount#

All payments are secure and encrypted.
        """
        messagebox.showinfo(EMOJI_PAYMENT + " Payment Methods", payment_info)

    def show_loyalty_info(self):
        user_profile = self.user_profiles.get(self.username, {})
        total_rides = user_profile.get('total_rides', 0)
        points = user_profile.get('loyalty_points', 0)
        
        # Calculate current tier
        current_tier = "Bronze"
        current_discount = 0
        for tier, info in LOYALTY_TIERS.items():
            if total_rides >= info['min_rides']:
                current_tier = info['name']
                current_discount = info['discount']
        
        loyalty_info = f"""
{EMOJI_LOYALTY} LOYALTY PROGRAM {EMOJI_LOYALTY}

Current Status: {current_tier} Tier
Total Rides: {total_rides}
Loyalty Points: {points}
Current Discount: {current_discount}%

Tiers:
• Bronze (0+ rides) - 0% discount
• Silver (10+ rides) - 5% discount  
• Gold (25+ rides) - 10% discount
• Platinum (50+ rides) - 15% discount

Earn 1 point for every 100 RWF spent!
        """
        messagebox.showinfo(EMOJI_LOYALTY + " Loyalty Program", loyalty_info)

    def show_safety_info(self):
        safety_info = f"""
{EMOJI_SAFETY} SAFETY FEATURES {EMOJI_SAFETY}

Emergency Contacts:
• Police: 112
• Ambulance: 912
• Fire: 111

Safety Tips:
• Always wear your seatbelt
• Keep valuables secure
• Report suspicious activity
• Follow COVID-19 guidelines

Vehicle Safety:
• Regular maintenance checks
• GPS tracking enabled
• Emergency exits marked
• First aid available

Your safety is our priority!
        """
        messagebox.showinfo(EMOJI_SAFETY + " Safety Information", safety_info)

    def show_weather_alert(self):
        # Simulate weather alerts
        weather_conditions = [
            "Sunny day - Safe travels!",
            "Light rain expected - Drive carefully",
            "Heavy rainfall warning - Possible delays",
            "Foggy conditions - Reduced visibility"
        ]
        
        alert = random.choice(weather_conditions)
        if alert != "Sunny day - Safe travels!":
            messagebox.showwarning(EMOJI_WEATHER + " Weather Alert", alert)

    def show_history(self):
        if not self.booking_history:
            messagebox.showinfo(EMOJI_HISTORY + " Booking History", "No bookings yet.")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title(EMOJI_HISTORY + " Booking History")
        history_window.geometry("800x600")
        
        text_area = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, width=80, height=30)
        text_area.pack(padx=10, pady=10, fill='both', expand=True)
        
        history_text = f"{EMOJI_HISTORY} Booking History for {self.username}\n{'='*50}\n\n"
        
        for idx, entry in enumerate(reversed(self.booking_history[-20:]), 1):  # Show last 20 bookings
            history_text += f"""Booking {idx}:
Route: {entry['name']}
Destination: {entry.get('destination', 'Unknown')}
Departure: {entry['departure']}
Date: {entry['date']}
Seat: {entry.get('seat', 'Any')}
Base Price: RWF {entry['base_price']:,}
Luggage: RWF {entry.get('luggage_price', 0):,}
Total Paid: RWF {entry['total_price']:,}
Payment: {entry.get('payment_method', 'Unknown')}
{'─'*40}\n
"""
        
        text_area.insert(tk.INSERT, history_text)
        text_area.config(state=tk.DISABLED)

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                for entry in self.booking_history:
                    line = f"{entry['name']}|{entry.get('destination', 'Unknown')}|{entry['departure']}|{entry['base_price']}|{entry.get('luggage_price', 0)}|{entry['total_price']}|{entry.get('payment_method', 'Unknown')}|{entry['date']}|{entry['user']}|{entry.get('seat', 'Any')}\n"
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
                    if len(parts) >= 9:
                        try:
                            self.booking_history.append({
                                'name': parts[0],
                                'destination': parts[1],
                                'departure': parts[2],
                                'base_price': int(parts[3]),
                                'luggage_price': int(parts[4]),
                                'total_price': int(parts[5]),
                                'payment_method': parts[6],
                                'date': parts[7],
                                'user': parts[8],
                                'seat': parts[9] if len(parts) > 9 else 'Any'
                            })
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error loading history: {e}")

    def save_user_profiles(self):
        try:
            with open(USER_PROFILES_FILE, "w") as f:
                json.dump(self.user_profiles, f)
        except Exception as e:
            print(f"Error saving user profiles: {e}")

    def load_user_profiles(self):
        if not os.path.exists(USER_PROFILES_FILE):
            self.user_profiles = {}
            return
        try:
            with open(USER_PROFILES_FILE, "r") as f:
                self.user_profiles = json.load(f)
        except Exception as e:
            print(f"Error loading user profiles: {e}")
            self.user_profiles = {}

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
            seats = 20
            schedule_index = 0
            name = option['name']
            if name in state:
                seats = state[name].get('seats', 20)
                schedule_index = state[name].get('schedule_index', 0)
                if not isinstance(schedule_index, int) or schedule_index < 0 or schedule_index >= len(schedule):
                    schedule_index = 0
            next_departure = schedule[schedule_index]
            self.transport_data[name] = {
                'seats': seats,
                'price': option['price'],
                'next_departure': next_departure,
                'type': option['type'],
                'destination': option.get('destination', 'Unknown'),
                'schedule': schedule,
                'schedule_index': schedule_index
            }

    def reset_seats(self):
        confirm = messagebox.askyesno(EMOJI_RESET + " Reset All Seats", 
                                    "Are you sure you want to reset all seats to 20 and schedules to the start?")
        if confirm:
            for option in transport_options:
                schedule = generate_schedule(option['start_time'])
                next_departure = schedule[0]
                seats = 20
                self.transport_data[option['name']] = {
                    'seats': seats,
                    'price': option['price'],
                    'next_departure': next_departure,
                    'type': option['type'],
                    'destination': option.get('destination', 'Unknown'),
                    'schedule': schedule,
                    'schedule_index': 0
                }
            self.save_state()
            self.refresh_treeview()
            messagebox.showinfo(EMOJI_RESET + " Reset Complete", "All seats and schedules have been reset!")

    def export_csv(self):
        if not self.booking_history:
            messagebox.showinfo(EMOJI_EXPORT + " Export CSV", "No bookings to export.")
            return
        try:
            with open(CSV_FILE, "w", newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'destination', 'departure', 'base_price', 'luggage_price', 'total_price', 'payment_method', 'date', 'user', 'seat']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for entry in self.booking_history:
                    writer.writerow(entry)
            messagebox.showinfo(EMOJI_EXPORT + " Export CSV", f"Booking history exported to {CSV_FILE}")
        except Exception as e:
            messagebox.showerror(EMOJI_FAIL + " Export CSV", f"Failed to export CSV: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TransportApp(root)
    root.mainloop()