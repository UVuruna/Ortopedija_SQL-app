import A_Variables as var
from A_Variables import *

def spam_stopper(button:ctk.CTkButton,root:Tk):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            button.configure(state='disabled')
            root.after(BUTTON_LOCK, lambda: button.configure(state='normal'))
            return result
        return wrapper
    return decorator

def method_efficency(session:dict):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time_ns()
            result = func(*args, **kwargs)
            end = time.time_ns()
            efficency = (end-start)/10**6
            print(f"Execution time {func.__name__}: {efficency:,.2f} ms")
            if not session:
                print(efficency)
            else:
                if func.__name__ not in session:
                    session[func.__name__] = efficency
                else:
                    session[func.__name__] += efficency
            return result
        return wrapper
    return decorator

def error_catcher(log:dict):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return {"Error":str(e),"Full Error":traceback.format_exc()}
        return wrapper
    return decorator

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