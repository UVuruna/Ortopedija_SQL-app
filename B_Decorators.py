from datetime import datetime
import functools
import traceback

def error_cathcer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {"Error":str(e),"Full Error":traceback.format_exc()}
    return wrapper

def password():
    return f"MUVS {(datetime.now() - datetime(1990, 6, 20, 11, 45, 0)).total_seconds()//13*13:,.0f} $"

class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance
    
if __name__=='__main__':
    print(password())