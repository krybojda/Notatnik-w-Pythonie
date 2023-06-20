from tkinter import Tk, Text, Button, filedialog, Menu, font, StringVar, IntVar, Scrollbar, Toplevel, Label, Entry, Listbox
import mysql.connector

srv = "localhost"
usr="root"
haslo=""
baza="notatnik"

def zapisz_notatke():
    if not tytul_aktualny:
        zapisz_jako()
    else:
        tresc = tekst.get("1.0", "end-1c")
        with open(tytul_aktualny, "w") as plik:
            plik.write(tresc)
        print("Notatka została zapisana.")
        zapisz_do_bazy_danych(tytul_aktualny, tresc)

def zapisz_do_bazy_danych(tytul, tresc):
    try:
        conn = mysql.connector.connect(
            host= srv,
            user= usr,
            password= haslo,
            database= baza
        )
        cursor = conn.cursor()
        query = "INSERT INTO notatki (tytul, tresc) VALUES (%s, %s)"
        values = (tytul, tresc)
        cursor.execute(query, values)
        conn.commit()
        print("Notatka została zapisana w bazie danych.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as error:
        print("Błąd podczas zapisywania notatki do bazy danych:", error)

def zapisz_jako():
    tytul = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Pliki tekstowe", "*.txt")])
    if tytul:
        global tytul_aktualny
        tytul_aktualny = tytul
        tresc = tekst.get("1.0", "end-1c")
        with open(tytul, "w") as plik:
            plik.write(tresc)
        print("Notatka została zapisana.")

def odczytaj_notatke():
    tytul = filedialog.askopenfilename(filetypes=[("Pliki tekstowe", "*.txt")])
    if tytul:
        with open(tytul, "r") as plik:
            tresc = plik.read()
            tekst.delete("1.0", "end")
            tekst.insert("1.0", tresc)
        global tytul_aktualny
        tytul_aktualny = tytul


def odczytaj_z_bazy_danych(tytul):
    try:
        conn = mysql.connector.connect(
            host=srv,
            user=usr,
            password=haslo,
            database=baza
        )
        cursor = conn.cursor()
        query = "SELECT tresc FROM notatki WHERE tytul = %s"
        values = (tytul,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        if result is not None:
            tresc = result[0]
            tekst.delete("1.0", "end")
            tekst.insert("1.0", tresc)
        cursor.close()
        conn.close()
        global tytul_aktualny
        tytul_aktualny = tytul
    except mysql.connector.Error as error:
        print("Błąd podczas odczytywania notatki z bazy danych:", error)

        

def nowy():
    global tytul_aktualny
    tekst.delete("1.0", "end")
    tytul_aktualny = None

def zmien_czcionke():
    wybrana_czcionka = font.Font(family=wybrana_czcionka_var.get(), size=wybrana_wielkosc_var.get(), weight=wybrany_styl_var.get())
    tekst.configure(font=wybrana_czcionka)

def zapisz_do_bazy():
    top = Toplevel()
    top.title("Zapisz do bazy danych")
    top.iconbitmap("icon.ico")  # Dodanie ikony do okna

    Label(top, text="Tytuł:").grid(row=0, column=0)
    tytul_entry = Entry(top)
    tytul_entry.grid(row=0, column=1)

    def save_to_database():
        zapisz_do_bazy_danych(tytul_entry.get(), tekst.get("1.0", "end-1c"))
        top.destroy()  # Zamknięcie okna po zapisie do bazy danych

    Button(top, text="Zapisz", command=save_to_database).grid(row=1, column=0, columnspan=2)

def odczytaj_z_bazy():
    top = Toplevel()
    top.title("Odczytaj z bazy danych")
    top.iconbitmap("icon.ico")  # Dodanie ikony do okna
    top.geometry("400x400")  # Ustawienie rozmiaru okna
    top.minsize(400, 400)  # Ograniczenie minimalnego rozmiaru okna

    try:
        conn = mysql.connector.connect(
            host=srv,
            user=usr,
            password=haslo,
            database=baza
        )
        cursor = conn.cursor()
        query = "SELECT tytul FROM notatki"
        cursor.execute(query)
        result = cursor.fetchall()

        Label(top, text="Wybierz notatkę:").pack()
        listbox = Listbox(top)
        listbox.pack(fill="both", expand=True)
        scrollbar = Scrollbar(top)
        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        for row in result:
            listbox.insert("end", row[0])

        def open_selected_note():
            selected_note = listbox.get(listbox.curselection())
            odczytaj_z_bazy_danych(selected_note)
            top.destroy()  # Zamknięcie okna po wybraniu notatki

        button_open = Button(top, text="Otwórz", command=open_selected_note)
        button_open.pack()  # Przycisk otwierający notatkę

        cursor.close()
        conn.close()

    except mysql.connector.Error as error:
        print("Błąd podczas odczytywania notatek z bazy danych:", error)

def wyswietl_informacje():
    top = Toplevel()
    top.title("Informacje")
    top.iconbitmap("icon.ico")  # Dodanie ikony do okna
    top.geometry("350x250")  # Ustawienie rozmiaru okna

    Label(top, text="Prosty notatnik który otwiera i zapisuje ").pack()
    Label(top, text="notatki z lokalizacji lokalnej oraz z bazy danych.").pack()
    Label(top, text="Notatnik wykonany w celach edukacyjnych.").pack()
    Label(top, text="Limit znaków: 5000").pack()
    Label(top, text="Dane logowania do bazy danych").pack()
    Label(top, text="Host: "+srv).pack()
    Label(top, text="User: "+usr).pack()
    Label(top, text="Hasło: " + (haslo if haslo else "Puste Pole")).pack()
    Label(top, text="Nazwa bazy: "+baza).pack()

def wyszukaj_w_tekscie():
    def search():
        query = search_entry.get()
        start_index = "1.0"
        while True:
            start_index = tekst.search(query, start_index, stopindex="end", nocase=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(query)}c"
            tekst.tag_add("search", start_index, end_index)
            start_index = end_index
        tekst.tag_config("search", background="yellow")

    top = Toplevel()
    top.title("Wyszukaj w tekście")
    top.geometry("200x100")  # Ustawienie rozmiaru okna
    top.iconbitmap("icon.ico")  # Dodanie ikony do okna

    Label(top, text="Wyszukaj tekst:").pack()
    search_entry = Entry(top)
    search_entry.pack()

    Button(top, text="Szukaj", command=search).pack()


# Tworzenie okna głównego
okno = Tk()
okno.title("Prosty Notatnik")
okno.iconbitmap("icon.ico")  # Dodanie ikony do okna

# Zmienna przechowująca aktualny tytuł notatki
tytul_aktualny = None

# Tworzenie paska menu
pasek_menu = Menu(okno)
okno.config(menu=pasek_menu)

# Tworzenie menu "Plik"
menu_plik = Menu(pasek_menu, tearoff=0)
pasek_menu.add_cascade(label="Plik", menu=menu_plik)
menu_plik.add_command(label="Nowy", command=nowy)
menu_plik.add_separator()
menu_plik.add_command(label="Odczytaj", command=odczytaj_notatke)
menu_plik.add_command(label="Odczytaj z bazy", command=odczytaj_z_bazy)
menu_plik.add_command(label="Zapisz", command=zapisz_notatke)
menu_plik.add_command(label="Zapisz jako", command=zapisz_jako)
menu_plik.add_command(label="Zapisz do bazy", command=zapisz_do_bazy)
menu_plik.add_command(label="Wyszukaj", command=wyszukaj_w_tekscie)
menu_plik.add_separator()
menu_plik.add_command(label="Zamknij", command=okno.quit)

# Tworzenie menu "Edycja"
menu_edycja = Menu(pasek_menu, tearoff=0)



# Tworzenie pola tekstowego
tekst = Text(okno)
tekst.pack(side="left", fill="both", expand=True)

# Tworzenie paska przewijania
pasek_przewijania = Scrollbar(okno)
pasek_przewijania.pack(side="right", fill="y")

# Podłączanie paska przewijania do pola tekstowego
tekst.config(yscrollcommand=pasek_przewijania.set)
pasek_przewijania.config(command=tekst.yview)

def utworz_menu_czcionki():
    global wybrana_czcionka_var, wybrana_wielkosc_var, wybrany_styl_var

    menu_czcionki = Menu(pasek_menu, tearoff=0)
    pasek_menu.add_cascade(label="Zmień czcionkę", menu=menu_czcionki)


    # Tworzenie menu "pomoc"
    menu_pomoc = Menu(pasek_menu, tearoff=0)
    pasek_menu.add_cascade(label="Pomoc", menu=menu_pomoc)
    menu_pomoc.add_command(label="Informacje", command=wyswietl_informacje)

    wybrana_czcionka_var = StringVar()
    wybrana_wielkosc_var = IntVar()
    wybrany_styl_var = StringVar()


    wybrana_czcionka_var.set("Arial")
    wybrana_wielkosc_var.set(12)
    wybrany_styl_var.set("normal")  


    menu_czcionki.add_radiobutton(label="Arial", variable=wybrana_czcionka_var, value="Arial")
    menu_czcionki.add_radiobutton(label="Times New Roman", variable=wybrana_czcionka_var, value="Times New Roman")
    menu_czcionki.add_radiobutton(label="Courier New", variable=wybrana_czcionka_var, value="Courier New")
    menu_czcionki.add_separator()
    menu_czcionki.add_radiobutton(label="Normalna", variable=wybrany_styl_var, value="normal")
    menu_czcionki.add_radiobutton(label="Pogrubiona", variable=wybrany_styl_var, value="bold")
    menu_czcionki.add_separator()
    menu_czcionki.add_radiobutton(label="10", variable=wybrana_wielkosc_var, value=10)
    menu_czcionki.add_radiobutton(label="12", variable=wybrana_wielkosc_var, value=12)
    menu_czcionki.add_radiobutton(label="14", variable=wybrana_wielkosc_var, value=14)
    menu_czcionki.add_radiobutton(label="16", variable=wybrana_wielkosc_var, value=16)
    menu_czcionki.add_radiobutton(label="18", variable=wybrana_wielkosc_var, value=18)
    menu_czcionki.add_radiobutton(label="20", variable=wybrana_wielkosc_var, value=20)

    # Funkcja do aktualizacji czcionki na bieżąco
    def aktualizuj_czcionke(*args):
        wybrana_czcionka = font.Font(family=wybrana_czcionka_var.get(), size=wybrana_wielkosc_var.get(), weight=wybrany_styl_var.get())
        tekst.configure(font=wybrana_czcionka)


    # Przypisanie funkcji aktualizuj_czcionke do zdarzenia zmiany wartości
    wybrana_czcionka_var.trace("w", aktualizuj_czcionke)
    wybrana_wielkosc_var.trace("w", aktualizuj_czcionke)
    wybrany_styl_var.trace("w", aktualizuj_czcionke)



utworz_menu_czcionki()

# Uruchomienie głównej pętli programu
okno.mainloop()
