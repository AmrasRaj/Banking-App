import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, csv, hashlib, secrets
from datetime import datetime
from decimal import Decimal, InvalidOperation

BASE = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE, "accounts.json")
TRANSACTIONS_FILE = os.path.join(BASE, "transactions.json")
RATES = {"Savings": 0.04, "Current": 0.00, "Fixed Deposit": 0.07}


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path, data):
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    os.replace(temporary, path)


def make_pin_hash(pin, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), 200000).hex()
    return salt, digest


def rupees(amount):
    return f"₹{float(amount):,.2f}"


class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NovaBank | Account Simulation")
        self.root.geometry("1120x760")
        self.root.minsize(940, 640)
        self.root.configure(bg="#F2F5FB")
        self.accounts = load_json(ACCOUNTS_FILE, {})
        self.transactions = load_json(TRANSACTIONS_FILE, [])
        self.logged_in = None
        self.colors = {
            "navy": "#14213D", "blue": "#2563EB", "cyan": "#06B6D4",
            "purple": "#7C3AED", "green": "#059669", "orange": "#EA580C",
            "red": "#DC2626", "bg": "#F2F5FB", "white": "#FFFFFF",
            "text": "#1F2937", "muted": "#64748B", "line": "#DCE4F0",
            "pale_blue": "#E8F0FF", "pale_cyan": "#E2F8FC", "pale_green": "#E4F8EF"
        }
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.colors["bg"], foreground=self.colors["navy"], font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background=self.colors["bg"], foreground=self.colors["muted"], font=("Segoe UI", 10))
        style.configure("Strong.TLabel", background=self.colors["bg"], foreground=self.colors["navy"], font=("Segoe UI", 13, "bold"))
        style.configure("Card.TFrame", background=self.colors["white"], relief="flat")
        style.configure("CardTitle.TLabel", background=self.colors["white"], foreground=self.colors["muted"], font=("Segoe UI", 10, "bold"))
        style.configure("CardValue.TLabel", background=self.colors["white"], foreground=self.colors["navy"], font=("Segoe UI", 17, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(13, 9), background=self.colors["blue"], foreground="white", borderwidth=0)
        style.map("TButton", background=[("active", "#1D4ED8"), ("pressed", "#1E40AF")], foreground=[("disabled", "#CBD5E1")])
        style.configure("Secondary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8), background="#E3EAF5", foreground=self.colors["navy"])
        style.map("Secondary.TButton", background=[("active", "#D2DEEF")])
        style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8), background=self.colors["green"], foreground="white")
        style.map("Success.TButton", background=[("active", "#047857")])
        style.configure("TEntry", padding=8, fieldbackground="white", foreground=self.colors["text"])
        style.configure("TCombobox", padding=7, fieldbackground="white")
        style.configure("TLabelframe", background=self.colors["white"], bordercolor=self.colors["line"], relief="solid")
        style.configure("TLabelframe.Label", background=self.colors["white"], foreground=self.colors["blue"], font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0, tabmargins=(2, 4, 2, 0))
        style.configure("TNotebook.Tab", padding=(17, 10), font=("Segoe UI", 10, "bold"), background="#E2E8F0", foreground=self.colors["navy"])
        style.map("TNotebook.Tab", background=[("selected", self.colors["blue"])], foreground=[("selected", "white")])
        style.configure("Treeview", background="white", fieldbackground="white", foreground=self.colors["text"], rowheight=30, font=("Segoe UI", 9), bordercolor=self.colors["line"])
        style.configure("Treeview.Heading", background=self.colors["navy"], foreground="white", font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", self.colors["navy"])])
        self.login_screen()

    def save_all(self):
        save_json(ACCOUNTS_FILE, self.accounts)
        save_json(TRANSACTIONS_FILE, self.transactions)

    def add_transaction(self, account_no, kind, amount, details=""):
        self.transactions.append({
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "account_no": account_no, "type": kind,
            "amount": round(float(amount), 2), "details": details
        })
        self.save_all()

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()

    def login_screen(self):
        self.logged_in = None
        self.clear()
        self.root.configure(bg=self.colors["bg"])
        shell = ttk.Frame(self.root, padding=28)
        shell.pack(fill="both", expand=True)
        banner = tk.Frame(shell, bg=self.colors["navy"], height=145)
        banner.pack(fill="x", pady=(0, 22))
        banner.pack_propagate(False)
        tk.Label(banner, text="NOVA BANK", bg=self.colors["navy"], fg="#67E8F9",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30, pady=(22, 3))
        tk.Label(banner, text="Your money. Your future.", bg=self.colors["navy"], fg="white",
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", padx=30)
        tk.Label(banner, text="A colorful, secure banking simulation", bg=self.colors["navy"], fg="#CBD5E1",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=32, pady=(4, 0))

        card = ttk.Frame(shell, style="Card.TFrame", padding=28)
        card.pack(anchor="n", ipadx=35, ipady=12)
        ttk.Label(card, text="Welcome back", font=("Segoe UI", 19, "bold"), background="white", foreground=self.colors["navy"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 3))
        ttk.Label(card, text="Sign in with your account number and PIN", background="white", foreground=self.colors["muted"]).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))
        ttk.Label(card, text="ACCOUNT NUMBER", background="white", foreground=self.colors["muted"], font=("Segoe UI", 9, "bold")).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 5))
        self.login_no = tk.StringVar()
        ttk.Entry(card, textvariable=self.login_no, width=37).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(card, text="SECURITY PIN", background="white", foreground=self.colors["muted"], font=("Segoe UI", 9, "bold")).grid(row=4, column=0, columnspan=2, sticky="w", pady=(3, 5))
        self.login_pin = tk.StringVar()
        pin_entry = ttk.Entry(card, textvariable=self.login_pin, show="●", width=37)
        pin_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        ttk.Button(card, text="SIGN IN  →", command=self.login, style="Success.TButton").grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Button(card, text="＋  Create New User / Account", command=self.create_form, style="Secondary.TButton").grid(row=7, column=0, columnspan=2, sticky="ew")
        ttk.Label(shell, text="🔒  PINs are stored as salted hashes. Use fictional details for this educational demo.", style="Subtitle.TLabel").pack(pady=18)
        pin_entry.bind("<Return>", lambda event: self.login())

    def login(self):
        no, pin = self.login_no.get().strip(), self.login_pin.get().strip()
        account = self.accounts.get(no)
        if not account or not pin:
            messagebox.showerror("Login failed", "Enter a valid account number and PIN.")
            return
        _, digest = make_pin_hash(pin, account["pin_salt"])
        if secrets.compare_digest(digest, account["pin_hash"]):
            self.logged_in = no
            self.dashboard()
        else:
            messagebox.showerror("Login failed", "Incorrect account number or PIN.")

    def create_form(self):
        self.clear()
        shell = ttk.Frame(self.root, padding=28)
        shell.pack(fill="both", expand=True)
        banner = tk.Frame(shell, bg=self.colors["purple"], height=92)
        banner.pack(fill="x", pady=(0, 22))
        banner.pack_propagate(False)
        tk.Label(banner, text="CUSTOMER ONBOARDING", bg=self.colors["purple"], fg="#EDE9FE",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24, pady=(15, 2))
        tk.Label(banner, text="Create your bank account", bg=self.colors["purple"], fg="white",
                 font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=24)
        card = ttk.Frame(shell, style="Card.TFrame", padding=25)
        card.pack(anchor="n", fill="x", padx=45)
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Savings")
        self.pin_var = tk.StringVar()
        self.balance_var = tk.StringVar(value="0")
        fields = [
            ("Customer name", self.name_var, "entry"),
            ("Phone (optional)", self.phone_var, "entry"),
            ("Account type", self.type_var, "combo"),
            ("PIN (4–8 digits)", self.pin_var, "pin"),
            ("Opening balance (₹)", self.balance_var, "entry")
        ]
        for i, (label, variable, kind) in enumerate(fields):
            ttk.Label(card, text=label, background="white", foreground=self.colors["navy"], font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", padx=(0, 30), pady=10)
            if kind == "combo":
                ttk.Combobox(card, textvariable=variable, values=list(RATES), state="readonly", width=32).grid(row=i, column=1, sticky="ew", pady=10)
            else:
                ttk.Entry(card, textvariable=variable, show="●" if kind == "pin" else "", width=35).grid(row=i, column=1, sticky="ew", pady=10)
        card.columnconfigure(1, weight=1)
        tk.Label(card, text="SAVINGS  •  4%     CURRENT  •  0%     FIXED DEPOSIT  •  7%", bg="white", fg=self.colors["blue"], font=("Segoe UI", 9, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", pady=(12, 16))
        buttons = ttk.Frame(card, style="Card.TFrame")
        buttons.grid(row=6, column=0, columnspan=2, sticky="w")
        ttk.Button(buttons, text="Create Account", command=self.create_account, style="Success.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(buttons, text="← Back to Login", command=self.login_screen, style="Secondary.TButton").pack(side="left")

    def create_account(self):
        name, phone = self.name_var.get().strip(), self.phone_var.get().strip()
        pin, typ = self.pin_var.get().strip(), self.type_var.get()
        try:
            opening = Decimal(self.balance_var.get().strip())
            if not opening.is_finite() or opening < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            messagebox.showerror("Invalid balance", "Enter a valid non-negative opening balance."); return
        if not name:
            messagebox.showerror("Missing name", "Enter the customer's name."); return
        if not (pin.isdigit() and 4 <= len(pin) <= 8):
            messagebox.showerror("Invalid PIN", "PIN must contain 4 to 8 digits."); return
        if typ == "Fixed Deposit" and opening <= 0:
            messagebox.showerror("Opening balance required", "Fixed Deposit requires a positive opening balance."); return
        no = "AC" + secrets.token_hex(4).upper()
        salt, digest = make_pin_hash(pin)
        self.accounts[no] = {
            "account_no": no, "name": name, "phone": phone, "account_type": typ,
            "balance": round(float(opening), 2), "pin_salt": salt, "pin_hash": digest,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds")
        }
        self.save_all()
        if opening > 0:
            self.add_transaction(no, "Opening Deposit", opening, "Opening balance")
        messagebox.showinfo("Account created", f"Account created successfully.\nAccount number: {no}\nKeep this number safe.")
        self.login_screen()

    def dashboard(self):
        self.clear()
        acc = self.accounts[self.logged_in]
        shell = ttk.Frame(self.root, padding=(22, 18))
        shell.pack(fill="both", expand=True)

        top = tk.Frame(shell, bg=self.colors["navy"], height=100)
        top.pack(fill="x", pady=(0, 16))
        top.pack_propagate(False)
        tk.Label(top, text="NOVA BANK  /  DIGITAL BANKING", bg=self.colors["navy"], fg="#67E8F9",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=22, pady=(14, 2))
        title_row = tk.Frame(top, bg=self.colors["navy"])
        title_row.pack(fill="x", padx=22)
        tk.Label(title_row, text=f"Hello, {acc['name']} 👋", bg=self.colors["navy"], fg="white",
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Button(title_row, text="Logout", command=self.login_screen, style="Secondary.TButton").pack(side="right", padx=(8, 0))

        cards = ttk.Frame(shell)
        cards.pack(fill="x", pady=(0, 16))
        card_specs = [
            ("AVAILABLE BALANCE", rupees(acc["balance"]), self.colors["blue"]),
            ("ACCOUNT TYPE", acc["account_type"], self.colors["purple"]),
            ("ACCOUNT NUMBER", self.logged_in, self.colors["green"]),
        ]
        for idx, (label, value, accent) in enumerate(card_specs):
            card = tk.Frame(cards, bg="white", highlightbackground=self.colors["line"], highlightthickness=1, padx=16, pady=13)
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0 if idx == 2 else 8))
            tk.Frame(card, bg=accent, height=4).pack(fill="x", pady=(0, 10))
            tk.Label(card, text=label, bg="white", fg=self.colors["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg="white", fg=self.colors["navy"], font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(5, 0))
            cards.columnconfigure(idx, weight=1, uniform="cards")

        detail = ttk.Label(shell, text="Choose an action below to manage transactions, transfer funds, calculate interest, or view your history.", style="Subtitle.TLabel")
        detail.pack(anchor="w", pady=(0, 9))
        book = ttk.Notebook(shell)
        book.pack(fill="both", expand=True)
        self.transaction_tab(book)
        self.transfer_tab(book)
        self.interest_tab(book)
        self.history_tab(book)

    def transaction_tab(self, book):
        tab = ttk.Frame(book, padding=20); book.add(tab, text="Deposit / Withdraw")
        amount = tk.StringVar(); kind = tk.StringVar(value="Deposit")
        ttk.Label(tab, text="Transaction type").grid(row=0, column=0, sticky="w", pady=8)
        ttk.Combobox(tab, textvariable=kind, values=["Deposit", "Withdraw"], state="readonly", width=22).grid(row=0, column=1, pady=8)
        ttk.Label(tab, text="Amount (₹)").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(tab, textvariable=amount, width=25).grid(row=1, column=1, pady=8)
        def submit():
            try:
                value = Decimal(amount.get().strip())
                if not value.is_finite() or value <= 0: raise InvalidOperation
            except (InvalidOperation, ValueError):
                messagebox.showerror("Invalid amount", "Enter an amount greater than zero."); return
            acc = self.accounts[self.logged_in]
            balance = Decimal(str(acc["balance"]))
            if kind.get() == "Withdraw":
                if acc["account_type"] == "Fixed Deposit":
                    messagebox.showwarning("Not allowed", "Withdrawals from Fixed Deposit are disabled in this demo."); return
                if value > balance:
                    messagebox.showerror("Insufficient funds", "Your balance is not enough."); return
                acc["balance"] = round(float(balance - value), 2)
            else:
                acc["balance"] = round(float(balance + value), 2)
            self.add_transaction(self.logged_in, kind.get(), value)
            messagebox.showinfo("Success", f"{kind.get()} successful.")
            self.dashboard()
        ttk.Button(tab, text="✓  Submit Transaction", command=submit, style="Success.TButton").grid(row=2, column=0, columnspan=2, pady=15, sticky="w")

    def transfer_tab(self, book):
        tab = ttk.Frame(book, padding=20); book.add(tab, text="Fund Transfer")
        receiver = tk.StringVar(); amount = tk.StringVar()
        ttk.Label(tab, text="Receiver account number").grid(row=0, column=0, sticky="w", pady=8)
        ttk.Entry(tab, textvariable=receiver, width=28).grid(row=0, column=1, pady=8)
        ttk.Label(tab, text="Amount (₹)").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Entry(tab, textvariable=amount, width=28).grid(row=1, column=1, pady=8)
        def submit_transfer():
            to = receiver.get().strip()
            if to == self.logged_in or to not in self.accounts:
                messagebox.showerror("Invalid receiver", "Enter a different existing account number."); return
            try:
                value = Decimal(amount.get().strip())
                if not value.is_finite() or value <= 0: raise InvalidOperation
            except (InvalidOperation, ValueError):
                messagebox.showerror("Invalid amount", "Enter an amount greater than zero."); return
            sender_acc, receiver_acc = self.accounts[self.logged_in], self.accounts[to]
            if sender_acc["account_type"] == "Fixed Deposit":
                messagebox.showwarning("Not allowed", "Transfers from Fixed Deposit are disabled in this demo."); return
            if value > Decimal(str(sender_acc["balance"])):
                messagebox.showerror("Insufficient funds", "Your balance is not enough."); return
            sender_acc["balance"] = round(float(Decimal(str(sender_acc["balance"])) - value), 2)
            receiver_acc["balance"] = round(float(Decimal(str(receiver_acc["balance"])) + value), 2)
            self.add_transaction(self.logged_in, "Transfer Sent", value, f"To {to}")
            self.add_transaction(to, "Transfer Received", value, f"From {self.logged_in}")
            messagebox.showinfo("Transfer complete", f"Transferred {rupees(value)} to {to}.")
            self.dashboard()
        ttk.Button(tab, text="⇄  Transfer Funds", command=submit_transfer, style="Success.TButton").grid(row=2, column=0, columnspan=2, pady=15, sticky="w")
        ttk.Label(tab, text="Both sender and receiver get a timestamped history entry.").grid(row=3, column=0, columnspan=2, sticky="w")

    def interest_tab(self, book):
        tab = ttk.Frame(book, padding=20); book.add(tab, text="Interest Calculator")
        acc = self.accounts[self.logged_in]; rate = RATES[acc["account_type"]]
        ttk.Label(tab, text=f"Account type: {acc['account_type']}").pack(anchor="w", pady=5)
        ttk.Label(tab, text=f"Demo annual rate: {rate * 100:.2f}%").pack(anchor="w", pady=5)
        ttk.Label(tab, text="Number of years").pack(anchor="w", pady=(12, 3))
        years = tk.StringVar(value="1"); ttk.Entry(tab, textvariable=years, width=15).pack(anchor="w")
        result = tk.StringVar(value="Estimated interest: —")
        ttk.Label(tab, textvariable=result, style="Strong.TLabel").pack(anchor="w", pady=12)
        def calc():
            try:
                yrs = Decimal(years.get().strip())
                if not yrs.is_finite() or yrs < 0: raise InvalidOperation
            except (InvalidOperation, ValueError):
                messagebox.showerror("Invalid years", "Enter a valid non-negative number."); return
            bal = Decimal(str(self.accounts[self.logged_in]["balance"]))
            interest = bal * Decimal(str(rate)) * yrs
            result.set(f"Estimated simple interest: {rupees(interest)} | Total: {rupees(bal + interest)}")
        ttk.Button(tab, text="Calculate Interest", command=calc, style="Success.TButton").pack(anchor="w", pady=5)
        ttk.Label(tab, text="Interest is estimated only; it is not automatically added to the balance.", foreground="gray").pack(anchor="w", pady=8)

    def history_tab(self, book):
        tab = ttk.Frame(book, padding=10); book.add(tab, text="Transaction History")
        cols = ("timestamp", "type", "amount", "details")
        tree = ttk.Treeview(tab, columns=cols, show="headings", height=14)
        for col, title, width in [
            ("timestamp", "Timestamp", 230), ("type", "Transaction", 150),
            ("amount", "Amount (₹)", 120), ("details", "Details", 300)
        ]:
            tree.heading(col, text=title); tree.column(col, width=width)
        tree.pack(fill="both", expand=True)
        txns = [t for t in self.transactions if t.get("account_no") == self.logged_in]
        for t in reversed(txns):
            tree.insert("", "end", values=(t.get("timestamp", ""), t.get("type", ""), f"{t.get('amount', 0):.2f}", t.get("details", "")))
        buttons = ttk.Frame(tab); buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="↻  Refresh", command=self.dashboard, style="Secondary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="↓  Export History to CSV", command=self.export_history, style="Success.TButton").pack(side="left")

    def export_history(self):
        txns = [t for t in self.transactions if t.get("account_no") == self.logged_in]
        if not txns:
            messagebox.showinfo("No history", "There are no transactions to export."); return
        filename = filedialog.asksaveasfilename(
            title="Export transaction history", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"transactions_{self.logged_in}.csv"
        )
        if not filename: return
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "account_no", "type", "amount", "details"])
            writer.writeheader(); writer.writerows(txns)
        messagebox.showinfo("Export complete", f"History saved to:\n{filename}")


if __name__ == "__main__":
    root = tk.Tk()
    BankApp(root)
    root.mainloop()
