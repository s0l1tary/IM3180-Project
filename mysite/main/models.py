from django.db import models

class Questions(models.Model):
    text = models.CharField(max_length = 255)
    option_A = models.CharField(max_length = 255)
    option_B = models.CharField(max_length = 255)
    option_C = models.CharField(max_length = 255)
    option_D = models.CharField(max_length = 255)
    correct_option = models.CharField(
        max_length = 1,
        choices = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    def __str__(self):
        return self.text
    