import re
import pandas as pd
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier, _tree
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
import csv
import warnings
import pickle


class Health_Data():
    def __init__(self):
        self.training = pd.read_csv('Data/new_Training.csv', encoding='utf-8')
        self.testing = pd.read_csv('Data/new_Testing.csv', encoding='utf-8')
        self.cols = self.training.columns
        self.symptemList = self.cols.to_list()
        self.serverity_dict = self.getSeverityDict()
        self.precaution_dict = self.getprecautionDict()
        self.description_list = self.getDescriptionList()
        self.clf = self.initModel()
        self.le = self.mapToNum(self.training['prognosis'])
        self.reduced_data = self.training.groupby(self.training['prognosis']).max()
        pass

    def mapToNum(self,inp):
        le = preprocessing.LabelEncoder()
        le.fit(inp)
        return le
    
    def getSeverityDict(self):
        severityDictionary = dict()
        with open('MasterData/new_symptom_severity.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                _severity = {row[0]: row[1]}
                severityDictionary.update(_severity)
        return severityDictionary

    def getprecautionDict(self):
        precautionDictionary = dict()
        with open('MasterData/new_symptom_precaution.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                _prec = {row[0]: [row[1], row[2], row[3], row[4]]}
                precautionDictionary.update(_prec)
        return precautionDictionary

    def getDescriptionList(self):
        description_list = dict()
        with open('MasterData/new_symptom_Description.csv', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                _dis = {row[0]: row[1]}
                description_list.update(_dis)
        return description_list
    
    def calc_condition(self,exp, days):
        sum = 0
        for item in exp:
            sum = sum+ self.serverity_dict[item]
        if((sum*days)/(len(exp)+1) > 13):
            print("ඔබ වෛද්යවරයෙකුගෙන් උපදෙස් ලබා ගත යුතුය. ")
        else:
            print("එය එතරම් නරක නොවිය හැකි නමුත් ඔබ පූර්වාරක්ෂාව ගත යුතුය.")

    def initModel(self):
        with open('decision_tree_model.pkl', 'rb') as f:
           clf = pickle.load(f)
        return clf


class Health_Bot():
    def __init__(self,  healthData: Health_Data()):
        self.health_data = healthData
        self.le = health_Data.le

    

    def check_pattern(self, dis_list, inp):
        inp = self.filter(inp)
        pred_list = []
        patt = f"{inp}"
        regexp = re.compile(patt)
        pred_list = [item for item in dis_list if regexp.search(item)]
        if(len(pred_list) > 0):
            return 1, pred_list
        else:
            return 0, []
    
    def filter(self, inp):
        inp_list = inp.split(" ")
        if len(inp_list) == 1:
            return inp
        filters = ["ලක්ෂණය", "තියෙනවා", "මට", "මගේ", "මම","වගේ","අමාරුව","මගෙ","රිදෙනවා" ,"වෙලා"] 
        in_list = []
        for item in inp_list:
            if item not in filters:
                print(item)
                in_list.append(item)
        print(in_list)
        return " ".join(in_list)
    
    def getSymptom1(self,disease_input):
        print("\n ඔබට තියෙන රෝග ලක්ෂණයක් සදහන් කරන්න \t\t", end="->")
        conf, cnf_dis = self.check_pattern(self.health_data.symptemList, disease_input)
        conf, cnf_dis
        if conf == 1:
            conf_inp = 0
            disease_input = cnf_dis[conf_inp]
            print("ඔබ සදහන් කරන ලද ලක්ෂණ ", ", ".join(cnf_dis)) 
            output = "ඔබ සදහන් කරන ලද ලක්ෂණ ", ", ".join(cnf_dis)                            
            return  output                                                                            # (output, h1)
        else:
            print("සමාවෙන්න ඔබ කියන රෝග ලක්ෂණ ගැන මම දන්නේ නෑ ")
            output =  "සමාවෙන්න ඔබ කියන රෝග ලක්ෂණ ගැන මම දන්නේ නෑ"                          # (output)
            return output
    def print_disease(self,node):
        node = node[0]
        val = node.nonzero()
        disease = self.le.inverse_transform(val[0])
        return list(map(lambda x: x.strip(), list(disease)))
    
    def sec_predict(self,symptoms_exp):
        df = pd.read_csv('Data/new_Training.csv')
        X = df.iloc[:, :-1]
        y = df['prognosis']
        X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=20)
        rf_clf = DecisionTreeClassifier()
        rf_clf.fit(X_train, y_train)
        symptoms_dict = {symptom: index for index, symptom in enumerate(X)}
        input_vector = np.zeros(len(symptoms_dict))
        for item in symptoms_exp:
            input_vector[[symptoms_dict[item]]] = 1

        return rf_clf.predict([input_vector])

    def one_symptom(self,node, depth,disease_input):
        tree_ = self.health_data.clf.tree_ 
        feature_names = self.health_data.cols
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "සොයාගත නොහැක!"
            for i in tree_.feature
        ]
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]

            if name == disease_input:
                val = 1
            else:
                val = 0
            if val <= threshold:
                self.recurse(tree_.children_left[node], depth + 1,disease_input)
            else:
                self.health_data.symptoms_present.append(name)
                self.recurse(tree_.children_right[node], depth + 1,disease_input)
        else:
            present_disease = self.print_disease(tree_.value[node])
        
            red_cols = self.health_data.reduced_data.columns
            symptoms_given = red_cols[self.health_data.reduced_data.loc[present_disease].values[0].nonzero(
            )]
        
            print("මෙම රෝග ලක්ෂණ ඔබට තිබෙනවද  ")
            print(' '.join([f"{syms}? :" for syms in list(symptoms_given)]))                                  # (output, h2)

    def final_prediction(self, present_disease, second_prediction, symptoms_exp):
        second_prediction = self.sec_predict(symptoms_exp)
        
        if(present_disease[0] == second_prediction[0]):
            print("ඔබට සමහර විට තියෙන්න පුළුවන් ", present_disease[0])
            print(self.health_data.description_list[present_disease[0]])
        else:
            print("ඔබට සමහර විට තියෙන්න පුළුවන් ",
                      present_disease[0], "or ", second_prediction[0])
            print(self.health_data.description_list[present_disease[0]])
            print(self.health_data.description_list[second_prediction[0]])           
             
        precution_list = self.health_data.precaution_dict[present_disease[0]]
        print("පහත පියවර ගන්න ")
        print(", ".join([f"{j}" for i, j in enumerate(precution_list)]))


    def recurse(self,node, depth,disease_input):
        tree_ = self.health_data.clf.tree_ 
        feature_names = self.health_data.cols
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "සොයාගත නොහැක!"
            for i in tree_.feature
        ]
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]

            if name == disease_input:
                val = 1
            else:
                val = 0
            if val <= threshold:
                self.recurse(tree_.children_left[node], depth + 1,disease_input)
            else:
                self.health_data.symptoms_present.append(name)
                self.recurse(tree_.children_right[node], depth + 1,disease_input)
        else:
            present_disease = self.print_disease(tree_.value[node])
        
            red_cols = self.health_data.reduced_data.columns
            symptoms_given = red_cols[self.health_data.reduced_data.loc[present_disease].values[0].nonzero(
            )]
        
            print("මෙම රෝග ලක්ෂණ ඔබට තිබෙනවද  ")
            symptoms_exp = []
            for syms in list(symptoms_given):
                inp = ""
                print(syms, "? : ", end='')
                while True:
                    inp = input("")                                                       # (input)
                    if(inp == "ඔව්" or inp == "නැත"):
                        break
                    else:
                        print("නිසි පිළිතුරු සපයන්න i.e. (ඔව්/නෑ) : ", end="")
                if(inp == "ඔව්"):
                    symptoms_exp.append(syms)

            second_prediction = self.sec_predict(symptoms_exp)
            
            if(present_disease[0] == second_prediction[0]):
                print("ඔබට සමහර විට තියෙන්න පුළුවන් ", present_disease[0])
                print(self.health_data.description_list[present_disease[0]])
            else:
                print("ඔබට සමහර විට තියෙන්න පුළුවන් ",
                      present_disease[0], "or ", second_prediction[0])
                print(self.health_data.description_list[present_disease[0]])
                print(self.health_data.description_list[second_prediction[0]])

            
            precution_list = self.health_data.precaution_dict[present_disease[0]]
            print("පහත පියවර ගන්න: ")
            print(", ".join([f"{j}" for i, j in enumerate(precution_list)]))


    


health_Data = Health_Data()
health_bot = Health_Bot(health_Data)
health_bot.getSymptom1("මගේ නහය හිර වෙලා වගේ")         # (output ,h1)

health_bot.recurse(0, 1, "මගේ නහය හිර වෙලා වගේ")