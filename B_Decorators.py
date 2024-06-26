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

def method_efficency(session:dict=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time_ns()
            result = func(*args, **kwargs)
            end = time.time_ns()
            efficency = (end-start)/10**6
            print(f"Execution time {func.__name__}: {efficency:,.2f} ms")
            if session:
                try:
                    key = session[func.__name__]
                    key['count'] += 1
                    key['time'] += efficency
                except KeyError:
                    print("Uslo")
                    session[func.__name__] = {'count':1 , 'time':efficency}
            return result
        return wrapper
    return decorator

def error_catcher(CLASS=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if CLASS:
                    # Ovo je da bi dobio 1 ms preciznost (0.000 s)
                    Time = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.{datetime.now().strftime("%f")[:3]}' 
                    fullerror = traceback.format_exc()
                    def execute():
                        CLASS.execute_Insert('logs',**{'ID Time':Time, 'Email':CLASS.GD.UserSession['User'],
                                                'Query':func.__name__, 'Full Query':CLASS.LoggingQuery,
                                                "Error":str(e), "Full Error": fullerror})
                    threading.Thread(target=execute).start()
                else:
                    print(str(e))
                    print(traceback.format_exc())
                return
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