import csv


def getAllSymptomps():
    """Get all symptomps from csv file"""
    with open('MasterData/new_Symptom_severity.csv', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        symptomps = []
        for row in csv_reader:
            symptomps.append(row[0])
    return symptomps


def capture_diseases(sentence, disease_list):
    captured_diseases = []
    sentence = sentence.lower()
    
    for disease in disease_list:
        words = disease.lower().split()
        if all(word in sentence for word in words):
            captured_diseases.append(disease)
    
    return captured_diseases

# Example usage
disease_list = getAllSymptomps()
sentence = "කිවිසුම් යාම,වෙව්ලීම,කදුළු ගැලීම වගේ ඒවා වෙන්නේ මොකද "

captured = capture_diseases(sentence, disease_list)
print(captured)