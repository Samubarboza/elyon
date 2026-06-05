from django.db import migrations


PLANS = [
    ('Starter', 3),
    ('Profesional', 6),
    ('Bussines', 15),
]


def create_plans_and_company(apps, schema_editor):
    Plan = apps.get_model('users', 'Plan')
    Company = apps.get_model('users', 'Company')
    for plan_name, max_users in PLANS:
        Plan.objects.get_or_create(name=plan_name, defaults={'max_users': max_users})
    starter_plan = Plan.objects.get(name='Starter')
    Company.objects.get_or_create(pk=1, defaults={'name': 'Mi empresa', 'plan': starter_plan})


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_plan_company'),
    ]

    operations = [
        migrations.RunPython(create_plans_and_company, migrations.RunPython.noop),
    ]
