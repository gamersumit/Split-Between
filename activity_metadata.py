
# Activity Types and Metadata:

# 1. FRIENDSHIP CREATION ACTIVITY (friend_added):
# metadata = {'friends' : [
#           {id : uuid, user : str, avatar : url, etc}, 
#           {id : uuid, user : str, avatar : url, etc}
#           ]}


# 2. GROUP CREATION ACTIVITY (group_created):
# metadata = {
#                 'creator' : {id : uuid, user : str, avatar : url, etc},
#                 'group' : {id : uuid, group_name : str},
#             },

# 3. GROUP NAME EDIT ACTIVITY (group_info_edited):
# metadata = {
#                'updated_by' : {id : uuid, user : str, avatar : url, etc},
#                'group' : {id : uuid, group_name : str},
#                'field' : str : choice : 'group_name', 
#                'new_name' : str,
#             }

# 4. GROUP DESCRIPTION EDIT ACTIVITY (group_info_edited):
# metadata = {
#                'updated_by' : {id : uuid, user : str, avatar : url, etc},
#                'group' : {id : uuid, group_name : str},
#                'field' : str : choice : 'description', 
#                'new_description' : str,
# 
#             }
# 5. GROUP DELETION ACTIVITY (group_deleted):
# metadata = {
#                'deleted_by' : {id : uuid, user : str, avatar : url, etc},
#                'group_' : {id : uuid, group_name : str},
#             }
                