import os
import tkinter as tk

import customtkinter as ctk
import mysql.connector

import database as db


ctk.set_appearance_mode("dark")

BG = "#12181F"
SIDEBAR = "#172129"
CARD = "#1B2530"
ACCENT = "#1FA398"
ACCENT_HOVER = "#17847B"
TEXT = "#E8ECEF"
SUBTEXT = "#8B98A5"
DANGER = "#D9534F"
DANGER_HOVER = "#B94441"

FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_HEADING = ("Segoe UI", 20, "bold")
FONT_SUB = ("Segoe UI", 14)
FONT_LABEL = ("Segoe UI", 13)
FONT_BUTTON = ("Segoe UI", 13, "bold")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
current_acc = None

root = ctk.CTk()
root.title("SecureBank")
root.configure(fg_color=BG)
try:
    root.state("zoomed")
except tk.TclError:
    root.geometry("1200x760")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

shell = ctk.CTkFrame(root, fg_color=BG, corner_radius=0)
shell.pack(fill="both", expand=True)


def clear(parent):
    for widget in parent.winfo_children():
        widget.destroy()


def entry(parent, placeholder, show=None, width=300):
    return ctk.CTkEntry(
        parent, placeholder_text=placeholder, show=show, width=width, height=40,
        corner_radius=7, fg_color=CARD, border_color=ACCENT, border_width=1,
        text_color=TEXT, font=FONT_LABEL
    )


def button(parent, text, command, danger=False, width=210):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=40,
        corner_radius=7, fg_color=DANGER if danger else ACCENT,
        hover_color=DANGER_HOVER if danger else ACCENT_HOVER,
        text_color="#FFFFFF", font=FONT_BUTTON
    )


def outline(parent, text, command, width=210):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=36,
        corner_radius=7, fg_color="transparent", border_width=1,
        border_color=SUBTEXT, text_color=SUBTEXT, hover_color=CARD,
        font=FONT_BUTTON
    )


def draw_bank_mark(parent, compact=False):
    image_path = os.path.join(os.path.dirname(__file__), "images.png")
    image = tk.PhotoImage(file=image_path)
    for pixel_x in range(image.width()):
        for pixel_y in range(image.height()):
            red, green, blue = image.get(pixel_x, pixel_y)
            if red > 245 and green > 245 and blue > 245:
                image.transparency_set(pixel_x, pixel_y, True)
    if compact:
        image = image.subsample(2, 2)
    logo = tk.Label(parent, image=image, bg=SIDEBAR, borderwidth=0)
    parent.logo_image = image
    logo.pack(pady=(5, 5) if compact else (20, 10))


def page_heading(parent, title, subtitle):
    ctk.CTkLabel(parent, text=title, font=FONT_TITLE, text_color=TEXT).pack(anchor="w")
    ctk.CTkLabel(parent, text=subtitle, font=FONT_SUB, text_color=SUBTEXT).pack(anchor="w", pady=(3, 22))


def show_message(parent, text, error=False):
    label = ctk.CTkLabel(parent, text=text, text_color=DANGER if error else ACCENT,
                         font=FONT_LABEL, wraplength=520, justify="left")
    label.pack(anchor="w", pady=(10, 0))
    return label


def nav_button(parent, text, command, selected=False):
    ctk.CTkButton(parent, text=text, command=command, width=205, height=38, corner_radius=7,
                  fg_color=ACCENT if selected else "transparent",
                  hover_color=ACCENT_HOVER if selected else CARD,
                  text_color=TEXT, anchor="w", font=FONT_BUTTON).pack(pady=4)


def show_customer_menu(nav, selected):
    menu = [
        ("Overview", show_customer_dashboard),
        ("Deposit", lambda: show_money_form("Deposit")),
        ("Withdraw", lambda: show_money_form("Withdraw")),
        ("Transfer", show_transfer_form),
        ("Transaction history", show_history),
        ("Change PIN", show_change_pin),
        ("Log out", logout_customer),
    ]
    for name, command in menu:
        nav_button(nav, name, command, name == selected)


