import tkinter as tk

# Create the main application window
root = tk.Tk()
root.title("DSP Lab - Tkinter GUI")
root.geometry("400x400")

# Create a label widget
tk.Label(root, text="").pack(pady=10)
tk.Label(root, text="").pack(pady=10)
label = tk.Label(root, text="This is a Label")
label.pack(pady=10)
tk.Label(root, text="").pack(pady=10)

# Create an entry widget
entry = tk.Entry(root)
entry.pack(pady=10)

# Create a button widget for the entry
def button_click():
    text = entry.get()
    label.config(text=f"Hello, {text}!")

button = tk.Button(root, text="Click Me", command=button_click)
button.pack(pady=10)
tk.Label(root, text="").pack(pady=10)

# Add two scale widgets and a button to show their sum
x = tk.DoubleVar()
y = tk.DoubleVar()

def calculate_sum():
    sum_value = x.get() + y.get()
    label.config(text=f"Sum = {sum_value}")

# First scale widget
scale1 = tk.Scale(root, from_=0, to=100, orient="horizontal", variable=x, label="Scale 1")
scale1.pack(pady=10)

# Second scale widget
scale2 = tk.Scale(root, from_=0, to=100, orient="horizontal", variable=y, label="Scale 2")
scale2.pack(pady=10)

# Button to calculate the sum
sum_button = tk.Button(root, text="Calculate Sum", command=calculate_sum)
sum_button.pack(pady=10)
tk.Label(root, text="").pack(pady=10)
tk.Label(root, text="").pack(pady=10)

# Create an additional widget: Checkbutton
check_var = tk.BooleanVar()

def checkbutton_action():
    status = "Checked" if check_var.get() else "Unchecked"
    label.config(text=f"Checkbutton is {status}")

checkbutton = tk.Checkbutton(root, text="Check Me", variable=check_var, command=checkbutton_action)
checkbutton.pack(pady=10)

# Run the application
root.mainloop()
