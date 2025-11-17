# models.py
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Banner(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.title

class Promotion(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='promotions/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.title

class HomeAd(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='home_ads/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Home Ad'
        verbose_name_plural = 'Home Ads'
        
    def __str__(self):
        return self.title









class CurrencySettingsTable(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('RUB', 'Russian Ruble (₽)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('ZAR', 'South African Rand (R)'),
        ('NZD', 'New Zealand Dollar (NZ$)'),
        ('SEK', 'Swedish Krona (kr)'),
        ('NOK', 'Norwegian Krone (kr)'),
        ('DKK', 'Danish Krone (kr)'),
        ('SGD', 'Singapore Dollar (S$)'),
        ('HKD', 'Hong Kong Dollar (HK$)'),
        ('KRW', 'South Korean Won (₩)'),
        ('MXN', 'Mexican Peso (MX$)'),
        ('TWD', 'New Taiwan Dollar (NT$)'),
        ('THB', 'Thai Baht (฿)'),
        ('MYR', 'Malaysian Ringgit (RM)'),
        ('IDR', 'Indonesian Rupiah (Rp)'),
        ('PHP', 'Philippine Peso (₱)'),
        ('VND', 'Vietnamese Dong (₫)'),
        ('AED', 'UAE Dirham (د.إ)'),
        ('SAR', 'Saudi Riyal (﷼)'),
        ('QAR', 'Qatari Riyal (ر.ق)'),
        ('KWD', 'Kuwaiti Dinar (د.ك)'),
        ('BHD', 'Bahraini Dinar (ب.د)'),
        ('OMR', 'Omani Rial (﷼)'),
        ('EGP', 'Egyptian Pound (E£)'),
        ('NGN', 'Nigerian Naira (₦)'),
        ('KES', 'Kenyan Shilling (KSh)'),
        ('TZS', 'Tanzanian Shilling (TSh)'),
        ('UGX', 'Ugandan Shilling (USh)'),
        ('GHS', 'Ghanaian Cedi (₵)'),
        ('MAD', 'Moroccan Dirham (د.م.)'),
        ('DZD', 'Algerian Dinar (دج)'),
        ('TND', 'Tunisian Dinar (د.ت)'),
        ('XOF', 'West African CFA Franc (CFA)'),
        ('XAF', 'Central African CFA Franc (FCFA)'),
        ('MUR', 'Mauritian Rupee (₨)'),
        ('SCR', 'Seychellois Rupee (₨)'),
        ('PKR', 'Pakistani Rupee (₨)'),
        ('BDT', 'Bangladeshi Taka (৳)'),
        ('LKR', 'Sri Lankan Rupee (Rs)'),
        ('NPR', 'Nepalese Rupee (Rs)'),
        ('MMK', 'Myanmar Kyat (Ks)'),
        ('KHR', 'Cambodian Riel (៛)'),
        ('LAK', 'Lao Kip (₭)'),
        ('BND', 'Brunei Dollar (B$)'),
        ('FJD', 'Fijian Dollar (FJ$)'),
        ('PGK', 'Papua New Guinean Kina (K)'),
        ('SBD', 'Solomon Islands Dollar (SI$)'),
        ('WST', 'Samoan Tala (T)'),
        ('TOP', 'Tongan Paʻanga (T$)'),
        ('VUV', 'Vanuatu Vatu (Vt)'),
        ('NZD', 'New Zealand Dollar (NZ$)'),
        ('ARS', 'Argentine Peso ($)'),
        ('CLP', 'Chilean Peso ($)'),
        ('COP', 'Colombian Peso ($)'),
        ('PEN', 'Peruvian Sol (S/)'),
        ('UYU', 'Uruguayan Peso ($U)'),
        ('PYG', 'Paraguayan Guarani (₲)'),
        ('BOB', 'Bolivian Boliviano (Bs)'),
        ('VEF', 'Venezuelan Bolívar (Bs)'),
        ('GTQ', 'Guatemalan Quetzal (Q)'),
        ('CRC', 'Costa Rican Colón (₡)'),
        ('DOP', 'Dominican Peso (RD$)'),
        ('JMD', 'Jamaican Dollar (J$)'),
        ('TTD', 'Trinidad and Tobago Dollar (TT$)'),
        ('BBD', 'Barbadian Dollar (Bds$)'),
        ('BSD', 'Bahamian Dollar (B$)'),
        ('HTG', 'Haitian Gourde (G)'),
        ('CUP', 'Cuban Peso (₱)'),
        ('ANG', 'Netherlands Antillean Guilder (ƒ)'),
        ('AWG', 'Aruban Florin (ƒ)'),
        ('SRD', 'Surinamese Dollar ($)'),
        ('GYD', 'Guyanese Dollar (G$)'),
        ('LRD', 'Liberian Dollar (L$)'),
        ('SLL', 'Sierra Leonean Leone (Le)'),
        ('BWP', 'Botswana Pula (P)'),
        ('ZMW', 'Zambian Kwacha (ZK)'),
        ('MWK', 'Malawian Kwacha (MK)'),
        ('MZN', 'Mozambican Metical (MT)'),
        ('ETB', 'Ethiopian Birr (Br)'),
        ('SDG', 'Sudanese Pound (SDG)'),
        ('SSP', 'South Sudanese Pound (£)'),
        ('MGA', 'Malagasy Ariary (Ar)'),
        ('KMF', 'Comorian Franc (CF)'),
        ('DJF', 'Djiboutian Franc (Fdj)'),
        ('BIF', 'Burundian Franc (FBu)'),
        ('RWF', 'Rwandan Franc (FRw)'),
        ('CDF', 'Congolese Franc (FC)'),
        ('AOA', 'Angolan Kwanza (Kz)'),
        ('MOP', 'Macanese Pataca (P)'),
        ('MVR', 'Maldivian Rufiyaa (Rf)'),
        ('KZT', 'Kazakhstani Tenge (₸)'),
        ('UZS', 'Uzbekistani Soʻm (soʻm)'),
        ('TJS', 'Tajikistani Somoni (ЅM)'),
        ('KGS', 'Kyrgyzstani Som (сом)'),
        ('AFN', 'Afghan Afghani (؋)'),
        ('IRR', 'Iranian Rial (﷼)'),
        ('IQD', 'Iraqi Dinar (ع.د)'),
        ('SYP', 'Syrian Pound (£S)'),
        ('LBP', 'Lebanese Pound (ل.ل)'),
        ('JOD', 'Jordanian Dinar (د.ا)'),
        ('ILS', 'Israeli New Shekel (₪)'),
        ('TRY', 'Turkish Lira (₺)'),
        ('AZN', 'Azerbaijani Manat (₼)'),
        ('GEL', 'Georgian Lari (₾)'),
        ('AMD', 'Armenian Dram (֏)'),
    ]
    
    currency_code = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        unique=True,
        verbose_name='Currency Code'
    )
    
    currency_symbol = models.CharField(
        max_length=5,
        default='$',
        verbose_name='Currency Symbol'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Currency'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Currency Setting'
        verbose_name_plural = 'Currency Settings'
        ordering = ['currency_code']
    
    def __str__(self):
        return f"{self.currency_code} ({self.currency_symbol})"
    
    def clean(self):
        # Ensure only one active currency exists
        if self.is_active:
            active_currencies = CurrencySettingsTable.objects.filter(is_active=True)
            if self.pk:
                active_currencies = active_currencies.exclude(pk=self.pk)
            if active_currencies.exists():
                raise ValidationError('Only one currency can be active at a time.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)