# from .models import Friendship, User
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver

# @receiver(post_save, sender=Friendship)
# def post_save_friendship(sender, instance, **kwargs):
#     """
#     Signal to be called before a Friendship instance is saved.
#     """
#     # Add custom logic here, for example, updating a log or sending a notification
#     print(f"Friendship is being created or updated: {instance.user1.username} and {instance.user2.username}")


# @receiver(post_delete, sender=Friendship)
# def post_delete_friendship(sender, instance, **kwargs):
#     """
#     Signal to be called before a Friendship instance is deleted.
#     """
#     # Add custom logic here, for example, updating a log or sending a notification
#     print(f"Friendship is being deleted: {instance.user1.username} and {instance.user2.username}")
