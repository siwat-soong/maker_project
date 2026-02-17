from user import *
from enum_class import *

class Club:
    def __init__(self, name):
        self.__name = name
        self.__user_list = []
        self.__instructor_list = []
        self.__admin_list = []
        self.__space_list = []
        self.__equipment_list = []
        self.__material_list = []
        self.__payment_method_list = []
        self.__event_list = []
    
    # Add Method
    def add_user(self, user):
        if isinstance(user, User):
            self.__user_list.append(user)

    def add_instructor(self, instructor):
        if isinstance(instructor, Instructor):
            self.__instructor_list.append(instructor)

    def add_admin(self, admin):
        if isinstance(admin, Admin):
            self.__admin_list.append(admin)

    # Search Method
    def search_user_by_id(self, user_id):
        for user in self.__user_list:
            if user.get_id == user_id:
                return user
        return None
    
    def search_member_by_id(self, user_id):
        for user in self.__user_list:
            if isinstance(user, Member) and user.get_id == user_id:
                return user
        return None


# Init Function
def system_init():
    try:
        maker = Club("maker")
        thana = Instructor("123", "Thana", "0123456789", Expertise.ADVANCE, 500)

        maker.add_instructor(thana)
        print(thana)

    except Exception as e:
        print(f"❌ {e}")

# test run - delete when use with API
system_init()