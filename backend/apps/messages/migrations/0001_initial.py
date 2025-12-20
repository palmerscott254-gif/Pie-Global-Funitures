# Generated migration for user_messages

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('new', 'New'), ('read', 'Read'), ('replied', 'Replied'), ('resolved', 'Resolved')], default='new', max_length=20)),
                ('reply_text', models.TextField(blank=True, null=True)),
                ('replied_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='usermessage',
            index=models.Index(fields=['status', '-created_at'], name='user_messag_status_idx'),
        ),
    ]
