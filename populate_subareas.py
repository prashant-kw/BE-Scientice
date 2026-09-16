import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from therapyareas.models import TherapyArea, TherapySubArea

data = {
    "Cardiology": [
        "American College of Cardiology (ACC)",
        "European Society of Cardiology (ESC)",
        "Society for Cardiovascular Angiography & Interventions (SCAI)",
        "Heart Failure Society of America (HFSA)",
        "Transcatheter Cardiovascular Therapeutics (TCT)",
        "American Heart Association (AHA)" 
    ],
    "Diabetes": [
        "Advanced Technologies & Treatments for Diabetes (ATTD)",
        "American Diabetes Association (ADA)",
        "Association of Diabetes Care & Education Specialists (ADCES)",
        "European Association for the Study of Diabetes (EASD)",
        "European Diabetes Meeting (EDM)" 
    ],
    "Neurology": [
        "American Academy of Neurology (AAN)",
        "European Academy of Neurology (EAN)",
        "American Neurological Association (ANA)",
        "American Epilepsy Society (AES)" 
    ],
    "Dermatology": [
        "American Academy of Dermatology (AAD)",
        "European Academy of Dermatology and Venereology (EADV)",
        "European Society for Dermatological Research (ESDR)"
    ],
    "Nephrology": [
        "World Congress of Nephrology (WCN)",
        "European Renal Association (ERA)",
        "American Society of Nephrology (ASN)" 
    ],
    "Gastroenterology/Hepatology": [
        "Digestive Disease Week (DDW)",
        "European Society of Gastrointestinal Endoscopy (ESGE)",
        "European Association for the Study of the Liver (EASL)",
        "American College of Gastroenterology (ACG)",
        "United European Gastroenterology (UEG)",
        "European Society for Paediatric Gastroenterology, Hepatology and Nutrition (ESPGHAN)" 
    ],
    "Pulmonology": [
        "American Thoracic Society (ATS)",
        "American College of Chest Physicians (CHEST)",
        "European Respiratory Society (ERS)"
    ],
    "Urology": [
        "European Association of Urology (EAU)",
        "American Urological Association (AUA)" 
    ],
    "Gynaecology / Reproductive Health": [
        "American College of Obstetricians and Gynecologists (ACOG)",
        "European Society of Human Reproduction and Embryology (ESHRE)",
        "American Society for Reproductive Medicine (ASRM)" 
    ],
    "Oncology": [
        "American Society of Clinical Oncology (ASCO)",
        "European Society for Medical Oncology (ESMO)"
    ]
}

def populate():
    print("Starting population...")
    for index, (area_name, sub_areas) in enumerate(data.items()):
        # Try to find existing therapy area or create it
        therapy_area, created = TherapyArea.objects.get_or_create(
            name=area_name,
            defaults={
                'order': index + 1,
                'is_active': True,
                'icon': 'Activity' # default icon
            }
        )
        
        if created:
            print(f"Created new Therapy Area: {area_name}")
        else:
            print(f"Found existing Therapy Area: {area_name}")
            
        for order_idx, sub_name in enumerate(sub_areas):
            sub_area, sub_created = TherapySubArea.objects.get_or_create(
                therapy_area=therapy_area,
                name=sub_name,
                defaults={
                    'order': order_idx + 1,
                    'is_active': True
                }
            )
            if sub_created:
                print(f"  -> Added Sub-Specialty: {sub_name}")
            else:
                print(f"  -> Sub-Specialty already exists: {sub_name}")

if __name__ == '__main__':
    populate()
    print("Done!")
