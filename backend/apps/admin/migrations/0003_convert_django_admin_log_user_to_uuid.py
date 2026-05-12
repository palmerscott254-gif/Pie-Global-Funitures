from django.db import migrations


def forward_convert_admin_log_user_to_uuid(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    schema_editor.execute(
        "ALTER TABLE IF EXISTS django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fkey;"
    )
    schema_editor.execute(
        "ALTER TABLE IF EXISTS django_admin_log DROP CONSTRAINT IF EXISTS \"django_admin_log_user_id_c564eba6_fk_auth_user_id\";"
    )
    schema_editor.execute(
        "ALTER TABLE django_admin_log ALTER COLUMN user_id DROP NOT NULL;"
    )
    schema_editor.execute(
        "UPDATE django_admin_log SET user_id = NULL;"
    )
    schema_editor.execute(
        "ALTER TABLE django_admin_log ALTER COLUMN user_id TYPE uuid USING (NULL::uuid);"
    )
    schema_editor.execute(
        "ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;"
    )


def reverse_convert_admin_log_user_to_uuid(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    schema_editor.execute(
        "ALTER TABLE IF EXISTS django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fkey;"
    )
    schema_editor.execute(
        "ALTER TABLE django_admin_log ALTER COLUMN user_id TYPE uuid USING (NULL::uuid);"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("pgf_admin", "0002_alter_adminauditlog_admin_user"),
        ("users", "0004_alter_user_options_alter_user_created_at_and_more"),
    ]

    operations = [
        migrations.RunPython(
            forward_convert_admin_log_user_to_uuid,
            reverse_convert_admin_log_user_to_uuid,
        )
    ]
