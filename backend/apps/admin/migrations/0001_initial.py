# Generated migration for AdminAuditLog model

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_admin_fields'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        # Create AdminAuditLog model
        migrations.CreateModel(
            name='AdminAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('action', models.CharField(choices=[('create', 'Created'), ('update', 'Updated'), ('delete', 'Deleted'), ('status_change', 'Status Changed'), ('marked_paid', 'Marked as Paid'), ('message_reply', 'Message Replied'), ('message_resolved', 'Message Resolved')], db_index=True, max_length=50)),
                ('changes', models.JSONField(blank=True, default=dict, help_text='JSON of {field: {old: value, new: value}}')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('admin_user', models.ForeignKey(blank=True, help_text='Admin user who performed the action', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_audit_logs', to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Admin Audit Log',
                'verbose_name_plural': 'Admin Audit Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['admin_user', '-timestamp'], name='audit_user_time_idx'),
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['content_type', '-timestamp'], name='audit_type_time_idx'),
        ),
    ]
