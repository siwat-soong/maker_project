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
    def add_user(self, user): self.__user_list.append(user)
    def add_instructor(self, instructor): self.__instructor_list.append(instructor)
    def add_admin(self, admin): self.__admin_list.append(admin)

    def add_space(self, space): self.__space_list.append(space)
    def add_equipment(self, equipment): self.__equipment_list.append(equipment)
    def add_material(self, material): self.__material_list.append(material)

    def add_payment_method(self, payment_method): self.__payment_method_list.append(payment_method)
    
    def add_event(self, event): self.__event_list.append(event)

    # Search Method

def system_init():
    try:
        print("✅ Init Success")
    except: print("❌ Init Failed")


system_init()