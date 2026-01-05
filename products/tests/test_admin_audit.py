from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from products.admin import ProductAdmin
from products.models import Product, Category
from audit_log.models import AuditLog


User = get_user_model()


class DummyAdminSite(AdminSite):
    pass


class AdminAuditLogTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = DummyAdminSite()

        self.superuser = User.objects.create_superuser(
            username="admin",
            password="pass1234",
        )

        self.user = User.objects.create_user(
            username="user",
            password="pass1234",
        )

        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category",
        )

        # ✅ Products with UNIQUE sku
        self.products = [
            Product.objects.create(
                category=self.category,
                name=f"Product {i}",
                sku=f"TEST-SKU-{i}",
                price=100,
                stock=10,
                owner=self.superuser,
                is_active=True,
            )
            for i in range(3)
        ]

        self.product_admin = ProductAdmin(Product, self.admin_site)

    # 1️⃣ Bulk Update Audit
    def test_bulk_update_audit_log_created(self):
        request = self.factory.post("/")
        request.user = self.superuser

        queryset = Product.objects.filter(id__in=[p.id for p in self.products])

        self.product_admin.bulk_deactivate_products(
            request=request,
            queryset=queryset,
        )

        log = AuditLog.objects.filter(action="bulk_update").last()

        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.superuser)
        self.assertEqual(log.object_type, "Product")
        self.assertIn("before", log.changes)
        self.assertIn("after", log.changes)

    # 2️⃣ Bulk Delete Audit (Admin Checkbox)
    def test_bulk_delete_audit_log_created(self):
        changelist_url = reverse("admin:products_product_changelist")
        request = self.factory.post(changelist_url)
        request.user = self.superuser

        queryset = Product.objects.filter(id__in=[p.id for p in self.products])

        self.product_admin.delete_queryset(request, queryset)

        log = AuditLog.objects.filter(action="bulk_delete").last()

        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.superuser)
        self.assertEqual(log.object_type, "Product")
        self.assertIn("count", log.changes)

    # 3️⃣ Instance Delete Signal Check
    def test_instance_delete_signal_still_works(self):
        product = Product.objects.create(
            category=self.category,
            name="Instance Delete",
            sku="INSTANCE-DELETE-SKU",
            price=200,
            stock=5,
            owner=self.superuser,
        )

        product.delete()

        log = AuditLog.objects.filter(
            action="delete",
            object_id=str(product.id)
        ).last()

        self.assertIsNotNone(log)
        self.assertIsNone(log.user)  # system / shell delete

    # 4️⃣ Permission Check for Bulk Actions
    def test_bulk_action_permission_denied_for_non_superuser(self):
        request = self.factory.post("/")
        request.user = self.user

        queryset = Product.objects.all()

        with self.assertRaises(PermissionDenied):
            self.product_admin.bulk_deactivate_products(
                request=request,
                queryset=queryset,
            )
