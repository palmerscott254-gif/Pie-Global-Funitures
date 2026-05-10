# Generated migration for User model admin fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, db_index=True, help_text='Designates whether user is staff (can access admin)'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, db_index=True, help_text='Designates whether user is superuser (full admin)'),
        ),
    ]
