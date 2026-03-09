from user_class import User

class Club:
    def __init__(self, name):
        self.__name = name
        
        # User Storage
        self.__user_list = []
        self.__instructor_list = []
        self.__admin_list = []

        # Resource Storage
        self.__space_list = []
        self.__equipment_list = []
        self.__material_list = []

        # Payment Method Storage
        self.__payment_method_list = []

        # Event Storage
        self.__event_list = []
    
    # Add Method
    def add_user(self, user: User): self.__user_list.append(user)
    def add_instructor(self, instructor): self.__instructor_list.append(instructor)
    def add_admin(self, admin): self.__admin_list.append(admin)

    def add_space(self, space): self.__space_list.append(space)
    def add_equipment(self, equipment): self.__equipment_list.append(equipment)
    def add_material(self, material): self.__material_list.append(material)

    def add_payment_method(self, payment_method): self.__payment_method_list.append(payment_method)
    
    def add_event(self, event): self.__event_list.append(event)

    # Search Method
    def search_user_by_id(self, user_id):
        for user in self.__user_list:
            if user.get_id == user_id: return user

def system_init():
    try:
        maker = Club("Maker Club")
        butter = User("4517", "Butter", "0144796685")

        maker.add_user(butter)

        print("✅ Init Success")
        return maker
    except: print("⛔ Init Failed")


system_init()