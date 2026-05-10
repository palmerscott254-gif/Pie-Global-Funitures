from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pgf_admin", "0002_alter_adminauditlog_admin_user"),
        ("users", "0004_alter_user_options_alter_user_created_at_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "BEGIN;"
                "-- Drop legacy FK constraints (both Django defaults and custom names)\n"
                "ALTER TABLE IF EXISTS django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fkey;\n"
                "ALTER TABLE IF EXISTS django_admin_log DROP CONSTRAINT IF EXISTS \"django_admin_log_user_id_c564eba6_fk_auth_user_id\";\n"
                "-- Drop NOT NULL constraint before setting values to NULL\n"
                "ALTER TABLE django_admin_log ALTER COLUMN user_id DROP NOT NULL;\n"
                "-- Set all user_id values to NULL (legacy integer IDs cannot be cast to uuid)\n"
                "UPDATE django_admin_log SET user_id = NULL;\n"
                "-- Alter column type to uuid\n"
                "ALTER TABLE django_admin_log ALTER COLUMN user_id TYPE uuid USING (NULL::uuid);\n"
                "-- Recreate FK referencing new users(id) column\n"
                "ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;\n"
                "COMMIT;"
            ),
            reverse_sql=(
                "BEGIN;"
                "ALTER TABLE IF EXISTS django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fkey;\n"
                "ALTER TABLE django_admin_log ALTER COLUMN user_id TYPE integer USING (NULL::integer);\n"
                "ALTER TABLE django_admin_log ALTER COLUMN user_id SET NOT NULL;\n"
                "ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE;\n"
                "COMMIT;"
            ),
        )
    ]
