from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menuapp', '0005_order_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('preparing', 'Preparing'),
                    ('ready', 'Ready'),
                    ('on_the_way', 'On the way'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
