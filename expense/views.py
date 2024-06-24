from django.shortcuts import render

# Create your views here.


# 1. Add Expense
# 2. EDIT expense
# 3. Delete Expense
# 4. List Expense of a group


class ExpenseListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       return self.request.user.activites.all()
    
    @swagger_auto_schema(tags = ['Activity'], 
    operation_summary= "LIST OF ALL THE ACTIVITY", 
    operation_description = 'PROVIDES A LIST OF ALL THE GROUP ACTIVITIES CONCERNING CURRENT USER WHERE THE CURRENT USER IS MEMBER OF THE GROUP.', 
    ) 
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)