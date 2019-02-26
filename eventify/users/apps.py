from django.apps import AppConfig


class UsersConfig(AppConfig): #Arver fra AppConfig
    name = 'users'

    def ready(self):        #Klargjør for å motta signal. Django åpner ingen filer automatisk som default.
        import users.signals