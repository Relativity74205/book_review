from passlib.hash import pbkdf2_sha256


class User:
    def __init__(self, name):
        self.name = name

    def set_password(self, password_hashed):
        self.password_sha = password_hashed

    def hash_password(self, password_clear):
        self.password_sha = pbkdf2_sha256.encrypt(password_clear, rounds=20000, salt_size=16)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_sha)

    def add_user(self, db):
        db.execute('INSERT INTO public.user (username, password_hashed) VALUES (:username, :password_sha)',
                   {"username": self.name, "password_sha": self.password_sha})
        db.commit()


class Review:
    def __init__(self, book_id, user_id, review_text, review_points):
        self.book_id = book_id
        self.user_id = user_id
        self.review_text = review_text
        self.review_points = review_points

    def add_review(self, db):
        db.execute('INSERT INTO public.review (review_points, review_text, book_id, user_id) '
                   'VALUES (:review_points, :review_text, :book_id, :user_id)',
                   {"review_points": self.review_points,
                    "review_text": self.review_text,
                    "book_id": self.book_id,
                    "user_id": self.user_id})
        db.commit()
