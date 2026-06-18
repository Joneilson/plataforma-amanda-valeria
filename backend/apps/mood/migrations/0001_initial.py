import django.db.models.deletion
from django.db import migrations, models

import apps.common.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoodEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('data', models.DateField(verbose_name='data')),
                ('nivel', models.PositiveSmallIntegerField(choices=[(1, 'Muito ruim'), (2, 'Ruim'), (3, 'Neutro'), (4, 'Bom'), (5, 'Ótimo')], verbose_name='nível')),
                ('emocoes', models.JSONField(blank=True, default=list, verbose_name='emoções')),
                ('anotacao', apps.common.fields.EncryptedTextField(blank=True, verbose_name='anotação')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mood_entries', to='patients.patient')),
            ],
            options={
                'verbose_name': 'registro de humor',
                'verbose_name_plural': 'registros de humor',
                'ordering': ('-data',),
            },
        ),
        migrations.AddConstraint(
            model_name='moodentry',
            constraint=models.UniqueConstraint(fields=('patient', 'data'), name='unique_mood_per_patient_day'),
        ),
        migrations.AddIndex(
            model_name='moodentry',
            index=models.Index(fields=['patient', 'data'], name='mood_patient_data_idx'),
        ),
    ]
