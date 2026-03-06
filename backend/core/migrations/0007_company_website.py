from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_unmatchedproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='website',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
