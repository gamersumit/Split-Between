# Generated by Django 5.0.6 on 2024-06-25 10:25

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=50)),
                ('group_icon', models.URLField(blank=True, null=True)),
                ('group_description', models.CharField(blank=True, max_length=200, null=True)),
                ('total_spending', models.FloatField(default=0)),
                ('is_simplified', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='group_admin', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='group_creator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('activity_type', models.CharField(choices=[('group_created', 'Group Created'), ('group_simplified', 'Group Simplified'), ('changed_group_name', 'Changed Group Name'), ('changed_group_description', 'Changed Group Description'), ('changed_group_icon', 'CHanged Group Icon'), ('group_deleted', 'Group Deleted'), ('member_invited', 'Member Invited to Join Group'), ('invitation_dropped', 'Reject/Cancel Invitation to Join Group'), ('member_joined', 'Member Joined Group'), ('member_left', 'Member Left Group'), ('member_removed', 'Member Left Group'), ('expense_added', 'Expense Added to Group'), ('settledup', 'Settled Up with User'), ('expense_edited', 'Expense Edited in Group'), ('expense_deleted', 'Expense Deleted from Group')], max_length=40)),
                ('triggered_at', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.JSONField(blank=True, default=dict, null=True)),
                ('triggered_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activities_triggered', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(related_name='activites', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activites', to='group.group')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='added_membership', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='group.group')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='Membership', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('group', 'user')},
            },
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='groups_membership', through='group.Membership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='PendingMembers',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_invited', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.group')),
                ('invited_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='invited_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitaions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('group', 'user')},
            },
        ),
        migrations.AddField(
            model_name='group',
            name='pending_members',
            field=models.ManyToManyField(blank=True, related_name='groups_pending', through='group.PendingMembers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='GroupBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField(default=0)),
                ('friend_owes', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='balence_owes', to=settings.AUTH_USER_MODEL)),
                ('friend_owns', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='balence_owns', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='balances', to='group.group')),
            ],
            options={
                'unique_together': {('group', 'friend_owes', 'friend_owns')},
            },
        ),
    ]
