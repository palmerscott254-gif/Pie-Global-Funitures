from django.db import migrations, models
import django.db.models.deletion
import django.contrib.auth.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)),
                ('title', models.CharField(max_length=255, help_text='Brief notification title')),
                ('message', models.TextField(help_text='Full notification message body')),
                ('notification_type', models.CharField(
                    choices=[
                        ('ORDER_CONFIRMED', 'Order Confirmed'),
                        ('PAYMENT_RECEIVED', 'Payment Received'),
                        ('ORDER_SHIPPED', 'Order Shipped'),
                        ('DELIVERY_UPDATE', 'Delivery Update'),
                        ('DELIVERED', 'Delivered Successfully'),
                        ('DELIVERY_FAILED', 'Failed Delivery Attempt'),
                        ('RESTOCKED_ITEM', 'Item Restocked'),
                        ('ADMIN_MESSAGE', 'Admin Message'),
                        ('WARRANTY_UPDATE', 'Warranty/Support Update'),
                        ('REFUND_STATUS', 'Refund Status'),
                        ('INVOICE_READY', 'Invoice Ready'),
                        ('DELIVERY_ETA', 'Delivery ETA'),
                        ('LOYALTY_POINTS', 'Loyalty/Reward Points'),
                        ('REVIEW_REMINDER', 'Review Reminder'),
                    ],
                    db_index=True,
                    max_length=50
                )),
                ('priority', models.CharField(
                    choices=[
                        ('LOW', 'Low'),
                        ('NORMAL', 'Normal'),
                        ('HIGH', 'High'),
                        ('URGENT', 'Urgent'),
                    ],
                    db_index=True,
                    default='NORMAL',
                    max_length=20
                )),
                ('is_read', models.BooleanField(db_index=True, default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False)),
                ('action_url', models.CharField(blank=True, max_length=500, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='auth.user')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_notifications', models.BooleanField(default=True)),
                ('promotional_notifications', models.BooleanField(default=True)),
                ('admin_notifications', models.BooleanField(default=True)),
                ('support_notifications', models.BooleanField(default=True)),
                ('quiet_hours_enabled', models.BooleanField(default=False)),
                ('quiet_hours_start', models.TimeField(blank=True, null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preference', to='auth.user')),
            ],
            options={
                'verbose_name': 'Notification Preference',
                'verbose_name_plural': 'Notification Preferences',
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_status', models.CharField(
                    choices=[
                        ('CREATED', 'Created'),
                        ('QUEUED', 'Queued'),
                        ('SENT', 'Sent'),
                        ('DELIVERED', 'Delivered'),
                        ('FAILED', 'Failed'),
                    ],
                    default='CREATED',
                    max_length=20
                )),
                ('websocket_delivered', models.BooleanField(default=False)),
                ('delivery_attempts', models.IntegerField(default=0)),
                ('last_error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notification', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='log', to='notifications.notification')),
            ],
            options={
                'verbose_name': 'Notification Log',
                'verbose_name_plural': 'Notification Logs',
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', '-created_at'], name='notification_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read', '-created_at'], name='notification_user_unread_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_deleted', '-created_at'], name='notification_user_deleted_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['notification_type', 'created_at'], name='notification_type_created_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['priority', '-created_at'], name='notification_priority_idx'),
        ),
    ]
