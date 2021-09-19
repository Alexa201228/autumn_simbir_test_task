# Generated by Django 3.2.7 on 2021-09-19 16:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0005_auto_20210919_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.CreateModel(
            name='Lobby',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('users_online', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]