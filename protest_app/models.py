from django.db import models


class CountryModel(models.Model):
    country_name = models.CharField(
        verbose_name='name', max_length=255, unique=True)
    country_code = models.CharField(verbose_name='country code', max_length=3)
    currency = models.CharField(max_length=3)
    calling_code = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'country'
        verbose_name_plural = 'countries'

    def __str__(self):
        return self.country_name

class StatesModel(models.Model):
    country = models.ForeignKey(CountryModel, on_delete=models.CASCADE, related_name="states")
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'state'
        verbose_name_plural = 'states'
        unique_together = ['country', 'name']

    def __str__(self):
        return self.name


class CitiesModel(models.Model):
    country = models.ForeignKey(CountryModel, on_delete=models.CASCADE, related_name="cities")
    state = models.ForeignKey(StatesModel, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'city'
        verbose_name_plural = 'cities'
        unique_together = ['state', 'name']

    def __str__(self):
        return self.name


class Members(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=10)
    country = models.ForeignKey(CountryModel, on_delete=models.CASCADE, related_name="members", blank=True, null=True)
    state = models.ForeignKey(StatesModel, on_delete=models.CASCADE, related_name="members", blank=True, null=True)
    city = models.ForeignKey(CitiesModel, on_delete=models.CASCADE, related_name="members")
    why_join = models.TextField(max_length=800, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0, choices=[(0, 'Active'), (1, 'Deleted')])

    class Meta:
        verbose_name = 'member'
        verbose_name_plural = 'members'
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['city', '-created_at']),
            models.Index(fields=['state', '-created_at']),
            models.Index(fields=['country', '-created_at']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return self.full_name
