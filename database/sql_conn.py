
class SQLConnectionSettings:
    # Class variables to store SQL connection settings
    HOST = None
    DATABASE = None
    USER = None
    PASSWORD = None
    
    @classmethod
    def set_config(cls, HOST,  DATABASE, USER, PASSWORD):
        cls.HOST = HOST
        cls.DATABASE = DATABASE
        cls.USER = USER
        cls.PASSWORD = PASSWORD

    @classmethod
    def get_config(cls) -> tuple:
        return (cls.HOST,  cls.DATABASE, cls.USER, cls.PASSWORD)

# # Usage
# SQLConnectionSettings.set_config("localhost", 5432, "mydatabase", "myuser", "mypassword")
# print(SQLConnectionSettings.get_config())
