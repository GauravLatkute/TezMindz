from django.core.management.base import BaseCommand
from academics.models import Class, Subject, ClassSubject


CLASS_DATA = [
    {
        "grade_number": 1,
        "name": "Grade 1",
        "class_label": "Class 1",
        "stage": "Little Explorer",
        "age_group": "Age 6 - 7",
        "category": "primary",
        "modules": {"math": 20, "science": 18, "english": 18},
    },
    {
        "grade_number": 2,
        "name": "Grade 2",
        "class_label": "Class 2",
        "stage": "Curious Learner",
        "age_group": "Age 7 - 8",
        "category": "primary",
        "modules": {"math": 22, "science": 20, "english": 20},
    },
    {
        "grade_number": 3,
        "name": "Grade 3",
        "class_label": "Class 3",
        "stage": "Young Thinker",
        "age_group": "Age 8 - 9",
        "category": "primary",
        "modules": {"math": 26, "science": 22, "english": 22},
    },
    {
        "grade_number": 4,
        "name": "Grade 4",
        "class_label": "Class 4",
        "stage": "Smart Solver",
        "age_group": "Age 9 - 10",
        "category": "primary",
        "modules": {"math": 30, "science": 26, "english": 24},
    },
    {
        "grade_number": 5,
        "name": "Grade 5",
        "class_label": "Class 5",
        "stage": "Olympiad Challenger",
        "age_group": "Age 10 - 11",
        "category": "middle",
        "modules": {"math": 40, "science": 36, "english": 36},
    },
    {
        "grade_number": 6,
        "name": "Grade 6",
        "class_label": "Class 6",
        "stage": "Logic Master",
        "age_group": "Age 11 - 12",
        "category": "middle",
        "modules": {"math": 48, "science": 40, "english": 38},
    },
    {
        "grade_number": 7,
        "name": "Grade 7",
        "class_label": "Class 7",
        "stage": "Advanced Scholar",
        "age_group": "Age 12 - 13",
        "category": "senior",
        "modules": {"math": 56, "science": 48, "english": 44},
    },
    {
        "grade_number": 8,
        "name": "Grade 8",
        "class_label": "Class 8",
        "stage": "National Champion",
        "age_group": "Age 13 - 14",
        "category": "senior",
        "modules": {"math": 68, "science": 56, "english": 50},
    },
]


class Command(BaseCommand):
    help = "Seeds all 8 Classes (Grade 1-8) with subjects Math, Science and English linked."

    def handle(self, *args, **options):
        self.stdout.write("Seeding all 8 classes...")

        # Ensure subjects exist
        math, _ = Subject.objects.get_or_create(
            title="Mathematics",
            defaults={
                "subtitle": "Numbers • Logic • Geometry",
                "olympiad_code": "IMO (Maths Olympiad)",
                "icon_type": "math",
                "color_theme": {
                    "bg": "bg-[#FFFBEB]",
                    "border": "border-amber-200/70",
                    "badgeBg": "bg-amber-500",
                    "accentText": "text-amber-700",
                    "buttonBg": "bg-amber-100 hover:bg-amber-200 text-amber-900",
                },
            },
        )

        sci, _ = Subject.objects.get_or_create(
            title="Science",
            defaults={
                "subtitle": "Physics • Chemistry • Biology",
                "olympiad_code": "NSO (Science Olympiad)",
                "icon_type": "science",
                "color_theme": {
                    "bg": "bg-[#ECFDF5]",
                    "border": "border-emerald-200/70",
                    "badgeBg": "bg-emerald-500",
                    "accentText": "text-emerald-700",
                    "buttonBg": "bg-emerald-100 hover:bg-emerald-200 text-emerald-900",
                },
            },
        )

        eng, _ = Subject.objects.get_or_create(
            title="English",
            defaults={
                "subtitle": "Grammar • Vocabulary • Comprehension",
                "olympiad_code": "IEO (English Olympiad)",
                "icon_type": "english",
                "color_theme": {
                    "bg": "bg-[#FFF1F2]",
                    "border": "border-rose-200/70",
                    "badgeBg": "bg-rose-500",
                    "accentText": "text-rose-700",
                    "buttonBg": "bg-rose-100 hover:bg-rose-200 text-rose-900",
                },
            },
        )

        subjects_map = {
            "math": math,
            "science": sci,
            "english": eng,
        }

        created_count = 0
        updated_count = 0

        for cls_data in CLASS_DATA:
            modules = cls_data.pop("modules")

            cls_obj, created = Class.objects.get_or_create(
                grade_number=cls_data["grade_number"],
                defaults={k: v for k, v in cls_data.items()},
            )

            if created:
                created_count += 1
                self.stdout.write(f"  [CREATED] {cls_obj.class_label}")
            else:
                # Update metadata in case it changed
                for field, val in cls_data.items():
                    setattr(cls_obj, field, val)
                cls_obj.save()
                updated_count += 1
                self.stdout.write(f"  [UPDATED] {cls_obj.class_label}")

            # Link subjects
            for subj_key, subj_obj in subjects_map.items():
                cs, cs_created = ClassSubject.objects.get_or_create(
                    student_class=cls_obj,
                    subject=subj_obj,
                    defaults={"total_modules": modules[subj_key]},
                )
                if cs_created:
                    self.stdout.write(f"    -> Linked {subj_obj.title} ({modules[subj_key]} modules)")
                else:
                    cs.total_modules = modules[subj_key]
                    cs.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! {created_count} classes created, {updated_count} classes updated."
            )
        )
