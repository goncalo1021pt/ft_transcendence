from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin 

from .models import User, FriendshipRequest, Ladderboard
# admin.site.register(User, UserAdmin)

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        additional_fields = ('is_42_user', 'id_42', 'uuid', 'rank', 'status', 'profile_pic')
        self.fieldsets = BaseUserAdmin.fieldsets + (
            ('Properties', {'fields': additional_fields}),
        )
        self.list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_42_user', 'rank', 'status', 'uuid', 'profile_pic')
        self.list_filter = BaseUserAdmin.list_filter + ('is_42_user', 'status')
        self.search_fields = BaseUserAdmin.search_fields + ('id_42', 'uuid')
        


@admin.register(FriendshipRequest)
class FriendshipRequestAdmin(admin.ModelAdmin):
	list_display = ('sender', 'receiver', 'status', 'created_at', 'updated_at')
	list_filter = ('status',)
	search_fields = ('sender__username', 'receiver__username')
	date_hierarchy = 'created_at'
	
	actions = ['accept_requests', 'reject_requests']
	
	def accept_requests(self, request, queryset):
		updated = queryset.update(status='accepted')
		self.message_user(request, f"{updated} friendship requests were accepted.")
	accept_requests.short_description = "Accept selected friendship requests"
	
	def reject_requests(self, request, queryset):
		updated = queryset.update(status='rejected')
		self.message_user(request, f"{updated} friendship requests were rejected.")
	reject_requests.short_description = "Reject selected friendship requests"


@admin.register(Ladderboard)
class LadderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank_value', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username',)
    ordering = ('-rank_value',)