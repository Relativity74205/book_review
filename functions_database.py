def search_user(username, db):
    query_results = db.execute("SELECT * FROM public.user WHERE username = :username",
                               {"username": username}).fetchall()
    return query_results


def search_book(search_text, db):
    search_text = '%' + search_text + '%'
    search_result = db.execute("SELECT * FROM public.book WHERE isbn LIKE :search_text "
                               "OR title LIKE :search_text OR author LIKE :search_text",
                               {"search_text": search_text}).fetchall()

    return search_result


def get_book(book_id, db):
    book = db.execute('SELECT * FROM public.book WHERE book_id = :book_id',
                      {"book_id": book_id}).fetchone()

    return book


def get_reviews(book_id, db):
    reviews = db.execute('SELECT r.*, u.username '
                         'FROM public.review r '
                         'LEFT JOIN public.user u '
                         'ON u.id = r.user_id '
                         'WHERE book_id = :book_id',
                         {"book_id": book_id}).fetchall()

    return reviews


def check_user_already_reviewed(book_id, user_id, db):
    review = db.execute('SELECT * FROM public.review WHERE book_id = :book_id AND user_id = :user_id',
                        {"book_id": book_id,
                         "user_id": user_id}).fetchone()
    if review is None:
        return False
    else:
        return True


def get_book_by_isbn(isbn, db):
    book = db.execute('''SELECT title, author, year, isbn, 
                            COUNT(*) AS review_count, ROUND(AVG(review_points), 1) AS average_score 
                            FROM public.book b LEFT JOIN public.review r ON b.book_id = r.book_id
                            WHERE isbn = :isbn
                            GROUP BY title, author, year, isbn''', {"isbn": isbn}).fetchone()

    return book

