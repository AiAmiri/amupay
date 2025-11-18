# Generated manually for adding saraf_location_google_map field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saraf_account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sarafaccount',
            name='saraf_location_google_map',
            field=models.URLField(blank=True, help_text='Google Maps location link for the saraf', max_length=500, null=True),
        ),
    ]

