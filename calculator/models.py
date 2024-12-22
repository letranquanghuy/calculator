from django.db import models

# Create your models here.
class CalculationHistory(models.Model):
    expression = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # To keep track of when the record was created

    def __str__(self):
        return f"{self.expression} = {self.result}"