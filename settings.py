import os


class Settings:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings,cls).__new__(cls)
        if not os.path.isfile("settings.txt"):
            default_settings={
                "thread_width":5,
                "ignore_close_pins":3

            }
            with open("settings.txt", "w") as f:
                for k,v in default_settings.values():
                    f.write(k+' = '+v)
            cls.settings=default_settings
        else:
            with open("settings.txt","r") as f:
                #TODO
                cls.settings={}
        return cls._instance
    def get_setting():
        pass

if __name__=="__main__":
    settings=Settings()