from django.core.management.base import BaseCommand
from django.db.models import Q
from core.models import Service, Fleet


class Command(BaseCommand):
    help = 'Normalize ordering for active Services and Fleet vehicles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['all', 'services', 'fleet'],
            help='Normalize services, fleet, or both'
        )

    def handle(self, *args, **options):
        target_type = options['type']
        
        if target_type in ['all', 'services']:
            self.normalize_services()
        
        if target_type in ['all', 'fleet']:
            self.normalize_fleet()
        
        self.stdout.write(
            self.style.SUCCESS('✓ Ordering normalization complete!')
        )

    def normalize_services(self):
        self.stdout.write('Normalizing Service orders...')
        
        # Get all active services with duplicate or missing orders
        active_services = Service.objects.filter(is_active=True).order_by('order', 'id')
        
        before_count = active_services.count()
        changes = 0
        
        for index, service in enumerate(active_services, start=1):
            if service.order != index:
                self.stdout.write(
                    f'  Updating: {service.title} (#{service.order} → #{index})'
                )
                service.order = index
                service.save(update_fields=['order'])
                changes += 1
        
        if changes == 0:
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ All {before_count} services already properly ordered')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Fixed {changes} service(s) out of {before_count}')
            )

    def normalize_fleet(self):
        from core.utils import normalize_fleet_orders

        self.stdout.write('Normalizing Fleet orders...')
        before_count = Fleet.objects.filter(is_active=True).count()
        if before_count == 0:
            self.stdout.write('  No fleet vehicles found')
            return
        before_map = dict(
            Fleet.objects.filter(is_active=True).values_list('id', 'order')
        )
        normalize_fleet_orders()
        after_map = dict(
            Fleet.objects.filter(is_active=True).values_list('id', 'order')
        )
        changes = sum(1 for pk, o in before_map.items() if after_map.get(pk) != o)
        if changes == 0:
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ All {before_count} fleet vehicles already properly ordered')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Fixed order for {changes} fleet vehicle(s) out of {before_count}')
            )