def make_customer_shell(title):
    sidebar = ctk.CTkFrame(shell, width=245, fg_color=SIDEBAR, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    draw_bank_mark(sidebar, compact=True)
    ctk.CTkLabel(sidebar, text=title, font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(pady=(8, 22))
    content = ctk.CTkFrame(shell, fg_color=BG, corner_radius=0)
    content.pack(side="left", fill="both", expand=True, padx=46, pady=46)
    return content, sidebar


def show_welcome():
    clear(shell)
    sidebar = ctk.CTkFrame(shell, width=245, fg_color=SIDEBAR, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    draw_bank_mark(sidebar)
    ctk.CTkLabel(sidebar, text="SECUREBANK", font=("Segoe UI", 18, "bold"), text_color=TEXT).pack()
    ctk.CTkLabel(sidebar, text="Everyday banking, made clear", font=("Segoe UI", 11), text_color=SUBTEXT).pack(pady=(2, 32))
    button(sidebar, "Login", show_customer_login, width=205).pack(pady=5)
    button(sidebar, "Sign up", show_create_account, width=205).pack(pady=5)
    outline(sidebar, "Exit", root.destroy, width=205).pack(pady=5)

    content = ctk.CTkFrame(shell, fg_color=BG, corner_radius=0)
    content.pack(side="left", fill="both", expand=True)
    inner = ctk.CTkFrame(content, fg_color=BG, width=720)
    inner.pack(expand=True, padx=40, pady=40)
    page_heading(inner, "Welcome to SecureBank", "A small banking system for accounts, payments, and records.")
    card = ctk.CTkFrame(inner, fg_color=CARD, corner_radius=10)
    card.pack(fill="x", pady=10)
    ctk.CTkLabel(card, text="Login, sign up, or exit", font=FONT_HEADING, text_color=TEXT).pack(anchor="w", padx=28, pady=(25, 8))
    ctk.CTkLabel(card, text="Administrators use the same Login form with the admin credentials configured in main.py.", font=FONT_SUB, text_color=SUBTEXT, justify="left", wraplength=620).pack(anchor="w", padx=28, pady=(0, 25))


def show_customer_login():
    clear(shell)
    content, nav = make_customer_shell("Customer sign in")
    nav_button(nav, "Login", show_customer_login, True)
    nav_button(nav, "Sign up", show_create_account)
    nav_button(nav, "Home", show_welcome)
    page_heading(content, "Login", "Customers enter an account number and PIN. Admins enter admin and the admin password.")
    form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    form.pack(anchor="w", fill="x", pady=5)
    acc_entry = entry(form, "Account number")
    acc_entry.pack(anchor="w", padx=28, pady=(28, 8))
    pin_entry = entry(form, "PIN or admin password", show="*")
    pin_entry.pack(anchor="w", padx=28, pady=8)
    status = ctk.CTkLabel(form, text="", text_color=DANGER, font=FONT_LABEL)
    status.pack(anchor="w", padx=28, pady=(4, 0))

    def attempt_login():
        global current_acc
        account = acc_entry.get().strip()
        password = pin_entry.get().strip()
        if account == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            show_admin_dashboard()
            return
        try:
            if db.verify_customer_login(account, password):
                current_acc = account
                show_customer_dashboard()
            else:
                status.configure(text="Invalid account number or PIN")
        except mysql.connector.Error as error:
            status.configure(text=f"Database error: {error}")

    button(form, "Login", attempt_login).pack(anchor="w", padx=28, pady=(18, 10))
    outline(form, "Forgot PIN?", show_forgot_pin).pack(anchor="w", padx=28, pady=(0, 28))


def show_forgot_pin():
    clear(shell)
    content, nav = make_customer_shell("Forgot PIN")
    nav_button(nav, "Login", show_customer_login)
    nav_button(nav, "Sign up", show_create_account)
    nav_button(nav, "Home", show_welcome)
    page_heading(content, "Forgot PIN", "Verify your account and phone number so support can contact you.")
    form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    form.pack(anchor="w", fill="x")
    account_entry = entry(form, "Account number")
    phone_entry = entry(form, "Phone number")
    account_entry.pack(anchor="w", padx=28, pady=(28, 8))
    phone_entry.pack(anchor="w", padx=28, pady=8)
    status = ctk.CTkLabel(form, text="", font=FONT_LABEL, text_color=DANGER, wraplength=520)
    status.pack(anchor="w", padx=28)

    def submit():
        account = account_entry.get().strip()
        phone = phone_entry.get().strip()
        if not account or not phone:
            status.configure(text="Enter both your account number and phone number")
            return
        try:
            verified = db.get_phone_for_account(account, phone)
        except mysql.connector.Error as error:
            status.configure(text=f"Database error: {error}")
            return
        if not verified:
            status.configure(text="The account number and phone number did not match")
            return
        masked_phone = "X" * max(0, len(phone) - 2) + phone[-2:]
        status.configure(text=f"You will be contacted at {masked_phone} by the bank support team.", text_color=ACCENT)

    button(form, "Request help", submit).pack(anchor="w", padx=28, pady=(18, 28))


def show_create_account():
    clear(shell)
    content, nav = make_customer_shell("Open an account")
    nav_button(nav, "Login", show_customer_login)
    nav_button(nav, "Sign up", show_create_account, True)
    nav_button(nav, "Home", show_welcome)
    page_heading(content, "Open an account", "Start with a name, a secure PIN, and at least Rs. 500.")
    form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    form.pack(anchor="w", fill="x", pady=5)
    fields = [entry(form, "Full name"), entry(form, "Phone number"),
              entry(form, "Set a 4-digit PIN", show="*"), entry(form, "Confirm PIN", show="*"),
              entry(form, "Initial deposit")]
    for field in fields:
        field.pack(anchor="w", padx=28, pady=6)
    status = ctk.CTkLabel(form, text="", text_color=DANGER, font=FONT_LABEL, wraplength=520)
    status.pack(anchor="w", padx=28, pady=(3, 0))

    def create():
        name, phone, pin, confirmation, deposit_text = [field.get().strip() for field in fields]
        if not all((name, phone, pin, confirmation, deposit_text)):
            status.configure(text="All fields are required")
            return
        if not phone.isdigit() or len(phone) < 7:
            status.configure(text="Enter a valid phone number")
            return
        if not pin.isdigit() or len(pin) != 4:
            status.configure(text="PIN must be exactly 4 digits")
            return
        if pin != confirmation:
            status.configure(text="PINs do not match")
            return
        try:
            deposit = float(deposit_text)
        except ValueError:
            status.configure(text="Initial deposit must be a number")
            return
        if deposit < 500:
            status.configure(text="Minimum initial deposit is 500")
            return
        try:
            acc_no = db.create_account(name, pin, phone, deposit)
        except mysql.connector.Error as error:
            status.configure(text=f"Database error: {error}")
            return
        status.configure(text=f"Account created. Your account number is {acc_no}. Keep it somewhere safe.", text_color=ACCENT)
        for field in fields:
            field.delete(0, "end")

    button(form, "Create account", create).pack(anchor="w", padx=28, pady=(18, 28))


def show_customer_dashboard():
    clear(shell)
    content, nav = make_customer_shell("Customer account")
    show_customer_menu(nav, "Overview")
    page_heading(content, "Your account", "A quick view of your current balance and available actions.")
    details = db.get_account_details(current_acc)
    if details is None:
        show_message(content, "Account could not be found.", True)
        return
    acc_no, name, balance, created = details
    summary = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    summary.pack(anchor="w", fill="x", pady=5)
    ctk.CTkLabel(summary, text=f"Hello, {name}", font=FONT_HEADING, text_color=TEXT).pack(anchor="w", padx=28, pady=(24, 2))
    ctk.CTkLabel(summary, text=f"Account {acc_no}  |  Opened {created}", font=FONT_LABEL, text_color=SUBTEXT).pack(anchor="w", padx=28)
    ctk.CTkLabel(summary, text=f"Rs. {balance:,.2f}", font=("Segoe UI", 34, "bold"), text_color=ACCENT).pack(anchor="w", padx=28, pady=(20, 28))
    show_message(content, "Select an action from the left menu. Transactions stay inside this window.")


def show_money_form(action):
    clear(shell)
    content, nav = make_customer_shell("Customer account")
    show_customer_menu(nav, action)
    page_heading(content, action, f"Enter the amount you want to {action.lower()}.")
    form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    form.pack(anchor="w", fill="x")
    amount_entry = entry(form, "Amount")
    amount_entry.pack(anchor="w", padx=28, pady=(28, 8))
    status = ctk.CTkLabel(form, text="", font=FONT_LABEL, text_color=DANGER)
    status.pack(anchor="w", padx=28)

    def submit():
        try:
            amount = float(amount_entry.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            status.configure(text="Enter an amount greater than 0")
            return
        if action == "Deposit":
            db.deposit(current_acc, amount)
            result = f"Rs. {amount:,.2f} deposited successfully."
            success = True
        else:
            success, result = db.withdraw(current_acc, amount)
        status.configure(text=result, text_color=ACCENT if success else DANGER)
        if success:
            amount_entry.delete(0, "end")

    button(form, action, submit).pack(anchor="w", padx=28, pady=(18, 28))


def show_transfer_form():
    clear(shell)
    content, nav = make_customer_shell("Customer account")
    show_customer_menu(nav, "Transfer")
    page_heading(content, "Transfer funds", "Send money to another SecureBank account.")
    form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    form.pack(anchor="w", fill="x")
    recipient = entry(form, "Recipient account number")
    amount = entry(form, "Amount")
    recipient.pack(anchor="w", padx=28, pady=(28, 8))
    amount.pack(anchor="w", padx=28, pady=8)
    status = ctk.CTkLabel(form, text="", font=FONT_LABEL, text_color=DANGER, wraplength=520)
    status.pack(anchor="w", padx=28)

    def submit():
        try:
            value = float(amount.get().strip())
            if value <= 0:
                raise ValueError
        except ValueError:
            status.configure(text="Enter an amount greater than 0")
            return
        success, result = db.transfer(current_acc, recipient.get().strip(), value)
        status.configure(text=result, text_color=ACCENT if success else DANGER)
        if success:
            recipient.delete(0, "end")
            amount.delete(0, "end")

    button(form, "Transfer", submit).pack(anchor="w", padx=28, pady=(18, 28))


def show_history():
    clear(shell)
    content, nav = make_customer_shell("Customer account")
    show_customer_menu(nav, "Transaction history")
    page_heading(content, "Transaction history", f"Recent activity for account {current_acc}.")
    scroll = ctk.CTkScrollableFrame(content, fg_color=CARD, corner_radius=10)
    scroll.pack(fill="both", expand=True)
    rows = db.get_transaction_history(current_acc)
    if not rows:
        ctk.CTkLabel(scroll, text="No transactions yet", text_color=SUBTEXT, font=FONT_SUB).pack(pady=30)
    for txn_type, amount, related_acc, txn_time in rows:
        line = f"{txn_type}    Rs. {amount:,.2f}"
        if related_acc:
            line += f"    Account {related_acc}"
        card = ctk.CTkFrame(scroll, fg_color=BG, corner_radius=7)
        card.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(card, text=line, font=FONT_LABEL, text_color=TEXT).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(card, text=str(txn_time), font=("Segoe UI", 11), text_color=SUBTEXT).pack(anchor="w", padx=16, pady=(0, 10))


def logout_customer():
    global current_acc
    current_acc = None
    show_welcome()


def show_change_pin():
    clear(shell)
    content, nav = make_customer_shell("Customer account")
    show_customer_menu(nav, "Change PIN")
    page_heading(content, "Change PIN", "Choose a new four-digit PIN for your account.")
    form = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    form.pack(anchor="w", fill="x")
    new_pin = entry(form, "New 4-digit PIN", show="*")
    confirm_pin = entry(form, "Confirm new PIN", show="*")
    new_pin.pack(anchor="w", padx=28, pady=(28, 8))
    confirm_pin.pack(anchor="w", padx=28, pady=8)
    status = ctk.CTkLabel(form, text="", font=FONT_LABEL, text_color=DANGER)
    status.pack(anchor="w", padx=28)

    def submit():
        pin = new_pin.get().strip()
        confirmation = confirm_pin.get().strip()
        if not pin.isdigit() or len(pin) != 4:
            status.configure(text="PIN must be exactly 4 digits")
            return
        if pin != confirmation:
            status.configure(text="PINs do not match")
            return
        changed = db.change_pin(current_acc, pin)
        status.configure(text="PIN changed successfully" if changed else "PIN could not be changed",
                         text_color=ACCENT if changed else DANGER)
        if changed:
            new_pin.delete(0, "end")
            confirm_pin.delete(0, "end")

    button(form, "Change PIN", submit).pack(anchor="w", padx=28, pady=(18, 28))


def show_admin_dashboard():
    clear(shell)
    sidebar = ctk.CTkFrame(shell, width=245, fg_color=SIDEBAR, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    draw_bank_mark(sidebar, compact=True)
    ctk.CTkLabel(sidebar, text="Admin workspace", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(pady=(8, 22))
    nav_button(sidebar, "Accounts", show_admin_dashboard, True)
    nav_button(sidebar, "Home", show_welcome)
    content = ctk.CTkFrame(shell, fg_color=BG, corner_radius=0)
    content.pack(side="left", fill="both", expand=True, padx=46, pady=46)
    page_heading(content, "Admin workspace", "Manage accounts and inspect activity from the same main window.")
    summary = ctk.CTkFrame(content, fg_color=CARD, corner_radius=10)
    summary.pack(fill="x", pady=(0, 12))
    account_count, total_balance = db.get_account_summary()
    ctk.CTkLabel(summary, text=f"Accounts: {account_count}", font=FONT_SUB, text_color=TEXT).pack(side="left", padx=20, pady=15)
    ctk.CTkLabel(summary, text=f"Total balance: Rs. {total_balance:,.2f}", font=FONT_SUB, text_color=ACCENT).pack(side="left", padx=20, pady=15)
    tabs = ctk.CTkTabview(content, fg_color=CARD, segmented_button_selected_color=ACCENT,
                           segmented_button_selected_hover_color=ACCENT_HOVER)
    tabs.pack(fill="both", expand=True)
    tabs.add("Accounts")
    tabs.add("New account")
    tabs.add("All transactions")

    accounts_scroll = ctk.CTkScrollableFrame(tabs.tab("Accounts"), fg_color=CARD)
    accounts_scroll.pack(fill="both", expand=True, padx=8, pady=8)
    search_entry = entry(tabs.tab("Accounts"), "Search by name or account number", width=360)
    search_entry.pack(anchor="w", padx=16, pady=(10, 0))

    def refresh_accounts():
        clear(accounts_scroll)
        search_text = search_entry.get().strip().lower()
        rows = db.get_all_accounts()
        if search_text:
            rows = [row for row in rows if search_text in str(row[0]).lower() or search_text in row[1].lower()]
        ctk.CTkLabel(accounts_scroll, text=f"{len(rows)} account(s)", font=FONT_SUB, text_color=SUBTEXT).pack(anchor="w", padx=10, pady=8)
        for acc_no, name, balance, created in rows:
            row = ctk.CTkFrame(accounts_scroll, fg_color=BG, corner_radius=7)
            row.pack(fill="x", padx=2, pady=4)
            ctk.CTkLabel(row, text=f"{name}\nAccount {acc_no}  |  Rs. {balance:,.2f}\nOpened {created}", justify="left", font=FONT_LABEL, text_color=TEXT).pack(side="left", padx=14, pady=10)
            button(row, "Delete", lambda number=acc_no: delete_admin_account(number), danger=True, width=90).pack(side="right", padx=12)

    button(tabs.tab("Accounts"), "Search / refresh", refresh_accounts, width=180).pack(anchor="w", padx=16, pady=(4, 8))

    def delete_admin_account(acc_no):
        deleted = db.delete_account(acc_no)
        refresh_accounts()
        if not deleted:
            show_message(accounts_scroll, f"Account {acc_no} was not found.", True)

    create_admin_form(tabs.tab("New account"), refresh_accounts)
    txn_scroll = ctk.CTkScrollableFrame(tabs.tab("All transactions"), fg_color=CARD)
    txn_scroll.pack(fill="both", expand=True, padx=8, pady=8)
    rows = db.get_all_transactions()
    if not rows:
        ctk.CTkLabel(txn_scroll, text="No transactions yet", text_color=SUBTEXT).pack(pady=30)
    for acc_no, txn_type, amount, related_acc, txn_time in rows:
        line = f"Account {acc_no}  |  {txn_type}  |  Rs. {amount:,.2f}"
        if related_acc:
            line += f"  |  Related account {related_acc}"
        ctk.CTkLabel(txn_scroll, text=f"{line}\n{txn_time}", justify="left", anchor="w", font=FONT_LABEL, text_color=TEXT, fg_color=BG, corner_radius=7).pack(fill="x", padx=2, pady=4, ipady=9)
    refresh_accounts()


def create_admin_form(parent, refresh_accounts):
    wrapper = ctk.CTkFrame(parent, fg_color=CARD)
    wrapper.pack(anchor="w", padx=30, pady=30)
    name = entry(wrapper, "Full name")
    phone = entry(wrapper, "Phone number")
    pin = entry(wrapper, "4-digit PIN")
    deposit = entry(wrapper, "Initial deposit")
    for field in (name, phone, pin, deposit):
        field.pack(anchor="w", pady=6)
    status = ctk.CTkLabel(wrapper, text="", font=FONT_LABEL, text_color=DANGER)
    status.pack(anchor="w", pady=4)

    def create():
        try:
            initial_deposit = float(deposit.get().strip())
        except ValueError:
            status.configure(text="Deposit must be a number")
            return
        pin_value = pin.get().strip()
        phone_value = phone.get().strip()
        if not name.get().strip() or not phone_value.isdigit() or len(phone_value) < 7:
            status.configure(text="Enter a name and a valid phone number")
            return
        if not pin_value.isdigit() or len(pin_value) != 4:
            status.configure(text="PIN must be exactly 4 digits")
            return
        if initial_deposit < 0:
            status.configure(text="Deposit cannot be negative")
            return
        acc_no = db.create_account(name.get().strip(), pin_value, phone_value, initial_deposit)
        status.configure(text=f"Created account {acc_no}", text_color=ACCENT)
        refresh_accounts()
        for field in (name, phone, pin, deposit):
            field.delete(0, "end")

    button(wrapper, "Create account", create).pack(anchor="w", pady=12)


show_welcome()
root.mainloop()
