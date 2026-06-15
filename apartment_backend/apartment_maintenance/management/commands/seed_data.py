from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apartment_maintenance.models import Wing, Floor, Flat, FlatOwner, MaintenanceDue
import datetime


class Command(BaseCommand):
    help = 'Seed real data from Radhika Apartment PDF (March 2026)'

    FLOOR_DATA = [
        (0, "Ground Floor"),
        (1, "First Floor"),
        (2, "Second Floor"),
        (3, "Third Floor"),
    ]

    # (wing, floor_num, room_no, flat_id, owner_name, phone, pending_months, balance)
    FLAT_DATA = [
        # ── B WING ──────────────────────────────────────────
        # Ground – 4 rooms
        ("B", 0, 1, "B-001", "Dhanle",               "9800000001", 3,  1200),
        ("B", 0, 2, "B-002", "Pawar Vijay D",         "9800000002", 0,  0),
        ("B", 0, 3, "B-003", "Parab Sanjay Madhukar", "9800000003", 0,  0),
        ("B", 0, 4, "B-004", "Bhane",                 "9800000004", 3,  1200),
        # First – 6 rooms
        ("B", 1, 1, "B-101", "Warpe Santosh",         "9800000005", 0,  0),
        ("B", 1, 2, "B-102", "Pal Bhulalya",          "9800000006", 0,  0),
        ("B", 1, 3, "B-103", "Mukhiya Ramchandra",    "9800000007", 0,  0),
        ("B", 1, 4, "B-104", "Singh Dileep Sachin",   "9800000008", 11, 4400),
        ("B", 1, 5, "B-105", "Bhane",                 "9800000009", 24, 9600),
        ("B", 1, 6, "B-106", "Bhane (Dongre)",        "9800000010", 0,  0),
        # Second – 6 rooms
        ("B", 2, 1, "B-201", "Gangude Bharat",        "9800000011", 3,  1200),
        ("B", 2, 2, "B-202", "Kale Pravin",           "9800000012", 6,  2400),
        ("B", 2, 3, "B-203", "Singh Ritesh",          "9800000013", 1,  400),
        ("B", 2, 4, "B-204", "Mulani Zainuddin",      "9800000014", 4,  1600),
        ("B", 2, 5, "B-205", "Bhane",                 "9800000015", 2,  800),
        ("B", 2, 6, "B-206", "Kawale Gaurav",         "9800000016", 1,  400),
        # Third – 6 rooms
        ("B", 3, 1, "B-301", "Mulani Samir",          "9800000017", 3,  1200),
        ("B", 3, 2, "B-302", "Sonawane Sopan",        "9800000018", 1,  400),
        ("B", 3, 3, "B-303", "Sonawane Vilas",        "9800000019", 5,  2000),
        ("B", 3, 4, "B-304", "Bhane",                 "9800000020", 3,  1200),
        ("B", 3, 5, "B-305", "Bhane",                 "9800000021", 0,  0),
        ("B", 3, 6, "B-306", "Bhane",                 "9800000022", 3,  1200),
        # ── A WING ──────────────────────────────────────────
        # Ground – 2 rooms
        ("A", 0, 1, "A-001", "Rajput Gajendra",       "9800000023", 14, 5600),
        ("A", 0, 2, "A-002", "Bhane",                 "9800000024", 4,  1600),
        # First – 5 rooms
        ("A", 1, 1, "A-101", "Pawar Sujata",          "9800000025", 3,  1200),
        ("A", 1, 2, "A-102", "Tripathi Sanjay",       "9800000026", 7,  2800),
        ("A", 1, 3, "A-103", "Bhane",                 "9800000027", 0,  0),
        ("A", 1, 4, "A-104", "Chauhan Ramchandra",    "9800000028", 5,  2000),
        ("A", 1, 5, "A-105", "Kale Kishor Dashrath",  "9800000029", 0,  0),
        # Second – 5 rooms
        ("A", 2, 1, "A-201", "Rasal Ganesh",          "9800000030", 1,  400),
        ("A", 2, 2, "A-202", "Jaiswal Surendra",      "9800000031", 2,  800),
        ("A", 2, 3, "A-203", "Kanojiya Bhimsen",      "9800000032", 0,  0),
        ("A", 2, 4, "A-204", "Kale Sunil",            "9800000033", 10, 4000),
        ("A", 2, 5, "A-205", "Bhane",                 "9800000034", 8,  3200),
        # Third – 5 rooms
        ("A", 3, 1, "A-301", "Sonawane Milind",       "9800000035", 2,  800),
        ("A", 3, 2, "A-302", "Pawar Sharad",          "9800000036", 3,  1200),
        ("A", 3, 3, "A-303", "Bhane",                 "9800000037", 3,  1200),
        ("A", 3, 4, "A-304", "Sonawane Nivritti",     "9800000038", 6,  2400),
        ("A", 3, 5, "A-305", "Bhane",                 "9800000039", 1,  400),
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🏢  Seeding Radhika Apartment — March 2026 data...\n'))

        # ── Superuser ──────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@radhika.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅  Superuser created  →  admin / admin123'))
        else:
            self.stdout.write('⚠️   Superuser already exists, skipping.')

        # ── Wings ──────────────────────────────────────────
        wing_a, _ = Wing.objects.get_or_create(name='A')
        wing_b, _ = Wing.objects.get_or_create(name='B')
        wings = {'A': wing_a, 'B': wing_b}
        self.stdout.write(self.style.SUCCESS('✅  Wings A & B ready'))

        # ── Floors ─────────────────────────────────────────
        floors = {}
        for num, name in self.FLOOR_DATA:
            floor, _ = Floor.objects.get_or_create(number=num, defaults={'name': name})
            floors[num] = floor
        self.stdout.write(self.style.SUCCESS('✅  4 floors ready (Ground / First / Second / Third)'))

        # ── Flats + Owners + Dues ──────────────────────────
        created_flats = 0
        created_dues  = 0

        for (wing_name, floor_num, room, flat_id, owner_name,
             phone, pending_months, balance) in self.FLAT_DATA:

            floor = floors[floor_num]
            wing  = wings[wing_name]

            # Flat
            flat, flat_new = Flat.objects.get_or_create(
                flat_number=flat_id,
                defaults={
                    'wing':               wing,
                    'floor':              floor,
                    'room_number':        room,
                    'monthly_maintenance': 400,
                    'is_occupied':        True,
                }
            )
            if flat_new:
                created_flats += 1

            # Owner
            safe_name = owner_name.split()[0].lower().replace('(','').replace(')','')
            FlatOwner.objects.get_or_create(
                flat=flat,
                defaults={
                    'name':  owner_name,
                    'phone': phone,
                    'email': f'{safe_name}@gmail.com',
                }
            )

            # Pending dues — work backwards from March 2026
            if pending_months > 0:
                base_year, base_month = 2026, 3
                for i in range(pending_months):
                    m = base_month - i
                    y = base_year
                    while m <= 0:
                        m += 12
                        y -= 1
                    _, due_new = MaintenanceDue.objects.get_or_create(
                        flat=flat, month=m, year=y,
                        defaults={
                            'amount':   400,
                            'due_date': datetime.date(y, m, 10),
                            'is_paid':  False,
                        }
                    )
                    if due_new:
                        created_dues += 1

        # ── Summary ────────────────────────────────────────
        total_flats = Flat.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f'✅  {created_flats} flats created  |  {created_dues} dues generated'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'✅  Total flats in DB: {total_flats}  '
            f'(B Wing: 22  |  A Wing: 17)'
        ))
        self.stdout.write(self.style.SUCCESS(
            '✅  Total outstanding: ₹56,800  '
            '(B Wing ₹29,200  |  A Wing ₹27,600)'
        ))
        self.stdout.write('')
        self.stdout.write('   🌐  Admin panel  →  http://localhost:8000/admin/')
        self.stdout.write('   🔑  Login        →  admin / admin123')
        self.stdout.write('   📡  API root     →  http://localhost:8000/api/')
        self.stdout.write('')
