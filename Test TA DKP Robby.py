import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import queue
import datetime
import tkinter.font as tkfont

class PlayStationRental:
    def __init__(self):
        self.ps_inventory = {
            'PS3': 2,
            'PS4': 3,
            'PS5': 2,
            'PS VR': 2
        }
        
        self.rental_queue = queue.Queue()
        self.rental_stack = []
        
        self.root = tk.Tk()
        self.root.title("PlayStation Rental Management System")
        self.root.geometry("700x800")
        self.root.configure(bg='#2c3e50')
        
        self.create_gui()
    
    def create_gui(self):
        # Custom fonts
        title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        button_font = tkfont.Font(family="Helvetica", size=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="PlayStation Rental System", 
                               font=title_font, fg='white', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # Inventory Status
        self.inventory_label = tk.Label(main_frame, 
                                        text=self.get_inventory_status(), 
                                        font=("Helvetica", 12), 
                                        fg='white', 
                                        bg='#2c3e50', 
                                        justify=tk.LEFT)
        self.inventory_label.pack(pady=10)
        
        # Rental Buttons Frame
        rental_frame = tk.Frame(main_frame, bg='#2c3e50')
        rental_frame.pack(pady=10)
        
        for console in self.ps_inventory.keys():
            btn = tk.Button(rental_frame, 
                            text=f"Rent {console}", 
                            command=lambda c=console: self.rent_console(c),
                            font=button_font,
                            bg='#3498db', 
                            fg='white', 
                            activebackground='#2980b9',
                            relief=tk.FLAT,
                            padx=10,
                            pady=5)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Return Buttons Frame
        return_frame = tk.Frame(main_frame, bg='#2c3e50')
        return_frame.pack(pady=10)
        
        for console in self.ps_inventory.keys():
            btn = tk.Button(return_frame, 
                            text=f"Return {console}", 
                            command=lambda c=console: self.return_console(c),
                            font=button_font,
                            bg='#2ecc71', 
                            fg='white', 
                            activebackground='#27ae60',
                            relief=tk.FLAT,
                            padx=10,
                            pady=5)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Action Buttons
        action_frame = tk.Frame(main_frame, bg='#2c3e50')
        action_frame.pack(pady=10)
        
        buttons = [
            ("View Waiting List", self.view_waiting_list),
            ("Return Specific Rental", self.return_specific_rental),
            ("View Rental History", self.view_rental_history)
        ]
        
        for text, command in buttons:
            btn = tk.Button(action_frame, 
                            text=text, 
                            command=command,
                            font=button_font,
                            bg='#9b59b6', 
                            fg='white', 
                            activebackground='#8e44ad',
                            relief=tk.FLAT,
                            padx=10,
                            pady=5)
            btn.pack(side=tk.LEFT, padx=5)
    
    def return_specific_rental(self):
        # Filter out already returned rentals
        active_rentals = [record for record in self.rental_stack if not record.get('returned', False)]
        
        if not active_rentals:
            messagebox.showinfo("Return Rental", "No active rentals to return")
            return
        
        # Create a top-level window for rental selection
        return_window = tk.Toplevel(self.root)
        return_window.title("Return Specific Rental")
        return_window.geometry("600x500")
        return_window.configure(bg='#34495e')
        
        # Title for the return window
        title_label = tk.Label(return_window, 
                               text="Select Rental to Return", 
                               font=("Helvetica", 16, "bold"), 
                               fg='white', 
                               bg='#34495e')
        title_label.pack(pady=10)
        
        # Create Treeview for rental selection
        columns = ("Console", "Customer", "Rental Date")
        tree = ttk.Treeview(return_window, columns=columns, show='headings', 
                            style='Custom.Treeview')
        
        # Configure Treeview Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.Treeview', 
                        background='#2c3e50', 
                        foreground='white', 
                        fieldbackground='#2c3e50')
        style.configure('Custom.Treeview.Heading', 
                        background='#34495e', 
                        foreground='white', 
                        font=('Helvetica', 10, 'bold'))
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col, anchor='center')
            tree.column(col, width=180, anchor='center')
        
        # Populate the treeview with active rentals
        for record in active_rentals:
            tree.insert('', 'end', values=(
                record['console'], 
                record['customer'], 
                record['date'].strftime('%Y-%m-%d %H:%M')
            ))
        
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        def process_return():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a rental to return")
                return
            
            values = tree.item(selected_item[0])['values']
            console, customer, _ = values
            
            for record in self.rental_stack:
                if (record['console'] == console and 
                    record['customer'] == customer and 
                    not record.get('returned', False)):
                    
                    record['returned'] = True
                    self.ps_inventory[console] += 1
                    
                    if not self.rental_queue.empty():
                        next_rental = self.rental_queue.get()
                        messagebox.showinfo("Waiting List", 
                                            f"Next in line for {next_rental[0]}: {next_rental[1]}")
                    
                    self.inventory_label.config(text=self.get_inventory_status())
                    tree.delete(selected_item)
                    
                    messagebox.showinfo("Return Successful", 
                                        f"{console} returned by {customer}")
                    break
            
            if len(tree.get_children()) == 0:
                return_window.destroy()
        
        # Return Button with improved styling
        return_btn = tk.Button(return_window, 
                               text="Return Selected Rental", 
                               command=process_return,
                               bg='#3498db', 
                               fg='white', 
                               font=("Helvetica", 10),
                               activebackground='#2980b9',
                               relief=tk.FLAT,
                               padx=10,
                               pady=5)
        return_btn.pack(pady=10)
    
    # Rest of the methods remain the same as in previous implementation
    
    def get_inventory_status(self):
        status = "Current Inventory:\n"
        for console, count in self.ps_inventory.items():
            status += f"{console}: {count} available\n"
        return status
    
    def rent_console(self, console):
        if self.ps_inventory[console] > 0:
            self.ps_inventory[console] -= 1
            
            customer = simpledialog.askstring("Rent Console", f"Enter name for {console} rental:")
            
            if customer:
                rental_record = {
                    'console': console,
                    'customer': customer,
                    'date': datetime.datetime.now(),
                    'returned': False
                }
                self.rental_stack.append(rental_record)
                
                messagebox.showinfo("Rental Successful", 
                                    f"{console} rented to {customer}")
            else:
                self.ps_inventory[console] += 1
        else:
            customer = simpledialog.askstring("Waiting List", 
                                              f"No {console} available. Enter your name:")
            if customer:
                self.rental_queue.put((console, customer))
                messagebox.showinfo("Waiting List", 
                                    f"{customer} added to {console} waiting list")
        
        self.inventory_label.config(text=self.get_inventory_status())
    
    def return_console(self, console):
        self.ps_inventory[console] += 1
        
        if not self.rental_queue.empty():
            next_rental = self.rental_queue.get()
            messagebox.showinfo("Waiting List", 
                                f"Next in line for {next_rental[0]}: {next_rental[1]}")
        
        self.inventory_label.config(text=self.get_inventory_status())
    
    def view_waiting_list(self):
        if self.rental_queue.empty():
            messagebox.showinfo("Waiting List", "No customers waiting")
        else:
            waiting_list = list(self.rental_queue.queue)
            message = "Waiting List:\n"
            for item in waiting_list:
                message += f"{item[1]} - {item[0]}\n"
            messagebox.showinfo("Waiting List", message)
    
    def view_rental_history(self):
        if not self.rental_stack:
            messagebox.showinfo("Rental History", "No rental history")
        else:
            history = "Rental History:\n"
            for record in reversed(self.rental_stack):
                status = "Returned" if record.get('returned', False) else "Active"
                history += (f"{record['console']} - {record['customer']} "
                            f"on {record['date'].strftime('%Y-%m-%d %H:%M')} - {status}\n")
            messagebox.showinfo("Rental History", history)
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PlayStationRental()
    app.run()
