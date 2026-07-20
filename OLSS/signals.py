from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Student
import random
from django.utils.timezone import now

@receiver(pre_save, sender=Student)
def generate_registration_id(sender, instance, **kwargs):
    if not instance.id:  # এখন primary key
        year = now().year
        random_number = random.randint(1000, 9999)
        instance.id = f"REG{year}{random_number}"
