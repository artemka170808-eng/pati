import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("900x600")
        self.data_file = "books.json"
        self.books = []  # список книг, каждая книга - dict

        # === Переменные для полей ввода ===
        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.pages_var = tk.StringVar()

        # === Переменные для фильтрации ===
        self.filter_genre_var = tk.StringVar()
        self.filter_pages_var = tk.StringVar(value="200")  # по умолчанию >200

        self.create_widgets()
        self.load_data()  # загрузка данных при старте

    def create_widgets(self):
        # --- Фрейм ввода данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить новую книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.title_var, width=40).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.author_var, width=40).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.genre_var, width=40).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Количество страниц:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.pages_var, width=40).grid(row=3, column=1, padx=5, pady=2)

        btn_add = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        btn_add.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Фрейм фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, sticky="w", padx=5)
        self.genre_combobox = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, state="readonly")
        self.genre_combobox.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Entry(filter_frame, textvariable=self.filter_pages_var, width=10).grid(row=0, column=3, padx=5)

        btn_filter = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=5)

        btn_reset = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        btn_reset.grid(row=0, column=5, padx=5)

        # --- Таблица (Treeview) ---
        tree_frame = ttk.LabelFrame(self.root, text="Список книг", padding=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")

        self.tree.column("title", width=250)
        self.tree.column("author", width=200)
        self.tree.column("genre", width=150)
        self.tree.column("pages", width=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления выделенной книги
        btn_delete = ttk.Button(self.root, text="Удалить выбранную книгу", command=self.delete_selected)
        btn_delete.pack(pady=5)

        # --- Кнопки сохранения/загрузки ---
        io_frame = ttk.Frame(self.root)
        io_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(io_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(io_frame, text="Загрузить из JSON", command=self.load_data).pack(side="left", padx=5)

        self.update_genre_combobox()  # начальное заполнение жанров (пока пусто)
        self.refresh_treeview()       # отображение всех книг

    def add_book(self):
        """Добавление новой книги с валидацией."""
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        genre = self.genre_var.get().strip()
        pages_str = self.pages_var.get().strip()

        # Проверка на пустые поля
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка, что страницы - целое положительное число
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным целым числом!")
            return

        # Добавление книги в список
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)

        # Очистка полей ввода
        self.title_var.set("")
        self.author_var.set("")
        self.genre_var.set("")
        self.pages_var.set("")

        self.update_genre_combobox()
        self.refresh_treeview()

    def delete_selected(self):
        """Удаление выделенной в таблице книги."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Информация", "Выберите книгу для удаления.")
            return

        # Получаем индекс в списке (соответствует iid в Treeview)
        item = selected_item[0]
        index = int(self.tree.item(item, "tags")[0])  # мы сохраняли индекс в тегах

        if messagebox.askyesno("Подтверждение", "Удалить выбранную книгу?"):
            del self.books[index]
            self.update_genre_combobox()
            self.refresh_treeview()

    def refresh_treeview(self, filtered_books=None):
        """Обновление таблицы: отображение всех книг или отфильтрованного списка."""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        books_to_show = filtered_books if filtered_books is not None else self.books

        for idx, book in enumerate(books_to_show):
            # В тегах храним оригинальный индекс книги в self.books (если показываем все)
            # При фильтрации нужно знать реальный индекс, поэтому сохраним его в тегах
            # Для этого найдем индекс в self.books
            real_index = self.books.index(book) if book in self.books else -1
            self.tree.insert("", "end", values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ), tags=(real_index,))

    def update_genre_combobox(self):
        """Обновление выпадающего списка жанров на основе уникальных жанров из книг."""
        genres = sorted({book["genre"] for book in self.books})
        self.genre_combobox["values"] = genres
        if genres:
            self.genre_combobox.current(0)
        else:
            self.filter_genre_var.set("")

    def apply_filter(self):
        """Применение фильтра по жанру и количеству страниц."""
        genre_filter = self.filter_genre_var.get().strip()
        pages_threshold_str = self.filter_pages_var.get().strip()

        # Проверка числа страниц для фильтра
        try:
            pages_threshold = int(pages_threshold_str) if pages_threshold_str else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число для фильтра по страницам.")
            return

        filtered = []
        for book in self.books:
            # Фильтр по жанру (если выбран)
            if genre_filter and book["genre"] != genre_filter:
                continue
            # Фильтр по страницам (> порога)
            if pages_threshold > 0 and book["pages"] <= pages_threshold:
                continue
            filtered.append(book)

        self.refresh_treeview(filtered)

    def reset_filter(self):
        """Сброс фильтра и отображение всех книг."""
        self.filter_genre_var.set("")
        self.filter_pages_var.set("200")  # вернём дефолтное значение
        self.refresh_treeview()

    def save_data(self):
        """Сохранение списка книг в JSON-файл."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        """Загрузка списка книг из JSON-файла."""
        if not os.path.exists(self.data_file):
            # Если файла нет, просто продолжаем с пустым списком
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.update_genre_combobox()
            self.refresh_treeview()
            messagebox.showinfo("Успех", f"Данные загружены из {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
