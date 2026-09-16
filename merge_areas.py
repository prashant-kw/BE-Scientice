import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from therapyareas.models import TherapyArea, TherapySubArea

def merge(old_name, new_name):
    try:
        old = TherapyArea.objects.get(name=old_name)
        new = TherapyArea.objects.get(name=new_name)
        
        # move subareas
        subs = TherapySubArea.objects.filter(therapy_area=old)
        for sub in subs:
            sub.therapy_area = new
            sub.save()
            print(f"Moved {sub.name} to {new_name}")
            
        old.delete()
        print(f"Deleted old {old_name}")
    except TherapyArea.DoesNotExist:
        print(f"Skipping merge for {old_name} -> {new_name}: One of them doesn't exist.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Merging Diabetes into Diabetology...")
    merge("Diabetes", "Diabetology")
    print("Done")
