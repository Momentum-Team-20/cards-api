# Generated by Django 5.0a1 on 2023-12-19 21:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0010_card_font_size_card_text_align"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="back_background_color",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
