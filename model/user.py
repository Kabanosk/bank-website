class User:
    def __init__(self, login, email, password):
        self.login = login
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            "login": self.login,
            "email": self.email,
            "password": self.password
        }

    @staticmethod
    def from_dict(user: dict):
        return User(user["login"], user['email'], user['password'])
