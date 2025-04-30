from django.db import models

class Subscription(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.email} - {'Active' if self.is_active else 'Inactive'}"

    def save(self, *args, **kwargs):
        if self.is_active:
            self.user.is_subscribed = True
        else:
            self.user.is_subscribed = False
        self.user.save()
        super().save(*args, **kwargs)