# Generated by Django 5.0.6 on 2024-05-25 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0002_alter_emprestimo_livro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livro',
            name='sinopse',
            field=models.TextField(max_length=1200),
        ),
    ]