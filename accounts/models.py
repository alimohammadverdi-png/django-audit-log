# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
   
    class Role(models.TextChoices):
        USER = 'user', 'User'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin'
    objects = UserManager()
    
    # 1. فیلد username را اضافه کن (اگر قبلا نداشتی)
    username = models.CharField(max_length=150, unique=True)
    
    # 2. فیلد role اصلاح‌شده
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # 3. فیلدهای الزامی برای AbstractBaseUser
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    # توجه: اگر فیلدهای دیگری مثل email, first_name, last_name داری
    # باید آن‌ها را هم اینجا تعریف کنی.
    # اما برای رفع مشکل فعلی، اینها کافی هستند.

    # Managers و سایر کدها...
